# Archived Code Gold Nuggets

This pass focused on `archive/` files to identify reusable ideas that are not clearly surfaced in the current top-level simulation entrypoints.

## Top Nuggets Worth Recovering

1. **Dual-threshold launch detection (liftoff vs stable ascent)**
   - `archive/main_v4.py` has separate detectors for **liftoff** (`0.01 m/s`) and **stable ascent** (`1.0 m/s for 0.2s`), which gives cleaner event segmentation than a single threshold trigger.
   - Reusable pieces: `DetectionSystem.update(velocity, dt)` and the two-detector flow in `run_single_test`.

2. **Deterministic, `dt`-driven detection timers**
   - Older detector logic increments a timer by `dt` instead of relying on wall-clock calls. That makes offline simulation runs reproducible and easier to test.
   - This is especially useful for unit tests and regression comparisons.

3. **State machine transition tracking for flight phases**
   - `archive/hover_v22.py` stores mode transitions with timestamps and logs mode changes in one place (`set_mode`), making behavior auditable.
   - Great foundation for post-flight analysis and debugging “why did the controller switch modes?”

4. **Landing feasibility predictor (`can_land`)**
   - `archive/hover_v22.py` includes a physics check that estimates whether available thrust can arrest descent before ground impact.
   - This is a practical safety gate before entering powered landing mode.

5. **Throttle smoothing to reduce control chatter**
   - `archive/hover_v22.py` applies first-order smoothing from previous throttle to requested throttle.
   - This is a simple but effective anti-oscillation improvement.

6. **Part-catalog vehicle builder abstraction**
   - `archive/hover_v20.py` and `archive/hover_v16.py` use `PARTS` + `build_vehicle(...)` to construct vehicle variants from reusable part definitions.
   - This makes scenario generation far easier than hard-coding constants per script.

7. **Telemetry verbosity levels (minimal/events/full)**
   - `archive/hover_v20.py` supports logging levels and separate event vs telemetry logging paths.
   - Useful for long runs where full logs are too noisy.

8. **Scenario batch harness for comparative runs**
   - `archive/test_v1.py` provides `run_scenario` + `analyze` for repeated scenario sweeps and summary stats.
   - Good seed for an experiments/benchmark command.

## Fastest “Low-Risk” Recoveries

- Extract `DetectionSystem(..., dt)` from `main_v4.py` into a reusable module and use it for both liftoff and ascent markers.
- Add transition history collection (`time, from_mode, to_mode`) to the currently active controller class.
- Add a lightweight `LOG_LEVEL` switch for simulation runs.
- Port the part-catalog/builder pattern so test vehicles can be declared in data instead of code.

## Cleanup Notes

- There is an extensionless duplicate file: `archive/hover_v7` (same-style content as `.py` versions). This is easy to miss and could be archived again under a clearer name or removed after verification.

