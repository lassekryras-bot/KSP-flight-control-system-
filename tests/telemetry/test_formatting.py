import math

from ksp_flight_control.logic import format_metric, format_telemetry_line
from tests.support.builders import make_telemetry


def test_should_show_dashes_for_nan_metric_values():
    # Given a metric value that is not yet ready
    # When the metric is formatted for telemetry output
    # Then the output should show placeholder dashes
    assert format_metric(math.nan, "m") == "      -- m"


def test_should_use_short_resource_labels_in_telemetry_output():
    # Given telemetry that includes known KSP resource names
    # When the telemetry line is formatted
    # Then the output should use the short resource labels
    values = make_telemetry(
        altitude=100.0,
        apoapsis=200.0,
        speed=30.0,
        vertical_speed=-10.0,
        surface_altitude=95.0,
        mass=12.5,
        resources={
            "LiquidFuel": {"amount": 10.0, "max": 20.0},
            "Oxidizer": {"amount": 12.0, "max": 22.0},
        },
    )

    line = format_telemetry_line(values)

    assert "LF: 10.0/20.0" in line
    assert "OX: 12.0/22.0" in line
