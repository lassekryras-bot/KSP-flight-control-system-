#!/usr/bin/env python3
"""Run simulation utilities for offline analysis.

Default behavior summarizes existing CSV run data. Optionally, this can run the
integrated deterministic simulator and print key events.
"""

from __future__ import annotations

import argparse
from pathlib import Path
from pprint import pprint
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from analysis.stats import analyze
from src.python.simulator import FlightSimulator
from src.python.vehicle_registry import build_vehicle


def run_stats(csv_file: Path) -> None:
    """Print summary stats from an existing run CSV."""
    analyze(str(csv_file))


def run_simulation(max_time: float) -> None:
    """Run the deterministic simulator and print event/transition output."""
    demo_vehicle = build_vehicle("Mk1 Command Pod", "LV-T45 Swivel", "Mk16", "FL-T100")
    print("Demo vehicle parts:")
    pprint(demo_vehicle)

    sim = FlightSimulator()
    result = sim.run(max_time=max_time)

    print("\n=== Simulation Summary ===")
    print(f"Liftoff event: {result['events']['liftoff']}")
    print(f"Stable ascent event: {result['events']['stable_ascent']}")
    print(f"Touchdown velocity: {result['touchdown_velocity']:.2f} m/s")
    print("Transitions:")
    for transition in result["transitions"]:
        print(f"  {transition}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run CSV stats or deterministic simulation.")
    parser.add_argument(
        "--mode",
        choices=("stats", "simulate"),
        default="stats",
        help="stats: summarize CSV data, simulate: run deterministic simulator",
    )
    parser.add_argument(
        "--csv",
        type=Path,
        default=REPO_ROOT / "data" / "runs.csv",
        help="CSV file for --mode stats",
    )
    parser.add_argument(
        "--max-time",
        type=float,
        default=90.0,
        help="Simulation max time in seconds for --mode simulate",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    if args.mode == "stats":
        run_stats(args.csv)
    else:
        run_simulation(args.max_time)
