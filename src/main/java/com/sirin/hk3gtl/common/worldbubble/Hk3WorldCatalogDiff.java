package com.sirin.hk3gtl.common.worldbubble;

import com.google.gson.JsonArray;
import com.google.gson.JsonObject;
import com.google.gson.JsonParser;
import com.mojang.brigadier.exceptions.CommandSyntaxException;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.nbt.TagParser;

import java.io.IOException;
import java.io.InputStreamReader;
import java.nio.charset.StandardCharsets;
import java.util.Map;
import java.util.TreeMap;

final class Hk3WorldCatalogDiff {
    private record Resource(JsonObject row, CompoundTag stackData) {}

    private Hk3WorldCatalogDiff() {}

    static JsonObject create(JsonObject current) throws IOException, CommandSyntaxException {
        JsonObject baseline;
        try (var reader = new InputStreamReader(Hk3WorldCatalogDiff.class.getResourceAsStream(
                "/data/hk3gtl/catalog/world_bubble_resources.json"), StandardCharsets.UTF_8)) {
            baseline = JsonParser.parseReader(reader).getAsJsonObject();
        }
        var before = resources(baseline);
        var after = resources(current);
        var added = new JsonArray(); var removed = new JsonArray(); var changed = new JsonArray();
        var addedNbt = new JsonArray(); var removedNbt = new JsonArray();
        after.forEach((key, resource) -> {
            var previous = before.get(key);
            if (previous == null) {
                added.add(resource.row());
                if (!resource.stackData().isEmpty()) addedNbt.add(resource.row());
            } else if (value(previous.row(), "tier") != value(resource.row(), "tier")
                    || value(previous.row(), "amount") != value(resource.row(), "amount")) {
                var row = new JsonObject();
                row.add("id", resource.row().get("id")); row.add("kind", resource.row().get("kind"));
                row.addProperty("stack_data", Hk3WorldResourceCatalog.canonical(resource.stackData()));
                row.add("before", quantities(previous.row())); row.add("after", quantities(resource.row()));
                changed.add(row);
            }
        });
        before.forEach((key, resource) -> {
            if (!after.containsKey(key)) {
                removed.add(resource.row());
                if (!resource.stackData().isEmpty()) removedNbt.add(resource.row());
            }
        });
        var result = new JsonObject(); result.addProperty("schema", 1);
        result.add("generated_at", current.get("generated_at"));
        result.add("baseline", metadata(baseline)); result.add("current", metadata(current));
        result.add("mods", current.get("mods"));
        result.addProperty("comparison", "按类型、注册ID和完整栈数据比较；changed只比较固定产量和来源执行电压Tier。");
        result.add("added", added); result.add("removed", removed); result.add("changed", changed);
        result.add("added_nbt_variants", addedNbt); result.add("removed_nbt_variants", removedNbt);
        var counts = new JsonObject(); counts.addProperty("baseline", before.size()); counts.addProperty("current", after.size());
        counts.addProperty("added", added.size()); counts.addProperty("removed", removed.size()); counts.addProperty("changed", changed.size());
        counts.addProperty("added_nbt_variants", addedNbt.size()); counts.addProperty("removed_nbt_variants", removedNbt.size());
        result.add("counts", counts);
        return result;
    }

    private static Map<String, Resource> resources(JsonObject catalog) throws CommandSyntaxException {
        var resources = new TreeMap<String, Resource>();
        for (String group : new String[]{"roots", "processed"}) for (var element : catalog.getAsJsonArray(group)) {
            var row = element.getAsJsonObject();
            var data = new CompoundTag();
            if (row.has("stack_data")) data = TagParser.parseTag(row.get("stack_data").getAsString());
            else if (row.has("nbt")) data.put("tag", TagParser.parseTag(row.get("nbt").getAsString()));
            String key = row.get("kind").getAsString() + "/" + Hk3WorldResourceCatalog.identity(row.get("id").getAsString(), data);
            resources.put(key, new Resource(row, data));
        }
        return resources;
    }

    private static JsonObject metadata(JsonObject catalog) {
        var result = new JsonObject(); result.add("profile", catalog.get("profile")); result.add("version", catalog.get("version"));
        if (catalog.has("catalog_hash")) result.add("catalog_hash", catalog.get("catalog_hash"));
        return result;
    }

    private static JsonObject quantities(JsonObject resource) {
        var result = new JsonObject(); result.addProperty("tier", value(resource, "tier"));
        result.addProperty("amount", value(resource, "amount")); return result;
    }

    private static int value(JsonObject resource, String name) { return resource.get(name).getAsInt(); }
}
