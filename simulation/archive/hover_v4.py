import math

# =========================================================
# --- CONFIGURATION
# =========================================================

TARGET_ALTITUDE = 2.0
MARGIN = 0.2
DT = 0.02

# Physics
DRY_MASS = 8000
FUEL_MASS = 1600
THRUST = 215000
G = 9.81

# Fuel
MAX_BURN_RATE = 50.0

# Control
Kp = 0.5
Kd = 0.3

# Mode thresholds (NEW)
ALT_THRESHOLD = 0.2
VEL_THRESHOLD = 0.1


# =========================================================
# --- PHYSICS MODEL
# =========================================================

def update_velocity(throttle, velocity, mass):
    force = throttle * THRUST
    weight = mass * G
    acceleration = (force - weight) / mass
    return velocity + acceleration * DT


def update_altitude(altitude, velocity):
    return altitude + velocity * DT


# =========================================================
# --- CONTROL (UNCHANGED)
# =========================================================

def compute_throttle(error, velocity, mass):
    hover_throttle = (mass * G) / THRUST
    throttle = hover_throttle + (Kp * error) - (Kd * velocity)
    return max(0.0, min(1.0, throttle))


# =========================================================
# --- SIMULATION
# =========================================================

def run_hover_test(max_time=100.0):

    time = 0.0
    altitude = 0.0
    velocity = 0.0

    fuel_mass = FUEL_MASS
    current_mass = DRY_MASS + fuel_mass

    mode = "approach"   # NEW

    # Logging
    log_time = []
    log_altitude = []
    log_velocity = []
    log_throttle = []
    log_error = []
    log_mass = []
    log_fuel = []
    log_mode = []       # NEW

    time_in_margin = 0.0

    while time < max_time:

        # --- Measure ---
        error = TARGET_ALTITUDE - altitude

        # --- Mode detection (NEW) ---
        if abs(error) <= ALT_THRESHOLD and abs(velocity) <= VEL_THRESHOLD:
            mode = "hover"
        else:
            mode = "approach"

        # --- Control ---
        throttle = compute_throttle(error, velocity, current_mass)

        # --- Fuel burn ---
        burn = MAX_BURN_RATE * throttle * DT
        fuel_mass = max(0.0, fuel_mass - burn)

        # --- Update mass ---
        current_mass = DRY_MASS + fuel_mass

        # --- Physics ---
        velocity = update_velocity(throttle, velocity, current_mass)
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
        log_mass.append(current_mass)
        log_fuel.append(fuel_mass)
        log_mode.append(mode)

        # --- Time ---
        time += DT

    return {
        "time": log_time,
        "altitude": log_altitude,
        "velocity": log_velocity,
        "throttle": log_throttle,
        "error": log_error,
        "mass": log_mass,
        "fuel": log_fuel,
        "mode": log_mode,
        "stable_time": time_in_margin
    }


# =========================================================
# --- ANALYSIS
# =========================================================

def analyze(result):
    final_altitude = result["altitude"][-1]
    stable_time = result["stable_time"]
    final_mode = result["mode"][-1]

    print("\n--- Hover Test Results (v4: Mode Awareness) ---")
    print("Final Altitude:", round(final_altitude, 2))
    print("Time in Stable Zone:", round(stable_time, 2), "sec")

    print("Final Mass:", round(result["mass"][-1], 1))
    print("Remaining Fuel:", round(result["fuel"][-1], 1))
    print("Final Mode:", final_mode)

    if stable_time > 5.0:
        print("✅ Stable hover with mode tracking")
    else:
        print("⚠️ Stability issue detected")


# =========================================================
# --- EXECUTE
# =========================================================

if __name__ == "__main__":
    result = run_hover_test()
    analyze(result)
