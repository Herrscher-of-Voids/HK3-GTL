package com.sirin.hk3gtl.common.recipe.honkai;

import com.gregtechceu.gtceu.api.GTValues;
import com.gregtechceu.gtceu.api.data.tag.TagPrefix;
import com.gregtechceu.gtceu.common.data.GTMaterials;
import com.gregtechceu.gtceu.common.data.GTRecipeTypes;
import com.gregtechceu.gtceu.data.recipe.CustomTags;
import com.sirin.hk3gtl.common.constants.Hk3Values;
import com.sirin.hk3gtl.common.item.honkai.HonkaiMaterialItems;
import com.sirin.hk3gtl.common.machine.energy.Hk3HonkaiNetworkInjectorMachine;
import com.sirin.hk3gtl.common.material.Hk3Materials;
import com.sirin.hk3gtl.common.recipe.Hk3IndustrialRecipeTypes;
import com.sirin.hk3gtl.common.registration.Hk3IndustrialContent;
import com.sirin.hk3gtl.common.registration.Hk3IndustrialFluids;
import net.minecraft.data.recipes.FinishedRecipe;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.item.ItemStack;
import com.lowdragmc.lowdraglib.side.fluid.FluidStack;
import java.util.function.Consumer;

/** 中文说明：该处说明已按当前代码行为整理。*/
/**
 * 【变更记录 #1】2026-09-24 16:37:18（内测5修订66）
 * 删除：旧共享精炼工艺注册，原文件完整归档。新增：专用工艺注册委托与高效采集研究门槛。
 * 修改：初始采集保持不变；用途：避免同一配方重复注册与旧能耗配置继续生效。
 */
/**
 * 【变更记录 #2】2026-09-27 01:54:24（第 2 次备注 · 内测5修订86）
 * 删除：无，保留全部历史注册与工艺。
 * 新增：燃料封装起步配方注册委托，沿现有液态工艺入口调用。
 * 修改：接入负责人确认的棒壳、封装样件与I02检测路线。
 * 用途：补齐RN-FRP实验入口，不注册I18，不跳过研究支付或前置。
 */
/**
 * 【变更记录 #3】2026-09-27 02:26:24（第 3 次备注 · 内测5修订87）
 * 删除：无，保留历史备注、稳定注册键和不相关工艺。
 * 新增：无新增采集配方。
 * 修改：I01高效采集的4份参考样本改为不消耗标准件；探测器、钨钢板、铂线、EU及研究门槛不变。
 * 用途：采集仍要求样本到位，但连续生产不再逐批销毁样本；I07校准与探测器制造不受影响。
 */
public final class HonkaiRecipes {
    private static final long MAX_EUT = Hk3Values.VA_LONG[GTValues.MAX];

    private HonkaiRecipes() {}

    private static ItemStack betaItem(String id, int amount) {
        var object = Hk3IndustrialContent.items().get(id);
        if (object == null) throw new IllegalStateException("Missing Beta 5 item registration: " + id);
        return new ItemStack(object.get(), amount);
    }

    private static FluidStack fluid(String id, int amount) {
        var material = Hk3IndustrialFluids.materials().get(id);
        if (material == null) throw new IllegalStateException("Missing Beta 5 fluid registration: " + id);
        return material.getFluid(amount);
    }

    /** 中文说明：该处备注已按当前代码行为整理，不使用问号占位。*/
    public static void addAbsorptionRecipes(Consumer<FinishedRecipe> provider) {
        Hk3IndustrialRecipeTypes.COLLECTION.recipeBuilder(new ResourceLocation("hk3gtl", "industrial_liquid_sampling"))
                .circuitMeta(3)
                .notConsumable(betaItem("prototype_honkai_detector", 1))
                .inputItems(com.gregtechceu.gtceu.api.data.tag.TagPrefix.plate, com.gregtechceu.gtceu.common.data.GTMaterials.StainlessSteel, 8)
                .inputItems(com.gregtechceu.gtceu.api.data.tag.TagPrefix.wireGtSingle, com.gregtechceu.gtceu.common.data.GTMaterials.Copper, 16)
                .inputItems(net.minecraft.world.item.Items.GLASS_PANE, 8)
                .outputFluids(Hk3Materials.LIQUID_HONKAI_ENERGY.getFluid(100))
                .duration(200).EUt(MAX_EUT).save(provider);

        com.sirin.hk3gtl.common.research.Hk3RecipeResearchGate.bind("industrial_honkai_collection", "industrial_liquid_collection", "RN-DMT");
        // 一阶探测器提升采集效率，但仍只在采集塔内作为非消耗工具使用。
        Hk3IndustrialRecipeTypes.COLLECTION.recipeBuilder(new ResourceLocation("hk3gtl", "industrial_liquid_collection"))
                .circuitMeta(4)
                .notConsumable(betaItem("liquid_honkai_detector", 1))
                .inputItems(com.gregtechceu.gtceu.api.data.tag.TagPrefix.plate, com.gregtechceu.gtceu.common.data.GTMaterials.TungstenSteel, 12)
                .inputItems(com.gregtechceu.gtceu.api.data.tag.TagPrefix.wireFine, com.gregtechceu.gtceu.common.data.GTMaterials.Platinum, 24)
                .notConsumable(betaItem("honkai_reference_sample", 4))
                .outputFluids(Hk3Materials.LIQUID_HONKAI_ENERGY.getFluid(2400))
                .duration(600).EUt(MAX_EUT).save(provider);
    }

    /** 中文说明：该处说明已按当前代码行为整理。*/
    public static void addCondensationRecipes(Consumer<FinishedRecipe> provider) {
        Hk3LiquidLineRecipes.processing(provider);
        Hk3FuelRodBootstrapRecipes.register(provider);
    }

    /** 液态、浓缩与结晶三条路径使用相同的正式网络结算。 */
    public static void addNetworkInjectionRecipes(Consumer<FinishedRecipe> provider) {
        Hk3LiquidLineRecipes.injection(provider);
    }
}

// 【变更记录 · 修订161】2026-10-17 14:11:55：本轮仅将活动类名、资源与工业配方引用迁移为长期业务命名；历史备注保留，不代表旧逻辑已全部按现行设计重写。
