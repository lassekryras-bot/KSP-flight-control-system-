public class FlightControllerV15BDDTest {

    private static void assertTrue(boolean condition, String message) {
        if (!condition) {
            throw new AssertionError(message);
        }
    }

    private static void assertNear(double expected, double actual, double tolerance, String message) {
        if (Math.abs(expected - actual) > tolerance) {
            throw new AssertionError(message + " expected=" + expected + " actual=" + actual);
        }
    }

    private static void givenNewController_whenFirstUpdate_thenThrottleStaysZeroInGroundMode() {
        // Given: a freshly initialized controller
        FlightControllerV15 controller = new FlightControllerV15(4500.0, 167000.0);

        // When: first update is processed
        controller.update(0.0, 0.0, 0.02);

        // Then: controller is in GROUND transition cycle so throttle remains 0
        assertNear(0.0, controller.getThrottle(), 1e-9, "Throttle should be zero on first update");
    }

    private static void givenGroundTransition_whenSecondUpdate_thenThrottleRampsTowardTakeoff() {
        // Given: a controller that already performed initial update
        FlightControllerV15 controller = new FlightControllerV15(4500.0, 167000.0);
        controller.update(0.0, 0.0, 0.02);

        // When: second update executes GROUND -> TAKEOFF
        controller.update(0.0, 0.0, 0.02);

        // Then: throttle ramps by smoothing factor (0.2) toward full takeoff throttle
        assertNear(0.2, controller.getThrottle(), 1e-9, "Throttle should ramp to 0.2 on TAKEOFF entry");
    }

    private static void givenTakeoffThrottle_whenThirdUpdate_thenThrottleContinuesSmoothing() {
        // Given: a controller already in TAKEOFF with prior throttle 0.2
        FlightControllerV15 controller = new FlightControllerV15(4500.0, 167000.0);
        controller.update(0.0, 0.0, 0.02);
        controller.update(0.0, 0.0, 0.02);

        // When: third update keeps TAKEOFF target at 1.0
        controller.update(0.0, 0.0, 0.02);

        // Then: throttle continues smoothing: 0.2 + (1.0 - 0.2) * 0.2 = 0.36
        assertNear(0.36, controller.getThrottle(), 1e-9, "Throttle should continue smoothing toward 1.0");
        assertTrue(controller.getThrottle() > 0.2, "Throttle should increase during takeoff");
    }

    public static void main(String[] args) {
        givenNewController_whenFirstUpdate_thenThrottleStaysZeroInGroundMode();
        givenGroundTransition_whenSecondUpdate_thenThrottleRampsTowardTakeoff();
        givenTakeoffThrottle_whenThirdUpdate_thenThrottleContinuesSmoothing();
        System.out.println("All Given-When-Then Java tests passed.");
    }
}
