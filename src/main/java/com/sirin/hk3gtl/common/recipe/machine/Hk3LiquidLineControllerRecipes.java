package com.sirin.hk3gtl.common.recipe.machine;

import com.gregtechceu.gtceu.api.GTValues;
import com.gregtechceu.gtceu.api.data.tag.TagPrefix;
import com.gregtechceu.gtceu.common.data.GTMaterials;
import com.gregtechceu.gtceu.common.data.GTRecipeTypes;
import com.gregtechceu.gtceu.data.recipe.CustomTags;
import com.sirin.hk3gtl.common.constants.Hk3Values;
import com.sirin.hk3gtl.common.machine.Hk3MachinesImpl;
import net.minecraft.data.recipes.FinishedRecipe;
import java.util.function.Consumer;

/** 中文维护备注：历史变更说明已整理；当前实现以代码为准。 */
/**
 * 【变更记录 #1】2026-09-24 16:38:00（内测5修订66）
 * 删除：只有三台控制器、没有研究顺序的旧清单。新增：七台正式控制器的多部件装配。
 * 修改：材料全部来自MAX前置，不要求本机独占产物；用途：保证首台设备与首轮实验可达。
 */
/**
 * 【变更记录 #2】2026-09-27 03:06:43（第 2 次备注 · 内测5修订88）
 * 删除：无，保留历史说明和原有结构几何。
 * 新增：负责人确认的GT MAX机械方块一对一改装配方：组装机、电路1、100 tick、30 EU/t，无额外材料。
 * 修改：接入工业接口机械方块；保留必要能力的全局数量约束。
 * 用途：让多余接口可以封闭，不用填充方块冒充真实仓室能力。
 */
/**
 * 【变更记录 #3】2026-10-15 01:15:46（第3次备注 · 内测5修订156）
 * 删除：I09–I12制造入口误用RN-CCE的门槛，避免前驱产线反被后续结晶研究锁住。
 * 新增：I13既有工业装配模板，以及S02–S05消耗上一阶控制器的研究所升级装配。
 * 修改：工业门槛与执行契约的SSP/NBS/NRA/NSP/HRC一致；研究所复用S01现成材料、1200tick和MAX耗电。
 * 用途：批准建筑在生存中具有获取入口；升级沿用ALE/QLE/ILE/CLE权限，不引入新材料或研究费用。
 */
