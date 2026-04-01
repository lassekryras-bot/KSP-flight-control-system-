from scripts.run_parachute_envelope import classify_result, run_sweep


def test_given_touchdown_velocity_when_classified_then_uses_acceptance_bands():
    assert classify_result(-4.0, 6.0) == "safe"
    assert classify_result(-8.5, 6.0) == "marginal"
    assert classify_result(-11.0, 6.0) == "fail"


def test_given_altitude_sweep_when_run_then_returns_observability_fields():
    results = run_sweep([2000, 1200, 800], max_time=60.0)

    assert len(results) == 3
    assert [row["deploy_altitude_setting_m"] for row in results] == [2000, 1200, 800]

    first = results[0]
    assert first["deploy_altitude_measured_m"] is not None
    assert first["deploy_velocity_mps"] is not None
    assert "touchdown_velocity_mps" in first
    assert first["outcome"] in {"safe", "marginal", "fail"}
