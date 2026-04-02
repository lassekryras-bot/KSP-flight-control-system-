import math
from dataclasses import dataclass

from ksp_flight_control.logic import (
    get_parachute_spec,
    get_parachutes,
    normalize_parachute_state,
    resolve_parachute_transition_conflicts,
)
from ksp_flight_control.sim import SimFlightState, SimTelemetry, SimVessel
from ksp_flight_control.specs import DEFAULT_PARACHUTE_SPEC, PROJECT_CONFIG, ParachuteSpec, SimPhysicsConfig


TERMINAL_PARACHUTE_STATES = {"fully_deployed", "cut"}


@dataclass(frozen=True)
class PhysicsStepResult:
    telemetry: SimTelemetry
    net_acceleration: float
    drag_acceleration: float
    pressure_atm: float


class BasicPhysicsSimulator:
    def __init__(
        self,
        sim_physics: SimPhysicsConfig = PROJECT_CONFIG.sim_physics,
        parachute_spec: ParachuteSpec = DEFAULT_PARACHUTE_SPEC,
        gravity_mps2: float = PROJECT_CONFIG.constants.kerbin_surface_gravity_mps2,
    ):
        self.sim_physics = sim_physics
        self.parachute_spec = parachute_spec
        self.gravity_mps2 = gravity_mps2

    def create_state(
        self,
        altitude: float,
        vertical_speed: float,
        mass_kg: float = 100.0,
        parachutes: list | None = None,
        situation: str = "flying",
        name: str = "Sim Vessel",
    ) -> SimFlightState:
        vessel = SimVessel(
            name=name,
            situation=situation,
            mass_kg=mass_kg,
            parachutes=[] if parachutes is None else parachutes,
        )
        pressure_atm = self.compute_pressure_atm(altitude)
        return SimFlightState(
            vessel=vessel,
            altitude=altitude,
            vertical_speed=vertical_speed,
            pressure_atm=pressure_atm,
        )

    def compute_pressure_atm(self, altitude: float) -> float:
        clamped_altitude = max(0.0, altitude)
        return math.exp(-clamped_altitude / self.sim_physics.atmosphere_scale_height_m)

    def compute_density(self, pressure_atm: float) -> float:
        return self.sim_physics.surface_density_kgpm3 * max(0.0, pressure_atm)

    def compute_effective_drag_area(self, vessel: SimVessel) -> float:
        area = self.sim_physics.base_drag_area_m2
        for parachute in get_parachutes(vessel):
            spec = get_parachute_spec(parachute, self.parachute_spec)
            state = normalize_parachute_state(parachute)
            if state == "semi_deployed":
                area += spec.deployment.semi.drag * self.sim_physics.parachute_drag_area_scale
            elif state == "fully_deployed":
                area += spec.deployment.full.drag * self.sim_physics.parachute_drag_area_scale
        return area

    def _transition_parachutes(self, state: SimFlightState):
        telemetry_values = state.as_telemetry().as_values()
        parachutes = get_parachutes(state.vessel)

        for parachute in parachutes:
            telemetry_values["time_in_state"] = parachute.time_in_state

        transitions = resolve_parachute_transition_conflicts(parachutes, telemetry_values)
        for parachute, evaluation in transitions:
            next_stage = evaluation["next_stage"]
            if next_stage == "semi_deployed":
                parachute.semi_deploy()
            elif next_stage == "fully_deployed":
                parachute.fully_deploy()

    def step(self, state: SimFlightState, dt: float | None = None) -> PhysicsStepResult:
        dt = self.sim_physics.time_step_seconds if dt is None else dt

        state.pressure_atm = self.compute_pressure_atm(state.altitude)
        self._transition_parachutes(state)

        density = self.compute_density(state.pressure_atm)
        drag_area = self.compute_effective_drag_area(state.vessel)
        drag_force = 0.5 * density * drag_area * (state.vertical_speed ** 2)
        drag_acceleration = drag_force / state.vessel.mass_kg if state.vessel.mass_kg > 0 else 0.0

        if state.vertical_speed < 0:
            drag_acceleration = abs(drag_acceleration)
        elif state.vertical_speed > 0:
            drag_acceleration = -abs(drag_acceleration)
        else:
            drag_acceleration = 0.0

        net_acceleration = -self.gravity_mps2 + drag_acceleration
        state.vertical_speed += net_acceleration * dt
        state.altitude += state.vertical_speed * dt
        state.elapsed_time += dt
        state.pressure_atm = self.compute_pressure_atm(state.altitude)

        for parachute in get_parachutes(state.vessel):
            parachute.advance_time(dt)

        if state.altitude <= 0.0:
            if state.impact_speed is None:
                state.impact_speed = abs(state.vertical_speed)
            state.altitude = 0.0
            state.vertical_speed = 0.0
            state.vessel.situation = "landed"
        elif state.vertical_speed < 0:
            state.vessel.situation = "flying"

        return PhysicsStepResult(
            telemetry=state.as_telemetry(),
            net_acceleration=net_acceleration,
            drag_acceleration=drag_acceleration,
            pressure_atm=state.pressure_atm,
        )

    def run_until_ground(
        self,
        state: SimFlightState,
        max_steps: int = 100000,
    ) -> list[PhysicsStepResult]:
        history = []
        for _ in range(max_steps):
            result = self.step(state)
            history.append(result)
            if state.altitude <= 0.0:
                break
        return history
