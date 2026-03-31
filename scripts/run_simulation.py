from pathlib import Path
from pprint import pprint
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.python.simulator import FlightSimulator
from src.python.vehicle_registry import build_vehicle


if __name__ == "__main__":
    # Demonstrates part-catalog construction while using the unified simulator.
    demo_vehicle = build_vehicle("Mk1 Command Pod", "LV-T45 Swivel", "Mk16", "FL-T100")
    print("Demo vehicle parts:")
    pprint(demo_vehicle)

    sim = FlightSimulator()
    result = sim.run(max_time=90)

    print("\n=== Simulation Summary ===")
    print(f"Liftoff event: {result['events']['liftoff']}")
    print(f"Stable ascent event: {result['events']['stable_ascent']}")
    print(f"Touchdown velocity: {result['touchdown_velocity']:.2f} m/s")
    print("Transitions:")
    for transition in result["transitions"]:
        print(f"  {transition}")
