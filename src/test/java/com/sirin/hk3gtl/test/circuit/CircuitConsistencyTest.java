package com.sirin.hk3gtl.test.circuit;

import com.google.gson.JsonObject;
import com.google.gson.JsonParser;
import com.sirin.hk3gtl.common.constants.Hk3Tiers;
import com.sirin.hk3gtl.common.item.Hk3CircuitCatalog;
import net.minecraft.resources.ResourceLocation;

import java.io.InputStreamReader;
import java.nio.charset.StandardCharsets;
import java.util.HashSet;
import java.util.Set;
import java.util.stream.Collectors;

public final class CircuitConsistencyTest {
    private static int checks;
    public static void main(String[] args) throws Exception {
        ElectronicResearchTest.run();
        RecipeGateMergeTest.run();
        var entries = Hk3CircuitCatalog.ENTRIES;
        check(entries.size() == 52 && new HashSet<>(Hk3CircuitCatalog.paths()).size() == 52, "52 distinct IDs");
        check(entries.stream().filter(Hk3CircuitCatalog.Entry::primary).count() == 16, "16 stable primary IDs");
        var families = entries.stream().collect(Collectors.groupingBy(Hk3CircuitCatalog.Entry::family));
        check(families.size() == 13, "13 families");
        for (var family : families.values()) {
            check(family.size() == 4, "four forms");
            int first = family.stream().mapToInt(Hk3CircuitCatalog.Entry::tier).min().orElseThrow();
            for (int form = 0; form < 4; form++) {
                int expected = form;
                var entry = family.stream().filter(e -> e.form() == expected).findFirst().orElseThrow();
                check(entry.tier() == first + form, "consecutive form voltage");
                check(Hk3CircuitCatalog.tier(new ResourceLocation("hk3gtl", entry.id())) == entry.tier(), "actual tier lookup");
            }
        }
        check(Hk3CircuitCatalog.tier(new ResourceLocation("minecraft", "hbv_processor")) == -1, "namespace isolation");
        check(Hk3CircuitCatalog.tier(new ResourceLocation("hk3gtl", "hbv_processor_mainframe")) == -1, "legacy placeholder not official");
        int tagChecks = 0;
        for (int index = 0; index < 16; index++) {
            int tier = 15 + index;
            Set<String> expected = entries.stream().filter(e -> e.tier() == tier).map(e -> "hk3gtl:" + e.id()).collect(Collectors.toSet());
            String key = Hk3Tiers.voltageKey(tier);
            check(Hk3CircuitCatalog.tagId(tier).toString().equals("forge:circuits/" + key), "actual generic tag");
            for (String namespace : new String[]{"forge", "gtceu"}) {
                for (String alias : new String[]{key}) {
                    check(tag(namespace + ":circuits/" + alias, new HashSet<>()).equals(expected), "same-tier alternatives " + namespace + ":" + alias);
                    tagChecks++;
                }
            }
        }
        System.out.println("Circuit consistency: " + checks + " checks passed; 52 circuits and " + tagChecks + " voltage tags");
    }
    private static Set<String> tag(String id, Set<String> visiting) throws Exception {
        if (!visiting.add(id)) throw new AssertionError("Tag cycle " + id);
        String[] parts = id.split(":", 2);
        String path = "data/" + parts[0] + "/tags/items/" + parts[1] + ".json";
        Set<String> values = new HashSet<>();
        try (var stream = CircuitConsistencyTest.class.getClassLoader().getResourceAsStream(path)) {
            if (stream == null) throw new AssertionError("Missing tag " + path);
            JsonObject json = JsonParser.parseReader(new InputStreamReader(stream, StandardCharsets.UTF_8)).getAsJsonObject();
            for (var element : json.getAsJsonArray("values")) {
                String value = element.isJsonPrimitive() ? element.getAsString() : element.getAsJsonObject().get("id").getAsString();
                if (value.startsWith("#")) values.addAll(tag(value.substring(1), visiting)); else values.add(value);
            }
        }
        visiting.remove(id); return values;
    }
    private static void check(boolean condition, String message) { checks++; if (!condition) throw new AssertionError(message); }
}
