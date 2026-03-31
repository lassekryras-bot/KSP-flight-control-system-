import math

# =========================================================
# --- CONFIGURATION
# =========================================================

TARGET_ALTITUDE = 2.0      # meters
MARGIN = 0.2               # acceptable hover range
DT = 0.02                  # timestep (seconds)

# Physics
MASS = 3600                # kg
THRUST = 215000            # Newton
G = 9.81                   # gravity

# Hover baseline (feedforward)
HOVER_THROTTLE = (MASS * G) / THRUST

# Control gains
Kp = 0.5
Kd = 0.3


# =========================================================
# --- PHYSICS MODEL
# =========================================================

def update_velocity(throttle, velocity):
    """
    Calculates new velocity based on thrust and gravity.
    """
    force = throttle * THRUST
    weight = MASS * G

    acceleration = (force - weight) / MASS

    return velocity + acceleration * DT


def update_altitude(altitude, velocity):
    """
    Updates altitude using velocity.
    """
    return altitude + velocity * DT


# =========================================================
# --- CONTROL SYSTEM (v1.1: PD control)
# =========================================================

def compute_throttle(error, velocity):
    """
    Control logic:
    - Hover baseline (physics)
    - Proportional correction (position)
    - Damping (velocity)
    """

    throttle = HOVER_THROTTLE + (Kp * error) - (Kd * velocity)

    # Clamp to valid engine range
    return max(0.0, min(1.0, throttle))


# =========================================================
# --- SIMULATION
# =========================================================

def run_hover_test(max_time=10.0):
    time = 0.0
    altitude = 0.0
    velocity = 0.0

    # Logging
    log_time = []
    log_altitude = []
    log_velocity = []
    log_throttle = []
    log_error = []

    time_in_margin = 0.0

    while time < max_time:

        # --- Measure ---
        error = TARGET_ALTITUDE - altitude

        # --- Control ---
        throttle = compute_throttle(error, velocity)

        # --- Physics ---
        velocity = update_velocity(throttle, velocity)
        altitude = update_altitude(altitude, velocity)

        # --- Stability check ---
        if abs(error) <= MARGIN:
            time_in_margin += DT
        else:
            time_in_margin = 0.0

        # --- Logging ---
        log_time.append(time)
        log_altitude.append(altitude)
        log_velocity.append(velocity)
        log_throttle.append(throttle)
        log_error.append(error)

        # --- Time step ---
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
    final_altitude = result["altitude"][-1]
    stable_time = result["stable_time"]

    print("\n--- Hover Test Results (v1.1) ---")
    print("Final Altitude:", round(final_altitude, 2))
    print("Time in Stable Zone:", round(stable_time, 2), "sec")

    if stable_time > 1.0:
        print("✅ Hover achieved")
    else:
        print("⚠️ Hover not stable")


# =========================================================
# --- EXECUTE
# =========================================================

if __name__ == "__main__":
    result = run_hover_test()
    analyze(result)
