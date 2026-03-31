import time, random
from ramp import ThrottleRamp
from detection import DetectionSystem


def get_velocity(throttle):
    # Deterministic + small noise for reliable detection
    return throttle * 5 + random.uniform(-0.2, 0.2)


def run_test(run_id):
    ramp = ThrottleRamp(0.25)
    # Easier detection for simulation
    detect = DetectionSystem(1.5, 0.2)

    ramp.start()
    start = time.time()

    while True:
        throttle = ramp.get_throttle()
        velocity = get_velocity(throttle)

        # Debug output so user can see activity
        print(f"[SIM] Throttle: {throttle:.2f}, Velocity: {velocity:.2f}")

        if detect.update(velocity):
            t = time.time() - start
            ramp.stop()

            # Ensure data folder exists path-wise
            try:
                with open("../data/runs.csv", "a") as f:
                    f.write(f"{run_id},0.25,{t},{throttle},{velocity}\n")
            except FileNotFoundError:
                import os
                os.makedirs("../data", exist_ok=True)
                with open("../data/runs.csv", "a") as f:
                    f.write("run_id,ramp_rate,time,throttle,velocity\n")
                    f.write(f"{run_id},0.25,{t},{throttle},{velocity}\n")

            print(f"[SIM] Detection at throttle: {throttle:.2f}")
            break

        time.sleep(0.01)


if __name__ == "__main__":
    for i in range(1, 6):
        run_test(i)
