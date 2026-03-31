import math

G = 9.81
DT = 0.02
LOG_INTERVAL = 5.0


# ----------------------------
# PART SYSTEM
# ----------------------------

class Engine:
    def __init__(self, thrust, burn_time, throttleable):
        self.thrust = thrust
        self.burn_time = burn_time
        self.throttleable = throttleable


class Vehicle:
    def __init__(self, mass, fuel_mass, engine, parachute=True):
        self.mass = mass
        self.fuel_mass = fuel_mass
        self.engine = engine
        self.parachute = parachute


# ----------------------------
# CONTROLLER
# ----------------------------

class FlightController:
    def __init__(self, vehicle):

        self.v = vehicle

        self.mode = None
        self.time = 0

        self.alt = 0
        self.vel = 0

        self.fuel = 1.0
        self.throttle = 0.0
        self.prev_throttle = 0.0

        self.chute_semi = False
        self.chute_full = False

        self.transitions = []

        self.last_log_time = -LOG_INTERVAL

    # ----------------------------
    # STATE MACHINE
    # ----------------------------

    def set_mode(self, new_mode):
        if self.mode != new_mode:
            print(f"[t={self.time:5.1f}] {self.mode} → {new_mode}")
            self.transitions.append((round(self.time, 2), self.mode, new_mode))
            self.mode = new_mode

    # ----------------------------
    # LANDING FEASIBILITY
    # ----------------------------

    def can_land(self):
        """Check if powered landing is possible"""

        if not self.v.engine.throttleable or self.fuel <= 0:
            return False

        max_acc = self.v.engine.thrust / self.v.mass

        if max_acc < G * 1.2:
            return False

        # Prevent divide issues
        if max_acc <= G:
            return False

        stopping_distance = (self.vel ** 2) / (2 * (max_acc - G))

        return stopping_distance < self.alt

    # ----------------------------
    # CONTROL LOGIC
    # ----------------------------

    def update_control(self):

        # --- GROUND ---
        if self.mode == "ground":
            self.set_mode("takeoff")

        # --- TAKEOFF ---
        elif self.mode == "takeoff":
            self.throttle = 1.0

            if self.alt > 200:
                self.set_mode("flying")

        # --- FLYING ---
        elif self.mode == "flying":
            self.throttle = 0.0

            if self.vel < 0:
                self.set_mode("descent")

        # --- DESCENT ---
        elif self.mode == "descent":

            self.throttle = 0.0

            # --- PARACHUTE ---
            if self.v.parachute:

                if not self.chute_semi and self.vel < -20 and self.alt < 2000:
                    self.chute_semi = True
                    print(f"[t={self.time:5.1f}] EVENT: chute SEMI")

                if self.chute_semi and not self.chute_full and self.alt < 1000:
                    self.chute_full = True
                    print(f"[t={self.time:5.1f}] EVENT: chute FULL")

            # --- DECISION ---
            if self.alt < 100:

                if self.v.parachute and self.chute_full:
                    self.set_mode("landing")

                elif self.can_land():
                    self.set_mode("landing")

                else:
                    self.set_mode("free_fall")

        # --- LANDING ---
        elif self.mode == "landing":

            print(f"[t={self.time:5.1f}] EVENT: landing")

            if self.v.engine.throttleable and self.fuel > 0:

                target_v = -2 if self.alt > 10 else -0.5
                error = target_v - self.vel

                raw_throttle = error * 0.2

                # Authority check
                if self.v.engine.thrust < self.v.mass * G * 0.5:
                    raw_throttle = 0

                raw_throttle = max(0.0, min(1.0, raw_throttle))

                # Smooth throttle
                self.throttle = self.prev_throttle + (raw_throttle - self.prev_throttle) * 0.2

            else:
                self.throttle = 0.0

        # --- FREE FALL ---
        elif self.mode == "free_fall":
            self.throttle = 0.0

        self.prev_throttle = self.throttle

    # ----------------------------
    # PHYSICS
    # ----------------------------

    def update_physics(self):

        thrust = 0

        if self.fuel > 0:
            if self.v.engine.throttleable:
                thrust = self.v.engine.thrust * self.throttle
                self.fuel -= DT / self.v.engine.burn_time
            else:
                thrust = self.v.engine.thrust
                self.fuel -= DT / self.v.engine.burn_time

        self.fuel = max(0, self.fuel)

        acc = (thrust / self.v.mass) - G

        # Parachute drag
        if self.chute_semi:
            acc += 15

        if self.chute_full:
            acc += 50

        self.vel += acc * DT
        self.alt += self.vel * DT

        if self.alt <= 0:
            self.alt = 0

    # ----------------------------
    # LOGGING (every 5 sec)
    # ----------------------------

    def log(self):
        if self.time - self.last_log_time >= LOG_INTERVAL:
            self.last_log_time = self.time
            print(
                f"[t={self.time:5.1f}] {self.mode:9} | alt={self.alt:6.0f}m | vel={self.vel:7.1f} | thr={self.throttle:.2f} | fuel={self.fuel:.2f}"
            )

    # ----------------------------
    # RUN
    # ----------------------------

    def run(self, max_time=300):

        self.set_mode("ground")

        while self.time < max_time:

            self.update_control()
            self.update_physics()
            self.log()

            self.time += DT

            if self.alt <= 0 and self.time > 1:
                break

        print("\nTouchdown Velocity:", round(self.vel, 2))

        if abs(self.vel) < 6:
            print("Result: safe")
        else:
            print("Result: crash")

        print("Transitions:")
        for t in self.transitions:
            print(" ", t)


# ----------------------------
# TESTS
# ----------------------------

def run_tests():

    print("\n=== v13.6 Unified Flight System ===\n")

    # --- Test 1: Flea (SRB + chute) ---
    flea_engine = Engine(160000, 8.5, False)
    flea = Vehicle(2.5, 1.0, flea_engine, parachute=True)

    print("--- Flea Rocket (SRB + chute) ---")
    FlightController(flea).run()

    # --- Test 2: Swivel (liquid + chute) ---
    swivel_engine = Engine(167000, 40, True)
    swivel = Vehicle(3.5, 1.0, swivel_engine, parachute=True)

    print("\n--- Swivel Rocket (Liquid + chute) ---")
    FlightController(swivel).run()

    # --- Test 3: Swivel (NO chute) ---
    swivel_no_chute = Vehicle(3.5, 1.0, swivel_engine, parachute=False)

    print("\n--- Swivel Rocket (NO parachute) ---")
    FlightController(swivel_no_chute).run()


if __name__ == "__main__":
    run_tests()
