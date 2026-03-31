import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayDeque;
import java.util.Deque;
import java.util.LinkedHashMap;
import java.util.Map;

public class ConfigLoader {

    public static Map<String, Object> load(String path) {
        try {
            return parseYamlMap(Files.readAllLines(Path.of(path)));
        } catch (IOException e) {
            throw new RuntimeException("Failed to load configuration: " + path, e);
        }
    }

    private static Map<String, Object> parseYamlMap(Iterable<String> lines) {
        Map<String, Object> root = new LinkedHashMap<>();

        Deque<Map<String, Object>> mapStack = new ArrayDeque<>();
        Deque<Integer> indentStack = new ArrayDeque<>();
        mapStack.push(root);
        indentStack.push(-1);

        for (String rawLine : lines) {
            String line = stripComment(rawLine);
            if (line.isBlank()) {
                continue;
            }

            int indent = countLeadingSpaces(line);
            String trimmed = line.trim();
            int colon = trimmed.indexOf(':');
            if (colon < 0) {
                continue;
            }

            String key = trimmed.substring(0, colon).trim();
            String value = trimmed.substring(colon + 1).trim();

            while (indent <= indentStack.peek()) {
                mapStack.pop();
                indentStack.pop();
            }

            Map<String, Object> current = mapStack.peek();
            if (value.isEmpty()) {
                Map<String, Object> child = new LinkedHashMap<>();
                current.put(key, child);
                mapStack.push(child);
                indentStack.push(indent);
            } else {
                current.put(key, parseScalar(value));
            }
        }

        return root;
    }

    private static String stripComment(String line) {
        int commentIndex = line.indexOf('#');
        return commentIndex >= 0 ? line.substring(0, commentIndex) : line;
    }

    private static int countLeadingSpaces(String line) {
        int count = 0;
        while (count < line.length() && line.charAt(count) == ' ') {
            count++;
        }
        return count;
    }

    private static Object parseScalar(String value) {
        if ("true".equalsIgnoreCase(value)) {
            return Boolean.TRUE;
        }
        if ("false".equalsIgnoreCase(value)) {
            return Boolean.FALSE;
        }

        try {
            if (value.contains(".")) {
                return Double.parseDouble(value);
            }
            return Integer.parseInt(value);
        } catch (NumberFormatException ignored) {
            return value;
        }
    }
}
