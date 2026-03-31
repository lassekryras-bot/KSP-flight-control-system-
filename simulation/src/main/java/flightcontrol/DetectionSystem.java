package flightcontrol;

public class DetectionSystem {

    private double velocityThreshold;
    private double requiredDuration;

    private long thresholdStartNano = -1;
    private boolean detected = false;

    public DetectionSystem(double velocityThreshold, double requiredDuration) {
        this.velocityThreshold = velocityThreshold;
        this.requiredDuration = requiredDuration;
    }

    public boolean update(double velocity) {
        long now = System.nanoTime();

        if (velocity >= velocityThreshold) {
            if (thresholdStartNano < 0) {
                thresholdStartNano = now;
            }

            double duration = (now - thresholdStartNano) / 1e9;

            if (duration >= requiredDuration) {
                detected = true;
                return true;
            }

        } else {
            thresholdStartNano = -1;
        }

        return false;
    }

    public boolean isDetected() {
        return detected;
    }

    public void reset() {
        thresholdStartNano = -1;
        detected = false;
    }
}
