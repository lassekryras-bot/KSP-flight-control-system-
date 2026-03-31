import math

# =========================================================
# --- CONFIGURATION
# =========================================================

TARGET_ALTITUDE = 100.0
MARGIN = 0.5
DT = 0.02

# Physics
DRY_MASS = 4000
THRUST = 215000
G = 9.81

# Fuel
MAX_BURN_RATE = 50.0

# Control
Kp = 0.5
Kd = 0.3

# Mode thresholds
ALT_THRESHOLD = 0.5
VEL_THRESHOLD = 0.2

# Descent
DESCENT_THROTTLE = 0.1


# =========================================================
# --- PHYSICS
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
# --- SIMULATION
# =========================================================

def run_hover_test(initial_fuel, label, max_time=100.0, start_altitude=0.0):

    time = 0.0
    altitude = start_altitude
    velocity = 0.0

    fuel_mass = initial_fuel
    current_mass = DRY_MASS + fuel_mass

    mode = "approach"
    time_in_margin = 0.0

    while time < max_time:

        # --- Measure ---
        error = TARGET_ALTITUDE - altitude

        # --- Mode detection ---
        if fuel_mass <= 0 and altitude > 0:
            mode = "descent"
        elif abs(error) <= ALT_THRESHOLD and abs(velocity) <= VEL_THRESHOLD:
            mode = "hover"
        else:
            mode = "approach"

        # --- Control ---
        if mode == "descent":
            throttle = DESCENT_THROTTLE
        else:
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

        # --- Ground hit ---
        if altitude <= 0.0 and velocity <= 0.0:
            altitude = 0.0
            velocity = 0.0
            mode = "ground_hit"
            break

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

    if result["final_mode"] == "ground_hit":
        print("🟥 Ground hit detected")

    if result["stable_time"] > 5.0:
        print("✅ Stable period achieved")
    else:
        print("⚠️ Stability limited")


# =========================================================
# --- EXECUTE TEST SUITE
# =========================================================

if __name__ == "__main__":

    print("\n=== Hover Test Results (v6: State Validation @100m) ===")

    # Test 1: Approach only
    test1 = run_hover_test(
        initial_fuel=2000,
        label="Test 1: Approach Only",
        max_time=2.0,
        start_altitude=0.0
    )

    # Test 2: Hover
    test2 = run_hover_test(
        initial_fuel=2000,
        label="Test 2: Hover",
        start_altitude=0.0
    )

    # Test 3: Descent (start above target)
    test3 = run_hover_test(
        initial_fuel=2000,
        label="Test 3: Descent",
        start_altitude=150.0
    )

    # Test 4: Ground Hit (low fuel)
    test4 = run_hover_test(
        initial_fuel=50,
        label="Test 4: Ground Hit",
        start_altitude=0.0
    )

    print_result(test1)
    print_result(test2)
    print_result(test3)
    print_result(test4)
