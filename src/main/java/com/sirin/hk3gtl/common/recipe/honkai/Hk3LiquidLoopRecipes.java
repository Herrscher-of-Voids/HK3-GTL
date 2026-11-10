package com.sirin.hk3gtl.common.recipe.honkai;

import com.gregtechceu.gtceu.api.data.tag.TagPrefix;
import com.gregtechceu.gtceu.common.data.GTMaterials;
import com.gregtechceu.gtceu.common.data.GTRecipeTypes;
import com.sirin.hk3gtl.common.material.Hk3Materials;
import com.sirin.hk3gtl.common.recipe.Hk3IndustrialRecipeTypes;
import net.minecraft.data.recipes.FinishedRecipe;
import java.util.function.Consumer;
import static com.sirin.hk3gtl.common.recipe.honkai.Hk3LiquidLineRecipes.*;

/**
 * L1配套化工、母液回流与余料处置，沿液态配方唯一入口注册。
 * 【变更记录 #1】2026-09-27 02:26:24（第 1 次备注 · 内测5修订87）
 * 删除：无，不替换L2燃料调配、浓缩或网络注入工艺。
 * 新增：前级GT混合机配制分析试剂；I03使用7500mB新采液和500mB除杂母液回流；I05处理过剩物料。
 * 修改：复用主工艺的MAX电压、研究门禁和注册工具；回流保留与新鲜分馏相同的碳、滤芯、基质及工时。
 * 用途：补足再生试剂和独立排污出口；回收不授予重复实验，不从零库存自启动，不无耗材复制主产物。
 */
public final class Hk3LiquidLoopRecipes {
    private Hk3LiquidLoopRecipes() {}

    public static void register(Consumer<FinishedRecipe> provider) {
        // 碱性醇水试剂来自前级化工原料；无崩坏研究门槛，也不依赖生产线自身的废液。
        recipe(GTRecipeTypes.MIXER_RECIPES,"industrial_fresh_analysis_reagent",3,600,null,null)
                .inputFluids(GTMaterials.DistilledWater.getFluid(750),GTMaterials.Ethanol.getFluid(250))
                .inputItems(TagPrefix.dust,GTMaterials.SodiumHydroxide,2)
                .outputFluids(fluid("honkai_analysis_reagent",1000)).save(provider);

        // 只用除杂后的独立流体替代等量新采液，净化仍完整产出晶种所需粒子。
        recipe(Hk3IndustrialRecipeTypes.LIQUID_REFINING,"industrial_liquid_fractionation_reflux",13,1600,"RN-LSE",null)
                .inputFluids(Hk3Materials.LIQUID_HONKAI_ENERGY.getFluid(7500),fluid("clarified_honkai_mother_liquor",500))
                .inputItems(TagPrefix.dust,GTMaterials.Carbon,16)
                .inputItems(item("separation_filter",8),item("directional_crystallization_matrix",4))
                .outputFluids(fluid("crude_honkai_energy",5000),fluid("honkai_mother_liquor",1500),fluid("honkai_analysis_reagent",1000))
                .outputItems(item("concentrated_honkai_impurity",32),item("separation_residue",16)).save(provider);

        // 两种固体分别处理，避免余料比例不同又造成互相等待；全部产物退出含能主线。
        recipe(Hk3IndustrialRecipeTypes.REGENERATION,"industrial_impurity_purge",14,500,"RN-BCE",null)
                .inputItems(item("concentrated_honkai_impurity",16)).inputItems(TagPrefix.dust,GTMaterials.Carbon,4)
                .inputFluids(GTMaterials.Water.getFluid(1000))
                .outputItems(item("inactive_fuel_residue",8)).outputFluids(fluid("unrecoverable_process_effluent",1000)).save(provider);
        recipe(Hk3IndustrialRecipeTypes.REGENERATION,"industrial_separation_residue_purge",15,500,"RN-BCE",null)
                .inputItems(item("separation_residue",16)).inputItems(TagPrefix.dust,GTMaterials.Carbon,4)
                .inputFluids(GTMaterials.Water.getFluid(1000))
                .outputItems(item("inactive_fuel_residue",8)).outputFluids(fluid("unrecoverable_process_effluent",1000)).save(provider);

        // 仅处理储罐中的多余量；正常回路优先回流或制新介质，排污不可再提取崩坏能。
        for (String excess : new String[]{"honkai_mother_liquor", "clarified_honkai_mother_liquor",
                "honkai_separation_medium", "honkai_stabilization_medium"}) {
            recipe(Hk3IndustrialRecipeTypes.REGENERATION,"industrial_purge_"+excess,16,400,"RN-BCE",null)
                    .inputFluids(fluid(excess,1000)).inputItems(TagPrefix.dust,GTMaterials.Carbon,4)
                    .outputFluids(fluid("unrecoverable_process_effluent",1000)).save(provider);
        }
    }
}

// 【变更记录 · 修订161】2026-10-17 14:11:55：本轮仅将活动类名、资源与工业配方引用迁移为长期业务命名；历史备注保留，不代表旧逻辑已全部按现行设计重写。
