#!/usr/bin/env python3
"""Run a lightweight offline simulation summary from recorded CSV runs."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path
import sys

# Allow importing from repository root when executed as a script.
REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from analysis.stats import analyze

REQUIRED_COLUMNS = {"run_id", "ramp_rate", "time", "throttle", "velocity"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run offline analysis on flight run CSV data."
    )
    parser.add_argument(
        "--data",
        default="data/runs.csv",
        help="Path to CSV file containing run data (default: data/runs.csv).",
    )
    return parser.parse_args()


def validate_csv(path: Path) -> None:
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None:
            raise ValueError("CSV file is missing a header row.")

        missing = REQUIRED_COLUMNS - set(reader.fieldnames)
        if missing:
            missing_str = ", ".join(sorted(missing))
            raise ValueError(f"CSV file is missing required columns: {missing_str}")


def main() -> int:
    args = parse_args()
    data_path = (REPO_ROOT / args.data).resolve()

    if not data_path.exists():
        print(f"Data file not found: {data_path}")
        return 1

    try:
        validate_csv(data_path)
    except ValueError as exc:
        print(f"Invalid data file: {exc}")
        return 2

    print("=== Flight Test Analysis ===")
    print(f"Data source: {data_path}")
    analyze(str(data_path))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
