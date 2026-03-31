// v15 Flight Controller (Guidance + Control + Detection)

import java.util.Map;

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

    private final double kp;
    private final double kd;
    private final double smoothing;

    private final double landingHighAltitudeVelocity;
    private final double landingLowAltitudeVelocity;
    private final double landingSwitchAltitude;
    private final double takeoffToAscentAltitude;
    private final double descentToLandingAltitude;

    private Mode mode = null;

    private double time = 0;
    private double altitude = 0;
    private double velocity = 0;

    private final double mass;
    private final double thrust;

    private double throttle = 0.0;
    private double prevThrottle = 0.0;

    public FlightControllerV15(double mass, double thrust) {
        this.mass = mass;
        this.thrust = thrust;

        Map<String, Object> config = requireMap(ConfigLoader.load("config.yaml"), "root");
        Map<String, Object> control = requireMap(config.get("control"), "control");
        Map<String, Object> guidance = requireMap(config.get("guidance"), "guidance");
        Map<String, Object> landing = requireMap(guidance.get("landing"), "guidance.landing");
        Map<String, Object> transitions = requireMap(config.get("state_transitions"), "state_transitions");

        this.kp = requireDouble(control, "kp", "control");
        this.kd = requireDouble(control, "kd", "control");
        this.smoothing = requireDouble(control, "smoothing", "control");

        this.landingHighAltitudeVelocity =
                requireDouble(landing, "high_altitude_velocity", "guidance.landing");
        this.landingLowAltitudeVelocity =
                requireDouble(landing, "low_altitude_velocity", "guidance.landing");
        this.landingSwitchAltitude =
                requireDouble(landing, "switch_altitude", "guidance.landing");

        this.takeoffToAscentAltitude =
                requireDouble(transitions, "takeoff_to_ascent_altitude", "state_transitions");
        this.descentToLandingAltitude =
                requireDouble(transitions, "descent_to_landing_altitude", "state_transitions");
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
        return altitude <= Math.max(burnAlt, descentToLandingAltitude);
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
                if (altitude > takeoffToAscentAltitude) setMode(Mode.FLYING);
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
        double raw = hover + kp * error - kd * velocity;
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
                double targetV = (altitude > landingSwitchAltitude)
                        ? landingHighAltitudeVelocity
                        : landingLowAltitudeVelocity;
                targetThrottle = computeThrottle(targetV);
                break;

            default:
                targetThrottle = 0.0;
        }

        throttle = ramp(prevThrottle, targetThrottle, smoothing);
        prevThrottle = throttle;
    }

    private double clamp(double v, double min, double max) {
        return Math.max(min, Math.min(max, v));
    }

    @SuppressWarnings("unchecked")
    private static Map<String, Object> requireMap(Object value, String path) {
        if (!(value instanceof Map<?, ?> rawMap)) {
            throw new IllegalArgumentException("Missing or invalid map at config path: " + path);
        }

        for (Map.Entry<?, ?> entry : rawMap.entrySet()) {
            if (!(entry.getKey() instanceof String)) {
                throw new IllegalArgumentException("Non-string key found in config map: " + path);
            }
        }

        return (Map<String, Object>) rawMap;
    }

    private static double requireDouble(Map<String, Object> map, String key, String path) {
        Object value = map.get(key);
        if (!(value instanceof Number number)) {
            throw new IllegalArgumentException(
                    "Missing or non-numeric value at config path: " + path + "." + key);
        }
        return number.doubleValue();
    }

    public double getThrottle() {
        return throttle;
    }
}
