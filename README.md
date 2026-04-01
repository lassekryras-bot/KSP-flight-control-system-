# 🚀 KSP Flight Control System

A lightweight **Java + Python** flight-control playground for Kerbal Space Program concepts using shared YAML configuration.

## 📦 Current Repository Layout

```text
KSP-flight-control-system-/
├── src/main/java/flightcontrol/       # Java controller + support classes
├── src/python/                        # Python simulator + support classes
├── tests/
│   ├── fixtures/telemetry_profile.csv # Shared telemetry input for parity tests
│   ├── java/flightcontrol/            # Java parity test harness
│   └── python/                        # Pytest parity test
├── scripts/run_simulation.py          # Offline CSV-based analysis runner
├── analysis/                          # Stats + plotting utilities
├── archive/                           # Historical single-script experiments
├── config.yaml                        # Shared config used by simulator/controller
└── requirements.txt                   # Python dependencies
```

## 🚀 Quick Start

### Python setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt pytest
```

### Python simulator run

```bash
python scripts/run_simulation.py
```

### Parachute envelope mapping sweep

```bash
python scripts/run_parachute_envelope.py
```

This command runs the mandatory deployment-altitude scenario matrix and prints:

- deployment altitude + velocity,
- time/velocity at full deployment,
- touchdown velocity,
- outcome classification using the mission acceptance metric (`≤ 6 m/s` safe touchdown).

Optional custom input file:

```bash
python scripts/run_simulation.py --data data/runs.csv
```

### Java compile check

```bash
javac src/main/java/flightcontrol/*.java
```

## ✅ Cross-language parity tests (same telemetry input)

The repo now includes one shared telemetry fixture (`tests/fixtures/telemetry_profile.csv`) that both Python and Java tests consume.

### Run Python parity test

```bash
pytest tests/python/test_detection_parity.py
```

### Run Java parity test

```bash
mkdir -p out
javac -d out src/main/java/flightcontrol/DetectionSystem.java tests/java/flightcontrol/DetectionParityTest.java
java -cp out flightcontrol.DetectionParityTest tests/fixtures/telemetry_profile.csv
```

## 🛰️ Option: “scooped” telemetry from KSP for Java tests

If you want Java tests that replay telemetry collected from the game (similar to the Python simulator flow), the recommended pattern is:

1. Record telemetry from kRPC to CSV (e.g., `time_s,vertical_velocity_mps`).
2. Keep that CSV under `tests/fixtures/` as a deterministic test input.
3. Run the Java parity test harness against that CSV.
4. Run the Python parity test against the same CSV and compare event timings.

This keeps both stacks deterministic and lets you validate controller logic without running KSP live in every test.


## 🎮 kRPC with Java (live KSP)

If you want to control **live KSP from Java** (instead of only replaying CSV fixtures), follow this flow:

1. Install the kRPC plugin in KSP (GitHub/SpaceDock/CKAN).
2. Launch KSP, load a save, open the kRPC window, and click **Start server**.
3. Keep protocol set to **Protobuf over TCP**.
4. Use `localhost` while your Java app runs on the same machine as KSP.
5. Keep default ports unless you have conflicts:
   - RPC: `50000`
   - Stream: `50001`

### Java client setup (accurate kRPC packaging)

Per the kRPC Java docs, the `krpc-java` client itself is distributed as a jar from GitHub releases (not as a normal Maven Central dependency).

1. Download these jars:
   - `krpc-java-<version>.jar` from kRPC GitHub releases
   - `protobuf-java` jar
   - `javatuples` jar
2. Put them in a local folder such as `libs/`.

#### Gradle example (local jars)

```gradle
dependencies {
    implementation files('libs/krpc-java-0.5.4.jar')
    implementation files('libs/protobuf-java-3.4.0.jar')
    implementation files('libs/javatuples-1.2.jar')
}
```

#### Maven example (install local jars once, then depend normally)

```bash
mvn install:install-file -Dfile=libs/krpc-java-0.5.4.jar -DgroupId=io.krpc -DartifactId=krpc-java -Dversion=0.5.4 -Dpackaging=jar
mvn install:install-file -Dfile=libs/javatuples-1.2.jar -DgroupId=org.javatuples -DartifactId=javatuples -Dversion=1.2 -Dpackaging=jar
```

`protobuf-java` can be pulled directly from Maven Central in your `pom.xml`.

### Minimal Java “hello vessel” example

A ready-to-run file is included at `examples/java/HelloKrpc.java`.

Compile/run manually with local jars:

```bash
javac -cp "libs/krpc-java-0.5.4.jar:libs/protobuf-java-3.4.0.jar:libs/javatuples-1.2.jar" examples/java/HelloKrpc.java
java -cp ".:examples/java:libs/krpc-java-0.5.4.jar:libs/protobuf-java-3.4.0.jar:libs/javatuples-1.2.jar" HelloKrpc
```

If this prints your active vessel name, your Java client is connected correctly.

### Troubleshooting checklist

- kRPC server window/icon in KSP is green.
- Java app and KSP point to the same host/ports.
- Firewall allows local TCP traffic for KSP and Java.
- If connection prompts appear in KSP, allow the Java client.
- Confirm you are running against a loaded flight/save (not only the KSP main menu).

## ⚙️ Configuration

The Python simulator reads from `config.yaml` using `src/python/config_loader.py`. Java `DetectionSystem` parity tests are currently fixture-driven and do not require YAML parsing.

## ℹ️ Notes

- `archive/` contains historical experiments and legacy versions.
- `simulation/` mirrors some files for experimentation.
