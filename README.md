# 🚀 KSP Flight Control System

A hybrid Java + Python sandbox for Kerbal Space Program-style flight control experiments.

This repository currently focuses on:
- Java controller logic (`FlightControllerV15`) with YAML-driven tuning.
- Python analysis utilities for reviewing captured run data.

## 📦 Repository layout

```text
KSP-flight-control-system-/
├── FlightController.java              # Simple Java demo controller
├── java/
│   ├── ConfigLoader.java              # Minimal YAML parser/loader
│   └── FlightControllerV15.java       # Guidance + mode + throttle controller
├── scripts/
│   └── run_simulation.py              # Offline analysis entrypoint
├── analysis/
│   ├── stats.py                       # Statistical summary (mean/stddev/min/max)
│   └── plot.py                        # Plot helper for run CSV files
├── data/
│   └── runs.csv                       # Example run dataset
├── config.yaml                        # Shared parameters for controller tuning
└── requirements.txt                   # Python dependencies
```

## 🚀 Quick start

### Python analysis

```bash
python scripts/run_simulation.py
```

Optional custom data path:

```bash
python scripts/run_simulation.py --data data/runs.csv
```

### Java compile smoke check

```bash
javac FlightController.java java/ConfigLoader.java java/FlightControllerV15.java
```

## ⚙️ Config keys used by `FlightControllerV15`

- `control.kp`
- `control.kd`
- `control.smoothing`
- `guidance.landing.high_altitude_velocity`
- `guidance.landing.low_altitude_velocity`
- `guidance.landing.switch_altitude`
- `state_transitions.takeoff_to_ascent_altitude`
- `state_transitions.descent_to_landing_altitude`

## 📊 Analysis notes

`analysis/stats.py` expects a CSV with these columns:
- `run_id`
- `ramp_rate`
- `time`
- `throttle`
- `velocity`

`scripts/run_simulation.py` validates these headers before printing summary output.

## ℹ️ Notes

- `archive/` contains historical/legacy experiment scripts.
- `simulation/` contains mirrored experimentation artifacts.
