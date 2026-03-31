import math

# =========================================================
# CONSTANTS
# =========================================================

G = 9.81
DT = 0.02

Kp = 0.4
Kd = 0.3

# =========================================================
# PART SYSTEM
# =========================================================

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


# =========================================================
# FLIGHT CONTROLLER
# =========================================================

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

        self.chute_state = "inactive"

        self.transitions = []

    # ----------------------------
    # STATE MACHINE
    # ----------------------------

    def set_mode(self, new_mode):
        if self.mode != new_mode:
            print(f"[t={self.time:5.1f}] {self.mode} → {new_mode}")
            self.transitions.append((round(self.time, 2), self.mode, new_mode))
            self.mode = new_mode

    # ----------------------------
    # CONTROL (PD)
    # ----------------------------

    def compute_throttle(self, target_v):

        if not self.v.engine.throttleable or self.fuel <= 0:
            return 0.0

        error = target_v - self.vel
        hover = (self.v.mass * G) / self.v.engine.thrust

        raw = hover + (Kp * error) - (Kd * self.vel)

        raw = max(0.0, min(1.0, raw))

        # smoothing
        throttle = self.prev_throttle + (raw - self.prev_throttle) * 0.2
        return throttle

    # ----------------------------
    # LANDING FEASIBILITY
    # ----------------------------

    def can_land(self):

        if not self.v.engine.throttleable or self.fuel <= 0:
            return False

        max_acc = (self.v.engine.thrust / self.v.mass) - G

        if max_acc <= 0:
            return False

        time_to_stop = abs(self.vel) / max_acc
        distance = abs(self.vel) * time_to_stop * 0.5

        return distance < self.alt

    # ----------------------------
    # CONTROL LOGIC
    # ----------------------------

    def update_control(self):

        if self.mode == "ground":
            self.set_mode("takeoff")

        elif self.mode == "takeoff":
            self.throttle = 1.0

            if self.alt > 200:
                self.set_mode("flying")

        elif self.mode == "flying":
            self.throttle = 0.0

            if self.vel < 0:
                self.set_mode("descent")

        elif self.mode == "descent":

            self.throttle = 0.0

            # --- Parachute logic ---
            if self.v.parachute:

                if self.chute_state == "inactive" and self.vel < -20 and self.alt < 2000:
                    self.chute_state = "semi"
                    print(f"[t={self.time:5.1f}] EVENT: chute SEMI")

                if self.chute_state == "semi" and self.alt < 1000:
                    self.chute_state = "full"
                    print(f"[t={self.time:5.1f}] EVENT: chute FULL")

            # --- Landing decision ---
            if self.alt < 100:

                if self.v.parachute and self.chute_state == "full":
                    self.set_mode("landing")

                elif self.can_land():
                    self.set_mode("landing")

                else:
                    self.set_mode("free_fall")

        elif self.mode == "landing":

            if self.alt > 10:
                target_v = -2
            else:
                target_v = -0.5

            self.throttle = self.compute_throttle(target_v)

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

        # --- Parachute drag ---
        drag = 0.0

        if self.chute_state == "semi":
            drag = 5 * self.vel * abs(self.vel)

        elif self.chute_state == "full":
            drag = 500 * self.vel * abs(self.vel)

        # --- Acceleration ---
        acc = (thrust - self.v.mass * G - drag) / self.v.mass

        self.vel += acc * DT
        self.alt += self.vel * DT

        if self.alt <= 0:
            self.alt = 0

    # ----------------------------
    # LOG
    # ----------------------------

    def log(self):

        print(
            f"[t={self.time:5.1f}] {self.mode:9} | "
            f"alt={self.alt:6.0f} | vel={self.vel:7.1f} | "
            f"thr={self.throttle:.2f} | fuel={self.fuel:.2f} | "
            f"chute={self.chute_state}"
        )

    # ----------------------------
    # RUN
    # ----------------------------

    def run(self, max_time=300):

        self.set_mode("ground")

        while self.time < max_time:

            self.update_control()
            self.update_physics()

            if int(self.time * 10) % 10 == 0:
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


# =========================================================
# TESTS
# =========================================================

def run_tests():

    print("\n=== v14 Unified Flight System ===\n")

    flea_engine = Engine(160000, 8.5, False)
    flea = Vehicle(2.5, 1.0, flea_engine, parachute=True)

    print("--- Flea (SRB + chute) ---")
    FlightController(flea).run()

    swivel_engine = Engine(167000, 40, True)
    swivel = Vehicle(3.5, 1.0, swivel_engine, parachute=True)

    print("\n--- Swivel (liquid + chute) ---")
    FlightController(swivel).run()

    swivel_no_chute = Vehicle(3.5, 1.0, swivel_engine, parachute=False)

    print("\n--- Swivel (NO chute) ---")
    FlightController(swivel_no_chute).run()


if __name__ == "__main__":
    run_tests()
