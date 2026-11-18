package com.sirin.hk3gtl.common.research;

import com.google.gson.JsonObject;
import java.util.ArrayList;
import java.util.List;







public final class Hk3ResearchRuntimeComparison {
    private Hk3ResearchRuntimeComparison() {}

    public static List<String> compare(JsonObject expected, JsonObject actual) {
        var failures = new ArrayList<String>();
        if (actual == null) return List.of("missing_recipe");
        for (String key : List.of("id", "type", "definition", "gates", "resolved_inputs", "resolved_outputs")) {
            if (!expected.has(key) || !actual.has(key) || !expected.get(key).equals(actual.get(key)))
                failures.add("mismatch:" + key);
        }
        if (!actual.has("empty_ingredients") || actual.getAsJsonArray("empty_ingredients").size() != 0)
            failures.add("empty_ingredients");
        return List.copyOf(failures);
    }
}
