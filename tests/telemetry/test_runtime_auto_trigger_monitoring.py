from ksp_flight_control.auto_trigger import AutoTriggerState
from ksp_flight_control.runtime import (
    apply_runtime_vertical_speed_fallback,
    build_auto_trigger_status_key,
    format_auto_trigger_status_line,
)


def test_should_format_runtime_auto_trigger_line_for_observe_only_policy():
    # Given an observe-only auto-trigger state during active monitoring
    # When the runtime status line is formatted
    # Then the output should describe the policy, classification, and reason
    state = AutoTriggerState(
        classification="risky",
        window_status="narrow",
        reason="Deployment window is narrow but still valid.",
    )

    line = format_auto_trigger_status_line("observe_only", state)

    assert "Auto-trigger observe_only: risky" in line
    assert "window: narrow" in line
    assert "action: monitor" in line


def test_should_include_best_effort_action_in_runtime_auto_trigger_line():
    # Given an unrecoverable state where policy allowed a best-effort trigger
    # When the runtime status line is formatted
    # Then the action text should remain distinct from the failure classification
    state = AutoTriggerState(
        trigger_count=1,
        classification="unrecoverable",
        window_status="missed",
        reason="Safe deployment window was missed; policy allowed a best-effort trigger.",
        best_effort=True,
    )

    line = format_auto_trigger_status_line("best_effort", state)

    assert "Auto-trigger best_effort: unrecoverable" in line
    assert "action: best-effort trigger" in line


def test_should_change_runtime_auto_trigger_status_key_when_reason_changes():
    # Given two monitoring states with the same classification but different reasons
    # When the runtime change-detection key is built
    # Then the keys should differ so the operator sees the update
    first = AutoTriggerState(classification="monitoring", window_status="closed", reason="Waiting for a valid descent phase.")
    second = AutoTriggerState(classification="monitoring", window_status="closed", reason="Telemetry is incomplete.")

    first_key = build_auto_trigger_status_key(first)
    second_key = build_auto_trigger_status_key(second)

    assert first_key != second_key


def test_should_use_derived_vertical_speed_when_live_stream_is_stale():
    # Given consecutive telemetry samples with changing altitude but zero reported vertical speed
    # When the runtime fallback computes vertical speed
    # Then the derived descent rate should replace the stale live value
    motion_state = {}
    first_values = {"surface_altitude": 1000.0, "vertical_speed": 0.0}
    second_values = {"surface_altitude": 900.0, "vertical_speed": 0.0}

    apply_runtime_vertical_speed_fallback(first_values, motion_state, now=10.0)
    result = apply_runtime_vertical_speed_fallback(second_values, motion_state, now=11.0)

    assert result["vertical_speed"] == -100.0
    assert result["vertical_speed_source"] == "derived"


def test_should_keep_reported_vertical_speed_when_live_stream_is_meaningful():
    # Given consecutive telemetry samples with a meaningful reported vertical speed
    # When the runtime fallback evaluates the same interval
    # Then the reported value should remain authoritative
    motion_state = {}
    first_values = {"surface_altitude": 1000.0, "vertical_speed": 0.0}
    second_values = {"surface_altitude": 900.0, "vertical_speed": -95.0}

    apply_runtime_vertical_speed_fallback(first_values, motion_state, now=10.0)
    result = apply_runtime_vertical_speed_fallback(second_values, motion_state, now=11.0)

    assert result["vertical_speed"] == -95.0
    assert result["vertical_speed_source"] == "reported"
