import time, random
from ramp import ThrottleRamp
from detection import DetectionSystem


def get_velocity():
    return random.uniform(0, 5)


def run_test(run_id):
    ramp = ThrottleRamp(0.25)
    detect = DetectionSystem(2.0, 0.5)

    ramp.start()
    start = time.time()

    while True:
        throttle = ramp.get_throttle()
        velocity = get_velocity()

        if detect.update(velocity):
            t = time.time() - start
            ramp.stop()

            with open("../data/runs.csv", "a") as f:
                f.write(f"{run_id},0.25,{t},{throttle},{velocity}\n")

            print(f"[SIM] Detection at {throttle:.2f}")
            break

        time.sleep(0.01)


if __name__ == "__main__":
    for i in range(1, 6):
        run_test(i)
