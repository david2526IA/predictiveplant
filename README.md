# PredictivePlant

> Explainable anomaly detection for industrial telemetry — designed as a portfolio-grade, reproducible reference project.

[![CI](https://github.com/david2526IA/predictiveplant/actions/workflows/ci.yml/badge.svg)](https://github.com/david2526IA/predictiveplant/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-2563EB.svg)](LICENSE)

PredictivePlant turns time-stamped measurements from pumps, motors or similar assets into an auditable anomaly report. It is intentionally small enough to understand end-to-end, while modelling the engineering practices expected in an industrial data product: input contracts, data-quality gates, explainable scoring, tests, a CLI and an optional API.

## Why it matters

Condition monitoring is only useful when the people operating a plant can understand and trust the alert. Rather than return an opaque label, PredictivePlant reports the signal and robust score behind each alert — for example, unusual vibration combined with a critical temperature threshold.

The included demo simulates two pumps and injects a progressive degradation episode into one of them. No claim is made that this synthetic example replaces calibrated thresholds, historian data or a safety-certified system.

## Features

- **Data contract:** strict CSV schema for timestamp, asset ID, temperature, vibration, pressure and power.
- **Quality gates:** engineering-range, finite-value and chronological-order checks before analysis.
- **Robust detection:** median absolute deviation (MAD) scoring resists distortion from outliers.
- **Explainable output:** severity, score and the exact reasons that generated an alert.
- **Reproducibility:** deterministic demo data, unit tests and a GitHub Actions workflow.
- **Integration-ready:** optional FastAPI service and Docker image.

## Architecture

```text
CSV / gateway export
        │
        ▼
  Schema + quality checks ── rejected data ──► actionable errors
        │
        ▼
 Robust baseline per asset (median / MAD)
        │
        ▼
 Explainable anomaly report (CSV or JSON API)
```

## Quick start

The core library has no third-party runtime dependencies.

```bash
git clone https://github.com/david2526IA/predictiveplant.git
cd predictiveplant
python -m venv .venv
```

Activate the virtual environment (`.venv\\Scripts\\Activate.ps1` on PowerShell, or `source .venv/bin/activate` on Linux/macOS), then:

```bash
pip install -e ".[dev]"
predictiveplant demo --output data/sample_telemetry.csv
predictiveplant analyze data/sample_telemetry.csv --output artifacts/anomalies.csv
pytest -q
```

Expected result: the synthetic degradation event in `PUMP-01` is detected and an `artifacts/anomalies.csv` report is written.

## Optional API

```bash
pip install -e ".[api]"
uvicorn predictiveplant.api:app --reload
```

Open `http://127.0.0.1:8000/docs` to explore the endpoint. For a containerised run:

```bash
docker build -t predictiveplant .
docker run --rm -p 8000:8000 predictiveplant
```

## Input contract

```csv
timestamp,asset_id,temperature_c,vibration_mm_s,pressure_bar,power_kw
2026-01-01T00:00:00+00:00,PUMP-01,62.4,2.7,7.4,18.1
```

Timestamps must be ISO 8601 and strictly increasing per asset. The validator rejects measurements outside conservative engineering bounds; adapt these bounds, thresholds and asset-specific baselines to the equipment and site before any real deployment.

## Roadmap

- [ ] OPC UA / MQTT ingestion adapters
- [ ] Configurable asset-specific thresholds
- [ ] Model registry and drift monitoring
- [ ] Dashboard for trends, acknowledgement and maintenance feedback
- [ ] Integration tests against a simulated PLC/SCADA source

## Safety and scope

This project is for learning, prototyping and portfolio demonstration. It must not directly control machinery or be used as the sole source for safety, maintenance or operational decisions.

## License

MIT © 2026 David Falcon
