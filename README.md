# 🚀 KSP Flight Control System

A lightweight **Java + Python** flight-control playground for Kerbal Space Program concepts using shared YAML configuration.

## 📦 Current Repository Layout

```text
KSP-flight-control-system-/
├── FlightController.java              # Simple Java demo controller
├── java/
│   ├── ConfigLoader.java              # Minimal YAML loader
│   └── FlightControllerV15.java       # Config-driven guidance/control logic
├── scripts/
│   └── run_simulation.py              # Offline CSV-based analysis runner
├── analysis/
│   ├── stats.py                       # Basic statistical summary
│   └── plot.py                        # Quick plotting helper
├── data/
│   └── runs.csv                       # Sample run data
├── config.yaml                        # Shared config used by Java controller
└── requirements.txt                   # Python dependencies
```

## 🚀 Quick Start

### Python offline analysis

```bash
python scripts/run_simulation.py
```

Optional custom input file:

```bash
python scripts/run_simulation.py --data data/runs.csv
```

### Java compile check

```bash
javac FlightController.java java/ConfigLoader.java java/FlightControllerV15.java
```

## ⚙️ Configuration

The Java `FlightControllerV15` currently reads these config sections from `config.yaml`:

- `control.kp`, `control.kd`, `control.smoothing`
- `guidance.landing.high_altitude_velocity`
- `guidance.landing.low_altitude_velocity`
- `guidance.landing.switch_altitude`
- `state_transitions.takeoff_to_ascent_altitude`
- `state_transitions.descent_to_landing_altitude`

## 📊 Analysis utilities

- `analysis/stats.py` prints average/stddev/min/max throttle.
- `analysis/plot.py` plots throttle over runs and histogram distribution.

## ℹ️ Notes

- `archive/` contains historical experiments and legacy versions.
- `simulation/` mirrors some files for experimentation.
