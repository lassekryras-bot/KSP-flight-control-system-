import math

DT = 0.02
G = 9.81

# =========================================================
# --- PART DATABASE
# =========================================================

PARTS = {

    # --- POD ---
    "Mk1 Command Pod": {
        "type": "pod",
        "mass": 840,
    },

    # --- BOOSTER (engine + fuel) ---
    "RT-5 Flea": {
        "type": "booster",
        "thrust": 163000,
        "fuel": 140.0,
        "burn_rate": 15.8,
        "dry_mass": 450,
        "fuel_mass": 1050,
    },

    # --- LIQUID ENGINE ---
    "LV-T45 Swivel": {
        "type": "liquid_engine",
        "thrust": 168000,
        "fuel_rate": 13.7,
        "mass": 1500,
    },

    # --- FUEL TANK ---
    "FL-T100": {
        "type": "fuel_tank",
        "fuel": 100.0,
        "fuel_mass": 500,
        "dry_mass": 62.5,
    },

    # --- PARACHUTE ---
    "Mk16": {
        "type": "parachute",
        "semi_drag": 5,
        "full_drag": 500,
        "deploy_altitude": 1000,
    },
}

# =========================================================
# --- VEHICLE BUILDER
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
    weight = mass * G
    acc = (thrust - weight - drag) / mass
    return velocity + acc * DT

def update_altitude(altitude, velocity):
    return altitude + velocity * DT

# =========================================================
# --- SIMULATION
# =========================================================

def run_sim(vehicle, label):

    time = 0.0
    altitude = 0.0
    velocity = 0.0

    pod_mass = vehicle["pod"]["mass"]
    engine = vehicle["engine"]
    chute = vehicle["chute"]
    tank = vehicle["tank"]

    # --- INIT ENGINE/FUEL ---
    if engine["type"] == "booster":
        fuel = engine["fuel"]
        fuel_mass = engine["fuel_mass"]
        engine_dry = engine["dry_mass"]

    else:
        fuel = tank["fuel"]
        fuel_mass = tank["fuel_mass"]
        engine_dry = engine["mass"]

    tank_dry = tank["dry_mass"] if tank else 0
    chute_mass = 100

    parachute_state = "inactive"
    deploy_time = None
    burnout_time = None

    while True:

        # --- ENGINE LOGIC ---
        if engine["type"] == "booster":

            thrust = engine["thrust"]

            burn = engine["burn_rate"] * DT
            fuel = max(0.0, fuel - burn)

            ratio = fuel / engine["fuel"]
            fuel_mass = engine["fuel_mass"] * ratio

            if fuel <= 0:
                thrust = 0
                if burnout_time is None:
                    burnout_time = time

        else:
            throttle = 1.0

            thrust = engine["thrust"] * throttle

            burn = engine["fuel_rate"] * throttle * DT
            fuel = max(0.0, fuel - burn)

            ratio = fuel / tank["fuel"]
            fuel_mass = tank["fuel_mass"] * ratio

            if fuel <= 0:
                thrust = 0
                if burnout_time is None:
                    burnout_time = time

        # --- MASS ---
        mass = pod_mass + engine_dry + tank_dry + fuel_mass + chute_mass

        # --- PARACHUTE LOGIC ---
        if (parachute_state == "inactive" and
            velocity < 0 and altitude < 1800):

            parachute_state = "semi"
            deploy_time = time

        if parachute_state == "semi" and altitude < chute["deploy_altitude"]:
            parachute_state = "full"

        # --- DRAG ---
        drag = 0.0

        if parachute_state == "semi" and velocity < 0:
            drag = chute["semi_drag"] * velocity * abs(velocity)

        elif parachute_state == "full" and velocity < 0:
            drag = chute["full_drag"] * velocity * abs(velocity)

        # --- PHYSICS ---
        velocity = update_velocity(thrust, velocity, mass, drag)
        altitude = update_altitude(altitude, velocity)

        # --- GROUND ---
        if altitude <= 0 and velocity <= 0:
            altitude = 0

            if velocity > -6:
                result = "safe"
            else:
                result = "crash"

            return {
                "label": label,
                "burnout": burnout_time,
                "deploy": deploy_time,
                "velocity": velocity,
                "result": result
            }

        time += DT

# =========================================================
# --- OUTPUT
# =========================================================

def print_result(r):
    print(f"\n--- {r['label']} ---")
    print("Burnout:", round(r["burnout"], 2) if r["burnout"] else None)
    print("Deploy:", round(r["deploy"], 2) if r["deploy"] else None)
    print("Touchdown Velocity:", round(r["velocity"], 2))
    print("Result:", r["result"])

# =========================================================
# --- RUN TESTS
# =========================================================

if __name__ == "__main__":

    print("\n=== v12.3 Full Vehicle Simulation ===")

    # --- Flea rocket ---
    v1 = build_vehicle("Mk1 Command Pod", "RT-5 Flea", "Mk16")

    # --- Liquid rocket ---
    v2 = build_vehicle("Mk1 Command Pod", "LV-T45 Swivel", "Mk16", "FL-T100")

    print_result(run_sim(v1, "Flea + Mk16"))
    print_result(run_sim(v2, "Swivel + Tank + Mk16"))
