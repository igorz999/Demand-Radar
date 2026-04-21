# DEMAND RADAR Project Report

## Important Changes

- Set up the project environment and installed the required Python dependencies.
- Fixed the Wikipedia pageviews integration to use the current Wikimedia REST API.
- Fixed the GDELT integration to use a working endpoint and JSON timeline parsing.
- Added retries and rate-limit handling for GDELT requests.
- Corrected Wikipedia article mappings for missing keywords.
- Built a preprocessing pipeline that aggregates source data into weekly signals.
- Added baseline statistics output for each keyword.
- Implemented trend, spike, and drop detectors.
- Added confidence scoring with source alignment, group consistency, magnitude, and keyword importance.
- Added an end-to-end pipeline runner that fetches, processes, detects, and scores alerts.
- Verified the full pipeline executes successfully and produces processed data and alert outputs.

## Exploration Phase

- Added the missing Exploration phase to the project plan.
- Defined this phase as exploratory data analysis before final feature selection.
- Added tasks to plot signals, compare keywords, validate seasonality, and remove noisy or ambiguous keywords.
- Switched from random keyword sets to structured sets for comparison.
- Set A: flu, fever, cough.
- Set B: influenza, rhinorrhea, pharyngitis.
- Established that keyword selection should be data-driven based on noise level, correlation, and interpretability.

## Conceptual Updates

- Reframed the goal from detect demand shifts 1-2 weeks before sales to detect early signals that may precede demand shifts.
- Increased detector thresholds to be more conservative.
- Added smoothing with rolling means before detection.
- Updated target thresholds:
  - Trend: 35-40% above baseline.
  - Spike: 80-100% above baseline.
  - Z-score: 3.0+.
  - Drop: 50% below peak.

## Outputs Now Available

- Raw Wikipedia and GDELT CSV files.
- Weekly processed dataset.
- Baseline statistics JSON.
- Raw alerts CSV.
- Confidence-scored alerts CSV.
- Pipeline summary JSON.

## Remaining Risks

- GDELT can still rate-limit individual keywords.
- Some keywords may need to be filtered or down-ranked after EDA.
- Detection thresholds should be validated again after exploratory analysis.
