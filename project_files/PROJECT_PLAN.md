# DEMAND RADAR - Complete Project Plan (5 Weeks)

## Project Overview

Build an **early warning system** that detects demand shifts for Cold & Flu products 1-2 weeks before sales data shows them, using public signals (Wikipedia pageviews + GDELT news mentions).

**Target Deadline:** 5 weeks from now
**Category:** Cold & Flu products
**Core Value:** Transform public signals into explainable, actionable alerts

---

## Phase 1: Foundation & Data Strategy (Week 1)

### 1.1 Keyword Strategy & Selection

**Deliverable:** List of 10-20 keywords for Cold & Flu category
**Tasks:**

- [ ] Research and finalize keyword list
  - Medical terms: "flu", "influenza", "cold", "cough", "fever", "decongestant"
  - Symptom-related: "runny nose", "sore throat", "congestion"
  - Medicine names: "ibuprofen", "acetaminophen", "antihistamine"
  - Context: "flu epidemic", "cold season", "outbreak"
- [ ] Categorize keywords by importance/reliability
- [ ] Document keyword rationale

**Input:** Interview insights, public health knowledge
**Output:** `keywords.json` - structured keyword definitions

---

### 1.2 Data Sources Research & API Setup

**Deliverable:** Working API connectors for data fetching
**Tasks:**

- [ ] Wikipedia Pageviews API
  - Research endpoint: https://pageviews.toolforge.org/
  - Set up authentication (none needed, public)
  - Test data fetching for sample keywords
  - Understand data format & limitations

- [ ] GDELT News Mentions API
  - Research GDELT 2.0 API documentation
  - Set up authentication (API key if needed)
  - Test news mention counting for keywords
  - Understand data granularity & format

- [ ] Optional sources (if time)
  - Google Trends API (or web scraping)
  - YouTube metadata
  - Weather APIs (temperature data for seasonality)

**Output:**

- `data_sources.md` - API documentation & setup guide
- Python modules for API calls ready

---

## Phase 2: Data Pipeline (Week 1-2)

### 2.1 Data Fetching & Collection

**Deliverable:** Historical dataset (12-16 weeks minimum)
**Tasks:**

- [ ] Build Wikipedia pageviews fetcher
  - Fetch weekly aggregates for all keywords
  - Handle missing data/errors gracefully
  - Store in CSV/JSON format

- [ ] Build GDELT news mentions fetcher
  - Count news mentions per keyword per week
  - Track article counts and date ranges
  - Store structured data

- [ ] Create data collection pipeline
  - Automated weekly data fetching
  - Data validation & quality checks
  - Logging & error handling

**Output:**

- `wikipedia_weekly_data.csv` - columns: [date, keyword, pageviews]
- `gdelt_weekly_data.csv` - columns: [date, keyword, mentions]
- `data_fetcher.py` - reusable fetching modules

---

### 2.2 Data Aggregation & Preprocessing

**Deliverable:** Clean, aggregated weekly time series
**Tasks:**

- [ ] Aggregate pageviews by keyword per week
- [ ] Normalize data (handle scale differences)
- [ ] Create composite signals
  - Combine Wikipedia + GDELT (weighted average)
  - Per-keyword baseline (mean over historical period)
  - Calculate variance/volatility

- [ ] Handle missing data, outliers
- [ ] Create train/validate/test splits

**Output:**

- `processed_data.csv` - clean weekly time series (all keywords + aggregates)
- `data_processor.py` - aggregation & normalization functions
- `baseline_stats.json` - baseline means/stds for all keywords

### 2.5 Exploration Phase: Data Understanding

**Deliverable:** Exploratory analysis to validate signal quality before final feature selection
**Tasks:**

- [ ] Plot Wikipedia and GDELT signals for each keyword
- [ ] Compare keywords by volume, volatility, and interpretability
- [ ] Validate seasonality and recurring patterns
- [ ] Remove or down-rank bad keywords with noisy or ambiguous behavior
- [ ] Use structured keyword sets instead of random selection
  - Set A (broad): flu, fever, cough
  - Set B (specific): influenza, rhinorrhea, pharyngitis
