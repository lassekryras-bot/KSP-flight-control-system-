// v15 Flight Controller (Guidance + Control + Detection)

public class FlightControllerV15 {

    public enum Mode {
        GROUND,
        TAKEOFF,
        FLYING,
        DESCENT,
        LANDING,
        FREE_FALL
    }

    private static final double G = 9.81;
    private static final double KP = 0.4;
    private static final double KD = 0.3;

    private Mode mode = null;

    private double time = 0;
    private double altitude = 0;
    private double velocity = 0;

    private double mass;
    private double thrust;

    private double throttle = 0.0;
    private double prevThrottle = 0.0;

    public FlightControllerV15(double mass, double thrust) {
        this.mass = mass;
        this.thrust = thrust;
    }

    public void update(double alt, double vel, double dt) {
        this.altitude = alt;
        this.velocity = vel;
        this.time += dt;

        updateMode();
        updateControl();
    }

    // ----------------------------
    // GUIDANCE
    // ----------------------------

    private double computeBurnAltitude() {
        double maxAcc = (thrust / mass) - G;
        if (maxAcc <= 0) return Double.MAX_VALUE;
        return (velocity * velocity) / (2 * maxAcc);
    }

    private boolean shouldStartLanding() {
        double burnAlt = computeBurnAltitude();
        return altitude <= burnAlt;
    }

    // ----------------------------
    // MODE
    // ----------------------------

    private void setMode(Mode newMode) {
        if (mode != newMode) {
            System.out.println("[t=" + String.format("%.2f", time) + "] " + mode + " → " + newMode);
            mode = newMode;
        }
    }

    private void updateMode() {
        if (mode == null) {
            setMode(Mode.GROUND);
            return;
        }

        switch (mode) {
            case GROUND:
                setMode(Mode.TAKEOFF);
                break;

            case TAKEOFF:
                if (altitude > 200) setMode(Mode.FLYING);
                break;

            case FLYING:
                if (velocity < 0) setMode(Mode.DESCENT);
                break;

            case DESCENT:
                if (shouldStartLanding()) setMode(Mode.LANDING);
                break;

            case LANDING:
                if (altitude <= 0) setMode(Mode.GROUND);
                break;

            case FREE_FALL:
                break;
        }
    }

    // ----------------------------
    // CONTROL
    // ----------------------------

    private double computeThrottle(double targetV) {
        double hover = (mass * G) / thrust;
        double error = targetV - velocity;
        double raw = hover + (KP * error) - (KD * velocity);
        return clamp(raw, 0.0, 1.0);
    }

    private double ramp(double current, double target, double rate) {
        return current + (target - current) * rate;
    }

    private void updateControl() {
        double targetThrottle = 0.0;

        switch (mode) {
            case TAKEOFF:
                targetThrottle = 1.0;
                break;

            case LANDING:
                double targetV = (altitude > 10) ? -2 : -0.5;
                targetThrottle = computeThrottle(targetV);
                break;

            default:
                targetThrottle = 0.0;
        }

        throttle = ramp(prevThrottle, targetThrottle, 0.2);
        prevThrottle = throttle;
    }

    private double clamp(double v, double min, double max) {
        return Math.max(min, Math.min(max, v));
    }

    public double getThrottle() {
        return throttle;
    }
}
