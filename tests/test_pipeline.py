from __future__ import annotations

from datetime import datetime, timedelta, timezone

from predictiveplant.detector import detect_anomalies
from predictiveplant.models import TelemetryRecord
from predictiveplant.synthetic import generate
from predictiveplant.io import load_telemetry
from predictiveplant.validation import validate


def _record(offset: int, vibration: float = 2.5) -> TelemetryRecord:
    return TelemetryRecord(
        timestamp=datetime(2026, 1, 1, tzinfo=timezone.utc) + timedelta(minutes=offset),
        asset_id="PUMP-01",
        temperature_c=62.0,
        vibration_mm_s=vibration,
        pressure_bar=7.4,
        power_kw=18.0,
    )


def test_generated_demo_is_valid_and_contains_anomalies(tmp_path) -> None:
    path = tmp_path / "telemetry.csv"
    generate(path, rows_per_asset=80)
    records = load_telemetry(path)
    report = validate(records)
    assert report.rejected_records == 0
    assert report.valid_records == 160
    assert any(item.asset_id == "PUMP-01" for item in detect_anomalies(records))


def test_detector_explains_critical_vibration() -> None:
    records = [_record(index) for index in range(12)] + [_record(12, vibration=12.0)]
    anomalies = detect_anomalies(records)
    assert len(anomalies) == 1
    assert anomalies[0].severity == "critical"
    assert "vibration critical" in " ".join(anomalies[0].reasons)


def test_quality_report_rejects_out_of_order_timestamp() -> None:
    report = validate([_record(5), _record(4)])
    assert report.rejected_records == 1
    assert "not strictly increasing" in report.issues[0]
