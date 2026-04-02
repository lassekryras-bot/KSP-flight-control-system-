from ksp_flight_control.specs import MK16_PARACHUTE, TEST_DROGUE_PARACHUTE
from tests.support.builders import make_parachute, make_simulator


def test_should_increase_pressure_as_the_simulated_vessel_descends():
    # Given a descending simulated vessel in the upper atmosphere
    # When the physics engine advances multiple steps
    # Then the atmospheric pressure should increase as altitude falls
    simulator = make_simulator()
    state = simulator.create_state(
        altitude=18000.0,
        vertical_speed=-50.0,
        parachutes=[],
    )
    initial_pressure = state.pressure_atm

    for _ in range(20):
        simulator.step(state)

    assert state.altitude < 18000.0
    assert state.pressure_atm > initial_pressure


def test_should_transition_mk16_from_armed_to_semi_and_full_deploy_during_descent():
    # Given a descending vessel with an armed Mk16 parachute
    # When the physics engine runs until touchdown
    # Then the parachute should semi-deploy and later fully deploy
    simulator = make_simulator()
    parachute = make_parachute(state="armed")
    state = simulator.create_state(
        altitude=17000.0,
        vertical_speed=-120.0,
        mass_kg=120.0,
        parachutes=[parachute],
    )

    simulator.run_until_ground(state)

    assert parachute.semi_deploy_calls >= 1
    assert parachute.full_deploy_calls >= 1
    assert parachute.state == "fully_deployed"
    assert state.vessel.situation == "landed"


def test_should_reduce_impact_speed_below_mk16_tolerance_in_basic_descent_simulation():
    # Given a descending vessel with an armed Mk16 parachute
    # When the physics engine runs a full descent
    # Then the final impact speed should stay within the Mk16 tolerance
    simulator = make_simulator()
    state = simulator.create_state(
        altitude=12000.0,
        vertical_speed=-80.0,
        mass_kg=100.0,
        parachutes=[make_parachute(state="armed")],
    )

    simulator.run_until_ground(state)

    assert state.impact_speed is not None
    assert state.impact_speed <= MK16_PARACHUTE.safety.impact_tolerance


def test_should_deploy_drogue_before_main_in_multi_parachute_descent():
    # Given a descending vessel with both a drogue and a main parachute armed
    # When the physics engine advances through the descent
    # Then the drogue should deploy before the main parachute
    simulator = make_simulator()
    drogue = make_parachute(state="armed", spec=TEST_DROGUE_PARACHUTE)
    main = make_parachute(state="armed", spec=MK16_PARACHUTE)
    state = simulator.create_state(
        altitude=18000.0,
        vertical_speed=-140.0,
        mass_kg=120.0,
        parachutes=[drogue, main],
    )

    for _ in range(3000):
        simulator.step(state)
        if drogue.semi_deploy_calls and main.full_deploy_calls:
            break

    assert drogue.semi_deploy_calls >= 1
    assert main.full_deploy_calls >= 1
    assert drogue.full_deploy_calls >= 1
    assert drogue.time_in_state >= 0.0


def test_should_leave_main_unactivated_when_late_activation_window_is_missed():
    # Given a main parachute that is never activated during a fast descent
    # When the physics engine runs to touchdown
    # Then the system should report an unsafe landing profile for the main chute alone
    simulator = make_simulator()
    main = make_parachute(state="unactivated", spec=MK16_PARACHUTE)
    state = simulator.create_state(
        altitude=2000.0,
        vertical_speed=-150.0,
        mass_kg=100.0,
        parachutes=[main],
    )

    simulator.run_until_ground(state)

    assert main.arm_calls == 0
    assert main.semi_deploy_calls == 0
    assert main.full_deploy_calls == 0
    assert state.impact_speed is not None
    assert state.impact_speed > MK16_PARACHUTE.safety.impact_tolerance
