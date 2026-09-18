package com.sirin.hk3gtl.common.recipe.machine;



import com.gregtechceu.gtceu.api.GTValues;
import com.gregtechceu.gtceu.common.data.GTRecipeTypes;
import com.gregtechceu.gtceu.data.recipe.CustomTags;
import com.sirin.hk3gtl.common.block.CasingBlocks;
import com.sirin.hk3gtl.common.constants.Hk3Tiers;
import com.sirin.hk3gtl.common.constants.Hk3Values;
import com.sirin.hk3gtl.common.item.abyss.AbyssCircuitItems;
import com.sirin.hk3gtl.common.item.abyss.AbyssFunctionalItems;
import com.sirin.hk3gtl.common.item.honkai.HonkaiMaterialItems;
import com.sirin.hk3gtl.common.machine.Hk3MachinesAbyssStage;
import com.sirin.hk3gtl.common.machine.Hk3MachinesMaxStage;
import com.sirin.hk3gtl.common.material.Hk3Materials;
import com.sirin.hk3gtl.common.research.Hk3RecipeResearchGate;
import net.minecraft.data.recipes.FinishedRecipe;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.block.Block;
import net.minecraftforge.registries.RegistryObject;
import org.gtlcore.gtlcore.common.data.GTLItems;

import java.util.function.Consumer;

/**
 * v0.3 控制器配方（海渊桶 12 台中除 P1 的 8 台）。
 */
public class ControllerRecipes {

    private static final long MAX_EUT = Hk3Values.VA_LONG[GTValues.MAX];
    private static final long AB1_EUT = Hk3Values.VA_LONG[Hk3Tiers.ABYSS_1];
    private static final long AB2_EUT = Hk3Values.VA_LONG[Hk3Tiers.ABYSS_2];

    public static void register(Consumer<FinishedRecipe> provider) {
        addMaxStageControllers(provider);
        addAbyssStageControllers(provider);
    }

    private static void addMaxStageControllers(Consumer<FinishedRecipe> provider) {
        GTRecipeTypes.ASSEMBLER_RECIPES.recipeBuilder("hk3gtl_void_archives_analysis_chamber")
                .inputItems(new ItemStack(CasingBlocks.CASING_ABYSS_RESEARCH.get(), 16))
                .inputItems(GTLItems.SENSOR_MAX.asStack(8))
                .inputItems(CustomTags.MAX_CIRCUITS, 16)
                .inputItems(new ItemStack(HonkaiMaterialItems.ANCIENT_LEGACY.get(), 2))
                .outputItems(Hk3MachinesMaxStage.VOID_ARCHIVES_ANALYSIS_CHAMBER.asStack())
                .duration(1200)
                .EUt(MAX_EUT)
                .save(provider);
        Hk3RecipeResearchGate.bind("assembler", "hk3gtl_void_archives_analysis_chamber", "R-AB-008");

        GTRecipeTypes.ASSEMBLER_RECIPES.recipeBuilder("hk3gtl_reason_reconstruction_array")
                .inputItems(new ItemStack(CasingBlocks.CASING_ABYSS_RESEARCH.get(), 16))
                .inputItems(GTLItems.FIELD_GENERATOR_MAX.asStack(8))
                .inputItems(CustomTags.MAX_CIRCUITS, 16)
                .inputItems(new ItemStack(HonkaiMaterialItems.HONKAI_ENERGY_CRYSTAL.get(), 64))
                .outputItems(Hk3MachinesMaxStage.REASON_RECONSTRUCTION_ARRAY.asStack())
                .duration(1200)
                .EUt(MAX_EUT)
                .save(provider);
        Hk3RecipeResearchGate.bind("assembler", "hk3gtl_reason_reconstruction_array", "R-AB-009");

        GTRecipeTypes.ASSEMBLER_RECIPES.recipeBuilder("hk3gtl_honkai_eu_converter")
                .inputItems(new ItemStack(CasingBlocks.CASING_ABYSS_ENERGY.get(), 16))
                .inputItems(GTLItems.ELECTRIC_MOTOR_MAX.asStack(8))
                .inputItems(GTLItems.ELECTRIC_PUMP_MAX.asStack(8))
                .inputItems(CustomTags.MAX_CIRCUITS, 8)
                .outputItems(Hk3MachinesMaxStage.HONKAI_EU_CONVERTER.asStack())
                .duration(900)
                .EUt(MAX_EUT)
                .save(provider);
        Hk3RecipeResearchGate.bind("assembler", "hk3gtl_honkai_eu_converter", "R-AB-006");

        // 崩坏能网络注入器（双能源引擎 D-01 充网入口）：门控绑定无线崩坏能传输原理研究
        GTRecipeTypes.ASSEMBLER_RECIPES.recipeBuilder("hk3gtl_honkai_network_injector")
                .inputItems(new ItemStack(CasingBlocks.CASING_ABYSS_ENERGY.get(), 16))
                .inputItems(GTLItems.EMITTER_MAX.asStack(8))
                .inputItems(GTLItems.ELECTRIC_PUMP_MAX.asStack(8))
                .inputItems(CustomTags.MAX_CIRCUITS, 8)
                .outputItems(Hk3MachinesMaxStage.HONKAI_NETWORK_INJECTOR.asStack())
                .duration(900)
                .EUt(MAX_EUT)
                .save(provider);
        Hk3RecipeResearchGate.bind("assembler", "hk3gtl_honkai_network_injector", "R-AB-009");

        GTRecipeTypes.ASSEMBLER_RECIPES.recipeBuilder("hk3gtl_abyss_circuit_foundry")
                .inputItems(new ItemStack(CasingBlocks.CASING_ABYSS_MECHANICAL.get(), 32))
                .inputItems(GTLItems.ROBOT_ARM_MAX.asStack(8))
                .inputItems(new ItemStack(AbyssCircuitItems.CIRCUIT_ABYSS_1.get(), 16))
                .inputItems(new ItemStack(HonkaiMaterialItems.HONKAI_ENERGY_CRYSTAL.get(), 64))
                .outputItems(Hk3MachinesMaxStage.ABYSS_CIRCUIT_FOUNDRY.asStack())
                .duration(1200)
                .EUt(AB1_EUT)
                .save(provider);
        Hk3RecipeResearchGate.bind("assembler", "hk3gtl_abyss_circuit_foundry", "R-AB-005");
    }

