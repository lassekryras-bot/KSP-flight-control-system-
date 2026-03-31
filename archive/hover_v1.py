import math

# =========================================================
# --- CONFIGURATION (easy to tweak later)
# =========================================================

TARGET_ALTITUDE = 2.0      # meters (hover target)
MARGIN = 0.2               # acceptable range ± around target
DT = 0.02                  # simulation timestep (seconds)

# Simple physics
MASS = 3600               # kg
THRUST = 215000           # Newton
G = 9.81                  # gravity

HOVER_THROTTLE = (MASS * G) / THRUST

# Control gain (how aggressively we adjust throttle)
Kp = 0.5


# =========================================================
# --- PHYSICS MODEL
# =========================================================

def update_velocity(throttle, velocity):
    """
    Calculates new velocity based on thrust and gravity.

    throttle: 0.0 → 1.0
    velocity: current vertical velocity
    """
    force = throttle * THRUST
    weight = MASS * G

    acceleration = (force - weight) / MASS

    return velocity + acceleration * DT


def update_altitude(altitude, velocity):
    """
    Updates altitude using current velocity.
    """
    return altitude + velocity * DT


# =========================================================
# --- CONTROL SYSTEM (v1: simple proportional control)
# =========================================================
def compute_throttle(error):
    """
    Improved control:
    - Base hover throttle (physics)
    - Plus proportional correction
    """
    throttle = hover + (Kp * error) - (Kd * velocity)


    # Clamp to valid engine range
    return max(0.0, min(1.0, throttle))

# =========================================================
# --- SIMULATION RUN
# =========================================================

def run_hover_test(max_time=10.0):
    """
    Runs a single hover simulation.

    Returns logged data for analysis.
    """

    time = 0.0
    altitude = 0.0
    velocity = 0.0
    throttle = 0.0

    # Logging arrays
    log_time = []
    log_altitude = []
    log_velocity = []
    log_throttle = []
    log_error = []

    # Stability tracking
    time_in_margin = 0.0

    while time < max_time:

        # --- 1. Measure system state ---
        error = TARGET_ALTITUDE - altitude

        # --- 2. Compute control ---
        throttle = compute_throttle(error)

        # --- 3. Update physics ---
        velocity = update_velocity(throttle, velocity)
        altitude = update_altitude(altitude, velocity)

        # --- 4. Check if within hover zone ---
        if abs(error) <= MARGIN:
            time_in_margin += DT
        else:
            time_in_margin = 0.0

        # --- 5. Log data ---
        log_time.append(time)
        log_altitude.append(altitude)
        log_velocity.append(velocity)
        log_throttle.append(throttle)
        log_error.append(error)

        # --- 6. Advance time ---
        time += DT

    return {
        "time": log_time,
        "altitude": log_altitude,
        "velocity": log_velocity,
        "throttle": log_throttle,
        "error": log_error,
        "stable_time": time_in_margin
    }


# =========================================================
# --- ANALYSIS
# =========================================================

def analyze(result):
    """
    Prints summary of hover performance.
    """

    final_altitude = result["altitude"][-1]
    stable_time = result["stable_time"]

    print("\n--- Hover Test Results ---")
    print("Final Altitude:", round(final_altitude, 2))
    print("Time in Stable Zone:", round(stable_time, 2), "sec")

    if stable_time > 1.0:
        print("✅ Hover achieved")
    else:
        print("⚠️ Hover not stable")


# =========================================================
# --- EXECUTION
# =========================================================

if __name__ == "__main__":
    result = run_hover_test()
    analyze(result)
