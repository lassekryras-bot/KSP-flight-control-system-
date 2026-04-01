.PHONY: test test-python test-java

test: test-python test-java

test-python:
	python -m unittest discover -s tests/python -p 'test_*.py'

test-java:
	javac java/ConfigLoader.java java/FlightControllerV15.java tests/java/FlightControllerV15BDDTest.java
	java -ea -cp .:java:tests/java FlightControllerV15BDDTest
