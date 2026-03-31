import math

# =========================================================
# --- CONFIGURATION
# =========================================================

TARGET_ALTITUDE = 100.0
DT = 0.02

# Physics
DRY_MASS = 4000
THRUST = 215000
G = 9.81

# Fuel
MAX_BURN_RATE = 50.0
FULL_FUEL = 2000.0
RETURN_FUEL_THRESHOLD = 0.25

# Control
Kp = 0.5
Kd = 0.3
K_LANDING = 0.4

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
    hover = (mass * G) / THRUST
    throttle = hover + (Kp * error) - (Kd * velocity)
    return max(0.0, min(1.0, throttle))


def landing_control(altitude, velocity, mass, fuel_mass):
    hover = (mass * G) / THRUST

    # =========================
    # --- EMERGENCY MODE (NEW)
    # =========================
    if fuel_mass < 100:
        target_velocity = -1.0  # faster descent to avoid running out

    # =========================
    # --- FLARE PHASE
    # =========================
    elif altitude < 2.0:
        target_velocity = -0.3

    else:
        target_velocity = -0.2 * altitude
        target_velocity = max(-MAX_DESCENT, min(-MIN_DESCENT, target_velocity))

    error = target_velocity - velocity
    throttle = hover + (K_LANDING * error)

    return max(0.0, min(1.0, throttle))


# =========================================================
# --- STATE MACHINE
# =========================================================

def update_mode(mode, altitude, velocity, fuel_mass, time):

    fuel_ratio = fuel_mass / FULL_FUEL

    if fuel_mass <= 0 and altitude > 0:
        return "free_fall"

    if mode == "returning" and altitude < LANDING_ALTITUDE and velocity < 0:
        return "landing"

    if mode == "takeoff":
        if altitude >= TARGET_ALTITUDE - 1:
            return "flying"

    elif mode == "flying":
        if fuel_ratio <= RETURN_FUEL_THRESHOLD:
            return "returning"
        if time >= 60:
            return "returning"

    elif mode == "returning":
        return "returning"

    return mode


def control_system(mode, error, velocity, mass, altitude, fuel_mass):

    if mode == "free_fall":
        return 0.0

    elif mode == "landing":
        return landing_control(altitude, velocity, mass, fuel_mass)

    elif mode == "returning":
        return landing_control(altitude, velocity, mass, fuel_mass)

    else:
        return compute_throttle(error, velocity, mass)


# =========================================================
# --- LANDING QUALITY
# =========================================================

def evaluate_landing(velocity):
    v = abs(velocity)

    if v < 1.0:
        return "soft_landing"
    elif v < 3.0:
        return "hard_landing"
    else:
        return "crash"


# =========================================================
# --- SIMULATION
# =========================================================

def run_hover_test(initial_fuel, label, max_time=120.0, start_altitude=0.0):

    time = 0.0
    altitude = start_altitude
    velocity = 0.0

    fuel_mass = initial_fuel
    current_mass = DRY_MASS + fuel_mass

    mode = "takeoff" if start_altitude < TARGET_ALTITUDE else "flying"

    transitions = []
    last_mode = None

    touchdown_velocity = None
    landing_result = None

    while time < max_time:

        mode = update_mode(mode, altitude, velocity, fuel_mass, time)

        if mode in ["returning", "landing"]:
            target = 0.0
        else:
            target = TARGET_ALTITUDE

        error = target - altitude

        if mode != last_mode:
            transitions.append((round(time, 2), last_mode, mode))
            last_mode = mode

        throttle = control_system(mode, error, velocity, current_mass, altitude, fuel_mass)

        # Fuel
        burn = MAX_BURN_RATE * throttle * DT
        fuel_mass = max(0.0, fuel_mass - burn)
        current_mass = DRY_MASS + fuel_mass

        # Physics
        velocity = update_velocity(throttle, velocity, current_mass)
        altitude = update_altitude(altitude, velocity)

        # Ground
        if altitude <= 0.0 and velocity <= 0.0:
            touchdown_velocity = velocity
            landing_result = evaluate_landing(velocity)

            altitude = 0.0
            velocity = 0.0
            mode = "ground_hit"

            transitions.append((round(time, 2), last_mode, mode))
            break

        time += DT

    return {
        "label": label,
        "final_altitude": altitude,
        "final_mode": mode,
        "transitions": transitions,
        "touchdown_velocity": touchdown_velocity,
        "landing_result": landing_result
    }


# =========================================================
# --- OUTPUT
# =========================================================

def print_result(result):
    print(f"\n--- {result['label']} ---")
    print("Final Altitude:", round(result["final_altitude"], 2))
    print("Final Mode:", result["final_mode"])

    if result["touchdown_velocity"] is not None:
        print("Touchdown Velocity:", round(result["touchdown_velocity"], 2))
        print("Landing Result:", result["landing_result"])

    print("Transitions:")
    for t in result["transitions"]:
        print(" ", t)


# =========================================================
# --- RUN
# =========================================================

if __name__ == "__main__":

    print("\n=== Hover Test Results (v11.2: Fuel-Aware Landing) ===")

    test1 = run_hover_test(2000, "Nominal Mission", start_altitude=0.0)
    test2 = run_hover_test(2000, "Start High", start_altitude=150.0)
    test3 = run_hover_test(200, "Low Fuel Return", start_altitude=100.0)

    print_result(test1)
    print_result(test2)
    print_result(test3)

