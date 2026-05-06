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
    initial_sidebar_state="expanded",
)

# Define paths
ROOT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT_DIR / "data"

# Add custom CSS (light, dashboard-friendly)
st.markdown(
    """
<style>
    .stAlert {
        border-radius: 8px;
    }
    .metric-card {
        background-color: #ffffff;
        padding: 16px;
        border-radius: 8px;
        border: 1px solid #e6e6e6;
        box-shadow: 0 1px 4px rgba(16,24,40,0.06);
    }
    .metric-value {
        font-size: 2.2rem;
        font-weight: 600;
        color: #0b69ff;
    }
    .metric-label {
        font-size: 0.95rem;
        color: #333;
    }
    .explanation-box {
        background-color: #f3f8ff;
        border-left: 4px solid #0b69ff;
        padding: 12px;
        margin: 10px 0;
        border-radius: 0 4px 4px 0;
        color: #0b1828;
    }
</style>
""",
    unsafe_allow_html=True,
)


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
st.markdown("""
**Welcome to Demand RADAR**

This dashboard helps you anticipate and respond to changes in demand for cold & flu products. All alerts and charts are explained in clear, actionable supply chain terms.
""")

# Tabs
tab1, tab2, tab3 = st.tabs(
    ["⭐ The Golden Signals", "📈 Time Series Explorer", "⚙️ Alert Configuration"]
)

with tab1:
    st.header("The Golden Signals: 2025-2026 Flu Season Lifecycle")
    st.markdown("""
    These 3 events show how public signals can help you make better supply chain decisions. Each alert comes with a recommendation for inventory management.
    """)

    col1, col2, col3 = st.columns(3)

    with col1:
        st.subheader("1. The Early Warning Spike")
        st.markdown("**December 15, 2025** · `body aches`")
        st.markdown(
            """
        <div class="explanation-box">
        <strong>What Happened:</strong> We look at news coverage here because GDELT shows what the public and media are talking about right now. In this case, just one keyword was enough: <em>body aches</em> spiked by +500% week-over-week, which is a strong early warning sign for the symptom group.<br><br>
        <strong>Supply Chain Recommendation:</strong> Increase inventory for pain relief products as soon as possible. For example, stock more acetaminophen or ibuprofen now, since a spike in body aches can be an early sign that more cold & flu support will be needed soon.
        </div>
        """,
            unsafe_allow_html=True,
        )
        # Create a mini chart
        kw_data = processed_df[processed_df["keyword"] == "body aches"]
        fig = px.line(
            kw_data,
            x="week_start",
            y="gdelt_mentions",
            title="News Mentions (Body Aches)",
            template="plotly_dark",
            height=250,
        )
        fig.add_vline(
            x="2025-12-15", line_width=2, line_dash="dash", line_color="orange"
        )
        fig.update_layout(margin=dict(l=0, r=0, t=30, b=0))
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("2. The Peak Confirmation")
        st.markdown("**January 5, 2026** · `flu` & `influenza`")
        st.markdown(
            """
        <div class="explanation-box">
        <strong>What Happened:</strong> We use Wikipedia here because it reflects direct public search interest, which is useful when people actively look up a disease term. We show two related keywords, <em>flu</em> and <em>influenza</em>, because both belong to the same outbreak group and help confirm the signal instead of relying on just one term. A sustained 4-week upward trend told us the peak was approaching.<br><br>
        <strong>Supply Chain Recommendation:</strong> Keep core flu treatments fully stocked and move faster on replenishment. If fever and flu interest are rising, products like Tamiflu (oseltamivir) and Xofluza (baloxavir) should be supplied to pharmacies as soon as possible.
        </div>
        """,
            unsafe_allow_html=True,
        )
        kw_data = processed_df[processed_df["keyword"] == "flu"]
        fig = px.line(
            kw_data,
            x="week_start",
            y="wiki_pageviews",
            title="Wiki Pageviews (Flu)",
            template="plotly_dark",
            height=250,
        )
        fig.add_vline(x="2026-01-05", line_width=2, line_dash="dash", line_color="red")
        fig.update_layout(margin=dict(l=0, r=0, t=30, b=0))
        st.plotly_chart(fig, use_container_width=True)

    with col3:
        st.subheader("3. The Resolution Drop")
        st.markdown("**April 6, 2026** · `flu`, `fever`")
        st.markdown(
            """
        <div class="explanation-box">
        <strong>What Happened:</strong> We compare both public search behavior and news attention here because the drop is strongest when multiple sources point in the same direction. We use two keywords, <em>flu</em> and <em>fever</em>, because the system is checking whether the disease signal and the symptom signal are both cooling off at the same time. The sharp -277% plunge shows demand is fading quickly across the group.<br><br>
        <strong>Supply Chain Recommendation:</strong> Slow down replenishment of cold & flu products and avoid overstocking. If public interest is dropping, order less aggressively for medications such as Tamiflu (oseltamivir) and Relenza (zanamivir).
        </div>
        """,
            unsafe_allow_html=True,
        )
        kw_data = processed_df[processed_df["keyword"] == "flu"]
        fig = px.line(
            kw_data,
            x="week_start",
            y="wiki_pageviews",
            title="Wiki Pageviews (Flu)",
            template="plotly_dark",
            height=250,
        )
        fig.add_vline(x="2026-04-06", line_width=2, line_dash="dash", line_color="blue")
        fig.update_layout(margin=dict(l=0, r=0, t=30, b=0))
        st.plotly_chart(fig, use_container_width=True)