    private static void addAbyssStageControllers(Consumer<FinishedRecipe> provider) {
        buildAbyssController(provider, "hk3gtl_large_honkai_reactor",
                Hk3MachinesAbyssStage.LARGE_HONKAI_REACTOR,
                CasingBlocks.CASING_ABYSS_ENERGY, 32,
                AbyssFunctionalItems.ABYSS_REACTOR_CORE, 4,
                AbyssCircuitItems.CIRCUIT_ABYSS_2, 16,
                AB2_EUT, "R-AB-007");

        buildAbyssController(provider, "hk3gtl_abyss_deep_smeltery",
                Hk3MachinesAbyssStage.ABYSS_DEEP_SMELTERY,
                CasingBlocks.CASING_REINFORCED_SOULIUM, 32,
                AbyssFunctionalItems.ABYSS_STABLE_FRAME, 4,
                AbyssCircuitItems.CIRCUIT_ABYSS_2, 16,
                AB2_EUT, "R-AB-013");

        buildAbyssController(provider, "hk3gtl_abyss_precision_workshop",
                Hk3MachinesAbyssStage.ABYSS_PRECISION_WORKSHOP,
                CasingBlocks.CASING_ABYSS_MECHANICAL, 32,
                AbyssFunctionalItems.ABYSS_DATA_CORE, 4,
                AbyssCircuitItems.CIRCUIT_ABYSS_2, 16,
                AB2_EUT, "R-AB-012");

        buildAbyssController(provider, "hk3gtl_abyss_particle_research_ring",
                Hk3MachinesAbyssStage.ABYSS_PARTICLE_RESEARCH_RING,
                CasingBlocks.CASING_ABYSS_RESEARCH, 32,
                AbyssFunctionalItems.ABYSS_MEASUREMENT_ARRAY, 4,
                AbyssCircuitItems.CIRCUIT_ABYSS_3, 16,
                Hk3Values.VA_LONG[Hk3Tiers.ABYSS_3], "R-AB-016");
    }

    private static void buildAbyssController(
            Consumer<FinishedRecipe> provider,
            String recipeId,
            com.gregtechceu.gtceu.api.machine.MultiblockMachineDefinition machine,
            RegistryObject<Block> casing,
            int casingCount,
            RegistryObject<net.minecraft.world.item.Item> coreItem,
            int coreCount,
            RegistryObject<net.minecraft.world.item.Item> circuit,
            int circuitCount,
            long eut,
            String researchId) {

        GTRecipeTypes.ASSEMBLER_RECIPES.recipeBuilder(recipeId)
                .inputItems(new ItemStack(casing.get(), casingCount))
                .inputItems(new ItemStack(coreItem.get(), coreCount))
                .inputItems(new ItemStack(circuit.get(), circuitCount))
                .inputItems(GTLItems.ROBOT_ARM_MAX.asStack(4))
                .inputFluids(Hk3Materials.LIQUID_HONKAI_ENERGY.getFluid(4608))
                .outputItems(machine.asStack())
                .duration(1200)
                .EUt(eut)
                .save(provider);

        if (researchId != null) {
            Hk3RecipeResearchGate.bind("assembler", recipeId, researchId);
        }
    }
}
