from dataclasses import replace

from ksp_flight_control.config import AppConfig
from ksp_flight_control.physics import BasicPhysicsSimulator
from ksp_flight_control.sim import SimParachute, SimTelemetry, SimVessel
from ksp_flight_control.specs import DEFAULT_PARACHUTE_SPEC, ParachuteSpec


def make_config(**overrides) -> AppConfig:
    base = AppConfig()
    return replace(base, **overrides)


def make_parachute(state: str = "unactivated", spec: ParachuteSpec = DEFAULT_PARACHUTE_SPEC) -> SimParachute:
    return SimParachute(state=state, spec=spec)


def make_vessel(
    situation: str = "flying",
    parachutes: list[SimParachute] | None = None,
    mass_kg: float = 100.0,
    has_command_module: bool = True,
    name: str = "Sim Vessel",
) -> SimVessel:
    return SimVessel(
        name=name,
        situation=situation,
        mass_kg=mass_kg,
        has_command_module=has_command_module,
        parachutes=[] if parachutes is None else parachutes,
    )


def make_telemetry(**overrides) -> dict:
    return SimTelemetry(**overrides).as_values()


def make_simulator() -> BasicPhysicsSimulator:
    return BasicPhysicsSimulator()
