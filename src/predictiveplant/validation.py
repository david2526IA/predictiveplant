"""Data-quality checks run before anomaly scoring."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from math import isfinite

from .models import TelemetryRecord


@dataclass(frozen=True)
class QualityReport:
    valid_records: int
    rejected_records: int
    issues: tuple[str, ...]


def validate(records: list[TelemetryRecord]) -> QualityReport:
    """Validate engineering ranges and timestamp ordering by asset.

    This deliberately rejects unsafe input rather than silently repairing it.
    """
    issues: list[str] = []
    last_timestamp: dict[str, object] = defaultdict(lambda: None)
    valid = 0
    for index, record in enumerate(records, start=1):
        row_issues: list[str] = []
        if not record.asset_id:
            row_issues.append("empty asset_id")
        if not all(isfinite(value) for value in (record.temperature_c, record.vibration_mm_s, record.pressure_bar, record.power_kw)):
            row_issues.append("non-finite measurement")
        if not (-40 <= record.temperature_c <= 200):
            row_issues.append("temperature outside engineering range")
        if not (0 <= record.vibration_mm_s <= 100):
            row_issues.append("vibration outside engineering range")
        if not (0 <= record.pressure_bar <= 500):
            row_issues.append("pressure outside engineering range")
        if not (0 <= record.power_kw <= 1_000):
            row_issues.append("power outside engineering range")
        previous = last_timestamp[record.asset_id]
        if previous is not None and record.timestamp <= previous:
            row_issues.append("timestamp is not strictly increasing for asset")
        if row_issues:
            issues.append(f"row {index}: {', '.join(row_issues)}")
        else:
            valid += 1
            last_timestamp[record.asset_id] = record.timestamp
    return QualityReport(valid, len(records) - valid, tuple(issues))
