"""Optional FastAPI service for integrating the detector into other systems."""

from __future__ import annotations

from datetime import datetime

from fastapi import FastAPI
from pydantic import BaseModel

from .detector import detect_anomalies
from .models import TelemetryRecord
from .validation import validate

app = FastAPI(title="PredictivePlant API", version="0.1.0")


class TelemetryPayload(BaseModel):
    timestamp: datetime
    asset_id: str
    temperature_c: float
    vibration_mm_s: float
    pressure_bar: float
    power_kw: float


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/v1/anomalies")
def analyse(payload: list[TelemetryPayload]) -> dict[str, object]:
    records = [TelemetryRecord(**item.model_dump()) for item in payload]
    quality = validate(records)
    return {
        "quality": {
            "valid_records": quality.valid_records,
            "rejected_records": quality.rejected_records,
            "issues": list(quality.issues),
        },
        "anomalies": [item.to_dict() for item in detect_anomalies(records)] if not quality.rejected_records else [],
    }
