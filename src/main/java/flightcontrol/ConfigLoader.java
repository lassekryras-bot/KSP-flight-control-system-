import org.yaml.snakeyaml.Yaml;
import java.io.InputStream;
import java.util.Map;

public class ConfigLoader {
    private Map<String, Object> config;

    public ConfigLoader(String fileName) {
        loadConfig(fileName);
    }

    private void loadConfig(String fileName) {
        Yaml yaml = new Yaml();
        try (InputStream in = getClass().getClassLoader().getResourceAsStream(fileName)) {
            if (in == null) {
                throw new RuntimeException("File not found: " + fileName);
            }
            config = yaml.load(in);
        } catch (Exception e) {
            throw new RuntimeException("Failed to load configuration: " + e.getMessage(), e);
        }
    }

    public Map<String, Object> getConfig() {
        return config;
    }
}