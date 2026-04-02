from dataclasses import dataclass

from ksp_flight_control.logic import (
    get_parachute_spec,
    get_parachutes,
    get_situation_name,
    is_finite_number,
    normalize_parachute_state,
)
from ksp_flight_control.specs import DEFAULT_PARACHUTE_SPEC, PROJECT_CONFIG, ParachuteSpec, SimPhysicsConfig


IDLE_SITUATIONS = {"pre_launch", "landed", "splashed"}


@dataclass
class AutoTriggerState:
    trigger_count: int = 0
    classification: str = "monitoring"
    window_status: str = "unknown"
    reason: str = "Waiting for a valid descent phase."
    best_effort: bool = False


class AutoParachuteTriggerController:
    def __init__(
        self,
        sim_physics: SimPhysicsConfig = PROJECT_CONFIG.sim_physics,
        default_spec: ParachuteSpec = DEFAULT_PARACHUTE_SPEC,
        policy_mode: str | None = None,
    ):
        self.sim_physics = sim_physics
        self.default_spec = default_spec
        self.policy_mode = sim_physics.default_policy_mode if policy_mode is None else policy_mode
        self.policy = sim_physics.policy_for(self.policy_mode)

    def is_descending(self, vessel, values) -> bool:
        vertical_speed = values.get("vertical_speed")
        situation_name = get_situation_name(vessel)
        return (
            is_finite_number(vertical_speed)
            and vertical_speed <= self.sim_physics.descent_detection_vertical_speed_mps
            and situation_name not in IDLE_SITUATIONS
        )

    def evaluate_window(self, spec: ParachuteSpec, values: dict) -> dict:
        pressure_atm = values.get("pressure_atm")
        vertical_speed = values.get("vertical_speed")
        altitude = values.get("surface_altitude")

        if not all(is_finite_number(value) for value in (pressure_atm, vertical_speed, altitude)):
            return {
                "pressure_ok": False,
                "speed_ok": False,
                "window_status": "unknown",
                "reason": "Telemetry is incomplete.",
            }

        pressure_ok = pressure_atm >= spec.deployment.semi.min_pressure
        speed_ok = abs(vertical_speed) <= spec.safety.max_safe_full_deploy_speed

        if altitude <= self.sim_physics.unrecoverable_altitude_m:
            window_status = "missed"
            reason = "Altitude is below the unrecoverable threshold."
        elif pressure_ok and speed_ok:
            if altitude <= spec.deployment.full.deploy_altitude + self.sim_physics.narrow_window_altitude_margin_m:
                window_status = "narrow"
                reason = "Deployment window is narrow but still valid."
            else:
                window_status = "open"
                reason = "Deployment window is open."
        elif altitude <= spec.deployment.full.deploy_altitude:
            window_status = "missed"
            reason = "Safe deployment window has already been compromised."
        else:
            window_status = "closed"
            reason = "Deployment window is not yet safe."

        return {
            "pressure_ok": pressure_ok,
            "speed_ok": speed_ok,
            "window_status": window_status,
            "reason": reason,
        }

    def classify_window(self, window_status: str) -> str:
        if window_status == "narrow":
            return "risky"
        if window_status == "missed":
            return "unrecoverable"
        if window_status in {"open", "closed"}:
            return "safe"
        return "monitoring"

    def should_trigger_for_classification(self, classification: str) -> bool:
        if classification == "safe":
            return self.policy.trigger_in_safe
        if classification == "risky":
            return self.policy.trigger_in_risky
        if classification == "unrecoverable":
            return self.policy.trigger_in_unrecoverable
        return False

    def step(self, vessel, values: dict, state: AutoTriggerState | None = None) -> AutoTriggerState:
        state = AutoTriggerState() if state is None else state
        parachutes = get_parachutes(vessel)
        state.best_effort = False

        if not parachutes:
            state.classification = "unrecoverable"
            state.window_status = "missed"
            state.reason = "No parachutes are available."
            return state

        if not getattr(vessel, "has_command_module", True):
            state.classification = "unrecoverable"
            state.window_status = "missed"
            state.reason = "No command module is available for automatic arming."
            return state

        if not self.is_descending(vessel, values):
            state.classification = "monitoring"
            state.window_status = "closed"
            state.reason = "Waiting for a valid descent phase."
            return state

        if state.trigger_count > 0:
            return state

        unactivated = [
            parachute
            for parachute in parachutes
            if normalize_parachute_state(parachute) == "unactivated"
        ]
        if not unactivated:
            state.classification = "safe"
            state.window_status = "open"
            state.reason = "Parachutes are already armed or deployed."
            return state

        spec = get_parachute_spec(unactivated[0], self.default_spec)
        window = self.evaluate_window(spec, values)
        state.window_status = window["window_status"]
        state.classification = self.classify_window(window["window_status"])

        if self.should_trigger_for_classification(state.classification):
            for parachute in unactivated:
                parachute.arm()
            state.trigger_count = 1
            if state.classification == "unrecoverable":
                state.best_effort = True
                state.reason = "Safe deployment window was missed; policy allowed a best-effort trigger."
            else:
                state.reason = window["reason"]
            return state

        if self.policy_mode == "observe_only":
            state.reason = f"{window['reason']} Observe-only policy suppressed deployment."
        elif state.classification == "unrecoverable":
            state.reason = "Safe deployment window was missed before trigger."
        else:
            state.reason = f"{window['reason']} Policy suppressed deployment."
        return state
