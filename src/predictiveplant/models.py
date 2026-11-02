"""Domain models shared by the ingestion, validation and detection layers."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime


@dataclass(frozen=True)
class TelemetryRecord:
    timestamp: datetime
    asset_id: str
    temperature_c: float
    vibration_mm_s: float
    pressure_bar: float
    power_kw: float


@dataclass(frozen=True)
class Anomaly:
    timestamp: datetime
    asset_id: str
    severity: str
    score: float
    reasons: tuple[str, ...]

    def to_dict(self) -> dict[str, object]:
        payload = asdict(self)
        payload["timestamp"] = self.timestamp.isoformat()
        payload["reasons"] = list(self.reasons)
        return payload
