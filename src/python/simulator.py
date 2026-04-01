from dataclasses import dataclass, field

from src.python.config_loader import load_config
from src.python.detection import DualThresholdLaunchDetector


@dataclass
class FlightSimulator:
    config: dict = field(default_factory=load_config)
    mode: str = "ground"
    time: float = 0.0
    altitude: float = 0.0
    velocity: float = 0.0
    throttle: float = 0.0
    prev_throttle: float = 0.0
    transitions: list[tuple[float, str, str]] = field(default_factory=list)
    parachute_armed: bool = False
    parachute_full_deploy: bool = False
    parachute_deploy_time: float | None = None
    parachute_deploy_altitude: float | None = None
    parachute_deploy_velocity: float | None = None
    parachute_full_deploy_time: float | None = None
    parachute_full_deploy_velocity: float | None = None

    def __post_init__(self) -> None:
        physics = self.config["physics"]
        vehicle = self.config["vehicle"]
        control = self.config["control"]

        self.g = physics["gravity"]
        self.dt = physics["timestep"]
        atmosphere = physics.get("atmosphere", {})
        self.air_density = atmosphere.get("density", 1.225)

        self.dry_mass = vehicle["dry_mass"] * 1000.0
        self.fuel_mass = vehicle["fuel_mass"] * 1000.0
        self.thrust = vehicle["engine"]["thrust"]
        self.throttleable = vehicle["engine"]["throttleable"]

        self.kp = control["kp"]
        self.kd = control["kd"]
        self.smoothing = control["smoothing"]

        self.mass = self.dry_mass + self.fuel_mass

        self.launch_detector = DualThresholdLaunchDetector(
            liftoff_threshold=0.01,
            ascent_threshold=1.0,
            ascent_duration=0.2,
        )
        parachute_cfg = self.config.get("detection", {}).get("parachute", {})
        self.parachute_semi_altitude = parachute_cfg.get("semi", {}).get("altitude", 1800.0)
        self.parachute_full_altitude = parachute_cfg.get("full", {}).get("altitude", 1000.0)
        drag_cfg = parachute_cfg.get("drag", {})
        self.parachute_semi_cd_area = drag_cfg.get("semi", {}).get("cd_area", 220.0)
        self.parachute_full_cd_area = drag_cfg.get("full", {}).get("cd_area", 960.0)
        self.safe_landing_velocity = self.config.get("guidance", {}).get("descent", {}).get(
            "safe_landing_velocity", 6.0
        )

    def _update_parachute_state(self) -> None:
        descending = self.velocity < 0.0
        if not self.parachute_armed and descending and self.altitude <= self.parachute_semi_altitude:
            self.parachute_armed = True
            self.parachute_deploy_time = self.time
            self.parachute_deploy_altitude = self.altitude
            self.parachute_deploy_velocity = self.velocity

        if self.parachute_armed and self.altitude <= self.parachute_full_altitude:
            self.parachute_full_deploy = True
            if self.parachute_full_deploy_time is None:
                self.parachute_full_deploy_time = self.time
                self.parachute_full_deploy_velocity = self.velocity

    def _compute_parachute_drag_acceleration(self) -> float:
        if not self.parachute_armed or self.velocity >= 0.0:
            return 0.0

        cd_area = self.parachute_full_cd_area if self.parachute_full_deploy else self.parachute_semi_cd_area
        drag_force = 0.5 * self.air_density * cd_area * (self.velocity * self.velocity)
        return drag_force / self.mass

    def set_mode(self, new_mode: str) -> None:
        if self.mode != new_mode:
            self.transitions.append((round(self.time, 2), self.mode, new_mode))
            self.mode = new_mode

    def can_land(self) -> bool:
        if not self.throttleable or self.fuel_mass <= 0:
            return False
        max_acc = (self.thrust / self.mass) - self.g
        if max_acc <= 0:
            return False
        t_stop = abs(self.velocity) / max_acc
        stopping_distance = abs(self.velocity) * t_stop * 0.5
        return stopping_distance < self.altitude

    def compute_throttle(self, target_velocity: float) -> float:
        if not self.throttleable:
            return 0.0

        hover = (self.mass * self.g) / self.thrust
        error = target_velocity - self.velocity
        raw = hover + (self.kp * error) - (self.kd * self.velocity)
        raw = max(0.0, min(1.0, raw))

        smoothed = self.prev_throttle + (raw - self.prev_throttle) * self.smoothing
        self.prev_throttle = smoothed
        return smoothed

    def step(self) -> dict:
        if self.mode == "ground":
            self.set_mode("takeoff")

        if self.mode == "takeoff":
            self.throttle = 1.0
            if self.altitude > self.config["state_transitions"]["takeoff_to_ascent_altitude"]:
                self.set_mode("ascent")
        elif self.mode == "ascent":
            self.throttle = self.compute_throttle(5.0)
            if self.velocity < 0:
                self.set_mode("descent")
        elif self.mode == "descent":
            self.throttle = 0.0
            if self.altitude < self.config["state_transitions"]["descent_to_landing_altitude"]:
                self.set_mode("landing" if self.can_land() else "free_fall")
        elif self.mode == "landing":
            switch_alt = self.config["guidance"]["landing"]["switch_altitude"]
            target = (
                self.config["guidance"]["landing"]["high_altitude_velocity"]
                if self.altitude > switch_alt
                else self.config["guidance"]["landing"]["low_altitude_velocity"]
            )
            self.throttle = self.compute_throttle(target)
        else:
            self.throttle = 0.0

        self._update_parachute_state()

        thrust_force = self.thrust * self.throttle if self.throttleable else self.thrust
        acceleration = (thrust_force - (self.mass * self.g)) / self.mass
        acceleration += self._compute_parachute_drag_acceleration()

        self.velocity += acceleration * self.dt
        self.altitude = max(0.0, self.altitude + self.velocity * self.dt)

        if self.fuel_mass > 0:
            self.fuel_mass = max(0.0, self.fuel_mass - (5.0 * self.dt))
            self.mass = self.dry_mass + self.fuel_mass

        liftoff, ascent = self.launch_detector.update(self.velocity, self.dt)

        self.time += self.dt
        return {
            "time": self.time,
            "mode": self.mode,
            "altitude": self.altitude,
            "velocity": self.velocity,
            "throttle": self.throttle,
            "parachute_armed": self.parachute_armed,
            "parachute_full_deploy": self.parachute_full_deploy,
            "liftoff_event": liftoff,
            "ascent_event": ascent,
        }

    def run(self, max_time: float = 60.0) -> dict:
        events = {"liftoff": None, "stable_ascent": None}
        while self.time < max_time:
            row = self.step()
            if row["liftoff_event"] and events["liftoff"] is None:
                events["liftoff"] = (row["time"], row["throttle"])
            if row["ascent_event"] and events["stable_ascent"] is None:
                events["stable_ascent"] = (row["time"], row["throttle"])

            if self.altitude <= 0 and self.time > 2.0:
                break

        return {
            "events": events,
            "touchdown_velocity": self.velocity,
            "landing_safe": abs(self.velocity) <= self.safe_landing_velocity,
            "deploy_altitude": self.parachute_deploy_altitude,
            "deploy_velocity": self.parachute_deploy_velocity,
            "time_to_full_deploy": (
                self.parachute_full_deploy_time - self.parachute_deploy_time
                if self.parachute_full_deploy_time is not None and self.parachute_deploy_time is not None
                else None
            ),
            "velocity_at_full_deploy": self.parachute_full_deploy_velocity,
            "transitions": self.transitions,
        }
