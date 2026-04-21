"""
Confidence scoring for DEMAND RADAR alerts.
Combines multi-source, correlation-group, magnitude, and keyword importance signals.
"""

from __future__ import annotations

import json
from typing import Dict

import pandas as pd


class ConfidenceScorer:
    """Assigns explainable confidence scores to detector alerts."""

    def __init__(self, keywords_json_path: str):
        with open(keywords_json_path, "r") as f:
            cfg = json.load(f)

        self.keyword_meta = {item["keyword"]: item for item in cfg["keywords"]}
        self.group_map: Dict[str, str] = {}
        for group_name, keywords in cfg.get("correlation_groups", {}).items():
            for kw in keywords:
                self.group_map[kw] = group_name

        self.importance_points = {
            "critical": 9,
            "high": 6,
            "medium": 3,
            "low": 1,
        }

    def _source_alignment_score(self, row: pd.Series, alert_type: str) -> float:
        if alert_type in {"trend", "spike"}:
            agree = int(row["wiki_z"] > 0.5) + int(row["gdelt_z"] > 0.5)
        else:
            agree = int(row["wiki_z"] < -0.5) + int(row["gdelt_z"] < -0.5)
        return {0: 0.0, 1: 12.0, 2: 24.0}[agree]

    def _group_consistency_score(
        self,
        processed_df: pd.DataFrame,
        keyword: str,
        week_start: str,
        alert_type: str,
    ) -> float:
        group_name = self.group_map.get(keyword)
        if not group_name:
            return 0.0

        group_rows = processed_df[
            (processed_df["week_start"] == pd.to_datetime(week_start))
            & (processed_df["keyword"].map(self.group_map.get) == group_name)
        ]
        if group_rows.empty:
            return 0.0

        # Prefer explicit composite when present; otherwise derive group signal
        # from the two normalized source channels.
        if "composite_signal" in group_rows.columns:
            group_signal = group_rows["composite_signal"]
        else:
            group_signal = group_rows[["wiki_z", "gdelt_z"]].mean(axis=1)

        if alert_type in {"trend", "spike"}:
            aligned = (group_signal > 0.5).sum()
        else:
            aligned = (group_signal < -0.5).sum()

        return float((aligned / len(group_rows)) * 20.0)

    @staticmethod
    def _magnitude_score(magnitude_pct: float, z_score: float) -> float:
        magnitude_component = min(abs(magnitude_pct), 300.0) / 300.0 * 12.0
        z_component = min(abs(z_score), 3.0) / 3.0 * 10.0
        return float(magnitude_component + z_component)

    @staticmethod
    def _data_quality_penalty(row: pd.Series) -> float:
        penalty = 0.0
        if row.get("wiki_observed", 1) == 0:
            penalty -= 5.0
        if row.get("gdelt_observed", 1) == 0:
            penalty -= 8.0
        return penalty

    def score_alerts(
        self,
        alerts_df: pd.DataFrame,
        processed_df: pd.DataFrame,
        min_confidence: float = 70.0,
    ) -> pd.DataFrame:
        """Score alerts and return enriched dataframe filtered by confidence threshold."""
        if alerts_df.empty:
            return alerts_df.copy()

        processed = processed_df.copy()
        processed["week_start"] = pd.to_datetime(processed["week_start"])

        scored_rows = []
        for _, alert in alerts_df.iterrows():
            kw = alert["keyword"]
            week = pd.to_datetime(alert["week_start"])
            row_match = processed[
                (processed["keyword"] == kw) & (processed["week_start"] == week)
            ]
            if row_match.empty:
                continue

            proc_row = row_match.iloc[0]
            source_score = self._source_alignment_score(proc_row, alert["alert_type"])
            group_score = self._group_consistency_score(
                processed,
                keyword=kw,
                week_start=str(week.date()),
                alert_type=alert["alert_type"],
            )
            mag_score = self._magnitude_score(
                float(alert["magnitude_pct"]), float(alert["z_score"])
            )

            importance = self.keyword_meta.get(kw, {}).get("importance", "low")
            importance_score = float(self.importance_points.get(importance, 2))
            quality_penalty = self._data_quality_penalty(proc_row)

            confidence = max(
                0.0,
                min(
                    100.0,
                    source_score
                    + group_score
                    + mag_score
                    + importance_score
                    + quality_penalty,
                ),
            )
            scored_rows.append(
                {
                    **alert.to_dict(),
                    "source_score": round(source_score, 2),
                    "group_score": round(group_score, 2),
                    "magnitude_score": round(mag_score, 2),
                    "importance_score": round(importance_score, 2),
                    "quality_penalty": round(quality_penalty, 2),
                    "confidence": round(confidence, 2),
                    "explanation": (
                        f"{alert['alert_type'].upper()} on {kw}: "
                        f"source={source_score:.1f}, group={group_score:.1f}, "
                        f"magnitude={mag_score:.1f}, importance={importance_score:.1f}, "
                        f"quality_penalty={quality_penalty:.1f}"
                    ),
                }
            )

        scored_df = pd.DataFrame(scored_rows)
        if scored_df.empty:
            return scored_df

        scored_df = scored_df.sort_values(
            ["confidence", "week_start"], ascending=[False, True]
        )
        return scored_df[scored_df["confidence"] >= min_confidence].reset_index(
            drop=True
        )
