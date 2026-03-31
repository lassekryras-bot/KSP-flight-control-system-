package flightcontrol;

import java.util.HashMap;
import java.util.Map;

public class TestRun {

    public int runId;
    public double rampRate;
    public long startTimeNano;
    public DetectionData detection;

    public TestRun(int runId, double rampRate) {
        this.runId = runId;
        this.rampRate = rampRate;
    }

    public void start() {
        this.startTimeNano = System.nanoTime();
    }

    public void recordDetection(double throttle, double velocity) {
        double timeSeconds = (System.nanoTime() - startTimeNano) / 1e9;
        this.detection = new DetectionData(timeSeconds, throttle, velocity);
    }

    public Map<String, Object> toMap() {
        Map<String, Object> map = new HashMap<>();
        map.put("run_id", runId);
        map.put("ramp_rate", rampRate);

        if (detection != null) {
            map.put("detection", detection.toMap());
        }

        return map;
    }

    public static class DetectionData {
        public double time;
        public double throttle;
        public double velocity;

        public DetectionData(double time, double throttle, double velocity) {
            this.time = time;
            this.throttle = throttle;
            this.velocity = velocity;
        }

        public Map<String, Object> toMap() {
            Map<String, Object> map = new HashMap<>();
            map.put("time", time);
            map.put("throttle", throttle);
            map.put("velocity", velocity);
            return map;
        }
    }
}
