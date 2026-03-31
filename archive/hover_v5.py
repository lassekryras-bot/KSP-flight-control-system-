import math

# =========================================================
# --- CONFIGURATION
# =========================================================

TARGET_ALTITUDE = 2.0
MARGIN = 0.2
DT = 0.02

# Physics
DRY_MASS = 4000           # UPDATED
THRUST = 215000
G = 9.81

# Fuel
MAX_BURN_RATE = 50.0

# Control
Kp = 0.5
Kd = 0.3

# Mode thresholds
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
# --- CONTROL
# =========================================================

def compute_throttle(error, velocity, mass):
    hover_throttle = (mass * G) / THRUST
    throttle = hover_throttle + (Kp * error) - (Kd * velocity)
    return max(0.0, min(1.0, throttle))


# =========================================================
# --- SIMULATION CORE
# =========================================================

def run_hover_test(initial_fuel, label, max_time=100.0):

    time = 0.0
    altitude = 0.0
    velocity = 0.0

    fuel_mass = initial_fuel
    current_mass = DRY_MASS + fuel_mass

    mode = "approach"

    time_in_margin = 0.0

    while time < max_time:

        # --- Measure ---
        error = TARGET_ALTITUDE - altitude

        # --- Mode ---
        if abs(error) <= ALT_THRESHOLD and abs(velocity) <= VEL_THRESHOLD:
            mode = "hover"
        else:
            mode = "approach"

        # --- Control ---
        throttle = compute_throttle(error, velocity, current_mass)

        # --- Engine cutoff ---
        if fuel_mass <= 0.0:
            throttle = 0.0

        # --- Fuel burn ---
        burn = MAX_BURN_RATE * throttle * DT
        fuel_mass = max(0.0, fuel_mass - burn)

        # --- Mass update ---
        current_mass = DRY_MASS + fuel_mass

        # --- Physics ---
        velocity = update_velocity(throttle, velocity, current_mass)
        altitude = update_altitude(altitude, velocity)

        # --- Stability ---
        if abs(error) <= MARGIN:
            time_in_margin += DT
        else:
            time_in_margin = 0.0

        time += DT

    return {
        "label": label,
        "final_altitude": altitude,
        "stable_time": time_in_margin,
        "final_mass": current_mass,
        "remaining_fuel": fuel_mass,
        "final_mode": mode
    }


# =========================================================
# --- ANALYSIS
# =========================================================

def print_result(result):
    print(f"\n--- {result['label']} ---")
    print("Final Altitude:", round(result["final_altitude"], 2))
    print("Time in Stable Zone:", round(result["stable_time"], 2), "sec")
    print("Final Mass:", round(result["final_mass"], 1))
    print("Remaining Fuel:", round(result["remaining_fuel"], 1))
    print("Final Mode:", result["final_mode"])

    if result["remaining_fuel"] == 0:
        print("⚠️ Fuel depleted")

    if result["stable_time"] > 5.0:
        print("✅ Stable period achieved")
    else:
        print("⚠️ Stability limited")


# =========================================================
# --- EXECUTE TESTS
# =========================================================

if __name__ == "__main__":

    # Test 1: High fuel
    test1 = run_hover_test(
        initial_fuel=2000,
        label="Test 1: High Fuel"
    )

    # Test 2: Low fuel
    test2 = run_hover_test(
        initial_fuel=100,
        label="Test 2: Low Fuel"
    )

    print("\n=== Hover Test Results (v5: Fuel Scenarios) ===")
    print_result(test1)
    print_result(test2)

