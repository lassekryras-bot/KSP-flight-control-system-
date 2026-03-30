# 🚀 KSP Flight Control System — v0.1 (Linear Thrust Ramp)

A deterministic flight test framework for Kerbal Space Program using a **time-consistent linear throttle ramp**, **velocity-based detection**, and **structured logging + analysis**.

---

## 🎯 Phase 0 Goals
- ✅ Predictable input (linear ramp)
- ✅ Measurable response (vertical velocity)
- ✅ Reliable detection (sustained threshold)
- ✅ Capture liftoff throttle
- ✅ Time-consistent behavior (frame independent)

---

## 🧱 Project Structure
```
src/main/java/flightcontrol/
├── TestRun.java                 # Per-run data model
├── ThrottleRampController.java # Time-based ramp (nanoTime)
├── DetectionSystem.java        # Sustained threshold detection
├── RunLogger.java              # JSON logging
├── FlightController.java       # Orchestrator
├── KRPCClient.java             # kRPC interface (stub)
└── AnalysisTool.java           # Post-run analysis
```

---

## ⚙️ System Loop
1. Ramp starts
2. Throttle increases linearly over time
3. Velocity monitored via kRPC
4. Detection triggers
5. Throttle recorded at detection
6. Ramp stops immediately
7. Run logged to file

---

## 🚀 Quick Start

### Run a Test
```java
FlightController controller = new FlightController(
    0.25,  // ramp rate (throttle/sec)
    2.0,   // velocity threshold (m/s)
    0.5,   // required duration (sec)
    "runs.json"
);

controller.runTest(1);
```

### Analyze Results
```java
AnalysisTool.analyze("runs.json");
```

---

## 🔌 kRPC Integration
Replace stub methods in `KRPCClient.java` with real kRPC calls.

Example direction:
```java
// Initialize once
Connection conn = Connection.newInstance("Flight Control");
SpaceCenter sc = SpaceCenter.newInstance(conn);
Vessel vessel = sc.getActiveVessel();

// Set throttle
vessel.getControl().setThrottle(value);

// Get vertical velocity
return vessel.flight().getVerticalSpeed();
```

---

## 📊 Example Output (runs.json)
```json
{
  "run_id": 1,
  "ramp_rate": 0.25,
  "detection": {
    "time": 2.84,
    "throttle": 0.71,
    "velocity": 3.12
  }
}
```

---

## 🧪 What to Look For
- Consistent **detection throttle** across runs
- Low standard deviation = stable system
- Outliers = investigate timing or detection issues

---

## ⚠️ Design Rules
- Use `System.nanoTime()` for all timing
- No frame-dependent logic
- Immediate ramp stop on detection
- Clean reset between runs

---

## 🧭 Next Steps
- 🔌 Full kRPC integration
- 🔁 Multi-run automation
- 📈 Advanced analysis (CSV, graphs)
- 🤖 Adaptive throttle control

---

## 📜 License
MIT (update as needed)
