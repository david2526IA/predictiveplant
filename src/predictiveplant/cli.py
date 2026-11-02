"""Command-line interface for local, reproducible analysis."""

from __future__ import annotations

import argparse
from pathlib import Path

from .detector import detect_anomalies
from .io import load_telemetry, write_anomalies
from .synthetic import generate
from .validation import validate


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="predictiveplant")
    commands = parser.add_subparsers(dest="command", required=True)
    demo = commands.add_parser("demo", help="generate deterministic pump telemetry")
    demo.add_argument("--output", default="data/sample_telemetry.csv")
    demo.add_argument("--rows", type=int, default=240)
    analyze = commands.add_parser("analyze", help="validate and analyse telemetry CSV")
    analyze.add_argument("input")
    analyze.add_argument("--output", default="artifacts/anomalies.csv")
    return parser


def main() -> None:
    args = _parser().parse_args()
    if args.command == "demo":
        Path(args.output).parent.mkdir(parents=True, exist_ok=True)
        generate(args.output, rows_per_asset=args.rows)
        print(f"Demo telemetry written to {args.output}")
        return
    records = load_telemetry(args.input)
    report = validate(records)
    if report.rejected_records:
        raise SystemExit("Data quality failed:\n- " + "\n- ".join(report.issues))
    anomalies = detect_anomalies(records)
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    write_anomalies(args.output, anomalies)
    critical = sum(item.severity == "critical" for item in anomalies)
    print(f"Validated {report.valid_records} records; found {len(anomalies)} anomalies ({critical} critical).")
    print(f"Anomaly report written to {args.output}")


if __name__ == "__main__":
    main()
