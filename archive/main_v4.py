import math
import random

# --- Constants ---
INITIAL_MASS = 3.6 * 1000   # kg
THRUST = 215000             # N
G = 9.81
DT = 0.01
FUEL_BURN_RATE = 5.0        # kg/sec
NOISE_LEVEL = 0.05          # velocity noise


# --- Throttle Ramp ---
class ThrottleRamp:
    def __init__(self, ramp_rate):
        self.ramp_rate = ramp_rate
        self.time = 0.0
        self.active = False

    def start(self):
        self.time = 0.0
        self.active = True

    def update(self, dt):
        if self.active:
            self.time += dt

    def get_throttle(self):
        if not self.active:
            return 0.0
        return min(self.ramp_rate * self.time, 1.0)


# --- Detection ---
class DetectionSystem:
    def __init__(self, threshold, duration):
        self.threshold = threshold
        self.duration = duration
        self.timer = 0.0
        self.triggered = False

    def update(self, velocity, dt):
        if self.triggered:
            return False

        if velocity >= self.threshold:
            self.timer += dt
            if self.timer >= self.duration:
                self.triggered = True
                return True
        else:
            self.timer = 0.0

        return False


# --- Physics ---
def update_velocity(throttle, velocity, mass):
    force = throttle * THRUST
    weight = mass * G
    acceleration = (force - weight) / mass

    # Add noise
    velocity += random.uniform(-NOISE_LEVEL, NOISE_LEVEL)

    return velocity + acceleration * DT


# --- Single Run ---
def run_single_test(ramp_rate=0.25):
    ramp = ThrottleRamp(ramp_rate)

    # Dual detection
    liftoff_detect = DetectionSystem(0.01, 0.0)
    ascent_detect = DetectionSystem(1.0, 0.2)

    velocity = 0.0
    mass = INITIAL_MASS

    ramp.start()

    liftoff_throttle = None
    ascent_throttle = None

    while True:
        ramp.update(DT)
        throttle = ramp.get_throttle()

        # Burn fuel
        mass = max(1000, mass - FUEL_BURN_RATE * DT)

        velocity = update_velocity(throttle, velocity, mass)

        # Detect liftoff
        if liftoff_throttle is None and liftoff_detect.update(velocity, DT):
            liftoff_throttle = throttle

        # Detect stable ascent
        if ascent_detect.update(velocity, DT):
            ascent_throttle = throttle
            break

    return liftoff_throttle, ascent_throttle


# --- Batch Run ---
def run_tests(n=20):
    liftoff_results = []
    ascent_results = []

    for i in range(n):
        liftoff, ascent = run_single_test()

        liftoff_results.append(liftoff)
        ascent_results.append(ascent)

        print(f"Run {i+1}: liftoff={liftoff:.3f}, ascent={ascent:.3f}")

    return liftoff_results, ascent_results


# --- Analysis ---
def analyze(label, results):
    avg = sum(results) / len(results)
    var = sum((x - avg) ** 2 for x in results) / len(results)
    std = math.sqrt(var)

    print(f"\n--- {label} ---")
    print("Average:", round(avg, 3))
    print("Std Dev:", round(std, 3))
    print("Min:", round(min(results), 3))
    print("Max:", round(max(results), 3))


# --- Export ---
def export_csv(liftoff, ascent):
    print("\nrun,liftoff,ascent")
    for i in range(len(liftoff)):
        print(f"{i+1},{liftoff[i]:.3f},{ascent[i]:.3f}")


# --- Execute ---
if __name__ == "__main__":
    liftoff, ascent = run_tests(20)

    analyze("Liftoff Threshold", liftoff)
    analyze("Stable Ascent", ascent)

    export_csv(liftoff, ascent)