- [ ] Evaluate noise level, correlation, and interpretability for each set
- [ ] Convert keyword choice into data-driven feature selection

**Output:**

- `eda_report.md` - plots, observations, and keyword filtering decisions
- `keyword_selection_notes.md` - why each keyword stays or is removed

---

## Phase 3: Detection Engine (Week 2-3)

### 3.1 Trend Detection

**Algorithm:** Moving average deviation + change-point detection
**Parameters:**

- Minimum change: 35-40% above baseline
- Minimum duration: 4+ weeks sustained
- Confidence threshold: 70%
- Apply rolling mean smoothing before detection

**Tasks:**

- [ ] Implement moving average (4-week window)
- [ ] Calculate deviation from baseline
- [ ] Detect sustained change (4+ weeks)
- [ ] Confidence scoring logic
- [ ] Test with sample data

**Output:**

- `trend_detector.py` with TrendDetector class
- Unit tests with synthetic examples

---

### 3.2 Spike Detection

**Algorithm:** Z-score analysis + outlier detection
**Parameters:**

- Minimum jump: 80-100% above baseline
- Duration: 1-2 weeks
- Z-score threshold: > 3.0 standard deviations
- Confidence threshold: 70%
- Apply rolling mean smoothing before detection

**Tasks:**

- [ ] Implement z-score calculation
- [ ] Outlier detection logic
- [ ] Distinguish spikes from noise (check sustained increase)
- [ ] Multi-keyword spike validation (do multiple keywords spike together?)
- [ ] Confidence scoring

**Output:**

- `spike_detector.py` with SpikeDetector class
- Test cases with known spikes

---

### 3.3 Drop Detection

**Algorithm:** Negative threshold + sustained duration analysis
**Parameters:**

- Minimum decline: 50% below peak
- Duration: 1-2 weeks
- Confidence threshold: 75%
- Apply rolling mean smoothing before detection

**Tasks:**

- [ ] Implement decline detection
- [ ] Duration validation
- [ ] Distinguish from normal fluctuation
- [ ] Confidence scoring

**Output:**

- `drop_detector.py` with DropDetector class
- Test cases

---

### 3.4 Confidence Scoring System

**Deliverable:** Explainable confidence metrics for all alerts
**Tasks:**

- [ ] Multi-source consistency scoring
  - If both Wikipedia & GDELT signal → higher confidence
  - If single source → lower confidence

- [ ] Keyword consistency scoring
  - If multiple related keywords signal → higher confidence
  - E.g., both "flu" and "influenza" trending

- [ ] Magnitude scoring
  - Larger change = higher confidence

- [ ] Duration scoring
  - Longer sustained signal = higher confidence

**Output:**

- `confidence_scorer.py` - confidence calculation logic
- Documentation of confidence formula

---

## Phase 4: Alert System (Week 3)

### 4.1 Alert Generation & Validation

**Deliverable:** Alert engine with rules & filtering
**Tasks:**

- [ ] Implement alert generation logic
  - Trigger: Detected change (Trend/Spike/Drop) + Confidence ≥ 70%

- [ ] Multi-source validation
  - Cross-check Wikipedia & GDELT consistency
  - Require agreement across sources (if both available)

