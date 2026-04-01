.PHONY: smoke-test python-smoke java-smoke test test-verbose python-test java-test

smoke-test: python-smoke java-smoke

python-smoke:
	python -m py_compile scripts/run_simulation.py analysis/stats.py analysis/plot.py
	python scripts/run_simulation.py --data data/runs.csv

java-smoke:
	javac --release 11 FlightController.java java/ConfigLoader.java java/FlightControllerV15.java

test: python-test java-test

test-verbose:
	@echo "=== Python tests (verbose) ==="
	pytest -vv -s tests/python
	@echo "=== Java detection parity test (verbose) ==="
	mkdir -p out
	javac -d out src/main/java/flightcontrol/DetectionSystem.java tests/java/flightcontrol/DetectionParityTest.java
	java -cp out flightcontrol.DetectionParityTest tests/fixtures/telemetry_profile.csv --verbose

python-test:
	pytest tests/python

java-test:
	mkdir -p out
	javac -d out src/main/java/flightcontrol/DetectionSystem.java tests/java/flightcontrol/DetectionParityTest.java
	java -cp out flightcontrol.DetectionParityTest tests/fixtures/telemetry_profile.csv
