package com.sirin.hk3gtl.common.recipe.main;

import com.gregtechceu.gtceu.api.GTValues;
import com.gregtechceu.gtceu.api.recipe.GTRecipeType;
import com.gregtechceu.gtceu.data.recipe.builder.GTRecipeBuilder;
import com.lowdragmc.lowdraglib.side.fluid.FluidStack;
import com.sirin.hk3gtl.common.constants.Hk3Values;
import com.sirin.hk3gtl.common.item.main.Hk3MainMaterialItems;
import com.sirin.hk3gtl.common.material.main.Hk3MainMaterialCatalog;
import com.sirin.hk3gtl.common.recipe.power.Hk3RecipePower;
import com.sirin.hk3gtl.common.research.Hk3RecipeResearchGate;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.data.recipes.FinishedRecipe;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.item.ItemStack;

import java.util.function.Consumer;

/**
 * 【文件职责】统一注册十六阶主材料实物工序、专属成板和有损回收，不新增机器或方块。
 * 【变更记录 #1】2026-10-17 16:26:09（第1次备注 · 修订165）
 * - 删除：无；旧魂钢L3与L1生产线不在此改写。
 * - 新增：整族注册入口、注册表严格解析和长整数电压元数据。
 * - 修改：生产、形态、回收拆分；HBV首制用MAX、量产用HBV，后阶首制使用前阶电压避免自锁。
 * - 用途：由配方总入口调用；未知原料拒绝注册，代码链不代表高阶硬件已能供电。
 */
public final class Hk3MainMaterialRecipes {
    private Hk3MainMaterialRecipes() {}

    public static void register(Consumer<FinishedRecipe> provider) {
        Hk3MainMaterialProductionLower.register(provider);
        Hk3MainMaterialProductionUpper.register(provider);
        for (var entry : Hk3MainMaterialCatalog.entries()) {
            Hk3MainMaterialFormRecipes.register(entry.tier(), provider);
            Hk3MainMaterialRecoveryRecipes.register(entry.tier(), provider);
        }
    }

    static GTRecipeBuilder process(GTRecipeType type, int tier, String step, int ticks) {
        // 后阶首制由前阶加工能力承担，HBV的正式L1/L3量产仍使用HBV。
        return process(type, tier, Hk3MainMaterialAccess.productionPowerTier(tier), step, ticks);
    }

    static GTRecipeBuilder process(GTRecipeType type, int materialTier, int energyTier, String step, int ticks) {
        var entry = Hk3MainMaterialCatalog.entry(materialTier);
        Hk3MainMaterialAccess.validateOperation(materialTier, energyTier);
        String path = "main_material/" + entry.key() + "/" + step;
        Hk3RecipeResearchGate.bindAll(type.registryName.getPath(), path,
                Hk3MainMaterialAccess.requirements(materialTier, energyTier));
        var builder = type.recipeBuilder(new ResourceLocation("hk3gtl", path))
                .duration(ticks).EUt(Hk3Values.VA_LONG[energyTier])
                .addData("hk3_material_product_tier", materialTier);
        // 此键保存工序所需绝对电压，而非产物所处等级，避免把MAX首制误判为HBV。
        if (energyTier > GTValues.MAX) builder.addData("hk3_main_material_tier", energyTier);
        return Hk3RecipePower.require(builder, energyTier);
    }

    static ItemStack material(int tier, String form, int count) {
        return Hk3MainMaterialItems.stack(tier, form, count);
    }

    static ItemStack external(String key, int count) {
        var id = new ResourceLocation(key);
        if (!BuiltInRegistries.ITEM.containsKey(id)) throw new IllegalStateException("主材原料未注册：" + id);
        return new ItemStack(BuiltInRegistries.ITEM.get(id), count);
    }

    static FluidStack fluid(String key, int amount) {
        var id = new ResourceLocation(key);
        if (!BuiltInRegistries.FLUID.containsKey(id)) throw new IllegalStateException("主材流体未注册：" + id);
        return FluidStack.create(BuiltInRegistries.FLUID.get(id), amount);
    }
}
