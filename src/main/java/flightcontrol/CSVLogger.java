package flightcontrol;

import java.io.FileWriter;
import java.io.IOException;

/**
 * Writes run data to CSV for external analysis (Python, Excel, etc.)
 */
public class CSVLogger {

    private String filePath;
    private boolean headerWritten = false;

    public CSVLogger(String filePath) {
        this.filePath = filePath;
    }

    public void log(TestRun run) {
        try (FileWriter writer = new FileWriter(filePath, true)) {

            if (!headerWritten) {
                writer.write("run_id,ramp_rate,time,throttle,velocity\n");
                headerWritten = true;
            }

            if (run.detection != null) {
                writer.write(
                        run.runId + "," +
                        run.rampRate + "," +
                        run.detection.time + "," +
                        run.detection.throttle + "," +
                        run.detection.velocity + "\n"
                );
            }

        } catch (IOException e) {
            e.printStackTrace();
        }
    }
}
