#!/usr/bin/env python3
"""Run parachute deployment envelope mapping scenarios.

This keeps flight logic unchanged and only sweeps the semi-deploy altitude
trigger to characterize safe vs. unsafe operating regions.
"""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.python.config_loader import load_config
from src.python.simulator import FlightSimulator


DEFAULT_SWEEP_ALTITUDES = [2000, 1800, 1500, 1200, 1000, 800, 600]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Sweep parachute deployment altitude and report landing envelope."
    )
    parser.add_argument(
        "--altitudes",
        nargs="+",
        type=float,
        default=DEFAULT_SWEEP_ALTITUDES,
        help="Semi-deployment trigger altitudes in meters.",
    )
    parser.add_argument(
        "--max-time",
        type=float,
        default=60.0,
        help="Simulation run time in seconds for each scenario.",
    )
    return parser.parse_args()


def classify_result(touchdown_velocity: float, safe_threshold: float) -> str:
    speed = abs(touchdown_velocity)
    if speed <= safe_threshold:
        return "safe"
    if speed <= safe_threshold * 1.5:
        return "marginal"
    return "fail"


def run_sweep(altitudes: list[float], max_time: float) -> list[dict]:
    results: list[dict] = []
    for altitude in altitudes:
        cfg = load_config()
        cfg["detection"]["parachute"]["semi"]["altitude"] = altitude
        cfg["vehicle"]["engine"]["throttleable"] = False
        cfg["vehicle"]["engine"]["thrust"] = 0.0
        cfg["vehicle"]["fuel_mass"] = 0.0

        sim = FlightSimulator(config=cfg)
        sim.mode = "descent"
        sim.altitude = max(altitudes) + 300.0
        sim.velocity = -55.0
        sim.fuel_mass = 0.0
        sim.mass = sim.dry_mass
        run = sim.run(max_time=max_time)

        threshold = cfg["guidance"]["descent"]["safe_landing_velocity"]
        results.append(
            {
                "deploy_altitude_setting_m": altitude,
                "deploy_altitude_measured_m": run["deploy_altitude"],
                "deploy_velocity_mps": run["deploy_velocity"],
                "velocity_at_full_deploy_mps": run["velocity_at_full_deploy"],
                "time_to_full_deploy_s": run["time_to_full_deploy"],
                "touchdown_velocity_mps": run["touchdown_velocity"],
                "outcome": classify_result(run["touchdown_velocity"], threshold),
            }
        )
    return results


def print_results(results: list[dict]) -> None:
    print("deployment_setting_m,deploy_measured_m,deploy_v_mps,full_deploy_v_mps,time_to_full_s,touchdown_v_mps,outcome")
    for row in results:
        print(
            "{setting:.0f},{measured:.2f},{deploy_v:.2f},{full_v},{time_full},{touchdown:.2f},{outcome}".format(
                setting=row["deploy_altitude_setting_m"],
                measured=row["deploy_altitude_measured_m"] or float("nan"),
                deploy_v=row["deploy_velocity_mps"] or float("nan"),
                full_v=(
                    f"{row['velocity_at_full_deploy_mps']:.2f}"
                    if row["velocity_at_full_deploy_mps"] is not None
                    else "NA"
                ),
                time_full=(
                    f"{row['time_to_full_deploy_s']:.2f}"
                    if row["time_to_full_deploy_s"] is not None
                    else "NA"
                ),
                touchdown=row["touchdown_velocity_mps"],
                outcome=row["outcome"],
            )
        )


def main() -> int:
    args = parse_args()
    results = run_sweep(args.altitudes, args.max_time)
    print_results(results)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
