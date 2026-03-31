#!/usr/bin/env python3
"""Run a lightweight offline simulation summary from recorded CSV runs.

This script validates that the data file exists and delegates statistical output
to analysis.stats.analyze.
"""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

# Allow importing from repository root when executed as a script.
REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from analysis.stats import analyze


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


def main() -> int:
    args = parse_args()
    data_path = REPO_ROOT / args.data

    if not data_path.exists():
        print(f"Data file not found: {data_path}")
        return 1

    print("=== Flight Test Analysis ===")
    print(f"Data source: {data_path}")
    analyze(str(data_path))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
