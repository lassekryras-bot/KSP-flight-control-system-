package flightcontrol;

public class ThrottleRampController {

    private double rampRate;
    private long startTimeNano;
    private boolean active = false;

    public ThrottleRampController(double rampRate) {
        this.rampRate = rampRate;
    }

    public void start() {
        this.startTimeNano = System.nanoTime();
        this.active = true;
    }

    public void stop() {
        this.active = false;
    }

    public double getThrottle() {
        if (!active) return 0.0;

        double elapsed = (System.nanoTime() - startTimeNano) / 1e9;
        double throttle = rampRate * elapsed;

        return Math.min(throttle, 1.0);
    }

    public boolean isActive() {
        return active;
    }
}
