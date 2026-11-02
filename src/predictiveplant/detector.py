"""Robust, explainable anomaly detection for multivariate industrial telemetry."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from statistics import median

from .models import Anomaly, TelemetryRecord


@dataclass(frozen=True)
class DetectionConfig:
    robust_z_threshold: float = 3.5
    critical_z_threshold: float = 6.0
    critical_temperature_c: float = 92.0
    critical_vibration_mm_s: float = 11.0


METRICS = ("temperature_c", "vibration_mm_s", "pressure_bar", "power_kw")


def _robust_z_score(value: float, values: list[float]) -> float:
    center = median(values)
    deviations = [abs(item - center) for item in values]
    mad = median(deviations)
    if mad == 0:
        return 0.0 if value == center else float("inf")
    return 0.6745 * (value - center) / mad


def detect_anomalies(
    records: list[TelemetryRecord], config: DetectionConfig | None = None
) -> list[Anomaly]:
    """Return anomalous observations with human-readable reasons.

    A median/MAD score is used instead of mean/stddev so a few bad readings do
    not distort the baseline they are being compared against.
    """
    config = config or DetectionConfig()
    by_asset: dict[str, list[TelemetryRecord]] = defaultdict(list)
    for record in records:
        by_asset[record.asset_id].append(record)

    anomalies: list[Anomaly] = []
    for asset_id, asset_records in by_asset.items():
        if len(asset_records) < 8:
            continue
        baselines = {
            metric: [getattr(item, metric) for item in asset_records]
            for metric in METRICS
        }
        for record in asset_records:
            reasons: list[str] = []
            scores: list[float] = []
            for metric in METRICS:
                score = _robust_z_score(getattr(record, metric), baselines[metric])
                if abs(score) >= config.robust_z_threshold:
                    reasons.append(f"{metric} robust-z={score:.2f}")
                    scores.append(abs(score))
            if record.temperature_c >= config.critical_temperature_c:
                reasons.append(f"temperature critical ({record.temperature_c:.1f} °C)")
            if record.vibration_mm_s >= config.critical_vibration_mm_s:
                reasons.append(f"vibration critical ({record.vibration_mm_s:.1f} mm/s)")
            if not reasons:
                continue
            score = max(scores, default=config.critical_z_threshold)
            severity = "critical" if (
                score >= config.critical_z_threshold
                or record.temperature_c >= config.critical_temperature_c
                or record.vibration_mm_s >= config.critical_vibration_mm_s
            ) else "warning"
            anomalies.append(
                Anomaly(record.timestamp, asset_id, severity, round(score, 3), tuple(reasons))
            )
    return sorted(anomalies, key=lambda anomaly: anomaly.timestamp)
