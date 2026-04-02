from ksp_flight_control.logic import (
    resolve_parachute_transition_conflicts,
)
from ksp_flight_control.specs import MK16_PARACHUTE, TEST_DROGUE_PARACHUTE
from tests.support.builders import make_parachute, make_telemetry


def test_should_assign_drogue_and_main_roles_from_part_specs():
    # Given the configured parachute specs
    # When the parachute roles are inspected
    # Then drogue and main roles should be distinct and ordered
    assert TEST_DROGUE_PARACHUTE.behavior.role == "drogue"
    assert MK16_PARACHUTE.behavior.role == "main"
    assert TEST_DROGUE_PARACHUTE.behavior.deployment_priority < MK16_PARACHUTE.behavior.deployment_priority


def test_should_choose_drogue_transition_before_main_when_both_are_eligible():
    # Given a drogue and a main parachute that are both eligible to transition in the same step
    # When deployment conflicts are resolved
    # Then the drogue should be selected first because it has higher priority
    drogue = make_parachute(state="armed", spec=TEST_DROGUE_PARACHUTE)
    main = make_parachute(state="armed", spec=MK16_PARACHUTE)
    values = make_telemetry(pressure_atm=0.05, surface_altitude=900.0)

    transitions = resolve_parachute_transition_conflicts([drogue, main], values)

    assert len(transitions) == 1
    assert transitions[0][0] is drogue
    assert transitions[0][1]["next_stage"] == "semi_deployed"
