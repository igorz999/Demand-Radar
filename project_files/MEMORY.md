# DEMAND RADAR - Project Memory & Context

## Project Overview

- **Goal:** Early warning system for Cold & Flu product demand shifts using Wikipedia + GDELT
- **Timeline:** 5 weeks
- **Category:** Cold & Flu products (decongestants, antihistamines, etc.)
- **Lead Contact:** Flavio Aliberti (Genpact) - flavio.aliberti@genpact.com

## Key Insights from Interview

- **Main challenge:** Not detection, but filtering noise and building trust
- **Critical factors:** Reliability > Accuracy; Explainability > Black-box detection
- **False positives worse than false negatives:** Users will ignore system if too many false alerts
- **Actionability:** Alerts must be understandable enough for supply chain teams to act on
- **Delay problem:** Sales data lags 2-4 weeks; public signals may precede demand shifts

## Three Signal Types

1. **Trend:** Gradual 20%+ increase over 4+ weeks
2. **Spike:** Sudden 50%+ jump in 1-2 weeks
3. **Drop:** 30%+ decline in 1-2 weeks

## Data Strategy

- **Mandatory:** Wikipedia pageviews + GDELT news mentions
- **Optional:** Google Trends, YouTube, weather data
- **Constraint:** Aggregated data only (privacy-first)
- **Granularity:** Weekly (less noisy than daily)

## Technical Approach

- Simple methods (moving avg, z-score, thresholds) → explainability
- 70% confidence threshold for alerts, but higher detector thresholds are preferred for noisy signals
- 7-day cooldown to prevent alert fatigue
- Multi-source validation (Wikipedia + GDELT agreement)
- Keyword consistency checking (multiple keywords signaling together)
- Add an exploration/EDA phase before final feature selection
- Prefer structured keyword sets:
  - Set A (broad): flu, fever, cough
  - Set B (specific): influenza, rhinorrhea, pharyngitis
- Use EDA to remove bad keywords and validate seasonality
- Apply rolling mean smoothing before detection
- Reframe the system as detecting early signals that may precede demand shifts, not guaranteeing a fixed lead time

## Success Factors (from Deliverable 1)

1. **Reliability:** Minimize false alerts
2. **Explainability:** Show why alert triggered (which keywords, which sources, confidence breakdown)
3. **Actionability:** Help supply chain understand "what to do"
4. **Trust:** Cross-validate signals, explain "why no alert" for noisy data

## Open Questions for Follow-up

- How to validate system performance over time?
- Should we weight certain keywords higher?
- How sensitive should thresholds be?
- Which data sources matter most?
- How to handle geographical variation?
- Should we account for seasonality differences?
