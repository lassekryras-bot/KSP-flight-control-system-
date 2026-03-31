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

    log_mode = []

    while time < max_time:

        error = TARGET_ALTITUDE - altitude

        # --- Mode detection ---
        if altitude <= 0.0 and velocity <= 0.0:
            mode = "ground_hit"

        elif fuel_mass <= 0 and altitude > 0:
            mode = "free_fall"

        elif altitude > TARGET_ALTITUDE + ALT_THRESHOLD:
            mode = "controlled_descent"

        elif abs(error) <= ALT_THRESHOLD and abs(velocity) <= VEL_THRESHOLD:
            mode = "hover"

        else:
            mode = "approach"

        # --- Control ---
        if mode == "free_fall":
            throttle = 0.0

        elif mode == "controlled_descent":
            throttle = DESCENT_THROTTLE

        else:
            throttle = compute_throttle(error, velocity, current_mass)

        # --- Fuel burn ---
        burn = MAX_BURN_RATE * throttle * DT
        fuel_mass = max(0.0, fuel_mass - burn)

        current_mass = DRY_MASS + fuel_mass

        # --- Physics ---
        velocity = update_velocity(throttle, velocity, current_mass)
        altitude = update_altitude(altitude, velocity)

        # --- Ground clamp ---
        if altitude <= 0.0 and velocity <= 0.0:
            altitude = 0.0
            velocity = 0.0
            mode = "ground_hit"
            log_mode.append(mode)
            break

        # --- Stability ---
        if abs(error) <= MARGIN:
            time_in_margin += DT
        else:
            time_in_margin = 0.0

        log_mode.append(mode)

        time += DT

    return {
        "label": label,
        "final_altitude": altitude,
        "stable_time": time_in_margin,
        "final_mass": current_mass,
        "remaining_fuel": fuel_mass,
        "final_mode": mode,
        "modes_seen": set(log_mode)
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
    print("Modes Seen:", result["modes_seen"])

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

    print("\n=== Hover Test Results (v7: Full State Validation) ===")

    # Test 1: Approach
    test1 = run_hover_test(
        initial_fuel=2000,
        label="Test 1: Approach",
        max_time=2.0,
        start_altitude=0.0
    )

    # Test 2: Hover
    test2 = run_hover_test(
        initial_fuel=2000,
        label="Test 2: Hover",
        start_altitude=0.0
    )

    # Test 3: Controlled Descent
    test3 = run_hover_test(
        initial_fuel=2000,
        label="Test 3: Controlled Descent",
        start_altitude=150.0
    )

    # Test 4: Free Fall
    test4 = run_hover_test(
        initial_fuel=0,
        label="Test 4: Free Fall",
        max_time=3.0,
        start_altitude=50.0
    )

    # Test 5: Ground Hit
    test5 = run_hover_test(
        initial_fuel=0,
        label="Test 5: Ground Hit",
        max_time=20.0,
        start_altitude=50.0
    )

    print_result(test1)
    print_result(test2)
    print_result(test3)
    print_result(test4)
    print_result(test5)
