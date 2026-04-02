import pytest

from ksp_flight_control.logic import (
    apply_parachute_safety,
    build_parachute_test_lines,
    evaluate_parachute_deployment,
    evaluate_parachute_safety,
)
from ksp_flight_control.specs import MK16_PARACHUTE
from tests.support.builders import make_config, make_parachute, make_telemetry, make_vessel


class TestAutoParachuteTrigger:
    def test_should_trigger_parachute_safety_for_descending_vessel_below_arm_altitude(self):
        # Given a descending vessel with an available parachute below the arm altitude
        # When parachute safety is evaluated
        # Then the evaluation should request parachute arming
        vessel = make_vessel(situation="flying", parachutes=[make_parachute()])
        values = make_telemetry(surface_altitude=900.0, vertical_speed=-30.0)
        config = make_config(parachute_mode="simulate", parachute_arm_altitude=1500.0, parachute_arm_speed=-5.0)

        evaluation = evaluate_parachute_safety(vessel, values, config)

        assert evaluation["should_arm"] is True
        assert len(evaluation["armable"]) == 1

    def test_should_not_arm_parachutes_in_simulate_mode(self):
        # Given a vessel that meets the parachute trigger conditions
        # When simulate mode applies parachute safety
        # Then the system should only report the action without arming parachutes
        vessel = make_vessel(situation="flying", parachutes=[make_parachute()])
        values = make_telemetry(surface_altitude=900.0, vertical_speed=-30.0)
        config = make_config(parachute_mode="simulate", parachute_arm_altitude=1500.0, parachute_arm_speed=-5.0)
        state = {"triggered": False}
        messages = []

        apply_parachute_safety(vessel, values, config, state, messages.append)

        assert state["triggered"] is True
        assert vessel.parachutes[0].arm_calls == 0
        assert len(messages) == 1
        assert "would arm 1 parachute(s)" in messages[0]

    def test_should_arm_parachutes_in_live_mode(self):
        # Given a vessel that meets the parachute trigger conditions
        # When live mode applies parachute safety
        # Then the system should arm the parachute
        vessel = make_vessel(situation="flying", parachutes=[make_parachute()])
        values = make_telemetry(surface_altitude=900.0, vertical_speed=-30.0)
        config = make_config(parachute_mode="live", parachute_arm_altitude=1500.0, parachute_arm_speed=-5.0)
        state = {"triggered": False}
        messages = []

        apply_parachute_safety(vessel, values, config, state, messages.append)

        assert state["triggered"] is True
        assert vessel.parachutes[0].arm_calls == 1
        assert len(messages) == 1
        assert "armed 1 parachute(s)" in messages[0]

    def test_should_trigger_deployment_only_once_per_parachute(self):
        # Given a live auto-trigger that has already fired once
        # When the safety check is evaluated again with the same conditions
        # Then the parachute should not be armed a second time
        vessel = make_vessel(situation="flying", parachutes=[make_parachute()])
        values = make_telemetry(surface_altitude=900.0, vertical_speed=-30.0)
        config = make_config(parachute_mode="live", parachute_arm_altitude=1500.0, parachute_arm_speed=-5.0)
        state = {"triggered": False}
        messages = []

        apply_parachute_safety(vessel, values, config, state, messages.append)
        apply_parachute_safety(vessel, values, config, state, messages.append)

        assert vessel.parachutes[0].arm_calls == 1
        assert len(messages) == 1

    def test_should_report_hold_decision_while_prelaunch(self):
        # Given a vessel on the pad before launch
        # When parachute test output is generated
        # Then the decision should remain hold
        vessel = make_vessel(situation="pre_launch", parachutes=[make_parachute()])
        values = make_telemetry(surface_altitude=100.0, vertical_speed=0.0)
        config = make_config(parachute_mode="simulate", parachute_arm_altitude=1500.0, parachute_arm_speed=-5.0)

        lines = build_parachute_test_lines(vessel, values, config)

        assert "Decision: hold" in lines
        assert any("pre_launch" in line for line in lines)

    @pytest.mark.parametrize(
        ("pressure_atm", "should_transition", "expected_stage"),
        [
            (0.039, False, "armed"),
            (0.040, True, "semi_deployed"),
            (0.041, True, "semi_deployed"),
        ],
    )
    def test_should_respect_mk16_semi_deploy_pressure_boundary(self, pressure_atm, should_transition, expected_stage):
        # Given an armed Mk16 parachute near its semi-deploy pressure threshold
        # When deployment is evaluated at the current pressure
        # Then the semi-deploy decision should match the spec boundary
        parachute = make_parachute(state="armed")
        values = make_telemetry(pressure_atm=pressure_atm)

        evaluation = evaluate_parachute_deployment(parachute, values, MK16_PARACHUTE)

        assert evaluation["should_transition"] is should_transition
        assert evaluation["next_stage"] == expected_stage

    @pytest.mark.parametrize(
        ("surface_altitude", "should_transition", "expected_stage"),
        [
            (1001.0, False, "semi_deployed"),
            (1000.0, True, "fully_deployed"),
            (999.0, True, "fully_deployed"),
        ],
    )
    def test_should_respect_mk16_full_deploy_altitude_boundary(
        self, surface_altitude, should_transition, expected_stage
    ):
        # Given a semi-deployed Mk16 parachute near its full-deploy altitude threshold
        # When deployment is evaluated after the deploy delay has elapsed
        # Then the full-deploy decision should match the spec boundary
        parachute = make_parachute(state="semi_deployed")
        values = make_telemetry(surface_altitude=surface_altitude, time_in_state=1.0)

        evaluation = evaluate_parachute_deployment(parachute, values, MK16_PARACHUTE)

        assert evaluation["should_transition"] is should_transition
        assert evaluation["next_stage"] == expected_stage

    def test_should_not_fully_deploy_before_full_deploy_delay_has_elapsed(self):
        # Given a semi-deployed Mk16 parachute below the full-deploy altitude
        # When the full-deploy delay has not elapsed yet
        # Then the parachute should remain semi-deployed
        parachute = make_parachute(state="semi_deployed")
        values = make_telemetry(surface_altitude=900.0, time_in_state=0.5)

        evaluation = evaluate_parachute_deployment(parachute, values, MK16_PARACHUTE)

        assert evaluation["should_transition"] is False
        assert evaluation["next_stage"] == "semi_deployed"

    def test_should_not_begin_deployment_without_activation(self):
        # Given an unactivated Mk16 parachute in deployable conditions
        # When deployment is evaluated
        # Then the parachute should remain unactivated
        parachute = make_parachute(state="unactivated")
        values = make_telemetry(pressure_atm=0.2, surface_altitude=500.0, time_in_state=5.0)

        evaluation = evaluate_parachute_deployment(parachute, values, MK16_PARACHUTE)

        assert evaluation["should_transition"] is False
        assert evaluation["next_stage"] == "unactivated"
