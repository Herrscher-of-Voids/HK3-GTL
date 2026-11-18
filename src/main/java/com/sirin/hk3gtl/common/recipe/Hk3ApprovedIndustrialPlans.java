package com.sirin.hk3gtl.common.recipe;

import com.google.gson.JsonArray;
import com.google.gson.JsonObject;
import com.google.gson.JsonParser;
import net.minecraft.resources.ResourceLocation;

import java.io.InputStreamReader;
import java.nio.charset.StandardCharsets;
import java.util.HashSet;
import java.util.Set;

public final class Hk3ApprovedIndustrialPlans {
    private static final JsonObject DATA = load("approved_industrial_processes");
    private static final Set<String> SUPERSEDED = ids();

    private Hk3ApprovedIndustrialPlans() {}

    private static JsonObject load(String file) {
        try (var input = Hk3ApprovedIndustrialPlans.class.getResourceAsStream(
                "/data/hk3gtl/research/" + file + ".json")) {
            return JsonParser.parseReader(new InputStreamReader(input, StandardCharsets.UTF_8)).getAsJsonObject();
        } catch (java.io.IOException failure) {
            throw new IllegalStateException("批准工业配方读取失败", failure);
        }
    }

    private static Set<String> ids() {
        var ids = new HashSet<String>();
        DATA.getAsJsonArray("superseded_ids").forEach(value -> ids.add(value.getAsString()));
        return Set.copyOf(ids);
    }

    public static boolean isSuperseded(ResourceLocation id) {
        if (!id.getNamespace().equals("hk3gtl") && !id.getNamespace().equals("gtceu")) return false;
        String path = id.getPath();
        if (SUPERSEDED.contains(path)) return true;
        for (int slash = path.indexOf('/'); slash >= 0; slash = path.indexOf('/', slash + 1)) {
            String suffix = path.substring(slash + 1);
            if (SUPERSEDED.contains(suffix)) return true;
        }
        for (var prefix : DATA.getAsJsonArray("superseded_prefixes")) {
            if (path.startsWith(prefix.getAsString()) || path.contains("/" + prefix.getAsString())) return true;
        }
        return false;
    }

    public static JsonArray merge(JsonArray original) {
        var recipes = new JsonArray();
        for (var value : original) {
            String id = value.getAsJsonObject().get("id").getAsString();
            if (!isSuperseded(new ResourceLocation("hk3gtl", id))) recipes.add(value);
        }
        recipes.addAll(DATA.getAsJsonArray("recipes"));
        return recipes;
    }
}
