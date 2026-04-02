import sys
import time

import krpc
from krpc.services.krpc import GameScene

from ksp_flight_control.auto_trigger import AutoParachuteTriggerController, AutoTriggerState
from ksp_flight_control.config import parse_args
from ksp_flight_control.logic import (
    DEFAULT_RESOURCE_NAMES,
    apply_parachute_safety,
    build_parachute_summary,
    build_parachute_test_lines,
    format_telemetry_line,
    get_parachutes,
)
from ksp_flight_control.specs import STANDARD_ATMOSPHERE_PA

VERTICAL_SPEED_ZERO_EPSILON = 0.05
DERIVED_VERTICAL_SPEED_MIN_DELTA_MPS = 0.5


def connect():
    try:
        return krpc.connect(name="KSP Flight Control")
    except ConnectionRefusedError:
        print("Could not connect to kRPC.", file=sys.stderr)
        print("Make sure KSP is running and the kRPC server is started.", file=sys.stderr)
        raise


def get_vessel(connection):
    try:
        return connection.space_center.active_vessel
    except ValueError:
        try:
            vessels = connection.space_center.vessels
        except krpc.error.RPCError:
            vessels = []

        if vessels:
            return vessels[0]

        return None


def discover_resources(vessel):
    resources = vessel.resources
    names = []
    capacities = {}

    for name in DEFAULT_RESOURCE_NAMES:
        try:
            if resources.has_resource(name):
                names.append(name)
                capacities[name] = resources.max(name)
        except krpc.error.RPCError:
            continue

    return resources, names, capacities


def create_telemetry_streams(connection, vessel):
    flight = vessel.flight()
    body_flight = vessel.flight(vessel.orbit.body.reference_frame)
    resources, resource_names, resource_capacities = discover_resources(vessel)

    streams = {
        "altitude": connection.add_stream(getattr, flight, "mean_altitude"),
        "apoapsis": connection.add_stream(getattr, vessel.orbit, "apoapsis_altitude"),
        "speed": connection.add_stream(getattr, body_flight, "speed"),
        "vertical_speed": connection.add_stream(getattr, flight, "vertical_speed"),
        "surface_altitude": connection.add_stream(getattr, flight, "surface_altitude"),
        "pressure_pa": connection.add_stream(getattr, flight, "static_pressure"),
        "mass": connection.add_stream(getattr, vessel, "mass"),
    }

    for name in resource_names:
        streams[f"resource:{name}"] = connection.add_stream(resources.amount, name)

    return {
        "streams": streams,
        "resource_names": resource_names,
        "resource_capacities": resource_capacities,
    }


def close_telemetry_streams(telemetry):
    if telemetry is None:
        return

    for stream in telemetry["streams"].values():
        try:
            stream.remove()
        except Exception:
            pass


def read_direct_telemetry(vessel):
    flight = vessel.flight()
    body_flight = vessel.flight(vessel.orbit.body.reference_frame)
    _, resource_names, resource_capacities = discover_resources(vessel)

    resources = {}
    for name in resource_names:
        resources[name] = {
            "amount": vessel.resources.amount(name),
            "max": resource_capacities[name],
        }

    return {
        "altitude": flight.mean_altitude,
        "apoapsis": vessel.orbit.apoapsis_altitude,
        "speed": body_flight.speed,
        "vertical_speed": flight.vertical_speed,
        "surface_altitude": flight.surface_altitude,
        "pressure_atm": flight.static_pressure / STANDARD_ATMOSPHERE_PA,
        "time_in_state": 0.0,
        "mass": vessel.mass,
        "resources": resources,
    }


def read_stream_telemetry(telemetry):
    resources = {}
    for name in telemetry["resource_names"]:
        resources[name] = {
            "amount": telemetry["streams"][f"resource:{name}"](),
            "max": telemetry["resource_capacities"][name],
        }

    return {
        "altitude": telemetry["streams"]["altitude"](),
        "apoapsis": telemetry["streams"]["apoapsis"](),
        "speed": telemetry["streams"]["speed"](),
        "vertical_speed": telemetry["streams"]["vertical_speed"](),
        "surface_altitude": telemetry["streams"]["surface_altitude"](),
        "pressure_atm": telemetry["streams"]["pressure_pa"]() / STANDARD_ATMOSPHERE_PA,
        "time_in_state": 0.0,
        "mass": telemetry["streams"]["mass"](),
        "resources": resources,
    }


