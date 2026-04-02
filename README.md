# KSP Flight Control System

Minimal Python starter for connecting to Kerbal Space Program through kRPC.

## Project layout

- `main.py` is the thin entrypoint
- `config/` contains YAML configuration split by concern
- `config/parts/` contains part definitions and the parts catalog index
- `ksp_flight_control/runtime.py` contains the live kRPC connection and stream loop
- `ksp_flight_control/logic.py` contains pure formatting and parachute-safety logic
- `ksp_flight_control/auto_trigger.py` contains the continuous auto-trigger controller
- `ksp_flight_control/sim.py` contains simulation classes used by the tests
- `ksp_flight_control/physics.py` contains the basic deterministic physics engine for tests
- `ksp_flight_control/specs.py` loads YAML config into typed Python specs
- `tests/` contains automated tests and shared test support helpers
- `tests/parachute/` contains parachute behavior and simulation tests
- `tests/support/` contains shared builders used by the test suites

## Test style

Tests keep the same behavior-driven structure:

- `Test case: should <expected behavior>`
- `Given <initial state>`
- `When <event or condition>`
- `Then <observable outcome>`

In practice this means:

- every test function uses a `test_should_...` name
- each test keeps explicit `Given / When / Then` comments
- shared setup lives in `tests/support/`, not inside the behavior tests

## Configuration layout

The project now uses YAML for readable, hierarchical configuration:

- `config/constants.yaml` for atmosphere, gravity, and shared unit constants
- `config/sim_physics.yaml` for simulation behavior such as parachute delay
- `config/sim_physics.yaml` also contains the basic descent engine tuning values
- `config/sim_physics.yaml` also contains auto-trigger policy modes such as `strict`, `best_effort`, and `observe_only`
- `config/pid_controllers.yaml` for future PID tuning values
- `config/math_equations.yaml` for reference equations and notes
- `config/parts/index.yaml` for the parts catalog
- `config/parts/mk16_parachute.yaml` for the Mk16 structured part spec

## Setup on Windows

1. Verify Python is installed:

```powershell
python --version
pip --version
```

2. Install the dependency:

```powershell
pip install -r requirements.txt
```

3. Start KSP and launch the kRPC server in-game.

4. Run the client:

```powershell
python main.py
```

Useful launch-safety modes:

```powershell
python main.py --parachute-test
python main.py --parachute-mode simulate
python main.py --parachute-mode live
python main.py --parachute-mode off --auto-trigger-policy observe_only
```

Run the tests:

```powershell
python -m pytest
```

Run a single test file:

```powershell
python -m pytest tests/parachute/test_auto_parachute_control_loop.py
```

Run one specific test:

```powershell
python -m pytest tests/parachute/test_auto_parachute_control_loop.py -k best_effort
```

## Troubleshooting

If you see an error about `active_vessel` being null, the kRPC connection worked, but KSP does not currently have an active craft selected.

The script now tries to fall back to the first vessel in the current save, but it still needs an open save with at least one vessel loaded.

Make sure:

- A save is loaded
- You are controlling a vessel, not sitting at the main menu or KSC overview
- The kRPC server is running in-game

## What the script does

`main.py` connects to the active vessel, or falls back to the first available vessel in the save, and prints:

- Mean altitude
- Apoapsis altitude
- Speed
- Vertical speed
- Vessel mass
- Common fuel/resource amounts

Telemetry is read through kRPC streams for cleaner and more efficient updates.
Non-ready values are shown as `--` instead of crashing or printing `nan`.

The script also includes parachute safety support:

- `--parachute-mode simulate` prints when parachutes would be armed
- `--parachute-mode live` actually arms parachutes when the safety conditions are met
- `--parachute-test` runs a one-shot safety evaluation and exits

The Mk16 parachute behavior is now formalized as a structured spec and used as the source of truth for:

- semi-deploy pressure threshold
- full-deploy altitude threshold
- deployment stage order
- modeled full-deploy delay

The test layer now also includes a basic vertical-descent simulation engine that models:

- gravity
- exponential atmosphere / pressure by altitude
- simple quadratic drag
- parachute drag from the structured spec
- step-based descent until landing

The control layer now also includes a continuous auto-trigger controller that:

- monitors descent over time instead of one-off checks
- classifies descent state as `safe`, `risky`, or `unrecoverable`
- applies policy-controlled behavior through `strict`, `best_effort`, and `observe_only` modes
- guarantees a single trigger decision per parachute in the covered path

The live runtime now also includes a supervised observe-only loop for that controller:

- it evaluates the continuous auto-trigger state during live kRPC telemetry updates
- it prints state changes such as `monitoring`, `risky`, and `unrecoverable`
- it does not control launch, throttle, or staging
- for pure monitoring, run `python main.py --parachute-mode off --auto-trigger-policy observe_only`

## Next steps

Good follow-up improvements for this project:

- Add throttle and steering controls
- Split connection, telemetry, and control logic into modules
