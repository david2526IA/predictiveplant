"""CSV ingestion and serialisation with an intentionally small dependency surface."""

from __future__ import annotations

import csv
from datetime import datetime
from pathlib import Path

from .models import Anomaly, TelemetryRecord

REQUIRED_COLUMNS = {
    "timestamp",
    "asset_id",
    "temperature_c",
    "vibration_mm_s",
    "pressure_bar",
    "power_kw",
}


def load_telemetry(path: str | Path) -> list[TelemetryRecord]:
    """Load a UTF-8 CSV export from a historian, gateway or simulator."""
    with Path(path).open(newline="", encoding="utf-8") as source:
        reader = csv.DictReader(source)
        columns = set(reader.fieldnames or [])
        missing = REQUIRED_COLUMNS - columns
        if missing:
            raise ValueError(f"Missing required columns: {', '.join(sorted(missing))}")

        records: list[TelemetryRecord] = []
        for line_number, row in enumerate(reader, start=2):
            try:
                records.append(
                    TelemetryRecord(
                        timestamp=datetime.fromisoformat(row["timestamp"]),
                        asset_id=row["asset_id"].strip(),
                        temperature_c=float(row["temperature_c"]),
                        vibration_mm_s=float(row["vibration_mm_s"]),
                        pressure_bar=float(row["pressure_bar"]),
                        power_kw=float(row["power_kw"]),
                    )
                )
            except (TypeError, ValueError) as error:
                raise ValueError(f"Invalid telemetry at line {line_number}: {error}") from error
    return records


def write_anomalies(path: str | Path, anomalies: list[Anomaly]) -> None:
    fields = ["timestamp", "asset_id", "severity", "score", "reasons"]
    with Path(path).open("w", newline="", encoding="utf-8") as destination:
        writer = csv.DictWriter(destination, fieldnames=fields)
        writer.writeheader()
        for anomaly in anomalies:
            row = anomaly.to_dict()
            row["reasons"] = " | ".join(anomaly.reasons)
            writer.writerow(row)
