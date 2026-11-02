"""PredictivePlant: explainable industrial telemetry monitoring."""

from .detector import DetectionConfig, detect_anomalies
from .models import Anomaly, TelemetryRecord

__all__ = ["Anomaly", "DetectionConfig", "TelemetryRecord", "detect_anomalies"]
