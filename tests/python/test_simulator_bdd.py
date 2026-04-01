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

    def test_given_ascending_vehicle_when_above_trigger_then_parachute_stays_disarmed(self):
        # Given: a simulator already moving upward near deployment altitude
        sim = FlightSimulator(config=load_config())
        sim.mode = "ascent"
        sim.altitude = 1500.0
        sim.velocity = 50.0

        # When: one simulation step is executed
        row = sim.step()

        # Then: deployment is blocked while ascending
        self.assertFalse(row["parachute_armed"])

    def test_given_descending_vehicle_when_below_trigger_then_parachute_arms(self):
        # Given: a simulator descending below the configured semi-deploy altitude
        sim = FlightSimulator(config=load_config())
        sim.mode = "descent"
        sim.altitude = 1500.0
        sim.velocity = -30.0

        # When: one simulation step is executed
        row = sim.step()

        # Then: parachute should enter at least semi-deployed state
        self.assertTrue(row["parachute_armed"])

    def test_given_full_deploy_parachute_when_simulated_then_velocity_stabilizes_near_terminal(self):
        # Given: a pure descent scenario with full parachute deployment
        cfg = load_config()
        cfg["vehicle"]["engine"]["throttleable"] = False
        cfg["vehicle"]["engine"]["thrust"] = 0.0
        cfg["vehicle"]["fuel_mass"] = 0.0
        cfg["detection"]["parachute"]["semi"]["altitude"] = 1500.0
        cfg["detection"]["parachute"]["full"]["altitude"] = 1200.0

        sim = FlightSimulator(config=cfg)
        sim.mode = "descent"
        sim.altitude = 1100.0
        sim.velocity = -40.0
        sim.mass = sim.dry_mass

        # When: simulating long enough to converge on terminal velocity
        velocity_trace = []
        for _ in range(2000):
            row = sim.step()
            velocity_trace.append(row["velocity"])

        # Then: velocity should settle into a stable terminal band around safe descent values
        tail = velocity_trace[-200:]
        self.assertTrue(all(-7.0 <= v <= -5.0 for v in tail))
        self.assertLess(max(tail) - min(tail), 0.2)


if __name__ == "__main__":
    unittest.main()
