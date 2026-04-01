.PHONY: smoke-test python-smoke java-smoke

smoke-test: python-smoke java-smoke

python-smoke:
	python -m py_compile scripts/run_simulation.py analysis/stats.py analysis/plot.py
	python scripts/run_simulation.py --data data/runs.csv

java-smoke:
	javac --release 11 FlightController.java java/ConfigLoader.java java/FlightControllerV15.java
