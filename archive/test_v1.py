from main_v4 import run_single_test
import math


# --- Helper: Run scenario ---
def run_scenario(name, runs=20):
    liftoff = []
    ascent = []

    for _ in range(runs):
        l, a = run_single_test()
        liftoff.append(l)
        ascent.append(a)

    return {
        "name": name,
        "liftoff": liftoff,
        "ascent": ascent
    }


# --- Analysis ---
def analyze(label, data):
    avg = sum(data) / len(data)
    var = sum((x - avg) ** 2 for x in data) / len(data)
    std = math.sqrt(var)

    return {
        "avg": avg,
        "std": std,
        "min": min(data),
        "max": max(data)
    }


# --- Scenario 1: Baseline ---
def scenario_baseline():
    result = run_scenario("baseline")

    liftoff_stats = analyze("liftoff", result["liftoff"])
    ascent_stats = analyze("ascent", result["ascent"])

    print("\n=== Scenario 1: Baseline ===")

    print("\nLiftoff:")
    print(liftoff_stats)

    print("\nAscent:")
    print(ascent_stats)

    # --- Assertions (Mission Contract) ---
    assert liftoff_stats["std"] < 0.01, "❌ Liftoff unstable"
    assert ascent_stats["std"] < 0.01, "❌ Ascent unstable"

    margin = ascent_stats["avg"] - liftoff_stats["avg"]
    assert margin > 0.05, "❌ Control margin too small"

    print("\n✅ Baseline PASSED")


# --- Execute ---
if __name__ == "__main__":
    scenario_baseline()
