import math

# =========================================================
# --- CONFIGURATION
# =========================================================

DT = 0.02

# Physics
DRY_MASS = 2000
BOOSTER_FUEL = 500
BOOSTER_THRUST = 250000
G = 9.81

# Booster
BURN_RATE = 20.0  # fuel per second

# Parachute
DEPLOY_ALTITUDE = 1800
DRAG_COEFF = 0.8

# Landing safety
SAFE_LANDING_VELOCITY = -6.0


# =========================================================
# --- PHYSICS
# =========================================================

def update_velocity(thrust, velocity, mass, parachute_deployed):
    weight = mass * G

    drag = 0.0
    if parachute_deployed:
        drag = DRAG_COEFF * velocity * abs(velocity)

    acceleration = (thrust - weight - drag) / mass
    return velocity + acceleration * DT


def update_altitude(altitude, velocity):
    return altitude + velocity * DT


# =========================================================
# --- SIMULATION
# =========================================================

def run_sim(label, deploy_altitude):

    time = 0.0
    altitude = 0.0
    velocity = 0.0

    fuel = BOOSTER_FUEL
    mass = DRY_MASS + fuel

    booster_active = True
    parachute_deployed = False

    deploy_time = None
    burnout_time = None

    while True:

        # --- Booster ---
        if booster_active:
            thrust = BOOSTER_THRUST
            burn = BURN_RATE * DT
            fuel = max(0.0, fuel - burn)

            if fuel <= 0:
                booster_active = False
                thrust = 0.0
                burnout_time = time
        else:
            thrust = 0.0

        # --- Parachute deployment ---
        if (not parachute_deployed and
            not booster_active and
            velocity < 0 and
            altitude < deploy_altitude):

            parachute_deployed = True
            deploy_time = time

        # --- Update mass ---
        mass = DRY_MASS + fuel

        # --- Physics ---
        velocity = update_velocity(thrust, velocity, mass, parachute_deployed)
        altitude = update_altitude(altitude, velocity)

        # --- Ground ---
        if altitude <= 0 and velocity <= 0:
            altitude = 0

            if velocity > SAFE_LANDING_VELOCITY:
                result = "safe"
            else:
                result = "crash"

            return {
                "label": label,
                "burnout_time": burnout_time,
                "deploy_time": deploy_time,
                "touchdown_velocity": velocity,
                "result": result
            }

        time += DT


# =========================================================
# --- OUTPUT
# =========================================================

def print_result(r):
    print(f"\n--- {r['label']} ---")
    print("Burnout Time:", round(r["burnout_time"], 2) if r["burnout_time"] else None)
    print("Parachute Deploy Time:", round(r["deploy_time"], 2) if r["deploy_time"] else None)
    print("Touchdown Velocity:", round(r["touchdown_velocity"], 2))
    print("Result:", r["result"])


# =========================================================
# --- RUN TESTS
# =========================================================

if __name__ == "__main__":

    print("\n=== Booster + Parachute Simulation (v12.0) ===")

    test1 = run_sim("Safe Deploy (1800m)", 1800)
    test2 = run_sim("Late Deploy (1200m)", 1200)
    test3 = run_sim("Too Late (600m)", 600)

    print_result(test1)
    print_result(test2)
    print_result(test3)