- [ ] Anti-spam filters
  - 7-day cooldown (don't re-alert for same keyword within 7 days)
  - Minimum sustained duration (2+ weeks for trends)
  - Magnitude thresholds (avoid noise)

- [ ] Alert storage (in-memory or SQLite)

**Output:**

- `alert_engine.py` - AlertEngine class with rules
- `alerts.db` or `alerts_history.json` - alert storage

---

### 4.2 Alert Explanation & Context

**Deliverable:** Rich explanations for each alert
**Tasks:**

- [ ] Generate alert explanations
  - "What": Type of change (Trend/Spike/Drop)
  - "When": Start date & duration
  - "Magnitude": % change from baseline
  - "Why": Which keywords signal, news context
  - "Confidence": Score + reasoning

- [ ] Extract supporting evidence
  - Which data sources confirm? (Wikipedia ✓, GDELT ✓)
  - Which keywords contribute? (list all)
  - Recent news links (if GDELT available)

- [ ] Explanatory text generator
  - Natural language summary of alerts

**Output:**

- `explanation_generator.py` - alert explanation logic
- Alert objects with rich metadata

---

## Phase 5: Dashboard & Visualization (Week 3-4)

### 5.1 Streamlit Dashboard Structure

**Deliverable:** Interactive web dashboard
**Tasks:**

- [ ] Set up Streamlit project structure
- [ ] Create multi-page app:
  - **Overview**: Current demand signals summary
  - **Time Series**: Interactive charts
  - **Alerts**: Alert history & details
  - **Configuration**: Threshold tuning
  - **Analysis**: Deep dive on signals

**Output:**

- `app.py` - main Streamlit application
- `requirements.txt` - dependencies

---

### 5.2 Dashboard Pages & Visualizations

#### Page 1: Overview Dashboard

- [ ] Current demand status (red/yellow/green)
- [ ] Latest alerts (past 2 weeks)
- [ ] Active signals across keywords
- [ ] Summary statistics (# trends, # spikes, # drops)

#### Page 2: Time Series View

- [ ] Multi-source line chart (Wikipedia + GDELT)
- [ ] Baseline overlay
- [ ] Detected changes highlighted
- [ ] Interactive date range selection
- [ ] Keyword multi-select

#### Page 3: Alert History & Details

- [ ] Table of all alerts (date, keyword, type, confidence)
- [ ] Alert detail view (click to expand)
  - Explanation text
  - Supporting evidence
  - News context
  - Confidence breakdown

#### Page 4: Configuration Interface

- [ ] Threshold sliders (Trend %, Spike %, Drop %)
- [ ] Confidence threshold slider
- [ ] Cooldown period input
- [ ] Keyword selection/weighting
- [ ] "Run detection" button to recalculate

#### Page 5: Analysis Deep Dive

- [ ] Multi-keyword comparison
- [ ] Seasonality patterns
- [ ] Source reliability metrics
- [ ] Historical accuracy (if validation data available)

**Output:**

- `pages/` directory with modular Streamlit pages
- Reusable chart components

---

## Phase 6: Testing & Validation (Week 4-5)

### 6.1 Data Validation

**Tasks:**

- [ ] Check data quality
  - No missing values (or documented)
  - Data range makes sense
  - No obvious data errors

- [ ] Data consistency
  - Wikipedia & GDELT correlate reasonably
  - Seasonal patterns visible

**Output:**

- `data_validation_report.md`

---

### 6.2 Algorithm Validation

**Tasks:**

- [ ] Test each detector with synthetic/historical examples
  - Real flu season data (should detect trend)
  - Known news events (should detect spikes)
  - Post-season drops (should detect drops)

- [ ] Validate confidence scoring
  - Check reasonableness of scores
  - Tune weights if needed

- [ ] Test anti-spam filters
  - Verify cooldown works
  - Check false positive rates

**Output:**

- `test_results.md` - test cases & results
- Parameter tuning notes

---

### 6.3 System Integration Testing

**Tasks:**

- [ ] End-to-end test: Data → Detection → Alert → Dashboard
- [ ] Test with full historical dataset
- [ ] Verify dashboard renders all alerts correctly
- [ ] Performance check (runtime acceptable?)

**Output:**

- `integration_test_report.md`

---

### 6.4 Refinement & Tuning

**Tasks:**

- [ ] Review false positives
  - Adjust thresholds if needed
  - Improve multi-source validation

- [ ] Improve explanations
  - Make alert text clearer
  - Add more context

- [ ] Performance optimization
  - Speed up data fetching if slow
  - Cache computations

**Output:**

- Parameter tuning notes
- Refinement log

---

## Phase 7: Documentation & Delivery (Week 5)

### 7.1 Technical Documentation

**Deliverables:**

- [ ] `README.md` - How to run the system
- [ ] `ARCHITECTURE.md` - System design overview
- [ ] `API_GUIDE.md` - How to use each module
- [ ] `KEYWORD_ANALYSIS.md` - Keyword selection rationale
- [ ] `PARAMETERS.md` - All thresholds & tuning guide

---

### 7.2 Results & Findings Report

**Deliverables:**

- [ ] `RESULTS.md` - Key findings
  - Which signals work best?
  - False positive/negative rates
  - Which keywords are most reliable?
  - Timing of detection vs actual demand shift
  - Recommendations for Genpact

- [ ] `LESSONS_LEARNED.md` - What we learned

---

### 7.3 Presentation & Demo

**Deliverables:**

- [ ] Live dashboard demonstration
- [ ] Presentation slides
  - Problem recap
  - Solution overview
  - Key results
  - Recommendations
  - Next steps

---

## Deliverables Summary

### Code Artifacts

```
project/
├── data/
│   ├── wikipedia_weekly_data.csv
│   ├── gdelt_weekly_data.csv
│   ├── processed_data.csv
│   └── baseline_stats.json
├── src/
│   ├── data_fetcher.py
│   ├── data_processor.py
│   ├── trend_detector.py
│   ├── spike_detector.py
│   ├── drop_detector.py
│   ├── confidence_scorer.py
│   ├── alert_engine.py
│   ├── explanation_generator.py
│   └── utils.py
├── dashboard/
│   ├── app.py
│   ├── pages/
│   │   ├── overview.py
│   │   ├── timeseries.py
│   │   ├── alerts.py
│   │   ├── config.py
│   │   └── analysis.py
│   └── requirements.txt
├── tests/
│   ├── test_detectors.py
│   ├── test_confidence.py
│   └── test_pipeline.py
└── docs/
    ├── README.md
    ├── ARCHITECTURE.md
    ├── PARAMETERS.md
    ├── RESULTS.md
    └── LESSONS_LEARNED.md
```

### Documentation Artifacts

- Project Plan (this file)
- Architecture document
- Parameter tuning guide
- Results & findings report
- Presentation slides

---

## Success Criteria

✅ **Must Have:**

- Data pipeline working (Wikipedia + GDELT)
- All 3 detectors implemented (Trend/Spike/Drop)
- Alert system with confidence scoring
- Working dashboard showing alerts
- Documentation

✅ **Should Have:**

- Anti-spam filters working well
- Multi-source validation
- Historical accuracy analysis
- Threshold tuning based on real data

✅ **Nice to Have:**

- Additional data sources (Google Trends, weather)
- Advanced visualizations
- Export/reporting features
- Automated weekly pipeline

---

## Risk Mitigation

| Risk              | Impact              | Mitigation                                           |
| ----------------- | ------------------- | ---------------------------------------------------- |
| API rate limits   | Data gaps           | Cache data, use backup sources                       |
| Insufficient data | Can't validate      | Use synthetic data for testing                       |
| False positives   | Loss of trust       | Careful threshold tuning, multi-source validation    |
| Missing signals   | Defeats purpose     | Lower thresholds if testing shows we're too cautious |
| Tight timeline    | Incomplete delivery | Prioritize MVP (data → detection → basic dashboard)  |

---

## Weekly Breakdown

- **Week 1:** Keywords finalized + Data APIs working
- **Week 2:** Historical data collected + Processing pipeline done
- **Week 3:** Detection algorithms (all 3 types) + Alert system
- **Week 4:** Dashboard built + Initial testing
- **Week 5:** Testing, tuning, documentation + Presentation prep

---

## Next Steps

1. Finalize keyword list
2. Set up project structure & Git repo
3. Get API access & test data fetching
4. Begin data collection (parallelizable with keyword finalization)
