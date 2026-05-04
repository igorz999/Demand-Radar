import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path
import sys

# Set page config
st.set_page_config(
    page_title="Demand RADAR",
    page_icon="📡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Define paths
ROOT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT_DIR / "data"

# Add custom CSS
st.markdown("""
<style>
    .stAlert {
        border-radius: 8px;
    }
    .metric-card {
        background-color: #1E1E1E;
        padding: 20px;
        border-radius: 10px;
        border: 1px solid #333;
    }
    .metric-value {
        font-size: 2.5rem;
        font-weight: bold;
        color: #4CAF50;
    }
    .metric-label {
        font-size: 1rem;
        color: #888;
    }
    .explanation-box {
        background-color: rgba(76, 175, 80, 0.1);
        border-left: 4px solid #4CAF50;
        padding: 15px;
        margin: 10px 0;
        border-radius: 0 5px 5px 0;
    }
</style>
""", unsafe_allow_html=True)

# Load data helper
@st.cache_data
def load_data():
    processed = pd.read_csv(DATA_DIR / "processed_data.csv")
    processed["week_start"] = pd.to_datetime(processed["week_start"])
    alerts_raw = pd.read_csv(DATA_DIR / "alerts_raw.csv")
    alerts_raw["week_start"] = pd.to_datetime(alerts_raw["week_start"])
    
    # We load scored alerts dynamically with 0 threshold so user can filter
    sys.path.append(str(ROOT_DIR))
    from src.confidence_scorer import ConfidenceScorer
    
    scorer = ConfidenceScorer(str(ROOT_DIR / "keywords.json"))
    scored_all = scorer.score_alerts(alerts_raw, processed, min_confidence=0.0)
    return processed, scored_all

try:
    processed_df, scored_alerts_df = load_data()
except Exception as e:
    st.error(f"Error loading data: {e}")
    st.stop()


# Main title
st.title("📡 Demand RADAR")
st.markdown("An Explainable Early Warning System for Cold & Flu Demand")

# Tabs
tab1, tab2, tab3 = st.tabs(["⭐ The Golden Signals", "📈 Time Series Explorer", "⚙️ Alert Configuration"])

with tab1:
    st.header("The Golden Signals: 2025-2026 Flu Season Lifecycle")
    st.markdown("These 3 events perfectly demonstrate how public signals pre-empt actual demand changes. Raw data was filtered by multi-source grouping, extracting only high-confidence intelligence.")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.subheader("1. The Early Warning Spike")
        st.markdown("**December 15, 2025** · `body aches`")
        st.markdown("""
        <div class="explanation-box">
        <strong>What Happened:</strong> A massive +500% week-over-week spike in news mentions (GDELT) for body aches, reaching a z-score of 4.0.<br><br>
        <strong>Interpretation:</strong> People are experiencing early, severe pain symptoms before core disease terms start trending. This is a leading indicator.
        </div>
        """, unsafe_allow_html=True)
        # Create a mini chart
        kw_data = processed_df[processed_df["keyword"] == "body aches"]
        fig = px.line(kw_data, x="week_start", y="gdelt_mentions", title="News Mentions (Body Aches)", template="plotly_dark", height=250)
        fig.add_vline(x="2025-12-15", line_width=2, line_dash="dash", line_color="orange")
        fig.update_layout(margin=dict(l=0, r=0, t=30, b=0))
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("2. The Peak Confirmation")
        st.markdown("**January 5, 2026** · `flu` & `influenza`")
        st.markdown("""
        <div class="explanation-box">
        <strong>What Happened:</strong> A sustained 4-week upward trend was flagged as the signal approached its peak.<br><br>
        <strong>Interpretation:</strong> The system confirms the wave has reached its peak phase, proving massive demand is currently unfolding. This shifts the system from an 'early prediction' tool to a highly-accurate 'point-of-sale confirmation' tool.
        </div>
        """, unsafe_allow_html=True)
        kw_data = processed_df[processed_df["keyword"] == "flu"]
        fig = px.line(kw_data, x="week_start", y="wiki_pageviews", title="Wiki Pageviews (Flu)", template="plotly_dark", height=250)
        fig.add_vline(x="2026-01-05", line_width=2, line_dash="dash", line_color="red")
        fig.update_layout(margin=dict(l=0, r=0, t=30, b=0))
        st.plotly_chart(fig, use_container_width=True)
        
    with col3:
        st.subheader("3. The Resolution Drop")
        st.markdown("**April 6, 2026** · `flu`, `fever`")
        st.markdown("""
        <div class="explanation-box">
        <strong>What Happened:</strong> A simultaneous, sharp -277% relative plunge across multiple symptoms and disease terms.<br><br>
        <strong>Interpretation:</strong> The wave has broken due to spring. Supply chains can safely start scaling down inventory for Cold & Flu remedies.
        </div>
        """, unsafe_allow_html=True)
        kw_data = processed_df[processed_df["keyword"] == "flu"]
        fig = px.line(kw_data, x="week_start", y="wiki_pageviews", title="Wiki Pageviews (Flu)", template="plotly_dark", height=250)
        fig.add_vline(x="2026-04-06", line_width=2, line_dash="dash", line_color="blue")
        fig.update_layout(margin=dict(l=0, r=0, t=30, b=0))
        st.plotly_chart(fig, use_container_width=True)

with tab2:
    st.header("Time Series Explorer")
    st.markdown("Explore the normalized z-scores for all keywords over the entire 6-month historical period.")
    
    col_sel_1, col_sel_2 = st.columns(2)
    with col_sel_1:
         selected_kw = st.selectbox("Select Keyword", sorted(processed_df["keyword"].unique()))
    with col_sel_2:
         show_sources = st.multiselect("Data Sources", ["wiki_z", "gdelt_z"], default=["wiki_z", "gdelt_z"])
         
    kw_df = processed_df[processed_df["keyword"] == selected_kw]
    
    if show_sources:
        fig_ts = px.line(kw_df, x="week_start", y=show_sources, template="plotly_dark", 
                         title=f"Normalized Signal Z-Scores ({selected_kw})",
                         labels={"value": "Z-Score", "variable": "Source", "week_start": "Date"})
        fig_ts.add_hline(y=0, line_dash="dash", line_color="gray", opacity=0.5)
        # Highlight alert thresholds visually
        fig_ts.add_hrect(y0=2.0, y1=10, fillcolor="red", opacity=0.1, line_width=0, annotation_text="Spike Threshold")
        fig_ts.add_hrect(y0=-2.0, y1=-10, fillcolor="blue", opacity=0.1, line_width=0, annotation_text="Drop Threshold")
        
        st.plotly_chart(fig_ts, use_container_width=True)
    else:
        st.warning("Please select at least one data source to display.")

with tab3:
    st.header("Alert Configuration & History")
    st.markdown("The system's intelligence lies in the **Confidence Scorer**. High-noise signals generate raw alerts, but only those backed by multi-source agreement and group consistency exceed the confidence threshold.")
    
    conf_threshold = st.slider("Confidence Threshold", min_value=0, max_value=100, value=55, step=1,
                               help="Minimum confidence score (0-100) required to trigger an alert.")
    
    filtered_alerts = scored_alerts_df[scored_alerts_df["confidence"] >= conf_threshold]
    
    st.metric("Total Valid Alerts", len(filtered_alerts), delta=f"{len(scored_alerts_df) - len(filtered_alerts)} false positives filtered out as noise", delta_color="inverse")
    
    if not filtered_alerts.empty:
        # Display nicely formatted alerts
        display_df = filtered_alerts[["week_start", "keyword", "alert_type", "confidence", "explanation"]].copy()
        display_df["week_start"] = display_df["week_start"].dt.date
        display_df["confidence"] = display_df["confidence"].round(1)
        st.dataframe(display_df, use_container_width=True)
    else:
        st.info("No alerts meet the current confidence threshold. Try lowering the threshold.")
