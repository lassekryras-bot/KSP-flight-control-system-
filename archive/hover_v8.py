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

# Landing control
K_LANDING = 0.4

# Mode thresholds
ALT_THRESHOLD = 0.5
VEL_THRESHOLD = 0.2

# Landing
LANDING_ALTITUDE = 10.0
MAX_DESCENT = 10.0
MIN_DESCENT = 1.0


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


def landing_control(altitude, velocity, mass):
    """
    Altitude-based velocity profile
    """

    hover = (mass * G) / THRUST

    # Velocity target based on altitude
    target_velocity = -0.2 * altitude

    # Clamp
    target_velocity = max(-MAX_DESCENT, min(-MIN_DESCENT, target_velocity))

    # Control error
    error = target_velocity - velocity

    # Control output
    throttle = hover + (K_LANDING * error)

    return max(0.0, min(1.0, throttle))


def determine_mode(altitude, velocity, fuel_mass, error):

    if fuel_mass <= 0 and altitude > 0:
        return "free_fall"

    elif altitude < LANDING_ALTITUDE and fuel_mass > 0:
        return "landing"

    elif altitude > TARGET_ALTITUDE + ALT_THRESHOLD:
        return "controlled_descent"

    elif abs(error) <= ALT_THRESHOLD and abs(velocity) <= VEL_THRESHOLD:
        return "hover"

    else:
        return "approach"


def control_system(mode, error, velocity, mass, altitude):

    if mode == "free_fall":
        return 0.0

    elif mode == "controlled_descent":
        return 0.1

    elif mode == "landing":
        return landing_control(altitude, velocity, mass)

    else:
        return compute_throttle(error, velocity, mass)


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

    telemetry = []
    transitions = []
    last_mode = None

    while time < max_time:

        error = TARGET_ALTITUDE - altitude

        mode = determine_mode(altitude, velocity, fuel_mass, error)

        if mode != last_mode:
            transitions.append((round(time, 2), last_mode, mode))
            last_mode = mode

        throttle = control_system(mode, error, velocity, current_mass, altitude)

        # Fuel burn
        burn = MAX_BURN_RATE * throttle * DT
        fuel_mass = max(0.0, fuel_mass - burn)
        current_mass = DRY_MASS + fuel_mass

        # Physics
        velocity = update_velocity(throttle, velocity, current_mass)
        altitude = update_altitude(altitude, velocity)

        # Ground
        if altitude <= 0.0 and velocity <= 0.0:
            altitude = 0.0
            velocity = 0.0
            mode = "ground_hit"
            transitions.append((round(time, 2), last_mode, mode))
            break

        # Stability
        if abs(error) <= MARGIN:
            time_in_margin += DT
        else:
            time_in_margin = 0.0

        telemetry.append({
            "time": time,
            "altitude": altitude,
            "velocity": velocity,
            "throttle": throttle,
            "mass": current_mass,
            "fuel": fuel_mass,
            "mode": mode
        })

        time += DT

    return {
        "label": label,
        "final_altitude": altitude,
        "final_mode": mode,
        "stable_time": time_in_margin,
        "transitions": transitions
    }


# =========================================================
# --- ANALYSIS
# =========================================================

def print_result(result):
    print(f"\n--- {result['label']} ---")
    print("Final Altitude:", round(result["final_altitude"], 2))
    print("Final Mode:", result["final_mode"])
    print("Stable Time:", round(result["stable_time"], 2))

    print("Transitions:")
    for t in result["transitions"]:
        print(" ", t)


# =========================================================
# --- EXECUTE TEST SUITE
# =========================================================

if __name__ == "__main__":

    print("\n=== Hover Test Results (v8: Controlled Landing) ===")

    test1 = run_hover_test(2000, "Hover → Landing", start_altitude=0.0)
    test2 = run_hover_test(2000, "Start High → Descend → Land", start_altitude=150.0)
    test3 = run_hover_test(50, "Low Fuel Landing Attempt", start_altitude=100.0)

    print_result(test1)
    print_result(test2)
    print_result(test3)
