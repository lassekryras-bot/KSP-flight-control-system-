# Policy Decision

Date: 2026-04-02
Project: KSP Flight Control System
Topic: Unrecoverable parachute deployment policy

## Decision Question

When the system classifies a descent as `unrecoverable`, should it still trigger parachute deployment as a last-chance best effort?

## Current Classification Model

- `safe`: deployment is inside the normal operating window
- `risky`: deployment is still possible, but with reduced safety margin
- `unrecoverable`: the safe deployment window is considered missed

## Policy Options

### Option 1: Strict Safety

The system does not trigger parachute deployment in `unrecoverable` state.
It reports failure only.

Implications:

- Preserves hard-rule compliance
- Avoids false confidence in impossible recovery conditions
- May give up on rare last-chance recoveries

### Option 2: Best-Effort Recovery

The system still triggers parachute deployment if a parachute is available, even in `unrecoverable` state.
The system still reports the descent as `unrecoverable`.

Implications:

- Maximizes last-chance survival attempts
- Keeps failure state visible
- Allows deployment outside the preferred safety envelope

### Option 3: Mode-Dependent Policy

The system behavior is configurable.
For example:

- `strict`: no deployment in `unrecoverable`
- `best_effort`: deploy anyway in `unrecoverable`
- `observe_only`: classify but do not act

Implications:

- Supports testing and mission-specific tuning
- Adds one more operational configuration choice
- Keeps the software flexible while policy is still being defined

## Why This Decision Matters

- It changes real mission behavior
- It affects how failure is reported and interpreted
- It determines whether the controller prioritizes rule compliance or last-chance survival

## Engineering Recommendation

- `risky` should trigger with warning
- `unrecoverable` should be a management policy choice
- Best default for development is `mode-dependent policy`

## Recommended Management Prompt

"In an unrecoverable descent, should the system preserve safety rules strictly, or attempt a final best-effort deployment while explicitly reporting likely mission loss?"