public final class Hk3LiquidLineControllerRecipes {
    private Hk3LiquidLineControllerRecipes() {}
    public static void register(Consumer<FinishedRecipe> provider) {
        // MAX机壳一对一改装；无研究门槛，不使用本产线的产物，避免接口填充件自锁。
        GTRecipeTypes.ASSEMBLER_RECIPES.recipeBuilder("hk3gtl_industrial_port_casing")
                .inputItems(new net.minecraft.world.item.ItemStack(
                        com.sirin.hk3gtl.common.multiblock.pattern.Hk3StructureBlocks.require("gtceu:max_machine_casing")))
                .outputItems(new net.minecraft.world.item.ItemStack(
                        com.sirin.hk3gtl.common.registration.Hk3IndustrialContent.blocks().get("industrial_port_casing").get()))
                .circuitMeta(1).duration(100).EUt(30).save(provider);
        controller(provider,"industrial_liquid_honkai_fractionation_controller",Hk3MachinesImpl.LIQUID_HONKAI_FRACTIONATION_CENTER,8,"RN-HSA");
        controller(provider,"industrial_liquid_honkai_stabilization_tower_controller",Hk3MachinesImpl.LIQUID_HONKAI_STABILIZATION_TOWER,10,"RN-LSE");
        controller(provider,"industrial_stabilization_medium_regeneration_tower_controller",Hk3MachinesImpl.STABILIZATION_MEDIUM_REGENERATION_TOWER,12,"RN-BCE");
        controller(provider,"industrial_honkai_fuel_blending_controller",Hk3MachinesImpl.HONKAI_FUEL_BLENDING_PLANT,12,"RN-BCE");
        controller(provider,"industrial_honkai_detector_calibration_controller",Hk3MachinesImpl.HONKAI_DETECTOR_CALIBRATION_BENCH,8,"RN-BCE");
        controller(provider,"industrial_core_crystallization_controller",Hk3MachinesImpl.IMITATION_CORE_CRYSTALLIZATION_CHAMBER,16,"RN-CCE");
        controller(provider,"industrial_soulium_precursor_mixing_controller",Hk3MachinesImpl.SOULIUM_PRECURSOR_MIXING_KETTLE,16,"RN-SSP");
        controller(provider,"industrial_nano_basic_unit_synthesizer_controller",Hk3MachinesImpl.NANO_BASIC_UNIT_SYNTHESIZER,16,"RN-NBS");
        controller(provider,"industrial_nanobot_assembly_array_controller",Hk3MachinesImpl.NANOBOT_ASSEMBLY_ARRAY,16,"RN-NRA");
        controller(provider,"industrial_nano_programming_chamber_controller",Hk3MachinesImpl.NANO_SELF_ORGANIZING_PROGRAMMING_CHAMBER,16,"RN-NSP");
        controller(provider,"industrial_honkai_resistant_coating_array_controller",Hk3MachinesImpl.I13_HONKAI_RESISTANT_COATING_ARRAY,16,"RN-HRC");
        // 修订213：批准的魂钢工艺复用前级装配用料，首台控制器不要求本机产物。
        controller(provider,"industrial_soulium_polymerization_controller",com.sirin.hk3gtl.common.machine.Hk3IndustrialExtensionMachines.SOULIUM_POLYMERIZATION_DIE_CASTER,16,"RN-SPC");
        controller(provider,"industrial_soulium_reconstruction_controller",com.sirin.hk3gtl.common.machine.Hk3IndustrialExtensionMachines.SOULIUM_RECONSTRUCTION_ANNEALING_FURNACE,16,"RN-SRA");
        controller(provider,"industrial_soulium_precision_controller",com.sirin.hk3gtl.common.machine.Hk3IndustrialExtensionMachines.SOULIUM_PRECISION_PROCESSING_CENTER,16,"RN-SPM");
        researchUpgrades(provider);
        controller(provider,"industrial_honkai_fuel_concentration_controller",Hk3MachinesImpl.HONKAI_FUEL_CONCENTRATION_PLANT,16,"RN-HFB");
        controller(provider,"hk3gtl_honkai_network_injector",com.sirin.hk3gtl.common.machine.Hk3MachinesMaxStage.HONKAI_NETWORK_INJECTOR,16,"RN-HFB");
    }
    /** 复用S01装配数值，每次额外消耗上一阶主控；研究后才开放，无新阶级专有产物造成自锁。 */
    private static void researchUpgrades(Consumer<FinishedRecipe> provider) {
        String[] gates = {"RN-ALE", "RN-QLE", "RN-ILE", "RN-CLE"};
        for (int stage = 2; stage <= 5; stage++) {
            String id = "hk3gtl_research_institute_upgrade_s0" + stage;
            GTRecipeTypes.ASSEMBLER_RECIPES.recipeBuilder(id)
                    .inputItems(com.sirin.hk3gtl.common.machine.research.Hk3ResearchMachines.institute(stage - 1).asStack())
                    .inputItems(TagPrefix.plate, GTMaterials.TungstenSteel, 16)
                    .inputItems(CustomTags.MAX_CIRCUITS, 4)
                    .inputItems(org.gtlcore.gtlcore.common.data.GTLItems.SENSOR_MAX.asStack(4))
                    .inputItems(org.gtlcore.gtlcore.common.data.GTLItems.EMITTER_MAX.asStack(2))
                    .inputItems(TagPrefix.wireGtSingle, GTMaterials.Platinum, 8)
                    .outputItems(com.sirin.hk3gtl.common.machine.research.Hk3ResearchMachines.institute(stage).asStack())
                    .duration(1200).EUt(Hk3Values.VA_LONG[GTValues.MAX]).save(provider);
            com.sirin.hk3gtl.common.research.Hk3RecipeResearchGate.bind("assembler", id, gates[stage - 2]);
        }
    }
    /** 方块数量为整数，焊锡单位mB；单次输出一个控制器，配方ID沿用已存档的路径。 */
    private static void controller(Consumer<FinishedRecipe> provider,String id,
            com.gregtechceu.gtceu.api.machine.MultiblockMachineDefinition machine,int circuits,String gate) {
        GTRecipeTypes.ASSEMBLER_RECIPES.recipeBuilder(id)
                .inputItems(CustomTags.MAX_CIRCUITS,circuits)
                .inputItems(org.gtlcore.gtlcore.common.data.GTLItems.ELECTRIC_PUMP_MAX.asStack(4))
                .inputItems(org.gtlcore.gtlcore.common.data.GTLItems.SENSOR_MAX.asStack(4))
                .inputItems(TagPrefix.plate,GTMaterials.TungstenSteel,32)
                .inputItems(TagPrefix.frameGt,GTMaterials.TungstenSteel,12)
                .inputItems(TagPrefix.pipeLargeFluid,GTMaterials.StainlessSteel,16)
                .inputItems(TagPrefix.wireGtSingle,GTMaterials.Platinum,24)
                .inputItems(TagPrefix.gem,GTMaterials.Diamond,12)
                .inputItems(TagPrefix.foil,GTMaterials.Polybenzimidazole,32)
                .inputFluids(GTMaterials.SolderingAlloy.getFluid(2304))
                .outputItems(machine.asStack()).duration(2400).EUt(Hk3Values.VA_LONG[GTValues.MAX]).save(provider);
        com.sirin.hk3gtl.common.research.Hk3RecipeResearchGate.bind("assembler",id,gate);
    }
}

// 【变更记录 · 修订161】2026-10-17 14:11:55：本轮仅将活动类名、资源与工业配方引用迁移为长期业务命名；历史备注保留，不代表旧逻辑已全部按现行设计重写。
