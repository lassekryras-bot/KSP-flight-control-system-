import math

from ksp_flight_control.specs import DEFAULT_PARACHUTE_SPEC


DEFAULT_RESOURCE_NAMES = (
    "LiquidFuel",
    "Oxidizer",
    "SolidFuel",
    "MonoPropellant",
    "ElectricCharge",
)

RESOURCE_LABELS = {
    "LiquidFuel": "LF",
    "Oxidizer": "OX",
    "SolidFuel": "SF",
    "MonoPropellant": "MP",
    "ElectricCharge": "EC",
}

IDLE_PARACHUTE_SITUATIONS = {"pre_launch", "landed", "splashed"}


def is_finite_number(value):
    return isinstance(value, (int, float)) and math.isfinite(value)


def format_metric(value, unit, width=8, precision=1):
    if not is_finite_number(value):
        return f"{'--':>{width}} {unit}".rstrip()
    return f"{value:{width}.{precision}f} {unit}".rstrip()


def format_resource_value(name, values):
    amount = values["amount"]
    maximum = values["max"]
    label = RESOURCE_LABELS.get(name, name)

    if not is_finite_number(amount) or not is_finite_number(maximum):
        return f"{label}: --/--"

    if maximum <= 0:
        return f"{label}: {amount:.1f}"

    return f"{label}: {amount:.1f}/{maximum:.1f}"


def format_resources(resources):
    if not resources:
        return "Fuel: --"

    return " | ".join(format_resource_value(name, values) for name, values in resources.items())


def format_telemetry_line(values):
    return (
        f"Alt: {format_metric(values['altitude'], 'm')} | "
        f"Apo: {format_metric(values['apoapsis'], 'm')} | "
        f"Spd: {format_metric(values['speed'], 'm/s', width=6)} | "
        f"VSpd: {format_metric(values['vertical_speed'], 'm/s', width=6)} | "
        f"Mass: {format_metric(values['mass'], 'kg', width=8)} | "
        f"{format_resources(values['resources'])}"
    )


def get_parachutes(vessel):
    parts = getattr(vessel, "parts", None)
    if parts is None:
        return []
    return list(getattr(parts, "parachutes", []))


def get_situation_name(vessel):
    situation = vessel.situation
    if isinstance(situation, str):
        return situation
    return getattr(situation, "name", str(situation))


def normalize_parachute_state(parachute):
    state = getattr(parachute, "state", "unactivated")
    if not isinstance(state, str):
        state = getattr(state, "name", str(state))

    state_map = {
        "stowed": "unactivated",
        "armed": "armed",
        "semi_deployed": "semi_deployed",
        "deployed": "fully_deployed",
        "fully_deployed": "fully_deployed",
        "cut": "cut",
        "unactivated": "unactivated",
    }
    return state_map.get(state, state)


def get_parachute_spec(parachute, default_spec=DEFAULT_PARACHUTE_SPEC):
    return getattr(parachute, "spec", default_spec)


def evaluate_parachute_deployment(parachute, values, spec=None):
    spec = get_parachute_spec(parachute, DEFAULT_PARACHUTE_SPEC) if spec is None else spec
    state = normalize_parachute_state(parachute)
    pressure_atm = values.get("pressure_atm")
    surface_altitude = values.get("surface_altitude")
    time_in_state = values.get("time_in_state", 0.0)

    if state == "unactivated":
        return {
            "current_stage": state,
            "next_stage": "unactivated",
            "should_transition": False,
            "reason": "Parachute requires activation before deployment can begin.",
        }

    if state == "armed":
        if not is_finite_number(pressure_atm):
            return {
                "current_stage": state,
                "next_stage": "armed",
                "should_transition": False,
                "reason": "Atmospheric pressure is not ready yet.",
            }

        if pressure_atm >= spec.deployment.semi.min_pressure:
            return {
                "current_stage": state,
                "next_stage": "semi_deployed",
                "should_transition": True,
                "reason": (
                    f"Pressure {pressure_atm:.3f} atm reached the "
                    f"semi-deploy threshold of {spec.deployment.semi.min_pressure:.3f} atm."
                ),
            }

        return {
            "current_stage": state,
            "next_stage": "armed",
            "should_transition": False,
            "reason": "Pressure is below the semi-deploy threshold.",
        }

    if state == "semi_deployed":
        if not is_finite_number(surface_altitude):
            return {
                "current_stage": state,
                "next_stage": "semi_deployed",
                "should_transition": False,
                "reason": "Surface altitude is not ready yet.",
            }

        if time_in_state < spec.behavior.full_deploy_delay_seconds:
            return {
                "current_stage": state,
                "next_stage": "semi_deployed",
                "should_transition": False,
                "reason": "Full deployment delay is still in progress.",
            }

        if surface_altitude <= spec.deployment.full.deploy_altitude:
            return {
                "current_stage": state,
                "next_stage": "fully_deployed",
                "should_transition": True,
                "reason": (
                    f"Altitude {surface_altitude:.1f} m is at or below the "
                    f"full-deploy threshold of {spec.deployment.full.deploy_altitude:.1f} m."
                ),
            }

        return {
            "current_stage": state,
            "next_stage": "semi_deployed",
            "should_transition": False,
            "reason": "Altitude is still above the full-deploy threshold.",
        }

    return {
        "current_stage": state,
        "next_stage": state,
        "should_transition": False,
        "reason": "Parachute is already in a terminal deployment state.",
    }


