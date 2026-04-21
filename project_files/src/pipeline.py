"""
End-to-end pipeline runner for DEMAND RADAR.
Fetches source data, processes weekly features, detects changes, and scores alerts.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path

from data_fetcher import DataFetcherOrchestrator
from data_processor import DemandRadarDataProcessor
from detectors import run_all_detectors
from confidence_scorer import ConfidenceScorer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def run_pipeline() -> None:
    project_root = Path(__file__).resolve().parent.parent

    orchestrator = DataFetcherOrchestrator(
        keywords_json_path=str(project_root / "keywords.json"),
        data_dir=str(project_root / "data"),
    )

    logger.info("Step 1/4: Fetching source data")
    wiki_df, gdelt_df = orchestrator.fetch_all_data(
        start_date="202510",
        end_date="202603",
        wiki_granularity="daily",
        gdelt_timespan="6m",
    )

    if wiki_df is None or gdelt_df is None or wiki_df.empty or gdelt_df.empty:
        logger.error("Data fetch failed or returned empty sources. Stopping pipeline.")
        return

    logger.info("Step 2/4: Processing weekly features")
    processor = DemandRadarDataProcessor(str(project_root / "keywords.json"))
    processed_df, baseline_stats = processor.process(
        wikipedia_csv_path=str(project_root / "data" / "wikipedia_data.csv"),
        gdelt_csv_path=str(project_root / "data" / "gdelt_data.csv"),
        processed_output_path=str(project_root / "data" / "processed_data.csv"),
        baseline_output_path=str(project_root / "data" / "baseline_stats.json"),
    )

    logger.info("Step 3/4: Running detectors")
    alerts_df = run_all_detectors(processed_df)
    alerts_path = project_root / "data" / "alerts_raw.csv"
    alerts_df.to_csv(alerts_path, index=False)

    logger.info("Step 4/4: Scoring confidence")
    scorer = ConfidenceScorer(str(project_root / "keywords.json"))
    scored_alerts = scorer.score_alerts(alerts_df, processed_df, min_confidence=70.0)
    scored_alerts_path = project_root / "data" / "alerts_scored.csv"
    scored_alerts.to_csv(scored_alerts_path, index=False)

    summary = {
        "processed_rows": int(len(processed_df)),
        "raw_alerts": int(len(alerts_df)),
        "scored_alerts": int(len(scored_alerts)),
        "baseline_keywords": int(len(baseline_stats)),
    }
    summary_path = project_root / "data" / "pipeline_summary.json"
    with open(summary_path, "w") as f:
        json.dump(summary, f, indent=2)

    logger.info("Pipeline complete")
    logger.info("Processed rows: %s", summary["processed_rows"])
    logger.info("Raw alerts: %s", summary["raw_alerts"])
    logger.info("Scored alerts: %s", summary["scored_alerts"])


if __name__ == "__main__":
    run_pipeline()
