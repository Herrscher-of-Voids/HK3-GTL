package com.sirin.hk3gtl.common.recipe;

import com.google.gson.JsonObject;
import com.sirin.hk3gtl.common.constants.Hk3Values;
import com.sirin.hk3gtl.common.item.Hk3ElectronicItems;
import com.sirin.hk3gtl.common.recipe.power.Hk3RecipePower;
import com.sirin.hk3gtl.common.research.Hk3ElectronicResearch;
import com.sirin.hk3gtl.common.research.Hk3RecipeResearchGate;
import net.minecraft.data.recipes.FinishedRecipe;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.item.crafting.RecipeSerializer;

import java.util.function.Consumer;

/**
 * 【文件职责】给本电子注册器被目标整合包自动复制的十条光刻配方保留研究和精确运行功率。
 * 【变更记录 #1】2026-10-17 17:47:19（第1次备注 · 修订165）
 * - 删除：无；不覆盖GTL/GTLAdditions全局复制回调，不修改第三方原料或配方。
 * - 新增：限定本模组五个源ID及两种实际复制类型的FinishedRecipe包装。
 * - 修改：光子副本维持原工况，维度聚焦副本使用原四倍long费用及升一阶的功率元数据；两者继承完整研究。
 * - 用途：copyFrom会清空onSave回调，故在本注册器输出边界修正实际序列化数据；不代表机器供电已实测。
 */
public final class Hk3ElectronicRecipeCopies {
    private Hk3ElectronicRecipeCopies() {}

    public static Consumer<FinishedRecipe> guard(Consumer<FinishedRecipe> provider) {
        return recipe -> {
            String[] path = recipe.getId().getPath().split("/", 2);
            if (path.length != 2 || !recipe.getId().getNamespace().equals("gtceu")) {
                provider.accept(recipe);
                return;
            }
            boolean dimensional = path[0].equals("dimensional_focus_engraving_array");
            if (!dimensional && !path[0].equals("photon_matrix_etch")) {
                provider.accept(recipe);
                return;
            }
            int platform = platform(path[1]);
            if (platform < 0) {
                provider.accept(recipe);
                return;
            }
            for (String research : Hk3ElectronicResearch.requirements(platform)) {
                Hk3RecipeResearchGate.bind(recipe.getId(), research);
            }
            int sourceTier = Hk3ElectronicRecipes.predecessorTier(platform);
            int powerTier = sourceTier + (dimensional ? 1 : 0);
            long expected = Math.multiplyExact(Hk3Values.VA_LONG[sourceTier], dimensional ? 4L : 1L);
            provider.accept(new FinishedRecipe() {
                @Override
                public void serializeRecipeData(JsonObject json) {
                    recipe.serializeRecipeData(json);
                    var eu = json.getAsJsonObject("tickInputs").getAsJsonArray("eu");
                    if (eu.size() != 1 || eu.get(0).getAsJsonObject().get("content").getAsLong() != expected) {
                        throw new IllegalStateException("电子光刻副本费用不符合目标实例复制合同：" + recipe.getId());
                    }
                    if (powerTier > 14) {
                        JsonObject data = json.has("data") ? json.getAsJsonObject("data") : new JsonObject();
                        data.addProperty(Hk3RecipePower.TIER_KEY, powerTier);
                        data.addProperty(Hk3RecipePower.MINIMUM_COST_KEY, Long.toString(expected));
                        json.add("data", data);
                    }
                }

                @Override public ResourceLocation getId() { return recipe.getId(); }
                @Override public RecipeSerializer<?> getType() { return recipe.getType(); }
                @Override public JsonObject serializeAdvancement() { return recipe.serializeAdvancement(); }
                @Override public ResourceLocation getAdvancementId() { return recipe.getAdvancementId(); }
            });
        };
    }

    private static int platform(String id) {
        if (id.equals("hk3gtl_electronic_lithography_mask")) return 0;
        for (int p = 0; p < Hk3ElectronicItems.PLATFORMS.size(); p++) {
            if (id.equals("hk3gtl_electronic_" + Hk3ElectronicItems.PLATFORMS.get(p) + "_logic_wafer")) return p;
        }
        return -1;
    }
}
