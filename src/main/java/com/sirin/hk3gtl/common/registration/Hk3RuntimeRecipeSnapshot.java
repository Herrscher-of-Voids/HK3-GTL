package com.sirin.hk3gtl.common.registration;

import com.google.gson.*;
import com.gregtechceu.gtceu.api.recipe.*;
import com.gregtechceu.gtceu.api.capability.recipe.*;
import com.mojang.serialization.JsonOps;
import com.sirin.hk3gtl.common.research.Hk3RecipeResearchGate;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.server.MinecraftServer;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.crafting.Recipe;
import java.util.*;

/**
 * 【文件职责】把最终运行时配方和已解析标签候选导出成只读JSON，保留GT条件和非消耗模板。
 * 【变更记录 #1】2026-09-30 00:54:00（第1次备注 · 内测5修订103）
 * 删除：无。新增：GT完整编解码定义、物品/流体候选、能量及门槛快照。
 * 修改：普通配方单独标注仅导出通用视图；用途：为资源目录提供候选来源，不自动认可生存可得性。
 */
public final class Hk3RuntimeRecipeSnapshot {
    private Hk3RuntimeRecipeSnapshot() {}

    public static JsonObject read(Recipe<?> recipe, MinecraftServer server) {
        JsonObject out = new JsonObject();
        out.addProperty("id", recipe.getId().toString());
        out.addProperty("type", String.valueOf(BuiltInRegistries.RECIPE_TYPE.getKey(recipe.getType())));
        out.addProperty("serializer", String.valueOf(BuiltInRegistries.RECIPE_SERIALIZER.getKey(recipe.getSerializer())));
        JsonArray gates = new JsonArray();
        Hk3RecipeResearchGate.getAllRequiredResearch(recipe.getId()).stream().sorted().forEach(gates::add);
        out.add("gates", gates);
        JsonArray empty = new JsonArray();
        if (recipe instanceof GTRecipe gt) {
            out.addProperty("view", "gt_full_codec_and_resolved_candidates");
            out.add("definition", GTRecipeSerializer.CODEC.encodeStart(JsonOps.INSTANCE, gt)
                    .getOrThrow(false, message -> {}));
            out.addProperty("eu_in_per_tick", RecipeHelper.getInputEUt(gt));
            out.addProperty("eu_out_per_tick", RecipeHelper.getOutputEUt(gt));
            out.add("resolved_inputs", contents(gt, true, empty));
            out.add("resolved_outputs", contents(gt, false, empty));
        } else {
            out.addProperty("view", "generic_ingredients_and_result_only");
            JsonArray inputs = new JsonArray();
            for (var ingredient : recipe.getIngredients()) {
                JsonObject row = new JsonObject();
                row.add("definition", ingredient.toJson());
                row.add("alternatives", items(ingredient.getItems()));
                inputs.add(row);
            }
            out.add("resolved_inputs", inputs);
            out.add("result", item(recipe.getResultItem(server.registryAccess())));
            out.addProperty("special", recipe.isSpecial());
        }
        out.add("empty_ingredients", empty);
        out.addProperty("survival_eligibility", "UNVERIFIED");
        return out;
    }

    private static JsonObject contents(GTRecipe recipe, boolean input, JsonArray empty) {
        JsonObject result = new JsonObject();
        JsonArray items = new JsonArray(), fluids = new JsonArray();
        var ic = ItemRecipeCapability.CAP;
        var fc = FluidRecipeCapability.CAP;
        for (var entry : input ? recipe.getInputContents(ic) : recipe.getOutputContents(ic)) {
            var alternatives = items(ic.of(entry.content).getItems());
            JsonObject row = new JsonObject();
            row.add("alternatives", alternatives);
            row.addProperty("chance", entry.chance);
            row.addProperty("max_chance", entry.maxChance);
            row.addProperty("tier_chance_boost", entry.tierChanceBoost);
            if (alternatives.isEmpty()) empty.add((input ? "input" : "output") + ":item:" + items.size());
            items.add(row);
        }
        for (var entry : input ? recipe.getInputContents(fc) : recipe.getOutputContents(fc)) {
            var ingredient = fc.of(entry.content);
            JsonObject row = new JsonObject();
            JsonArray alternatives = new JsonArray();
            Arrays.stream(ingredient.getStacks()).map(stack -> BuiltInRegistries.FLUID.getKey(stack.getFluid()).toString())
                    .distinct().sorted().forEach(alternatives::add);
            row.add("alternatives", alternatives);
            row.addProperty("amount", ingredient.getAmount());
            row.addProperty("chance", entry.chance);
            row.addProperty("max_chance", entry.maxChance);
            if (alternatives.isEmpty()) empty.add((input ? "input" : "output") + ":fluid:" + fluids.size());
            fluids.add(row);
        }
        result.add("items", items); result.add("fluids", fluids);
        return result;
    }

    private static JsonArray items(ItemStack[] stacks) {
        JsonArray result = new JsonArray();
        Arrays.stream(stacks).filter(s -> !s.isEmpty()).map(Hk3RuntimeRecipeSnapshot::item)
                .sorted(Comparator.comparing(JsonObject::toString)).forEach(result::add);
        return result;
    }
    private static JsonObject item(ItemStack stack) {
        JsonObject result = new JsonObject();
        result.addProperty("id", BuiltInRegistries.ITEM.getKey(stack.getItem()).toString());
        result.addProperty("count", stack.getCount());
        if (stack.hasTag()) result.addProperty("nbt", stack.getTag().toString());
        return result;
    }
}
