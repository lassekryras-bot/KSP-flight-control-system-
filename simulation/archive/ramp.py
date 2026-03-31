import time

class ThrottleRamp:
    def __init__(self, ramp_rate):
        self.ramp_rate = ramp_rate
        self.start_time = None
        self.active = False

    def start(self):
        self.start_time = time.time()
        self.active = True

    def stop(self):
        self.active = False

    def get_throttle(self):
        if not self.active:
            return 0.0
        elapsed = time.time() - self.start_time
        return min(self.ramp_rate * elapsed, 1.0)
