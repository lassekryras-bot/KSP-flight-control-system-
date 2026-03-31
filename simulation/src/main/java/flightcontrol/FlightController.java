package flightcontrol;

/**
 * Orchestrates the full test loop:
 * - Starts ramp
 * - Monitors detection
 * - Stops ramp
 * - Logs result
 */
public class FlightController {

    private ThrottleRampController ramp;
    private DetectionSystem detection;
    private RunLogger logger;

    public FlightController(double rampRate, double velocityThreshold, double duration, String logFile) {
        this.ramp = new ThrottleRampController(rampRate);
        this.detection = new DetectionSystem(velocityThreshold, duration);
        this.logger = new RunLogger(logFile);
    }

    public void runTest(int runId) {
        TestRun run = new TestRun(runId, ramp.getThrottle());

        run.start();
        ramp.start();

        while (true) {
            double throttle = ramp.getThrottle();

            // Send throttle to KRPC
            KRPCClient.setThrottle(throttle);

            double velocity = KRPCClient.getVerticalVelocity();

            if (detection.update(velocity)) {
                run.recordDetection(throttle, velocity);
                ramp.stop();
                logger.log(run);
                break;
            }

            sleep(10);
        }

        detection.reset();
    }

    private void sleep(int ms) {
        try {
            Thread.sleep(ms);
        } catch (InterruptedException ignored) {}
    }
}
