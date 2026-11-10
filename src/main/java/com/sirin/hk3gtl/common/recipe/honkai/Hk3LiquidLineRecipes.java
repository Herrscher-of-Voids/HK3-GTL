package com.sirin.hk3gtl.common.recipe.honkai;

/**
 * 【文件职责／本轮边界】分析试剂、冷却剂和残液的扩展回收改由RN-SMR开放；基础再生保留原起步门槛。
 * 【变更记录 #3】2026-09-29 21:06:40（第 3 次编号备注 · 内测5修订100）
 * 删除：取消已被批准规则替代的研究个人独占、旧数值或在线限定分支；历史备注与其他系统保留。
 * 新增／修改：分析试剂、冷却剂和残液的扩展回收改由RN-SMR开放；基础再生保留原起步门槛。
 * 用途：接通实际证据→付款→研究完成与权限检查；不授予缺真实证据的课题。
 * 边界：编译和账本测试不代表游戏验收；S02至S05正式结构及未接线课题仍未完成。
 * 追溯：logs/research-mainline-r100；R100_FINAL_RECORD。
 */

import com.gregtechceu.gtceu.api.GTValues;
import com.gregtechceu.gtceu.api.data.tag.TagPrefix;
import com.gregtechceu.gtceu.api.recipe.GTRecipeType;
import com.gregtechceu.gtceu.common.data.GTMaterials;
import com.gregtechceu.gtceu.common.data.GTRecipeTypes;
import com.gregtechceu.gtceu.data.recipe.CustomTags;
import com.gregtechceu.gtceu.data.recipe.builder.GTRecipeBuilder;
import com.sirin.hk3gtl.common.constants.Hk3Values;
import com.sirin.hk3gtl.common.item.honkai.HonkaiMaterialItems;
import com.sirin.hk3gtl.common.material.Hk3Materials;
import com.sirin.hk3gtl.common.recipe.Hk3IndustrialRecipeTypes;
import com.sirin.hk3gtl.common.research.Hk3RecipeResearchGate;
import com.sirin.hk3gtl.common.registration.Hk3IndustrialContent;
import com.sirin.hk3gtl.common.registration.Hk3IndustrialFluids;
import com.sirin.hk3gtl.common.machine.research.Hk3LiquidProcessMachine;
import com.lowdragmc.lowdraglib.side.fluid.FluidStack;
import net.minecraft.data.recipes.FinishedRecipe;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;
import java.util.function.Consumer;

/**
 * 液态工业线的正式工艺、冷却和损耗处理；数量分别为物品个数、流体mB、tick和EU/t。
 * 【变更记录 #1】2026-09-24 16:45:00（内测5修订66）
 * 删除：旧全类型工艺、低于MAX的错误能耗以及无新鲜来源的介质回路。
 * 新增：七设备分工、基础介质、校准报告、回收及最终废物处理，真实生产实验元数据。
 * 修改：初始实验只要求前一研究，不能要求它自己将授予凭据的研究；回收均有损耗。
 * 用途：从MAX基础材料启动到液体燃料入网，保留后续固态及燃料棒系统的独立边界。
 */
/**
 * 【变更记录 #2】2026-09-27 02:26:24（第 2 次备注 · 内测5修订87）
 * 删除：无，保留历史备注、稳定注册键和不相关工艺。
 * 新增：净化附产500mB独立除杂母液；调用Hk3LiquidLoopRecipes注册化工补充、回流与排污。
 * 修改：净化粒子256→320；每次介质再生残渣16→8、杂质8→4；5000mB粗液和800mB稳定液不变。
 * 用途：使4批分馏供5批稳定化的80晶种，消除再生耗材赤字；新鲜启动不依赖I05回收或回流库存。
 */
