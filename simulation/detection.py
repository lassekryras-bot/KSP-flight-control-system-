import time

class DetectionSystem:
    def __init__(self, threshold, duration):
        self.threshold = threshold
        self.duration = duration
        self.start_time = None

    def update(self, velocity):
        now = time.time()
        if velocity >= self.threshold:
            if self.start_time is None:
                self.start_time = now
            if (now - self.start_time) >= self.duration:
                return True
        else:
            self.start_time = None
        return False
