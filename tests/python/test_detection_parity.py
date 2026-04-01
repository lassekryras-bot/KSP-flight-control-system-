from __future__ import annotations

import csv
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.python.detection import DualThresholdLaunchDetector


FIXTURE = Path(__file__).resolve().parents[1] / "fixtures" / "telemetry_profile.csv"


def load_fixture() -> list[tuple[float, float]]:
    with FIXTURE.open("r", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        return [
            (float(row["time_s"]), float(row["vertical_velocity_mps"]))
            for row in reader
        ]


def test_dual_threshold_detector_with_shared_fixture() -> None:
    detector = DualThresholdLaunchDetector(
        liftoff_threshold=0.01,
        ascent_threshold=1.0,
        ascent_duration=0.2,
    )

    telemetry = load_fixture()
    prev_time = telemetry[0][0]

    liftoff_time = None
    stable_ascent_time = None

    for current_time, velocity in telemetry:
        dt = current_time - prev_time
        prev_time = current_time

        liftoff_event, ascent_event = detector.update(velocity, dt)

        if liftoff_event and liftoff_time is None:
            liftoff_time = current_time
        if ascent_event and stable_ascent_time is None:
            stable_ascent_time = current_time

    assert liftoff_time == 0.1
    assert stable_ascent_time == 0.5
