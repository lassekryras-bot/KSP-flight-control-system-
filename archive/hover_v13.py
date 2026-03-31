import math

# =========================================================
# --- CONSTANTS
# =========================================================

DT = 0.02
G = 9.81

# PD control
Kp = 0.4
Kd = 0.3

# Targets
TAKEOFF_TARGET = 100
CRUISE_TARGET = 300

# =========================================================
# --- PARTS
# =========================================================

PARTS = {

    "Mk1 Command Pod": {
        "type": "pod",
        "mass": 840,
    },

    "RT-5 Flea": {
        "type": "booster",
        "thrust": 163000,
        "fuel": 140.0,
        "burn_rate": 15.8,
        "dry_mass": 450,
        "fuel_mass": 1050,
    },

    "LV-T45 Swivel": {
        "type": "liquid_engine",
        "thrust": 168000,
        "fuel_rate": 13.7,
        "mass": 1500,
    },

    "FL-T100": {
        "type": "fuel_tank",
        "fuel": 100.0,
        "fuel_mass": 500,
        "dry_mass": 62.5,
    },

    "Mk16": {
        "type": "parachute",
        "semi_drag": 5,
        "full_drag": 500,
        "deploy_altitude": 1000,
    },
}

# =========================================================
# --- BUILD
# =========================================================

def build_vehicle(pod, engine, chute, tank=None):
    return {
        "pod": PARTS[pod],
        "engine": PARTS[engine],
        "tank": PARTS[tank] if tank else None,
        "chute": PARTS[chute],
    }

# =========================================================
# --- PHYSICS
# =========================================================

def update_velocity(thrust, velocity, mass, drag):
    acc = (thrust - mass * G - drag) / mass
    return velocity + acc * DT

def update_altitude(altitude, velocity):
    return altitude + velocity * DT

# =========================================================
# --- CONTROL (PD)
# =========================================================

def compute_throttle(target_alt, altitude, velocity, mass, thrust):

    error = target_alt - altitude
    hover = (mass * G) / thrust

    throttle = hover + (Kp * error) - (Kd * velocity)

    return max(0.0, min(1.0, throttle))

# =========================================================
# --- MODE SYSTEM
# =========================================================

def determine_mode(time, altitude, velocity, fuel_ratio):

    if altitude <= 0 and velocity <= 0:
        return "ground"

    if fuel_ratio < 0.25:
        return "returning"

    if time < 5:
        return "takeoff"

    if velocity > 0:
        return "flying"

    return "descent"

# =========================================================
# --- SIMULATION
# =========================================================

def run_sim(vehicle, label):

    time = 0.0
    altitude = 0.0
    velocity = 0.0

    pod = vehicle["pod"]
    engine = vehicle["engine"]
    tank = vehicle["tank"]
    chute = vehicle["chute"]

    # --- INIT ---
    pod_mass = pod["mass"]
    chute_mass = 100

    if engine["type"] == "booster":
        fuel = engine["fuel"]
        fuel_mass = engine["fuel_mass"]
        engine_dry = engine["dry_mass"]

    else:
        fuel = tank["fuel"]
        fuel_mass = tank["fuel_mass"]
        engine_dry = engine["mass"]

    tank_dry = tank["dry_mass"] if tank else 0

    parachute = "inactive"
    transitions = []
    last_mode = None

    while True:

        # --- MASS ---
        mass = pod_mass + engine_dry + tank_dry + fuel_mass + chute_mass

        # --- FUEL RATIO ---
        max_fuel = engine["fuel"] if engine["type"] == "booster" else tank["fuel"]
        fuel_ratio = fuel / max_fuel if max_fuel > 0 else 0

        # --- MODE ---
        mode = determine_mode(time, altitude, velocity, fuel_ratio)

        if mode != last_mode:
            transitions.append((round(time,2), last_mode, mode))
            last_mode = mode

        # --- CONTROL ---
        if engine["type"] == "liquid_engine":

            if mode == "takeoff":
                target = TAKEOFF_TARGET

            elif mode == "flying":
                target = CRUISE_TARGET

            elif mode == "returning":
                target = 0

            else:
                target = 0

            throttle = compute_throttle(target, altitude, velocity, mass, engine["thrust"])
            thrust = engine["thrust"] * throttle

            burn = engine["fuel_rate"] * throttle * DT
            fuel = max(0.0, fuel - burn)

            fuel_ratio_now = fuel / tank["fuel"]
            fuel_mass = tank["fuel_mass"] * fuel_ratio_now

            if fuel <= 0:
                thrust = 0

        else:
            # booster
            thrust = engine["thrust"]

            burn = engine["burn_rate"] * DT
            fuel = max(0.0, fuel - burn)

            ratio = fuel / engine["fuel"]
            fuel_mass = engine["fuel_mass"] * ratio

            if fuel <= 0:
                thrust = 0

        # --- PARACHUTE ---
        if parachute == "inactive" and velocity < -5 and altitude < 2000:
            parachute = "semi"

        if parachute == "semi" and altitude < chute["deploy_altitude"]:
            parachute = "full"

        drag = 0.0
        if parachute == "semi":
            drag = chute["semi_drag"] * velocity * abs(velocity)
        elif parachute == "full":
            drag = chute["full_drag"] * velocity * abs(velocity)

        # --- PHYSICS ---
        velocity = update_velocity(thrust, velocity, mass, drag)
        altitude = update_altitude(altitude, velocity)

        # --- GROUND ---
        if altitude <= 0 and velocity <= 0:
            altitude = 0

            result = "safe" if velocity > -6 else "crash"

            return {
                "label": label,
                "velocity": velocity,
                "result": result,
                "transitions": transitions
            }

        time += DT

# =========================================================
# --- RUN
# =========================================================

def print_result(r):

    print(f"\n--- {r['label']} ---")
    print("Touchdown Velocity:", round(r["velocity"], 2))
    print("Result:", r["result"])
    print("Transitions:")
    for t in r["transitions"]:
        print(" ", t)


if __name__ == "__main__":

    print("\n=== v13 Unified Flight System ===")

    v1 = build_vehicle("Mk1 Command Pod", "RT-5 Flea", "Mk16")
    v2 = build_vehicle("Mk1 Command Pod", "LV-T45 Swivel", "Mk16", "FL-T100")

    print_result(run_sim(v1, "Flea Rocket"))
    print_result(run_sim(v2, "Swivel Rocket"))