def read_telemetry(connection, vessel, telemetry):
    if telemetry is None:
        return None, read_direct_telemetry(vessel), False

    try:
        return telemetry, read_stream_telemetry(telemetry), False
    except krpc.error.RPCError as error:
        print(f"Telemetry stream error: {error}", file=sys.stderr)
        print("Recreating telemetry streams...", file=sys.stderr)

        close_telemetry_streams(telemetry)

        try:
            refreshed = create_telemetry_streams(connection, vessel)
        except krpc.error.RPCError as refresh_error:
            print(f"Stream recreation failed: {refresh_error}", file=sys.stderr)
            print("The vessel or game scene likely changed. Waiting for a valid flight scene.", file=sys.stderr)
            return None, None, True

        try:
            return refreshed, read_stream_telemetry(refreshed), False
        except krpc.error.RPCError as retry_error:
            print(f"Stream recovery failed: {retry_error}", file=sys.stderr)
            print("Falling back to direct telemetry reads.", file=sys.stderr)

            close_telemetry_streams(refreshed)
            try:
                return None, read_direct_telemetry(vessel), False
            except krpc.error.RPCError as direct_error:
                print(f"Direct telemetry read failed: {direct_error}", file=sys.stderr)
                print("The vessel or game scene likely changed. Waiting for a valid flight scene.", file=sys.stderr)
                return None, None, True


def get_game_scene(connection):
    try:
        return connection.krpc.current_game_scene
    except krpc.error.RPCError:
        return None


def handle_runtime_parachute_safety(vessel, values, config, parachute_state):
    try:
        return apply_parachute_safety(vessel, values, config, parachute_state, print)
    except krpc.error.RPCError as error:
        print(f"Parachute safety check failed: {error}", file=sys.stderr)
        print("The vessel likely changed. Waiting for a valid flight scene.", file=sys.stderr)
        return True


def apply_runtime_vertical_speed_fallback(values, motion_state, now=None):
    now = time.monotonic() if now is None else now
    altitude = values.get("surface_altitude")
    reported_vertical_speed = values.get("vertical_speed")
    values["vertical_speed_source"] = "reported"

    previous_altitude = motion_state.get("surface_altitude")
    previous_timestamp = motion_state.get("timestamp")

    if (
        previous_altitude is not None
        and previous_timestamp is not None
        and altitude is not None
        and now > previous_timestamp
    ):
        dt = now - previous_timestamp
        derived_vertical_speed = (altitude - previous_altitude) / dt
        values["derived_vertical_speed"] = derived_vertical_speed

        if (
            not isinstance(reported_vertical_speed, (int, float))
            or abs(reported_vertical_speed) <= VERTICAL_SPEED_ZERO_EPSILON
        ) and abs(derived_vertical_speed) >= DERIVED_VERTICAL_SPEED_MIN_DELTA_MPS:
            values["vertical_speed"] = derived_vertical_speed
            values["vertical_speed_source"] = "derived"

    motion_state["surface_altitude"] = altitude
    motion_state["timestamp"] = now
    return values


def build_auto_trigger_status_key(state: AutoTriggerState):
    return (
        state.classification,
        state.window_status,
        state.reason,
        state.best_effort,
        state.trigger_count,
    )


def format_auto_trigger_status_line(policy_mode: str, state: AutoTriggerState):
    action = "monitor"
    if state.trigger_count > 0:
        action = "best-effort trigger" if state.best_effort else "trigger"

    return (
        f"Auto-trigger {policy_mode}: {state.classification} | "
        f"window: {state.window_status} | action: {action} | "
        f"reason: {state.reason}"
    )


def handle_runtime_auto_trigger_monitor(vessel, values, controller, state, last_status_key):
    try:
        state = controller.step(vessel, values, state)
    except krpc.error.RPCError as error:
        print(f"Auto-trigger monitor failed: {error}", file=sys.stderr)
        print("The vessel likely changed. Waiting for a valid flight scene.", file=sys.stderr)
        return state, last_status_key, True

    status_key = build_auto_trigger_status_key(state)
    if status_key != last_status_key:
        print(format_auto_trigger_status_line(controller.policy_mode, state))

    return state, status_key, False


