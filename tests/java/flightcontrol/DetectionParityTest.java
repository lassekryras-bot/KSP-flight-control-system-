package flightcontrol;

import java.io.BufferedReader;
import java.io.FileReader;
import java.io.IOException;

public class DetectionParityTest {

    public static void main(String[] args) throws Exception {
        String path = args.length > 0 ? args[0] : "tests/fixtures/telemetry_profile.csv";

        DetectionSystem liftoff = new DetectionSystem(0.01, 0.0);
        DetectionSystem ascent = new DetectionSystem(1.0, 0.2);

        Double liftoffTime = null;
        Double ascentTime = null;

        try (BufferedReader reader = new BufferedReader(new FileReader(path))) {
            String line = reader.readLine(); // header
            if (line == null) {
                throw new IllegalStateException("Telemetry fixture is empty");
            }

            double previousTime = 0.0;
            while ((line = reader.readLine()) != null) {
                String[] parts = line.split(",");
                double currentTime = Double.parseDouble(parts[0]);
                double velocity = Double.parseDouble(parts[1]);
                double dt = currentTime - previousTime;
                previousTime = currentTime;

                if (liftoff.update(velocity, dt) && liftoffTime == null) {
                    liftoffTime = currentTime;
                }
                if (ascent.update(velocity, dt) && ascentTime == null) {
                    ascentTime = currentTime;
                }
            }
        } catch (IOException io) {
            throw new RuntimeException("Failed to read fixture: " + path, io);
        }

        assertEqual("liftoff", 0.1, liftoffTime);
        assertEqual("stable_ascent", 0.5, ascentTime);

        System.out.println("Detection parity test passed.");
    }

    private static void assertEqual(String label, double expected, Double actual) {
        if (actual == null || Math.abs(expected - actual) > 1e-9) {
            throw new IllegalStateException(
                "Expected " + label + " at " + expected + " but got " + actual
            );
        }
    }
}