def evaluate_parachute_safety(vessel, values, config):
    parachutes = get_parachutes(vessel)
    armable = []

    for parachute in parachutes:
        if not parachute.armed and not parachute.deployed:
            armable.append(parachute)

    if not parachutes:
        return {"total": 0, "armable": [], "should_arm": False, "reason": "No parachutes detected."}

    situation_name = get_situation_name(vessel)
    if situation_name in IDLE_PARACHUTE_SITUATIONS:
        return {
            "total": len(parachutes),
            "armable": armable,
            "should_arm": False,
            "reason": f"Vessel situation is '{situation_name}', so parachute safety is idle.",
        }

    surface_altitude = values["surface_altitude"]
    vertical_speed = values["vertical_speed"]

    if not is_finite_number(surface_altitude) or not is_finite_number(vertical_speed):
        return {
            "total": len(parachutes),
            "armable": armable,
            "should_arm": False,
            "reason": "Surface altitude or vertical speed is not ready yet.",
        }

    if vertical_speed > config.parachute_arm_speed:
        return {
            "total": len(parachutes),
            "armable": armable,
            "should_arm": False,
            "reason": "Vessel is not descending fast enough for parachute arming.",
        }

    if surface_altitude > config.parachute_arm_altitude:
        return {
            "total": len(parachutes),
            "armable": armable,
            "should_arm": False,
            "reason": "Vessel is still above the parachute arm altitude.",
        }

    if not armable:
        return {
            "total": len(parachutes),
            "armable": [],
            "should_arm": False,
            "reason": "All parachutes are already armed or deployed.",
        }

    return {
        "total": len(parachutes),
        "armable": armable,
        "should_arm": True,
        "reason": (
            f"Descending at {vertical_speed:.1f} m/s and {surface_altitude:.1f} m above the surface."
        ),
    }


def build_parachute_summary(vessel, config):
    parachutes = get_parachutes(vessel)
    spec = config.parachute_spec
    return (
        f"Parachutes detected: {len(parachutes)} | "
        f"mode: {config.parachute_mode} | "
        f"semi: {spec.deployment.semi.min_pressure:.3f} atm | "
        f"full: {spec.deployment.full.deploy_altitude:.0f} m AGL | "
        f"safety arm: below {config.parachute_arm_altitude:.0f} m AGL and "
        f"vertical speed <= {config.parachute_arm_speed:.1f} m/s"
    )


def resolve_parachute_transition_conflicts(parachutes, values):
    candidates = []

    for parachute in parachutes:
        evaluation = evaluate_parachute_deployment(parachute, values)
        if evaluation["should_transition"]:
            candidates.append((parachute, evaluation))

    if len(candidates) <= 1:
        return candidates

    # Higher-priority parachutes transition first if several are eligible in the same step.
    highest_priority = min(
        get_parachute_spec(parachute).behavior.deployment_priority
        for parachute, _ in candidates
    )
    return [
        (parachute, evaluation)
        for parachute, evaluation in candidates
        if get_parachute_spec(parachute).behavior.deployment_priority == highest_priority
    ]


def apply_parachute_safety(vessel, values, config, parachute_state, emit):
    if config.parachute_mode == "off":
        return False

    evaluation = evaluate_parachute_safety(vessel, values, config)
    if not evaluation["should_arm"] or parachute_state["triggered"]:
        return False

    count = len(evaluation["armable"])
    if config.parachute_mode == "simulate":
        emit(f"SIM parachute safety: would arm {count} parachute(s). {evaluation['reason']}")
        parachute_state["triggered"] = True
        return False

    for parachute in evaluation["armable"]:
        parachute.arm()

    emit(f"LIVE parachute safety: armed {count} parachute(s). {evaluation['reason']}")
    parachute_state["triggered"] = True
    return False


def build_parachute_test_lines(vessel, values, config):
    evaluation = evaluate_parachute_safety(vessel, values, config)
    return [
        "Parachute test:",
        f"Detected parachutes: {evaluation['total']}",
        f"Armable parachutes: {len(evaluation['armable'])}",
        f"Safety mode: {config.parachute_mode}",
        f"Decision: {'trigger' if evaluation['should_arm'] else 'hold'}",
        f"Reason: {evaluation['reason']}",
    ]
