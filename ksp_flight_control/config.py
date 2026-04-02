import argparse
from dataclasses import dataclass, field

from ksp_flight_control.specs import DEFAULT_PARACHUTE_SPEC, PROJECT_CONFIG, ParachuteSpec


@dataclass(frozen=True)
class AppConfig:
    parachute_mode: str = "simulate"
    parachute_test: bool = False
    parachute_arm_altitude: float = 1500.0
    parachute_arm_speed: float = PROJECT_CONFIG.sim_physics.default_safe_vertical_speed_mps
    auto_trigger_policy_mode: str = "observe_only"
    parachute_spec: ParachuteSpec = field(default_factory=lambda: DEFAULT_PARACHUTE_SPEC)


def parse_args() -> AppConfig:
    parser = argparse.ArgumentParser(description="Basic kRPC launch telemetry and recovery helper.")
    parser.add_argument(
        "--parachute-mode",
        choices=("off", "simulate", "live"),
        default="simulate",
        help="How parachute safety should behave.",
    )
    parser.add_argument(
        "--parachute-test",
        action="store_true",
        help="Run a one-shot parachute safety evaluation for the current vessel, then exit.",
    )
    parser.add_argument(
        "--parachute-arm-altitude",
        type=float,
        default=1500.0,
        help="Surface altitude in meters below which parachutes may be armed.",
    )
    parser.add_argument(
        "--parachute-arm-speed",
        type=float,
        default=PROJECT_CONFIG.sim_physics.default_safe_vertical_speed_mps,
        help="Vertical speed threshold in m/s for parachute arming. Negative means descending.",
    )
    parser.add_argument(
        "--auto-trigger-policy",
        choices=("strict", "best_effort", "observe_only"),
        default="observe_only",
        help="Policy mode for the continuous auto-trigger controller.",
    )
    namespace = parser.parse_args()
    return AppConfig(
        parachute_mode=namespace.parachute_mode,
        parachute_test=namespace.parachute_test,
        parachute_arm_altitude=namespace.parachute_arm_altitude,
        parachute_arm_speed=namespace.parachute_arm_speed,
        auto_trigger_policy_mode=namespace.auto_trigger_policy,
    )
