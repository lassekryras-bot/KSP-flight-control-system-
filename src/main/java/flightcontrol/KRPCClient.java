package flightcontrol;

/**
 * Lightweight kRPC integration shim.
 *
 * <p>This class now includes game-mode aware throttle behavior so integration
 * can respect common KSP save constraints while still being runnable offline.
 */
public final class KRPCClient {

    public enum GameMode {
        SANDBOX,
        SCIENCE,
        CAREER;

        public static GameMode fromString(String value) {
            if (value == null || value.isBlank()) {
                return SANDBOX;
            }

            try {
                return GameMode.valueOf(value.trim().toUpperCase());
            } catch (IllegalArgumentException ignored) {
                return SANDBOX;
            }
        }
    }

    private static GameMode gameMode = GameMode.SANDBOX;
    private static boolean careerAutomationUnlocked = true;

    private KRPCClient() {
    }

    public static void setGameMode(GameMode mode) {
        gameMode = (mode == null) ? GameMode.SANDBOX : mode;
    }

    public static GameMode getGameMode() {
        return gameMode;
    }

    /**
     * Career saves may block control authority until comms/probe-control rules are met.
     */
    public static void setCareerAutomationUnlocked(boolean unlocked) {
        careerAutomationUnlocked = unlocked;
    }

    public static void setThrottle(double value) {
        double throttle = Math.max(0.0, Math.min(1.0, value));

        if (gameMode == GameMode.CAREER && !careerAutomationUnlocked) {
            throttle = 0.0;
        }

        // TODO: integrate with kRPC Java client.
        // Example with real client objects:
        // vessel.getControl().setThrottle((float) throttle);
    }

    public static double getVerticalVelocity() {
        // TODO: integrate with kRPC Java client.
        // Example: return vessel.flight(vessel.getSurfaceReferenceFrame()).getVerticalSpeed();
        return Math.random() * 5; // placeholder for offline runs
    }
}
