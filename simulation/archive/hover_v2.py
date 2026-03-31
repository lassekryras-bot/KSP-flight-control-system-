import math

# =========================================================
# --- CONFIGURATION
# =========================================================

TARGET_ALTITUDE = 2.0
MARGIN = 0.2
DT = 0.02

# Physics (based on KSP parts)
DRY_MASS = 8000           # kg (structure + engine)
FUEL_MASS = 1600          # kg (fuel tank)
THRUST = 215000           # Newton
G = 9.81

# Fuel system
MAX_BURN_RATE = 50.0       # kg/sec at full throttle

# Hover baseline (STATIC — intentional)
INITIAL_MASS = DRY_MASS + FUEL_MASS
HOVER_THROTTLE = (INITIAL_MASS * G) / THRUST

# Control
Kp = 0.5
Kd = 0.3


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

def compute_throttle(error, velocity):
    throttle = HOVER_THROTTLE + (Kp * error) - (Kd * velocity)
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

    # Logging
    log_time = []
    log_altitude = []
    log_velocity = []
    log_throttle = []
    log_error = []
    log_mass = []
    log_fuel = []

    time_in_margin = 0.0

    while time < max_time:

        # --- Measure ---
        error = TARGET_ALTITUDE - altitude

        # --- Control ---
        throttle = compute_throttle(error, velocity)

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
        "stable_time": time_in_margin
    }


# =========================================================
# --- ANALYSIS
# =========================================================

def analyze(result):
    final_altitude = result["altitude"][-1]
    stable_time = result["stable_time"]

    print("\n--- Hover Test Results (v2: Dynamic Mass) ---")
    print("Final Altitude:", round(final_altitude, 2))
    print("Time in Stable Zone:", round(stable_time, 2), "sec")

    print("Final Mass:", round(result["mass"][-1], 1))
    print("Remaining Fuel:", round(result["fuel"][-1], 1))

    if stable_time > 5.0:
        print("✅ Stable under dynamic mass")
    else:
        print("⚠️ Stability degraded")


# =========================================================
# --- EXECUTE
# =========================================================

if __name__ == "__main__":
    result = run_hover_test()
    analyze(result)
