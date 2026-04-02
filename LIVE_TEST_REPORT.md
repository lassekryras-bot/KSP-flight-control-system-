# Live Test Report

Date: 2026-04-02
Project: KSP Flight Control System
Test type: Supervised in-game observe-only validation
Scope: Live kRPC connection, telemetry integrity, vessel reacquisition, and continuous auto-trigger monitoring

## Executive Summary

Live in-game validation progressed in two passes.

- Pass 1 exposed a telemetry fault: live `vertical_speed` remained flat at `0.0 m/s`
- A runtime fallback vertical-speed estimate was then implemented from altitude delta over time
- Pass 2 validated live ascent/descent detection and monitor state transitions
- Remaining blocker: the parachute is still being armed by craft staging, so deployment timing is not yet independently validated

- Status: Partial pass, improved
- Environment: Kerbal Space Program with kRPC, Windows, Python 3.10.6
- Mode: `--parachute-mode off --auto-trigger-policy observe_only`
- Automation level: observe-only, no live parachute action

## Management Summary

- The live runtime shell is working
- The telemetry fault was detected before any deployment authority was granted
- The fallback vertical-speed logic corrected live ascent/descent recognition
- The monitor now exits `monitoring` and produces live classification changes
- The next remaining issue is test setup contamination, not controller blindness

Operational conclusion:

The system is now live-monitoring-capable, but not yet ready for autonomous deployment authority because the test craft still arms the parachute outside controller control.

## Test Command

```powershell
.\.venv\Scripts\python.exe main.py --parachute-mode off --auto-trigger-policy observe_only
```

## Phase Summary

### Phase 1: Telemetry Anomaly Discovery

- kRPC connection succeeded
- Scene transitions were handled correctly
- Telemetry streamed through launch, coast, descent, and landing
- `vertical_speed` remained `0.0 m/s` despite obvious altitude and speed changes
- The monitor remained stuck in:
  - classification: `monitoring`
  - window: `closed`
  - reason: `Waiting for a valid descent phase.`

Result:

- Telemetry shell validated
- Descent detection not validated
- Progress halted correctly

### Phase 2: Fallback Vertical-Speed Validation

- Runtime fallback vertical speed was derived from altitude change over time
- Live ascent showed positive `VSpd`
- Near apogee `VSpd` approached zero
- Live descent showed negative `VSpd`
- The monitor exited `monitoring` and entered active evaluation states

Representative observed behavior:

- ascent: `VSpd` rose above `200 m/s`
- near apogee: `VSpd` dropped toward single digits
- descent: `VSpd` became strongly negative, including values below `-150 m/s`
- monitor output changed to:
  - `safe | window: open`
  - later `safe | window: closed`
  - then back to `safe | window: open`

Result:

- Live descent detection validated
- Live classification transition validated
- Policy-controlled observe-only monitoring validated

## What Worked

- kRPC connection established successfully
- KSP scene monitoring behaved correctly across `space_center`, `editor_vab`, and `flight`
- Vessel acquisition in the flight scene worked
- Telemetry output remained stable throughout the flights
- Resource and mass telemetry updated during booster burn
- The observe-only monitor initialized and reported its policy correctly
- The runtime fallback restored live vertical-speed usefulness
- The controller now detects ascent, apogee transition, and descent in live flight

## Key Findings

### Finding 1: Sensor Integrity Fault Was Real

The original live `vertical_speed` signal was not trustworthy for this craft/test profile.

Observed mismatch:

- altitude changed significantly
- total speed changed significantly
- reported `vertical_speed` remained `0.0 m/s`

### Finding 2: Fallback Reconstruction Worked

The derived vertical-speed path corrected the fault well enough for the observe-only controller to function during live flight.

This validates:

- FR-17: derived vertical velocity from altitude over time
- part of FR-18: telemetry validation and substitution when the live signal is stale

### Finding 3: Deployment Timing Is Still Not Cleanly Tested

The log still contains:

- `Parachutes are already armed or deployed.`

That means the craft or staging setup is still arming the parachute before the controller can demonstrate an independent deployment decision.

## Assessment

Current maturity:

- automated simulation and controller tests: strong
- live observe-only integration: present
- live descent-state detection: validated
- live deployment timing validation: not yet clean
- live autonomous recovery: not ready

## Risk Statement

The highest current operational risk is no longer telemetry blindness. The current risk is test contamination: the parachute is being armed by the vessel setup, preventing a clean measurement of when the controller alone would choose deployment.

## Recommended Next Step

Run one more supervised observe-only flight with a corrected craft/staging setup:

- keep one parachute only
- do not arm the parachute during launch staging
- place the parachute in a later stage or otherwise keep it untouched during ascent

Acceptance criteria for the next run:

- monitor leaves `monitoring`
- classification changes occur during descent
- no `already armed or deployed` message before the trigger-worthy moment
- a clean controller-only deploy-worthy state can be identified

## Management Recommendation

Do not approve live autonomous parachute deployment yet.

Approve one additional supervised observe-only validation cycle with corrected parachute staging so deployment timing can be verified without craft-side interference.
