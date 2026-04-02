from dataclasses import dataclass, field

from ksp_flight_control.specs import DEFAULT_PARACHUTE_SPEC, ParachuteSpec


@dataclass
class SimParachute:
    state: str = "unactivated"
    spec: ParachuteSpec = DEFAULT_PARACHUTE_SPEC
    time_in_state: float = 0.0
    arm_calls: int = 0
    semi_deploy_calls: int = 0
    full_deploy_calls: int = 0

    @property
    def armed(self):
        return self.state in {"armed", "semi_deployed", "fully_deployed"}

    @property
    def deployed(self):
        return self.state in {"semi_deployed", "fully_deployed"}

    def arm(self):
        if self.state != "armed":
            self.state = "armed"
            self.time_in_state = 0.0
            self.arm_calls += 1

    def semi_deploy(self):
        if self.state != "semi_deployed":
            self.state = "semi_deployed"
            self.time_in_state = 0.0
            self.semi_deploy_calls += 1

    def fully_deploy(self):
        if self.state != "fully_deployed":
            self.state = "fully_deployed"
            self.time_in_state = 0.0
            self.full_deploy_calls += 1

    def advance_time(self, dt: float):
        self.time_in_state += dt


@dataclass
class SimParts:
    parachutes: list[SimParachute] = field(default_factory=list)


@dataclass
class SimVessel:
    name: str = "Sim Vessel"
    situation: str = "flying"
    mass_kg: float = 100.0
    has_command_module: bool = True
    parachutes: list[SimParachute] = field(default_factory=list)

    def __post_init__(self):
        self.parts = SimParts(parachutes=self.parachutes)


@dataclass
class SimTelemetry:
    altitude: float = 0.0
    apoapsis: float = 0.0
    speed: float = 0.0
    vertical_speed: float = 0.0
    surface_altitude: float = 0.0
    pressure_atm: float = 0.0
    time_in_state: float = 0.0
    mass: float = 0.0
    resources: dict = field(default_factory=dict)

    def as_values(self):
        return {
            "altitude": self.altitude,
            "apoapsis": self.apoapsis,
            "speed": self.speed,
            "vertical_speed": self.vertical_speed,
            "surface_altitude": self.surface_altitude,
            "pressure_atm": self.pressure_atm,
            "time_in_state": self.time_in_state,
            "mass": self.mass,
            "resources": self.resources,
        }


@dataclass
class SimFlightState:
    vessel: SimVessel
    altitude: float
    vertical_speed: float
    elapsed_time: float = 0.0
    pressure_atm: float = 0.0
    impact_speed: float | None = None

    def as_telemetry(self):
        return SimTelemetry(
            altitude=self.altitude,
            apoapsis=self.altitude,
            speed=abs(self.vertical_speed),
            vertical_speed=self.vertical_speed,
            surface_altitude=self.altitude,
            pressure_atm=self.pressure_atm,
            mass=self.vessel.mass_kg,
        )