def configure_parachutes(vessel, config):
    spec = config.parachute_spec
    for parachute in get_parachutes(vessel):
        try:
            parachute.deploy_min_pressure = spec.deployment.semi.min_pressure
            parachute.deploy_altitude = spec.deployment.full.deploy_altitude
        except krpc.error.RPCError:
            continue


def run(config):
    connection = connect()
    vessel = None
    telemetry = None
    last_status = None
    parachute_state = {"triggered": False}
    auto_trigger_controller = AutoParachuteTriggerController(policy_mode=config.auto_trigger_policy_mode)
    auto_trigger_state = AutoTriggerState()
    auto_trigger_status_key = None
    motion_state = {}

    print("Connected to kRPC.")
    print("Waiting for a vessel in the flight scene. Press Ctrl+C to stop.")

    try:
        while True:
            scene = get_game_scene(connection)

            if scene != GameScene.flight:
                if last_status != scene:
                    scene_name = "unknown" if scene is None else scene.name
                    print(f"KSP scene is '{scene_name}'. Waiting for the flight scene...")
                    last_status = scene
                close_telemetry_streams(telemetry)
                telemetry = None
                vessel = None
                auto_trigger_state = AutoTriggerState()
                auto_trigger_status_key = None
                motion_state = {}
                time.sleep(1)
                continue

            if vessel is None:
                vessel = get_vessel(connection)
                if vessel is None:
                    if last_status != "no_vessel":
                        print("Flight scene is active, but no vessel is available yet. Waiting...")
                        last_status = "no_vessel"
                    time.sleep(1)
                    continue

                try:
                    configure_parachutes(vessel, config)
                    telemetry = create_telemetry_streams(connection, vessel)
                    print(f"Connected to vessel: {vessel.name}")
                    print("Streaming telemetry...")
                    print(build_parachute_summary(vessel, config))
                except krpc.error.RPCError as error:
                    print(f"Could not create telemetry streams: {error}", file=sys.stderr)
                    print("Retrying while the vessel becomes available...", file=sys.stderr)
                    vessel = None
                    telemetry = None
                    time.sleep(1)
                    continue

                last_status = f"vessel:{vessel.name}"
                parachute_state = {"triggered": False}
                auto_trigger_state = AutoTriggerState()
                auto_trigger_status_key = None
                motion_state = {}
                print(f"Auto-trigger monitor policy: {config.auto_trigger_policy_mode}")

            telemetry, values, needs_reacquire = read_telemetry(connection, vessel, telemetry)
            if needs_reacquire:
                close_telemetry_streams(telemetry)
                telemetry = None
                vessel = None
                last_status = None
                parachute_state = {"triggered": False}
                auto_trigger_state = AutoTriggerState()
                auto_trigger_status_key = None
                motion_state = {}
                time.sleep(1)
                continue

            values = apply_runtime_vertical_speed_fallback(values, motion_state)

            if config.parachute_test:
                for line in build_parachute_test_lines(vessel, values, config):
                    print(line)
                return

            auto_trigger_state, auto_trigger_status_key, needs_reacquire = handle_runtime_auto_trigger_monitor(
                vessel,
                values,
                auto_trigger_controller,
                auto_trigger_state,
                auto_trigger_status_key,
            )
            if needs_reacquire:
                close_telemetry_streams(telemetry)
                telemetry = None
                vessel = None
                last_status = None
                parachute_state = {"triggered": False}
                auto_trigger_state = AutoTriggerState()
                auto_trigger_status_key = None
                motion_state = {}
                time.sleep(1)
                continue

            if handle_runtime_parachute_safety(vessel, values, config, parachute_state):
                close_telemetry_streams(telemetry)
                telemetry = None
                vessel = None
                last_status = None
                parachute_state = {"triggered": False}
                auto_trigger_state = AutoTriggerState()
                auto_trigger_status_key = None
                motion_state = {}
                time.sleep(1)
                continue

            print(format_telemetry_line(values))
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nDisconnected.")
    finally:
        close_telemetry_streams(telemetry)
        connection.close()


def main():
    run(parse_args())
