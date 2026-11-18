package com.sirin.hk3gtl.common.recipe.honkai;

import com.google.gson.JsonObject;
import com.google.gson.JsonParser;
import com.sirin.hk3gtl.common.recipe.Hk3ResearchProcessPlans.Fluid;
import com.sirin.hk3gtl.common.recipe.Hk3ResearchProcessPlans.Item;
import com.sirin.hk3gtl.common.recipe.Hk3ResearchProcessPlans.Plan;

import java.io.IOException;
import java.io.InputStreamReader;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

public final class Hk3FuelBundlePlans {
    public record Operation(Plan plan, int bundleSize, int rodsPerBatch, int activityMultiplier,
                            double heatPerRodTick, int heatLimit, boolean highGrade) {}
    private static final Map<String, Operation> OPERATIONS = load();

    private Hk3FuelBundlePlans() {}

    public static Operation get(String id) { return OPERATIONS.get(id); }

    public static List<Plan> expand(List<Plan> plans) {
        var all = new ArrayList<>(plans.stream().filter(plan -> !Hk3ReactorFuels.reactor(plan.role())).toList());
        OPERATIONS.values().stream().map(Operation::plan).forEach(all::add);
        return List.copyOf(all);
    }

    private static Map<String, Operation> load() {
        try (var input = Hk3FuelBundlePlans.class.getResourceAsStream("/data/hk3gtl/research/reactor_fuel_processes.json")) {
            var root = JsonParser.parseReader(new InputStreamReader(input, StandardCharsets.UTF_8)).getAsJsonObject();
            var operations = new ArrayList<Operation>();
            for (var raw : root.getAsJsonArray("reactor_recipes")) {
                var recipe = raw.getAsJsonObject();
                var plan = new Plan(recipe.get("id").getAsString(), recipe.get("role").getAsString(),
                        strings(recipe, "requirements"), items(recipe, "item_inputs"), items(recipe, "item_outputs"),
                        fluids(recipe, "fluid_inputs"), fluids(recipe, "fluid_outputs"), List.of(),
                        recipe.get("ticks").getAsInt(), recipe.get("energy_tier").getAsInt(), "output",
                        strings(recipe, "facts"), "", false, recipe.get("network_credit").getAsLong(),
                        recipe.get("output_eut").getAsLong(), 0, List.of(), 0, 0, List.of());
                operations.add(new Operation(plan, recipe.get("bundle_size").getAsInt(),
                        recipe.get("rods_per_batch").getAsInt(), recipe.get("activity_multiplier").getAsInt(),
                        recipe.get("heat_per_rod_tick").getAsDouble(), recipe.get("heat_limit").getAsInt(),
                        recipe.get("high_grade").getAsBoolean()));
            }
            return operations.stream().collect(Collectors.toUnmodifiableMap(value -> value.plan().id(), value -> value));
        } catch (IOException failure) {
            throw new IllegalStateException("反应堆运行配方读取失败", failure);
        }
    }

    private static List<String> strings(JsonObject recipe, String key) {
        var values = new ArrayList<String>();
        recipe.getAsJsonArray(key).forEach(value -> values.add(value.getAsString()));
        return List.copyOf(values);
    }

    private static List<Item> items(JsonObject recipe, String key) {
        var values = new ArrayList<Item>();
        recipe.getAsJsonArray(key).forEach(raw -> {
            var value = raw.getAsJsonObject();
            values.add(new Item(value.get("id").getAsString(), value.get("count").getAsInt()));
        });
        return List.copyOf(values);
    }

    private static List<Fluid> fluids(JsonObject recipe, String key) {
        var values = new ArrayList<Fluid>();
        recipe.getAsJsonArray(key).forEach(raw -> {
            var value = raw.getAsJsonObject();
            values.add(new Fluid(value.get("id").getAsString(), value.get("amount").getAsInt()));
        });
        return List.copyOf(values);
    }
}
