package com.sirin.hk3gtl.common.research;

 









 

import com.google.gson.JsonParser;
import java.io.InputStreamReader;
import java.nio.charset.StandardCharsets;
import java.util.*;

public final class Hk3ResearchPlans {
    public record Material(String tag, long count, double sensitivity) {
        public Material(String tag, long count) { this(tag, count, 1.0); }
        public Material {
            if (!Double.isFinite(sensitivity) || sensitivity < 0 || sensitivity > 1) throw new IllegalArgumentException("Invalid sensitivity");
            if (tag == null || !tag.matches("[a-z0-9_.-]+:[a-z0-9_/.-]+") || count < 1)
                throw new IllegalArgumentException("Invalid material cost");
        }
    }
    /** 点数为整数、时间为基础tick；英文/中文课题名由lang键展示。 / Integer points and base ticks; topic names use language keys. */
    public record Plan(String id, long points, long ticks, String evidence, String result, List<Material> materials, long eut) {
        public Plan {
            if (points < 1 || ticks < 1 || eut < 1 || materials.isEmpty()) throw new IllegalArgumentException("Invalid plan");
            materials = List.copyOf(materials);
        }
        public String nameKey() { return "hk3gtl.research.topic." + id.toLowerCase(Locale.ROOT); }
    }
    private Hk3ResearchPlans() {}
    /** 顺序与已确认目录一致，返回不可变映射。 / Immutable plans in accepted catalog order. */
    public static Map<String, Plan> all() { return Holder.PLANS; }
    public static Plan get(String id) { return all().get(id); }
    private static final class Holder { private static final Map<String, Plan> PLANS = load(); }
    private static Map<String, Plan> load() {
        try (var in = Hk3ResearchPlans.class.getResourceAsStream("/data/hk3gtl/research/research_costs.json")) {
            if (in == null) throw new IllegalStateException("Missing research costs");
            var root = JsonParser.parseReader(new InputStreamReader(in, StandardCharsets.UTF_8)).getAsJsonObject();
            if (root.get("schema").getAsInt() != 1) throw new IllegalArgumentException("Unsupported costs version");
            Map<String, Plan> result = new LinkedHashMap<>();
            for (var element : root.getAsJsonArray("topics")) {
                var object = element.getAsJsonObject(); String id = object.get("id").getAsString();
                List<Material> materials = new ArrayList<>();
                for (var raw : object.getAsJsonArray("materials")) {
                    var material = raw.getAsJsonObject();
                    materials.add(new Material(material.get("tag").getAsString(), material.get("count").getAsLong(), material.get("sensitivity").getAsDouble()));
                }
                Plan plan = new Plan(id, object.get("points").getAsLong(), object.get("ticks").getAsLong(),
                        object.get("evidence").getAsString(), object.get("result").getAsString(), materials, object.get("eut").getAsLong());
                if (Hk3ResearchCatalog.bundled().get(id) == null || result.putIfAbsent(id, plan) != null)
                    throw new IllegalArgumentException("Unknown/duplicate research cost: " + id);
            }
            if (!result.keySet().equals(Hk3ResearchCatalog.bundled().topics().keySet()))
                throw new IllegalArgumentException("Incomplete research costs");
            return Collections.unmodifiableMap(result);
        } catch (Exception e) { throw new IllegalStateException("Cannot load research costs", e); }
    }
}

 
