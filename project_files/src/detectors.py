"""
Detection engines for DEMAND RADAR.
Implements trend, spike, and drop alerts from processed weekly signals.
"""

from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Dict, List

import pandas as pd


@dataclass
class Alert:
    keyword: str
    week_start: str
    alert_type: str
    magnitude_pct: float
    z_score: float
    duration_weeks: int


class TrendDetector:
    """Detects sustained upward trends using moving-average deviation."""

    def __init__(
        self,
        signal_column: str = "composite_signal",
        min_change_pct: float = 20.0,
        min_duration_weeks: int = 4,
    ):
        self.signal_column = signal_column
        self.min_change_pct = min_change_pct
        self.min_duration_weeks = min_duration_weeks

    def detect(self, df: pd.DataFrame) -> List[Alert]:
        # Skip if signal column doesn't exist
        if self.signal_column not in df.columns:
            return []

        alerts: List[Alert] = []
        for keyword, group in df.groupby("keyword"):
            group = group.sort_values("week_start").copy()
            signal = group[self.signal_column]
            group["ma_4"] = signal.rolling(4, min_periods=4).mean()
            denom = max(float(signal.std(ddof=0)), 0.75)
            group["deviation_pct"] = ((group["ma_4"] - signal.mean()) / denom) * 100
            group["deviation_pct"] = group["deviation_pct"].clip(-500, 500)
            condition = group["deviation_pct"] >= self.min_change_pct

            run = 0
            emitted = False
            for _, row in group.iterrows():
                if bool(condition.loc[row.name]):
                    run += 1
                else:
                    run = 0
                    emitted = False
                if run >= self.min_duration_weeks and not emitted:
                    alerts.append(
                        Alert(
                            keyword=keyword,
                            week_start=str(pd.to_datetime(row["week_start"]).date()),
                            alert_type="trend",
                            magnitude_pct=float(row["deviation_pct"]),
                            z_score=float(row.get(self.signal_column, 0.0)),
                            duration_weeks=run,
                        )
                    )
                    emitted = True
        return alerts


class SpikeDetector:
    """Detects sudden spikes using z-score and week-over-week growth."""

    def __init__(
        self,
        signal_column: str = "composite_signal",
        z_threshold: float = 2.5,
        min_jump_pct: float = 50.0,
    ):
        self.signal_column = signal_column
        self.z_threshold = z_threshold
        self.min_jump_pct = min_jump_pct

    def detect(self, df: pd.DataFrame) -> List[Alert]:
        # Skip if signal column doesn't exist
        if self.signal_column not in df.columns:
            return []

        alerts: List[Alert] = []
        for keyword, group in df.groupby("keyword"):
            group = group.sort_values("week_start").copy()
            signal = group[self.signal_column]
            std = signal.std(ddof=0)
            if std <= 1e-9:
                continue

            group["z_score"] = (signal - signal.mean()) / std
            prev = signal.shift(1)
            prev_denom = prev.abs().clip(lower=0.75)
            group["wow_jump_pct"] = ((signal - prev) / prev_denom) * 100
            group["wow_jump_pct"] = group["wow_jump_pct"].clip(-500, 500)

            candidates = group[
                (group["z_score"] >= self.z_threshold)
                & (group["wow_jump_pct"].fillna(0) >= self.min_jump_pct)
            ]
            for _, row in candidates.iterrows():
                alerts.append(
                    Alert(
                        keyword=keyword,
                        week_start=str(pd.to_datetime(row["week_start"]).date()),
                        alert_type="spike",
                        magnitude_pct=float(row["wow_jump_pct"]),
                        z_score=float(row["z_score"]),
                        duration_weeks=1,
                    )
                )
        return alerts


class DropDetector:
    """Detects sharp declines relative to recent peak levels."""

    def __init__(
        self, signal_column: str = "composite_signal", min_drop_pct: float = 30.0
    ):
        self.signal_column = signal_column
        self.min_drop_pct = min_drop_pct

    def detect(self, df: pd.DataFrame) -> List[Alert]:
        # Skip if signal column doesn't exist
        if self.signal_column not in df.columns:
            return []

        alerts: List[Alert] = []
        for keyword, group in df.groupby("keyword"):
            group = group.sort_values("week_start").copy()
            signal = group[self.signal_column]
            rolling_peak = signal.rolling(8, min_periods=2).max()
            denom = rolling_peak.abs().clip(lower=0.75)
            group["drop_pct"] = ((signal - rolling_peak) / denom) * 100
            group["drop_pct"] = group["drop_pct"].clip(-500, 500)
            candidates = group[group["drop_pct"].fillna(0) <= -self.min_drop_pct]
            for _, row in candidates.iterrows():
                alerts.append(
                    Alert(
                        keyword=keyword,
                        week_start=str(pd.to_datetime(row["week_start"]).date()),
                        alert_type="drop",
                        magnitude_pct=float(abs(row["drop_pct"])),
                        z_score=float(row.get(self.signal_column, 0.0)),
                        duration_weeks=1,
                    )
                )
        return alerts


def run_all_detectors(processed_df: pd.DataFrame) -> pd.DataFrame:
    """Run all detector classes on both wiki_z and gdelt_z signals independently."""
    all_rows = []

    # Run detectors on both sources
    for signal_col in ["wiki_z", "gdelt_z"]:
        source = "wiki" if signal_col == "wiki_z" else "gdelt"
        trend_alerts = TrendDetector(signal_column=signal_col).detect(processed_df)
        spike_alerts = SpikeDetector(signal_column=signal_col).detect(processed_df)
        drop_alerts = DropDetector(signal_column=signal_col).detect(processed_df)
        for alert in trend_alerts + spike_alerts + drop_alerts:
            row = asdict(alert)
            row["signal_source"] = source
            all_rows.append(row)

    if not all_rows:
        return pd.DataFrame(
            columns=[
                "keyword",
                "week_start",
                "alert_type",
                "magnitude_pct",
                "z_score",
                "duration_weeks",
                "signal_source",
            ]
        )

    alerts_df = pd.DataFrame(all_rows)
    # Keep the strongest row when two sources emit the same keyword/week/type.
    alerts_df["_abs_z"] = alerts_df["z_score"].abs()
    alerts_df = alerts_df.sort_values(
        ["keyword", "week_start", "alert_type", "_abs_z"],
        ascending=[True, True, True, False],
    ).drop_duplicates(subset=["keyword", "week_start", "alert_type"], keep="first")
    alerts_df = alerts_df.drop(columns=["_abs_z"])
    alerts_df = alerts_df.sort_values(
        ["week_start", "keyword", "alert_type"]
    ).reset_index(drop=True)
    return alerts_df
