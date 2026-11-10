import com.google.gson.*;
import java.lang.reflect.*;
import java.nio.charset.StandardCharsets;
import java.nio.file.*;
import java.util.*;

/** Uses the real vanilla 1.20.1 classes; names are from Mojang's local official mapping. */
public class HallAzuRegistryAudit {
    public static void main(String[] args) throws Exception {
        Class.forName("aa").getMethod("a").invoke(null); // SharedConstants.tryDetectVersion
        Class.forName("acs").getMethod("a").invoke(null); // Bootstrap.bootStrap
        Class<?> registryClass = Class.forName("hr"), locationClass = Class.forName("acq");
        Class<?> blockClass = Class.forName("cpn"), definitionClass = Class.forName("dcc");
        Class<?> propertyClass = Class.forName("dde"), holderClass = Class.forName("dcd");
        Object registry = Class.forName("jb").getField("f").get(null); // BuiltInRegistries.BLOCK
        Method contains = registryClass.getMethod("c", locationClass);
        Method get = registryClass.getMethod("a", locationClass);
        Method definition = blockClass.getMethod("l"), defaultState = blockClass.getMethod("n");
        Method properties = definitionClass.getMethod("d"), property = definitionClass.getMethod("a", String.class);
        Method possibleStates = definitionClass.getMethod("a");
        Method name = propertyClass.getMethod("f"), values = propertyClass.getMethod("a");
        Method valueName = propertyClass.getMethod("a", Comparable.class), parseValue = propertyClass.getMethod("b", String.class);
        Method setValue = holderClass.getMethod("a", propertyClass, Comparable.class);
        JsonArray input = JsonParser.parseString(Files.readString(Path.of(args[0]), StandardCharsets.UTF_8)).getAsJsonArray();
        JsonArray checked = new JsonArray();
        JsonObject definitions = new JsonObject();
        for (JsonElement entry : input) {
            String state = entry.getAsString(), blockId = state.split("\\[", 2)[0];
            Object location = locationClass.getConstructor(String.class).newInstance(blockId);
            boolean exists = (boolean) contains.invoke(registry, location);
            JsonObject result = new JsonObject();
            result.addProperty("state", state);
            result.addProperty("block", blockId);
            result.addProperty("block_exists", exists);
            JsonArray errors = new JsonArray(), missing = new JsonArray();
            JsonObject requested = new JsonObject();
            if (state.contains("[")) {
                for (String pair : state.substring(state.indexOf('[') + 1, state.length() - 1).split(",")) {
                    String[] item = pair.split("=", 2);
                    requested.addProperty(item[0], item[1]);
                }
            }
            result.add("properties", requested);
            if (exists) {
                Object block = get.invoke(registry, location), def = definition.invoke(block);
                Object instance = defaultState.invoke(block);
                JsonObject allowed = new JsonObject();
                for (Object prop : (Collection<?>) properties.invoke(def)) {
                    String key = (String) name.invoke(prop);
                    JsonArray valid = new JsonArray();
                    for (Object value : (Collection<?>) values.invoke(prop)) {
                        valid.add((String) valueName.invoke(prop, value));
                    }
                    allowed.add(key, valid);
                    if (!requested.has(key)) missing.add(key);
                }
                definitions.add(blockId, allowed);
                for (Map.Entry<String, JsonElement> pair : requested.entrySet()) {
                    Object prop = property.invoke(def, pair.getKey());
                    if (prop == null) {
                        errors.add("不存在属性：" + pair.getKey());
                        continue;
                    }
                    Optional<?> parsed = (Optional<?>) parseValue.invoke(prop, pair.getValue().getAsString());
                    if (parsed.isEmpty()) errors.add("不存在属性值：" + pair.getKey() + "=" + pair.getValue().getAsString());
                    else instance = setValue.invoke(instance, prop, parsed.get());
                }
                result.addProperty("state_instance_verified", errors.isEmpty() && missing.isEmpty()
                    && ((Collection<?>) possibleStates.invoke(def)).contains(instance));
            } else {
                errors.add("不存在方块ID：" + blockId);
                result.addProperty("state_instance_verified", false);
            }
            result.add("property_errors", errors);
            result.add("omitted_properties", missing);
            checked.add(result);
        }
        JsonObject report = new JsonObject();
        report.add("block_state_definitions", definitions);
        report.add("states", checked);
        Files.writeString(Path.of(args[1]), new GsonBuilder().setPrettyPrinting().create().toJson(report), StandardCharsets.UTF_8);
        System.out.println("AUDIT_COMPLETE states=" + checked.size() + " block_ids=" + definitions.size());
    }
}
