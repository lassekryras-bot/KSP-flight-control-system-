from ksp_flight_control.auto_trigger import AutoParachuteTriggerController, AutoTriggerState
from tests.support.builders import make_parachute, make_simulator, make_telemetry, make_vessel


def test_should_arm_once_in_a_narrow_deployment_window():
    # Given a parachute system entering a narrow but still valid deployment window
    # When the continuous control loop evaluates the descent repeatedly
    # Then it should trigger exactly once
    controller = AutoParachuteTriggerController(policy_mode="strict")
    vessel = make_vessel(parachutes=[make_parachute()])
    values = make_telemetry(surface_altitude=1100.0, vertical_speed=-20.0, pressure_atm=0.2)
    state = AutoTriggerState()

    controller.step(vessel, values, state)
    controller.step(vessel, values, state)

    assert vessel.parachutes[0].arm_calls == 1
    assert state.trigger_count == 1
    assert state.classification == "risky"


def test_should_trigger_best_effort_in_unrecoverable_mode():
    # Given an unrecoverable descent with policy set to best_effort
    # When the continuous control loop evaluates the missed window
    # Then it should still arm once while preserving the failure classification
    controller = AutoParachuteTriggerController(policy_mode="best_effort")
    vessel = make_vessel(parachutes=[make_parachute()])
    values = make_telemetry(surface_altitude=800.0, vertical_speed=-300.0, pressure_atm=0.8)
    state = AutoTriggerState()

    controller.step(vessel, values, state)

    assert vessel.parachutes[0].arm_calls == 1
    assert state.trigger_count == 1
    assert state.classification == "unrecoverable"
    assert state.best_effort is True


def test_should_suppress_unrecoverable_trigger_in_strict_mode():
    # Given an unrecoverable descent with policy set to strict
    # When the continuous control loop evaluates the missed window
    # Then it should report failure without arming the parachute
    controller = AutoParachuteTriggerController(policy_mode="strict")
    vessel = make_vessel(parachutes=[make_parachute()])
    values = make_telemetry(surface_altitude=800.0, vertical_speed=-300.0, pressure_atm=0.9)
    state = AutoTriggerState()

    controller.step(vessel, values, state)

    assert vessel.parachutes[0].arm_calls == 0
    assert state.trigger_count == 0
    assert state.classification == "unrecoverable"


def test_should_classify_only_in_observe_only_mode_during_unrecoverable_descent():
    # Given an unrecoverable descent with policy set to observe_only
    # When the continuous control loop evaluates the missed window
    # Then it should preserve the failure classification without taking action
    controller = AutoParachuteTriggerController(policy_mode="observe_only")
    vessel = make_vessel(parachutes=[make_parachute()])
    values = make_telemetry(surface_altitude=800.0, vertical_speed=-300.0, pressure_atm=0.9)
    state = AutoTriggerState()

    controller.step(vessel, values, state)

    assert vessel.parachutes[0].arm_calls == 0
    assert state.trigger_count == 0
    assert state.classification == "unrecoverable"
    assert "Observe-only policy suppressed deployment." in state.reason


def test_should_keep_monitoring_until_a_valid_descent_phase_exists():
    # Given a vessel that is not yet descending
    # When the continuous control loop evaluates the state
    # Then it should remain in monitoring mode without triggering
    controller = AutoParachuteTriggerController(policy_mode="strict")
    vessel = make_vessel(parachutes=[make_parachute()])
    values = make_telemetry(surface_altitude=5000.0, vertical_speed=0.0, pressure_atm=0.01)
    state = AutoTriggerState()

    controller.step(vessel, values, state)

    assert vessel.parachutes[0].arm_calls == 0
    assert state.trigger_count == 0
    assert state.classification == "monitoring"


def test_should_classify_a_continuous_late_start_descent_as_unrecoverable_after_touchdown():
    # Given a high-speed descent with no auto-trigger start until the craft is already too low
    # When the simulator and control loop advance together
    # Then the control loop should end in an unrecoverable state
    simulator = make_simulator()
    controller = AutoParachuteTriggerController(policy_mode="strict")
    vessel_state = simulator.create_state(
        altitude=90.0,
        vertical_speed=-180.0,
        parachutes=[make_parachute()],
    )
    state = AutoTriggerState()

    controller.step(vessel_state.vessel, vessel_state.as_telemetry().as_values(), state)
    simulator.run_until_ground(vessel_state, max_steps=200)

    assert state.classification == "unrecoverable"
    assert vessel_state.impact_speed is not None
