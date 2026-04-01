package flightcontrol;

public class DetectionSystem {

    private final double velocityThreshold;
    private final double requiredDuration;

    private long lastUpdateNano = -1;
    private double thresholdTimerSeconds = 0.0;
    private boolean detected = false;

    public DetectionSystem(double velocityThreshold, double requiredDuration) {
        this.velocityThreshold = velocityThreshold;
        this.requiredDuration = requiredDuration;
    }

    public boolean update(double velocity) {
        long now = System.nanoTime();
        double dt = 0.0;
        if (lastUpdateNano > 0) {
            dt = (now - lastUpdateNano) / 1e9;
        }
        lastUpdateNano = now;
        return update(velocity, dt);
    }

    public boolean update(double velocity, double dtSeconds) {
        if (detected) {
            return false;
        }

        if (velocity >= velocityThreshold) {
            thresholdTimerSeconds += Math.max(0.0, dtSeconds);
            if (thresholdTimerSeconds >= requiredDuration) {
                detected = true;
                return true;
            }
        } else {
            thresholdTimerSeconds = 0.0;
        }

        return false;
    }

    public boolean isDetected() {
        return detected;
    }

    public void reset() {
        thresholdTimerSeconds = 0.0;
        lastUpdateNano = -1;
        detected = false;
    }
}
