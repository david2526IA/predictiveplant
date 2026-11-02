"""Deterministic synthetic industrial telemetry for demos and automated tests."""

from __future__ import annotations

import csv
import random
from datetime import datetime, timedelta, timezone
from pathlib import Path


def generate(path: str | Path, rows_per_asset: int = 240, seed: int = 42) -> None:
    """Generate two pump signals and inject labelled degradation episodes."""
    if rows_per_asset < 24:
        raise ValueError("rows_per_asset must be at least 24")
    randomizer = random.Random(seed)
    start = datetime(2026, 1, 1, tzinfo=timezone.utc)
    fields = ["timestamp", "asset_id", "temperature_c", "vibration_mm_s", "pressure_bar", "power_kw"]
    with Path(path).open("w", newline="", encoding="utf-8") as destination:
        writer = csv.DictWriter(destination, fieldnames=fields)
        writer.writeheader()
        for asset_index, asset_id in enumerate(("PUMP-01", "PUMP-02")):
            for index in range(rows_per_asset):
                degradation = 0.0
                if asset_id == "PUMP-01" and rows_per_asset * 0.72 <= index < rows_per_asset * 0.80:
                    degradation = 7.5
                writer.writerow(
                    {
                        "timestamp": (start + timedelta(minutes=15 * index)).isoformat(),
                        "asset_id": asset_id,
                        "temperature_c": round(62 + asset_index + degradation * 3.4 + randomizer.gauss(0, 0.8), 3),
                        "vibration_mm_s": round(2.6 + degradation + randomizer.gauss(0, 0.16), 3),
                        "pressure_bar": round(7.4 - degradation * 0.23 + randomizer.gauss(0, 0.08), 3),
                        "power_kw": round(18 + degradation * 0.65 + randomizer.gauss(0, 0.22), 3),
                    }
                )
