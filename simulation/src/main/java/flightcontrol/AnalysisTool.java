package flightcontrol;

import java.io.BufferedReader;
import java.io.FileReader;
import java.util.ArrayList;
import java.util.List;

/**
 * Simple analysis tool to evaluate throttle consistency.
 */
public class AnalysisTool {

    public static void analyze(String filePath) {
        List<Double> throttles = new ArrayList<>();

        try (BufferedReader reader = new BufferedReader(new FileReader(filePath))) {
            String line;
            while ((line = reader.readLine()) != null) {
                // Very naive parsing (works with our format)
                int idx = line.indexOf("\"throttle\":");
                if (idx != -1) {
                    String sub = line.substring(idx + 11);
                    String value = sub.split(",|}")[0];
                    throttles.add(Double.parseDouble(value));
                }
            }
        } catch (Exception e) {
            e.printStackTrace();
        }

        if (throttles.isEmpty()) {
            System.out.println("No data.");
            return;
        }

        double sum = 0;
        for (double t : throttles) sum += t;
        double avg = sum / throttles.size();

        double variance = 0;
        for (double t : throttles) variance += Math.pow(t - avg, 2);
        variance /= throttles.size();

        double stdDev = Math.sqrt(variance);

        System.out.println("Runs: " + throttles.size());
        System.out.println("Average throttle: " + avg);
        System.out.println("Std deviation: " + stdDev);
    }
}