with tab2:
    st.header("Time Series Explorer")
    st.markdown(
        """
    This chart shows weekly demand signals for your selected product or symptom. 
    <span style='color:red'><b>Spikes</b></span> indicate sudden increases (potential supply risk), <span style='color:green'><b>trends</b></span> show sustained growth, and <span style='color:blue'><b>drops</b></span> highlight sharp declines (potential for excess stock).
    <br><br>
    <b>How do we define these events?</b><br>
    <ul>
    <li><b>Spike:</b> A sudden, very large jump in demand compared to last week (over 2.5× normal and at least 50% higher than the previous week).</li>
    <li><b>Trend:</b> Demand stays high (at least 20% above normal) for 4 weeks in a row.</li>
    <li><b>Drop:</b> Demand falls at least 30% below its recent peak.</li>
    </ul>
    """,
        unsafe_allow_html=True,
    )

    col_sel_1, col_sel_2 = st.columns(2)
    with col_sel_1:
        selected_kw = st.selectbox(
            "Select Keyword", sorted(processed_df["keyword"].unique())
        )
    with col_sel_2:
        show_sources = st.multiselect(
            "Data Sources", ["wiki_z", "gdelt_z"], default=["wiki_z", "gdelt_z"]
        )

    kw_df = processed_df[processed_df["keyword"] == selected_kw]

    if show_sources:
        fig_ts = px.line(
            kw_df,
            x="week_start",
            y=show_sources,
            template="plotly_dark",
            title=f"Normalized Signal Z-Scores ({selected_kw})",
            labels={"value": "Z-Score", "variable": "Source", "week_start": "Date"},
        )
        fig_ts.add_hline(y=0, line_dash="dash", line_color="gray", opacity=0.5)
        # Highlight alert thresholds visually
        fig_ts.add_hrect(
            y0=2.0,
            y1=10,
            fillcolor="red",
            opacity=0.1,
            line_width=0,
            annotation_text="Spike Threshold",
        )
        fig_ts.add_hrect(
            y0=-2.0,
            y1=-10,
            fillcolor="blue",
            opacity=0.1,
            line_width=0,
            annotation_text="Drop Threshold",
        )

        # Add summary of key events (spikes/trends/drops)
        summary_lines = []
        # Example: highlight spikes
        spike_weeks = (
            kw_df[kw_df[show_sources].max(axis=1) > 2.5]["week_start"]
            .dt.strftime("%b %d")
            .tolist()
        )
        if spike_weeks:
            summary_lines.append(
                f"<span style='color:red'><b>Spikes:</b></span> {', '.join(spike_weeks)}"
            )
        drop_weeks = (
            kw_df[kw_df[show_sources].min(axis=1) < -2.0]["week_start"]
            .dt.strftime("%b %d")
            .tolist()
        )
        if drop_weeks:
            summary_lines.append(
                f"<span style='color:blue'><b>Drops:</b></span> {', '.join(drop_weeks)}"
            )
        if summary_lines:
            st.markdown(
                f"<div class='explanation-box'><b>Key events detected:</b><br>{'<br>'.join(summary_lines)}</div>",
                unsafe_allow_html=True,
            )

        st.plotly_chart(fig_ts, use_container_width=True)
    else:
        st.warning("Please select at least one data source to display.")

