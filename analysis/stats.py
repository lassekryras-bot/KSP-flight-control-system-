import math


def analyze(file="../data/runs.csv"):
    throttles = []

    try:
        with open(file, "r", encoding="utf-8") as f:
            lines = f.readlines()

        for i, line in enumerate(lines):
            if i == 0:
                continue  # skip header

            parts = line.strip().split(",")
            if len(parts) < 5:
                continue

            try:
                throttle = float(parts[3])
            except ValueError:
                continue
            throttles.append(throttle)

    except FileNotFoundError:
        print("No data file found.")
        return

    if not throttles:
        print("No data available.")
        return

    count = len(throttles)
    avg = sum(throttles) / count
    min_v = min(throttles)
    max_v = max(throttles)

    variance = sum((t - avg) ** 2 for t in throttles) / count
    std_dev = math.sqrt(variance)

    print(f"Runs: {count}")
    print(f"Average throttle: {avg:.3f}")
    print(f"Std Dev: {std_dev:.3f}")
    print(f"Min: {min_v:.3f}")
    print(f"Max: {max_v:.3f}")

    if std_dev < 0.02:
        print("✅ Stable system")
    else:
        print("⚠️ Unstable system")


if __name__ == "__main__":
    analyze()