public final class Hk3LiquidLineRecipes {
    private static final long MAX=Hk3Values.VA_LONG[GTValues.MAX];
    private Hk3LiquidLineRecipes() {}
    public static ItemStack item(String id,int count) {
        var registered=Hk3IndustrialContent.items().get(id);
        if(registered==null)throw new IllegalStateException("未注册工业物品："+id);
        return new ItemStack(registered.get(),count);
    }
    public static FluidStack fluid(String id,int amount) {
        var material=Hk3IndustrialFluids.materials().get(id);
        if(material==null)throw new IllegalStateException("未注册工业流体："+id);
        return material.getFluid(amount);
    }
    /** 将显示门槛和服务端门槛登记到同一完整配方ID，实验字段随运行批次保存。 */
    static GTRecipeBuilder recipe(GTRecipeType type,String id,int circuit,int ticks,String gate,String evidence) {
        if(gate!=null)Hk3RecipeResearchGate.bind(type.registryName.getPath(),id,gate);
        var builder=type.recipeBuilder(new ResourceLocation("hk3gtl",id)).circuitMeta(circuit).duration(ticks).EUt(MAX);
        if(evidence!=null)builder.addData(Hk3LiquidProcessMachine.EXPERIMENT,evidence);
        return builder;
    }
    public static void processing(Consumer<FinishedRecipe> provider) {
        // 首次分离可在光谱研究后执行；滤芯和结晶基质全部来自基础MAX加工。
        recipe(Hk3IndustrialRecipeTypes.LIQUID_REFINING,"industrial_liquid_fractionation",1,1600,"RN-HSA","RN-LSE")
                .inputFluids(Hk3Materials.LIQUID_HONKAI_ENERGY.getFluid(8000))
                .inputItems(TagPrefix.dust,GTMaterials.Carbon,16)
                .inputItems(item("separation_filter",8),item("directional_crystallization_matrix",4))
                .outputFluids(fluid("crude_honkai_energy",5000),fluid("honkai_mother_liquor",1500),fluid("honkai_analysis_reagent",1000))
                .outputItems(item("concentrated_honkai_impurity",32),item("separation_residue",16)).save(provider);
        recipe(Hk3IndustrialRecipeTypes.LIQUID_REFINING,"industrial_liquid_purification",2,2000,"RN-LSE",null)
                .inputFluids(fluid("honkai_mother_liquor",1500),fluid("honkai_analysis_reagent",1000))
                .inputItems(item("concentrated_honkai_impurity",16),item("separation_residue",8),item("separation_filter",4))
                .outputFluids(fluid("honkai_separation_medium",1200),fluid("spent_analysis_reagent",500),fluid("unrecoverable_process_effluent",250),fluid("clarified_honkai_mother_liquor",500))
                .outputItems(new ItemStack(HonkaiMaterialItems.RAW_HONKAI_PARTICLE.get(),320)).save(provider);

        // 新鲜稳定介质先由分离产物制造，回收只是补充，第一轮不依赖废介质。
        recipe(GTRecipeTypes.MIXER_RECIPES,"industrial_fresh_stabilization_medium",1,600,null,null)
                .inputFluids(fluid("honkai_separation_medium",500),GTMaterials.DistilledWater.getFluid(1000))
                .inputItems(TagPrefix.dust,GTMaterials.Sodium,16).inputItems(TagPrefix.dust,GTMaterials.Platinum,2)
                .outputFluids(fluid("honkai_stabilization_medium",1500)).save(provider);
        recipe(GTRecipeTypes.MIXER_RECIPES,"industrial_fresh_honkai_coolant",2,500,null,null)
                .inputFluids(GTMaterials.DistilledWater.getFluid(4000))
                .inputItems(TagPrefix.dust,GTMaterials.Silver,8).inputItems(TagPrefix.dust,GTMaterials.Carbon,16)
                .outputFluids(fluid("honkai_coolant",4000)).save(provider);

        recipe(Hk3IndustrialRecipeTypes.STABILIZATION,"industrial_liquid_stabilization",3,2400,"RN-LSE","RN-LES")
                .inputFluids(fluid("crude_honkai_energy",4000),fluid("honkai_stabilization_medium",1000),fluid("honkai_coolant",500))
                .inputItems(TagPrefix.foil,GTMaterials.Platinum,8)
                .inputItems(item("honkai_crystal_seed",16),item("directional_crystallization_matrix",8),item("concentrated_honkai_impurity",8))
                .outputFluids(fluid("stabilized_liquid_honkai_energy",800),fluid("spent_honkai_stabilization_medium",800),
                        fluid("crystallization_residual_liquid",200),fluid("hot_honkai_coolant",500))
                .outputItems(new ItemStack(HonkaiMaterialItems.HONKAI_ENERGY_CRYSTAL.get(),64),item("separation_residue",8)).save(provider);

        recipe(Hk3IndustrialRecipeTypes.REGENERATION,"industrial_stabilization_medium_recovery",4,1800,"RN-BCE","RN-SMR")
                .inputFluids(fluid("spent_honkai_stabilization_medium",800),fluid("honkai_analysis_reagent",500))
                .inputItems(item("separation_residue",8),item("concentrated_honkai_impurity",4),item("fuel_matrix",4))
                .outputFluids(fluid("honkai_stabilization_medium",600),fluid("unrecoverable_process_effluent",200))
                .outputItems(item("separation_filter",4),item("fuel_blending_residue",2)).save(provider);
        recipe(Hk3IndustrialRecipeTypes.FUEL_BLENDING,"industrial_liquid_fuel_blending",5,2200,"RN-BCE","RN-HFB")
                .inputFluids(fluid("stabilized_liquid_honkai_energy",800),fluid("honkai_stabilization_medium",200))
                .inputItems(item("fuel_matrix",32),new ItemStack(HonkaiMaterialItems.HONKAI_ENERGY_CRYSTAL.get(),32),item("honkai_reference_sample",4),item("separation_residue",8))
                .outputFluids(fluid("liquid_honkai_fuel",600),fluid("fuel_refining_residual",180))
                .outputItems(item("fuel_blending_residue",4)).save(provider);
        // 液体浓缩起步工艺不依赖尚未开放的固态采集；后续RN-CFR正式路线仍保留原研究前置。
        recipe(Hk3IndustrialRecipeTypes.CONCENTRATION,"industrial_liquid_fuel_concentration",6,2800,"RN-HFB","RN-CFR")
                .inputFluids(fluid("liquid_honkai_fuel",1200),fluid("honkai_stabilization_medium",400),fluid("honkai_coolant",300))
                .inputItems(new ItemStack(HonkaiMaterialItems.HONKAI_ENERGY_CRYSTAL.get(),128),item("fuel_matrix",16),item("concentrated_honkai_impurity",4),item("honkai_adapted_circuit_substrate",8))
                .outputFluids(fluid("concentrated_liquid_honkai_fuel",800),fluid("fuel_refining_residual",300),fluid("hot_honkai_coolant",300))
                .outputItems(item("fuel_blending_residue",8)).save(provider);

        // I02保持纯物品接口；上游基板配方已实际消耗稳定液，实验返回样件而不复制样件。
        recipe(Hk3IndustrialRecipeTypes.SPECTRUM_ANALYSIS,"industrial_circuit_adaptation_experiment",2,400,"RN-LES","RN-BCE")
                .inputItems(item("honkai_adapted_circuit_substrate",2)).inputItems(CustomTags.MAX_CIRCUITS,2)
                .inputItems(Items.PAPER,8).inputItems(org.gtlcore.gtlcore.common.data.GTLItems.SENSOR_MAX.asStack(2))
                .outputItems(item("honkai_adapted_circuit_substrate",2),item("analyzed_honkai_sample",2)).save(provider);
        recipe(Hk3IndustrialRecipeTypes.CALIBRATION,"industrial_prototype_detector_calibration",1,800,"RN-BCE","RN-DMT")
                .inputItems(item("prototype_honkai_detector",1),item("honkai_reference_sample",4),item("analyzed_honkai_sample",4))
                .inputItems(Items.PAPER,16).inputItems(TagPrefix.foil,GTMaterials.Platinum,16)
                .outputItems(item("prototype_honkai_detector",1),item("honkai_detector_calibration_report",1)).save(provider);
        recipe(Hk3IndustrialRecipeTypes.CALIBRATION,"industrial_liquid_detector_calibration",2,800,"RN-DMT",null)
                .inputItems(item("liquid_honkai_detector",1),item("honkai_reference_sample",4),item("analyzed_honkai_sample",4))
                .inputItems(Items.PAPER,16).inputItems(TagPrefix.foil,GTMaterials.Platinum,16)
                .outputItems(item("liquid_honkai_detector",1),item("honkai_detector_calibration_report",1)).save(provider);
        Hk3LiquidLoopRecipes.register(provider);
        recovery(provider);
    }
    /** 各残液独立处理，回收小于投入；不可再生部分最终转成可处置的惰性灰分。 */
    private static void recovery(Consumer<FinishedRecipe> provider) {
        // 修订100：基础再生先给SMR证据；SMR完成后才开放扩展回收种类。
        recipe(Hk3IndustrialRecipeTypes.REGENERATION,"industrial_analysis_reagent_recovery",7,600,"RN-SMR",null)
                .inputFluids(fluid("spent_analysis_reagent",500),GTMaterials.DistilledWater.getFluid(1000))
                .inputItems(item("separation_filter",2)).inputItems(TagPrefix.dust,GTMaterials.Carbon,8)
                .outputFluids(fluid("honkai_analysis_reagent",300),fluid("unrecoverable_process_effluent",200)).save(provider);
        for(String residual:new String[]{"crystallization_residual_liquid","fuel_refining_residual"})
            recipe(Hk3IndustrialRecipeTypes.REGENERATION,"industrial_recover_"+residual,8,700,"RN-SMR",null)
                    .inputFluids(fluid(residual,1000)).inputItems(item("separation_filter",4))
                    .inputItems(TagPrefix.dust,GTMaterials.Carbon,16)
                    .outputFluids(fluid("honkai_separation_medium",200),fluid("unrecoverable_process_effluent",800)).save(provider);
        recipe(Hk3IndustrialRecipeTypes.REGENERATION,"industrial_coolant_reconditioning",9,600,"RN-SMR",null)
                .inputFluids(fluid("hot_honkai_coolant",500),GTMaterials.DistilledWater.getFluid(1000))
                .inputItems(item("separation_filter",1)).inputItems(TagPrefix.dust,GTMaterials.Silver,1)
                .outputFluids(fluid("honkai_coolant",450),fluid("lost_coolant_residue",50)).save(provider);
        recipe(Hk3IndustrialRecipeTypes.REGENERATION,"industrial_lost_coolant_treatment",10,400,"RN-BCE",null)
                .inputFluids(fluid("lost_coolant_residue",1000)).inputItems(TagPrefix.dust,GTMaterials.Carbon,16)
                .outputFluids(fluid("unrecoverable_process_effluent",1000)).save(provider);
        recipe(Hk3IndustrialRecipeTypes.REGENERATION,"industrial_effluent_solidification",11,800,"RN-BCE",null)
                .inputFluids(fluid("unrecoverable_process_effluent",1000)).inputItems(TagPrefix.dust,GTMaterials.Stone,32)
                .inputItems(TagPrefix.dust,GTMaterials.Carbon,16).outputItems(item("inactive_fuel_residue",16)).save(provider);
        recipe(Hk3IndustrialRecipeTypes.REGENERATION,"industrial_tail_material_treatment",12,600,"RN-BCE",null)
                .inputItems(item("fuel_blending_residue",16)).inputItems(TagPrefix.dust,GTMaterials.Carbon,4)
                .inputFluids(GTMaterials.Water.getFluid(1000)).outputItems(item("inactive_fuel_residue",8)).save(provider);
        recipe(GTRecipeTypes.CENTRIFUGE_RECIPES,"industrial_inert_residue_disposal",1,400,null,null)
                .inputItems(item("inactive_fuel_residue",16)).inputFluids(GTMaterials.Water.getFluid(1000))
                .outputItems(TagPrefix.dust,GTMaterials.Ash,16).save(provider);
    }
    public static void injection(Consumer<FinishedRecipe> provider) {
        recipe(Hk3IndustrialRecipeTypes.NETWORK_INJECTION,"industrial_inject_liquid_honkai_fuel",1,400,"RN-HFB",null)
                .inputFluids(fluid("liquid_honkai_fuel",16000))
                .inputItems(item("honkai_adapted_circuit_substrate",16),item("fuel_matrix",8),item("honkai_reference_sample",2))
                .addData(Hk3LiquidProcessMachine.CREDIT,16000L).save(provider);
        recipe(Hk3IndustrialRecipeTypes.NETWORK_INJECTION,"industrial_inject_honkai_crystal",2,240,"RN-HFB",null)
                .inputItems(new ItemStack(HonkaiMaterialItems.HONKAI_ENERGY_CRYSTAL.get(),128),
                        new ItemStack(HonkaiMaterialItems.COMPRESSED_HONKAI_CORE.get(),8),item("honkai_adapted_circuit_substrate",8))
                .addData(Hk3LiquidProcessMachine.CREDIT,6400L).save(provider);
        recipe(Hk3IndustrialRecipeTypes.NETWORK_INJECTION,"industrial_inject_concentrated_fuel",3,600,"RN-HFB",null)
                .inputFluids(fluid("concentrated_liquid_honkai_fuel",8000))
                .inputItems(item("honkai_adapted_circuit_substrate",24),item("fuel_matrix",16),item("honkai_reference_sample",4))
                .addData(Hk3LiquidProcessMachine.CREDIT,16000L).save(provider);
    }
}

// 【变更记录 · 修订161】2026-10-17 14:11:55：本轮仅将活动类名、资源与工业配方引用迁移为长期业务命名；历史备注保留，不代表旧逻辑已全部按现行设计重写。
