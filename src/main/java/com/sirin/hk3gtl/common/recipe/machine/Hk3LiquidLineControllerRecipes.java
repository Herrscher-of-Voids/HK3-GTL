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

 
