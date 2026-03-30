package flightcontrol;

import java.io.FileWriter;
import java.io.IOException;
import java.util.Map;

public class RunLogger {

    private String filePath;

    public RunLogger(String filePath) {
        this.filePath = filePath;
    }

    public void log(TestRun run) {
        try (FileWriter writer = new FileWriter(filePath, true)) {
            String json = toJson(run.toMap());
            writer.write(json + "\n");
        } catch (IOException e) {
            e.printStackTrace();
        }
    }

    private String toJson(Map<String, Object> map) {
        StringBuilder sb = new StringBuilder("{");

        boolean first = true;
        for (Map.Entry<String, Object> entry : map.entrySet()) {
            if (!first) sb.append(",");
            first = false;

            sb.append("\"").append(entry.getKey()).append("\":");

            if (entry.getValue() instanceof String) {
                sb.append("\"").append(entry.getValue()).append("\"");
            } else if (entry.getValue() instanceof Map) {
                sb.append(toJson((Map<String, Object>) entry.getValue()));
            } else {
                sb.append(entry.getValue());
            }
        }

        sb.append("}");
        return sb.toString();
    }
}
