import unittest

from src.python.config_loader import load_config
from src.python.simulator import FlightSimulator


class TestFlightSimulatorBDD(unittest.TestCase):
    def test_given_default_config_when_loaded_then_contains_core_sections(self):
        # Given: default repository configuration path
        # When: loading config without explicit path
        cfg = load_config()

        # Then: required top-level sections are present
        for key in ("physics", "vehicle", "control", "guidance", "state_transitions"):
            self.assertIn(key, cfg)

    def test_given_non_throttleable_vehicle_when_compute_throttle_then_returns_zero(self):
        # Given: a simulator with non-throttleable engine
        cfg = load_config()
        cfg["vehicle"]["engine"]["throttleable"] = False
        sim = FlightSimulator(config=cfg)

        # When: throttle is requested for a target velocity
        throttle = sim.compute_throttle(target_velocity=-1.0)

        # Then: throttle must remain zero
        self.assertEqual(throttle, 0.0)

    def test_given_ground_mode_when_step_called_then_enters_takeoff_with_positive_throttle(self):
        # Given: a new simulator at ground state
        sim = FlightSimulator(config=load_config())

        # When: one simulation step is executed
        row = sim.step()

        # Then: mode transitions to takeoff and throttle is commanded
        self.assertEqual(row["mode"], "takeoff")
        self.assertGreater(row["throttle"], 0.0)


if __name__ == "__main__":
    unittest.main()