with tab3:
    st.header("Alert Configuration & History")
    st.markdown(
        """
    Configure how sensitive the system is to changes in demand. Lower thresholds mean more alerts, higher thresholds mean only the most unusual events trigger an alert.<br>
    <b>Confidence level:</b> Only show alerts when the system is highly certain a real demand change is happening.
    """,
        unsafe_allow_html=True,
    )

    conf_threshold = st.slider(
        "Confidence Threshold",
        min_value=0,
        max_value=100,
        value=55,
        step=1,
        help="Minimum confidence score (0-100) required to trigger an alert. Higher = only the most certain alerts.",
    )

    st.markdown(
        """
    <ul>
    <li><b>z-score</b>: <span title='How unusual the demand is compared to normal weeks.'>How unusual the demand is compared to normal weeks.</span></li>
    <li><b>Confidence</b>: <span title='How sure the system is that this alert is important for your business.'>How sure the system is that this alert is important for your business.</span></li>
    </ul>
    """,
        unsafe_allow_html=True,
    )

    # Scoring summary cards are shown below and update when an alert is selected

    filtered_alerts = scored_alerts_df[scored_alerts_df["confidence"] >= conf_threshold]

    st.metric(
        "Total Valid Alerts",
        len(filtered_alerts),
        delta=f"{len(scored_alerts_df) - len(filtered_alerts)} false positives filtered out as noise",
        delta_color="inverse",
    )

    if not filtered_alerts.empty:
        # Display nicely formatted alerts
        display_df = filtered_alerts[
            ["week_start", "keyword", "alert_type", "confidence", "explanation"]
        ].copy()
        display_df["week_start"] = display_df["week_start"].dt.date
        display_df["confidence"] = display_df["confidence"].round(1)

        # Add supply chain recommendation column
        def supply_chain_reco(row):
            if row["alert_type"] == "spike":
                return "Increase inventory to meet expected surge."
            elif row["alert_type"] == "trend":
                return "Monitor and gradually increase stock."
            elif row["alert_type"] == "drop":
                return "Reduce inventory to avoid overstock."
            else:
                return "Monitor situation."

        display_df["recommendation"] = display_df.apply(supply_chain_reco, axis=1)

        # Add plain-language breakdown column
        def plain_explanation(row):
            parts = []
            if row["alert_type"] == "spike":
                parts.append("A sudden, very large jump in demand was detected.")
            elif row["alert_type"] == "trend":
                parts.append("Demand has stayed high for several weeks in a row.")
            elif row["alert_type"] == "drop":
                parts.append(
                    "A sharp decline in demand was detected compared to recent weeks."
                )
            # Source
            if "source" in row["explanation"]:
                parts.append("Both data sources agree on this signal.")
            # Group
            if "group" in row["explanation"]:
                parts.append("Many related symptoms or products show the same pattern.")
            # Magnitude
            if "magnitude" in row["explanation"]:
                parts.append("The change is much larger than normal.")
            # Importance
            if "importance" in row["explanation"]:
                parts.append("This is a key product or symptom for demand.")
            # Quality
            if "quality_penalty=0.0" in row["explanation"]:
                parts.append("Data quality is high (no missing data).")
            return " ".join(parts)

        display_df["why_this_alert"] = display_df.apply(plain_explanation, axis=1)

        st.dataframe(
            display_df[
                [
                    "week_start",
                    "keyword",
                    "alert_type",
                    "confidence",
                    "recommendation",
                    "why_this_alert",
                ]
            ],
            use_container_width=True,
        )
        # --- Interactive inspector: select an alert and see component strengths ---
        select_opts = filtered_alerts.apply(
            lambda r: f"{r['week_start'].date()} | {r['keyword']} | {r['alert_type']} | {r['confidence']:.1f}%",
            axis=1,
        ).tolist()

        sel = st.selectbox(
            "Select an alert to inspect", options=["(none)"] + select_opts
        )

        if sel != "(none)":
            # map selection back to row
            idx = select_opts.index(sel)
            row = filtered_alerts.reset_index(drop=True).iloc[idx]

            # read component scores (fall back to 0 if missing)
            source_score = float(row.get("source_score", 0) or 0)
            group_score = float(row.get("group_score", 0) or 0)
            magnitude_score = float(row.get("magnitude_score", 0) or 0)
            importance_score = float(row.get("importance_score", 0) or 0)
            quality_penalty = float(row.get("quality_penalty", 0) or 0)

            comps = {
                "Source agreement": source_score,
                "Group consistency": group_score,
                "Signal magnitude": magnitude_score,
                "Keyword importance": importance_score,
                "Data quality (penalty)": abs(quality_penalty),
            }

            total = sum(comps.values())
            if total <= 0:
                # avoid division by zero — show equal small bars
                pct_map = {k: 20 for k in comps}
            else:
                pct_map = {k: round(v / total * 100, 1) for k, v in comps.items()}

            # render cards with proportional bars
            cols = st.columns(5)
            colors = {
                "Data quality (penalty)": "#ff6b6b",
            }
            default_color = "#0b69ff"

            for col, (k, v) in zip(cols, comps.items()):
                with col:
                    pct = pct_map[k]
                    color = colors.get(k, default_color)
                    # show numeric breakdown and bar
                    st.markdown(
                        f"""
                        <div class="metric-card">
                          <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;">
                            <h4 style="margin:0;font-size:1rem;color:#111;">{k}</h4>
                            <div style="font-weight:600;color:{color};">{v:.1f}</div>
                          </div>
                          <div style="background:#f1f5f9;border-radius:6px;height:12px;width:100%;">
                            <div style="width:{pct}%;height:12px;background:{color};border-radius:6px;"></div>
                          </div>
                          <div style="margin-top:6px;font-size:0.85rem;color:#666;">{pct}% of total contribution</div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
    else:
        st.info(
            "No alerts meet the current confidence threshold. Try lowering the threshold."
        )
