from dataclasses import dataclass


@dataclass
class DetectionSystem:
    threshold: float
    duration: float
    triggered: bool = False
    _timer: float = 0.0

    def reset(self) -> None:
        self.triggered = False
        self._timer = 0.0

    def update(self, value: float, dt: float) -> bool:
        """Deterministic dt-driven threshold detector."""
        if self.triggered:
            return False

        if value >= self.threshold:
            self._timer += dt
            if self._timer >= self.duration:
                self.triggered = True
                return True
        else:
            self._timer = 0.0

        return False


class DualThresholdLaunchDetector:
    """Tracks liftoff and stable-ascent separately."""

    def __init__(self, liftoff_threshold: float, ascent_threshold: float, ascent_duration: float) -> None:
        self.liftoff = DetectionSystem(liftoff_threshold, 0.0)
        self.ascent = DetectionSystem(ascent_threshold, ascent_duration)

    def update(self, vertical_velocity: float, dt: float) -> tuple[bool, bool]:
        liftoff_event = self.liftoff.update(vertical_velocity, dt)
        ascent_event = self.ascent.update(vertical_velocity, dt)
        return liftoff_event, ascent_event
