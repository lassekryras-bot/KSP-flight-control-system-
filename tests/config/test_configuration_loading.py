from ksp_flight_control.specs import MK16_PARACHUTE, PROJECT_CONFIG


def test_should_load_mk16_spec_from_yaml_configuration():
    # Given the project configuration files
    # When the Mk16 parachute spec is loaded
    # Then the structured spec should match the YAML source values
    assert MK16_PARACHUTE.part_name == "Mk16 Parachute"
    assert MK16_PARACHUTE.deployment.semi.min_pressure == 0.04
    assert MK16_PARACHUTE.deployment.full.deploy_altitude == 1000


def test_should_load_core_constants_from_yaml_configuration():
    # Given the project configuration files
    # When global constants are loaded
    # Then the expected atmospheric and gravity constants should be available
    assert PROJECT_CONFIG.constants.standard_atmosphere_pa == 101325.0
    assert PROJECT_CONFIG.constants.kerbin_surface_gravity_mps2 == 9.81
    assert PROJECT_CONFIG.sim_physics.time_step_seconds == 0.1


def test_should_load_auto_trigger_policy_modes_from_yaml_configuration():
    # Given the project configuration files
    # When auto-trigger policy settings are loaded
    # Then the approved policy modes should be available with the expected defaults
    assert PROJECT_CONFIG.sim_physics.default_policy_mode == "strict"
    assert PROJECT_CONFIG.sim_physics.policy_for("strict").trigger_in_unrecoverable is False
    assert PROJECT_CONFIG.sim_physics.policy_for("best_effort").trigger_in_unrecoverable is True
    assert PROJECT_CONFIG.sim_physics.policy_for("observe_only").trigger_in_safe is False
