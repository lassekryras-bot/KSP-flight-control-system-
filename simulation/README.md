# 🚀 KSP Flight Control System

A hybrid **Java + Python** flight control system for Kerbal Space Program using shared YAML configuration, deterministic testing, and real-time kRPC integration.

---

## 📋 Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                   SHARED CONFIG (YAML)                      │
│  ↓ Read by both Java & Python for consistency              │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ☕ JAVA BRAIN                  🐍 PYTHON SIMULATION       │
│  ├─ FlightController            ├─ simulator.py            │
│  ├─ ThrottleRampController      ├─ analysis.py             │
│  ├─ DetectionSystem             ├─ logger.py               │
│  ├─ KRPCClient (Real-time)      └─ config_loader.py       │
│  └─ ConfigLoader.java                                      │
│                                                             │
│  ⬆️  Uses config.yaml                ⬆️  Uses config.yaml   │
│  ⬅️  Control commands      ➜ Data Exchange ➜  Test Results │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 🎯 Key Features

### ✅ Java Brain (Real-time Control)
- **FlightController** - Orchestrates test sequence
- **ThrottleRampController** - Linear throttle control (frame-independent)
- **DetectionSystem** - Event detection with sustained threshold logic
- **KRPCClient** - Real-time communication with Kerbal Space Program
- **ConfigLoader** - YAML configuration reader

### ✅ Python Simulation & Analysis
- **FlightSimulator** - Physics engine for validation testing
- **FlightAnalyzer** - Statistical analysis (mean, std dev, min/max)
- **FlightLogger** - JSON-based data logging
- **config_loader.py** - Shared YAML configuration

### ✅ Shared Configuration
- Single `config.yaml` file read by both Java and Python
- Physics constants, control parameters, vehicle specs
- No code duplication - configure once, run everywhere

---

## 📦 Project Structure

```
KSP-flight-control-system/
├── config.yaml                          # Shared configuration
├── requirements.txt                     # Python dependencies
├── pom.xml                              # Java build configuration
├── .gitignore
│
├── src/
│   ├── main/java/flightcontrol/
│   │   ├── ConfigLoader.java
│   │   ├── FlightController.java
│   │   ├── ThrottleRampController.java
│   │   ├── DetectionSystem.java
│   │   ├── KRPCClient.java
│   │   └── RunLogger.java
│   │
│   └── python/
│       ├── config_loader.py
│       ├── simulator.py
│       ├── analysis.py
│       └── logger.py
│
├── scripts/
│   ├── run_simulation.py
│   └── run_java_control.sh
│
├── data/
│   ├── runs.json
│   └── results.csv
│
└── tests/
    ├── java/
    └── python/
```

---

## 🚀 Quick Start

### Prerequisites
- **Java 11+** (with Maven)
- **Python 3.8+**
- **Kerbal Space Program** (with kRPC for real flights)

### Installation

```bash
# Clone repository
git clone https://github.com/lassekryras-bot/KSP-flight-control-system-.git
cd KSP-flight-control-system-

# Install Python dependencies
pip install -r requirements.txt

# Build Java (optional)
mvn clean package
```

---

## 🧪 Usage

### Python Simulation (Offline Testing)

```bash
python scripts/run_simulation.py
```

Output:
```
=== Flight Test Analysis ===

Run #1: duration=30.0s, altitude=450.23m
Throttle Statistics:
  average: 0.5234
  std_dev: 0.0821
  min: 0.3421
  max: 0.7156
```

### Java Controller (Real KSP Flight)

```bash
bash scripts/run_java_control.sh
```

Requirements:
- Kerbal Space Program running
- kRPC server enabled (`localhost:50000`)
- Active vessel on launch pad

---

## ⚙️ Configuration

Edit `config.yaml`:

```yaml
physics:
  gravity: 9.81
  timestep: 0.02

throttle_ramp:
  ramp_rate: 0.25          # throttle/second

detection:
  liftoff:
    velocity_threshold: 0.01
    sustained_duration: 0.0
  ascent:
    velocity_threshold: 1.0
    sustained_duration: 0.2

control_parameters:
  kp: 0.4                  # Proportional gain
  kd: 0.3                  # Derivative gain

vehicle_parts:
  engine:
    thrust: 200000         # Newtons
```

---

## 📊 Analysis

View results:

```python
from src.python.analysis import FlightAnalyzer

analyzer = FlightAnalyzer("data/runs.json")
analyzer.print_summary()
analyzer.export_csv("data/results.csv")
```

---

## 🔌 kRPC Integration

### Setup
1. Install kRPC mod in KSP
2. Enable server (Settings → kRPC → Enable)
3. Default: `localhost:50000`

### Usage
```java
KRPCClient.connect("localhost", 50000);
KRPCClient.setThrottle(0.75);
double velocity = KRPCClient.getVerticalVelocity();
KRPCClient.disconnect();
```

---

## 📈 How It Works

**Throttle Ramp**
```
throttle = rampRate × time
Example: 0.25/sec → full throttle in 4 seconds
```

**Detection System**
```
Trigger when velocity ≥ threshold for sustained_duration
Drop below threshold = reset timer
```

**PD Control**
```
error = target_altitude - current_altitude
throttle = hover + (Kp × error) - (Kd × velocity)
```

---

## 🤝 Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature/name`
3. Make changes
4. Test with Python sim + Java tests
5. Submit PR

---

## 🐛 Troubleshooting

| Issue | Solution |
|-------|----------|
| ConfigLoader file not found | Ensure `config.yaml` in root |
| kRPC connection failed | Check KSP is running, server enabled |
| No output files | Create `data/` directory |
| Java compile error | Install Java 11+, Maven |

---

## 📚 Resources

- [Kerbal Space Program](https://www.kerbalspaceprogram.com/)
- [kRPC Documentation](https://krpc.github.io/)
- [YAML Specification](https://yaml.org/)

---

## 📜 License

MIT License

---

## 👨‍💻 Author

**Lasse Kry Ras** (lassekryras-bot)

---

## 🎓 Key Learnings

- **Frame-independent timing** with `System.nanoTime()`
- **Sustained threshold detection** pattern
- **Shared configuration** across languages
- **PD control** implementation
- **Physics simulation** basics

---

## 🗺️ Roadmap

- [ ] Adaptive thrust control
- [ ] Multi-stage rocket support
- [ ] Advanced aerodynamics
- [ ] Real-time visualization dashboard
- [ ] Machine learning parameter tuning
- [ ] Hardware-in-the-loop support

---

## 💬 Questions?

Open an issue on GitHub!
