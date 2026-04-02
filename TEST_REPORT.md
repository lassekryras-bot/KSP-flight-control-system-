# Test Report

Date: 2026-04-02
Project: KSP Flight Control System
Test scope: Configuration loading, telemetry formatting, auto parachute trigger logic, continuous control-loop behavior, parachute role logic, and simulator-backed descent testing

## Executive Summary

The automated test suite is stable and passing in both terminal and VS Code workflows.
Core parachute behavior is now validated against a structured Mk16 YAML spec, and a deterministic vertical-descent simulator is being used to exercise staged deployment behavior under simplified physics.
The project now contains a dedicated `Auto Parachute Trigger` suite for single-parachute trigger behavior.
The project also now contains a continuous control-loop suite covering late activation, narrow-window triggering, unrecoverable descent classification, policy-controlled deployment behavior, and runtime observe-only monitoring output.

- Status: Pass
- Framework: pytest
- Total tests: 34
- Passed: 34
- Failed: 0
- Environment: local Python `3.10.6`, no live KSP dependency required

## Management Summary

- The current baseline is stable and repeatable
- The system now validates both rule-based logic and simplified descent behavior
- The highest remaining risk is not software instability, but model scope:
  the simulator is intentionally simplified and has not yet been cross-validated against live kRPC flight runs

## Test Run Result

Command used:

```powershell
.\.venv\Scripts\python.exe -m pytest
```

Observed result:

```text
34 passed in 0.43s
```

## Test Suite Structure

- `tests/config/`: configuration loading and spec integrity
- `tests/telemetry/`: telemetry formatting behavior
- `tests/telemetry/test_runtime_auto_trigger_monitoring.py`: runtime observe-only auto-trigger status output
- `tests/parachute/test_auto_parachute_trigger.py`: single-parachute auto-trigger requirements
- `tests/parachute/test_auto_parachute_control_loop.py`: continuous control-loop and late-activation scenarios
- `tests/parachute/test_parachute_logic.py`: role-aware and priority logic
- `tests/parachute/test_parachute_physics.py`: simulator-backed parachute descent scenarios
- `tests/support/`: shared builders and test helpers

## What Is Proven Now

- YAML configuration is loading correctly for Mk16 spec values and shared constants
- Telemetry formatting is deterministic and handles non-ready values safely
- Auto parachute trigger behavior is consistent across simulate and live modes
- Single-trigger behavior is enforced for the auto-trigger path
- Mk16 deployment thresholds are respected at pressure and altitude boundaries
- Continuous control-loop behavior is covered for monitoring, narrow-window, best-effort, and unrecoverable states
- Policy-controlled override behavior is covered for `strict`, `best_effort`, and `observe_only`
- A supervised observe-only runtime loop is now integrated for live in-game monitoring
- Role-aware parachute priority is available for drogue/main style expansion
- A descending vessel in the simplified simulator transitions through semi and full deploy as expected
- The current simplified descent model lands within Mk16 impact tolerance for the covered scenario

## Behaviors Covered

- Displays `--` for telemetry values that are not ready yet
- Uses short resource labels in telemetry output
- Triggers the auto parachute system when descent conditions are met
- Does not arm parachutes in simulate mode
- Arms parachutes in live mode
- Guarantees a single trigger per parachute in the covered auto-trigger path
- Reports a hold decision while the vessel is still in pre-launch state
- Keeps monitoring until a valid descent phase exists
- Triggers exactly once in a narrow deployment window
- Preserves unrecoverable classification when best-effort policy still allows action
- Suppresses unrecoverable deployment in `strict` mode
- Suppresses deployment entirely in `observe_only` mode while preserving classification
- Formats observe-only runtime status lines for live supervision
- Respects the Mk16 semi-deploy pressure boundary
- Respects the Mk16 full-deploy altitude boundary
- Prevents deployment before activation
- Prevents immediate full deployment before the modeled delay has elapsed
- Loads Mk16 parachute values from YAML configuration
- Loads shared atmosphere and gravity constants from YAML configuration
- Increases atmospheric pressure as a simulated vessel descends
- Transitions the Mk16 through semi and full deploy during a simulated descent
- Lands within Mk16 impact tolerance in the current basic descent simulation
- Resolves drogue/main transition conflicts by deployment priority

## Quality Notes

- Tests are deterministic and run without Kerbal Space Program being open
- Test names follow the outcome-based `should ...` convention
- Test bodies keep the `Given / When / Then` structure for readability and review
- Deployment thresholds are now driven by a structured Mk16 spec, not ad hoc hardcoded values
- A deterministic test-only physics engine is available for repeatable descent scenarios
- A time-aware auto-trigger controller is available for continuous decision testing
- Policy mode is now externalized in YAML rather than hardcoded in controller logic
- A supervised live observe-only loop is now present, but not yet fully cross-validated in live descent campaigns

## Current Risks / Gaps

- No end-to-end test against a live kRPC session
- The modeled full-deploy delay and drag model are engineering assumptions in the current simulation layer
- The current physics engine is intentionally simplified to vertical motion only
- The observe-only live loop is integrated, but still needs practical in-game validation
- No mission-scenario suite yet for alternative chute profiles beyond the current covered cases
- No live autonomous deployment path yet through the new controller

## Recommended Next Step

Run supervised in-game observe-only descent campaigns, compare controller classifications against real flight behavior, and only then consider live autonomous deployment.
