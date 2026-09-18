package com.sirin.hk3gtl.common.recipe.finality;

import com.sirin.hk3gtl.common.block.CasingBlocks;
import com.sirin.hk3gtl.common.constants.Hk3Tiers;
import com.sirin.hk3gtl.common.constants.Hk3Values;
import com.sirin.hk3gtl.common.item.finality.FinalityCircuitItems;
import com.sirin.hk3gtl.common.item.finality.FinalityComponentItems;
import com.sirin.hk3gtl.common.item.honkai.HonkaiMaterialItems;
import com.sirin.hk3gtl.common.item.quantum.QuantumCircuitItems;
import com.sirin.hk3gtl.common.material.Hk3Materials;
import com.sirin.hk3gtl.common.recipe.Hk3RecipeTypesFinality;
import com.sirin.hk3gtl.common.recipe.Hk3RecipeTypesWonder;
import com.sirin.hk3gtl.common.research.Hk3RecipeResearchGate;
import net.minecraft.data.recipes.FinishedRecipe;
import net.minecraft.world.item.ItemStack;

import java.util.function.Consumer;


public final class FinalityStageRecipes {

    private static final long F1_EUT = Hk3Values.VA_LONG[Hk3Tiers.FINALITY_1];
    private static final long F2_EUT = Hk3Values.VA_LONG[Hk3Tiers.FINALITY_2];
    private static final long F3_EUT = Hk3Values.VA_LONG[Hk3Tiers.FINALITY_3];
    private static final long F4_EUT = Hk3Values.VA_LONG[Hk3Tiers.FINALITY_4];

    private FinalityStageRecipes() {}

    public static void register(Consumer<FinishedRecipe> provider) {
        addFinalityCircuitRecipes(provider);
        addFinalityMachineRecipes(provider);
        addWonderMachineRecipes(provider);
    }

    private static void addFinalityCircuitRecipes(Consumer<FinishedRecipe> provider) {
        Hk3RecipeTypesFinality.SHIPBOARD_FINALITY_OBSERVATION.recipeBuilder("finality_circuit_1_synthesis")
                .inputItems(new ItemStack(QuantumCircuitItems.CIRCUIT_QUANTUM_4.get(), 32))
                .inputItems(new ItemStack(HonkaiMaterialItems.ANCIENT_LEGACY.get(), 8))
                .inputItems(new ItemStack(HonkaiMaterialItems.ADVANCED_GAZE_BUFFER_UNIT.get(), 64))
                .inputFluids(Hk3Materials.LIQUID_HONKAI_ENERGY.getFluid(147456))
                .outputItems(new ItemStack(FinalityCircuitItems.CIRCUIT_FINALITY_1.get(), 4))
                .duration(2400)
                .EUt(F1_EUT)
                .save(provider);
        Hk3RecipeResearchGate.bind("shipboard_finality_observation", "finality_circuit_1_synthesis", "R-FN-001");

        Hk3RecipeTypesFinality.SHIPBOARD_ENDGAME_COORDINATION.recipeBuilder("finality_circuit_2_synthesis")
                .inputItems(new ItemStack(FinalityCircuitItems.CIRCUIT_FINALITY_1.get(), 64))
                .inputItems(new ItemStack(HonkaiMaterialItems.DATA_RESEARCH_PACKAGE.get(), 32))
                .inputItems(new ItemStack(HonkaiMaterialItems.STABILIZED_HONKAI_CRYSTAL.get(), 512))
                .inputFluids(Hk3Materials.LIQUID_HONKAI_ENERGY.getFluid(196608))
                .outputItems(new ItemStack(FinalityCircuitItems.CIRCUIT_FINALITY_2.get(), 4))
                .duration(2800)
                .EUt(F2_EUT)
                .save(provider);
        Hk3RecipeResearchGate.bind("shipboard_endgame_coordination", "finality_circuit_2_synthesis", "R-FN-004");

        Hk3RecipeTypesFinality.FINALITY_CIVILIZATION_CONSTRUCTION.recipeBuilder("finality_circuit_3_synthesis")
                .inputItems(new ItemStack(FinalityCircuitItems.CIRCUIT_FINALITY_2.get(), 64))
                .inputItems(new ItemStack(HonkaiMaterialItems.WORLD_BUBBLE_SAMPLE.get(), 32))
                .inputItems(new ItemStack(HonkaiMaterialItems.ANCIENT_LEGACY.get(), 16))
                .inputFluids(Hk3Materials.LIQUID_HONKAI_ENERGY.getFluid(262144))
                .outputItems(new ItemStack(FinalityCircuitItems.CIRCUIT_FINALITY_3.get(), 2))
                .duration(3200)
                .EUt(F3_EUT)
                .save(provider);
        Hk3RecipeResearchGate.bind("finality_civilization_construction", "finality_circuit_3_synthesis", "R-FN-006");

        Hk3RecipeTypesFinality.CIVILIZATION_VALIDATION.recipeBuilder("finality_circuit_4_synthesis")
                .inputItems(new ItemStack(FinalityCircuitItems.CIRCUIT_FINALITY_3.get(), 64))
                .inputItems(new ItemStack(HonkaiMaterialItems.ANCIENT_LEGACY.get(), 32))
                .inputItems(new ItemStack(HonkaiMaterialItems.STABILIZED_HONKAI_CRYSTAL.get(), 1024))
                .inputFluids(Hk3Materials.LIQUID_HONKAI_ENERGY.getFluid(327680))
                .outputItems(new ItemStack(FinalityCircuitItems.CIRCUIT_FINALITY_4.get(), 2))
                .duration(3600)
                .EUt(F4_EUT)
                .save(provider);
        Hk3RecipeResearchGate.bind("civilization_validation", "finality_circuit_4_synthesis", "R-FN-008");
    }

    private static void addFinalityMachineRecipes(Consumer<FinishedRecipe> provider) {
        Hk3RecipeTypesFinality.HYPERION_FLAGSHIP_PROCESSING.recipeBuilder("hyperion_core_assembly")
                .inputItems(new ItemStack(FinalityCircuitItems.CIRCUIT_FINALITY_1.get(), 8))
                .inputItems(new ItemStack(HonkaiMaterialItems.ANCIENT_LEGACY.get(), 8))
                .outputItems(new ItemStack(FinalityComponentItems.ROBOT_ARM_FINALITY_1.get(), 4))
                .duration(1600)
                .EUt(F1_EUT)
                .save(provider);

        Hk3RecipeTypesFinality.SHIPBOARD_FINALITY_OBSERVATION.recipeBuilder("shipboard_sensor_bundle")
                .inputItems(new ItemStack(FinalityCircuitItems.CIRCUIT_FINALITY_1.get(), 8))
                .inputItems(new ItemStack(HonkaiMaterialItems.WORLD_BUBBLE_SAMPLE.get(), 8))
                .outputItems(new ItemStack(FinalityComponentItems.SENSOR_FINALITY_1.get(), 4))
                .duration(1600)
                .EUt(F1_EUT)
                .save(provider);

        Hk3RecipeTypesFinality.SHIPBOARD_DUAL_ENERGY_REACTOR.recipeBuilder("shipboard_dual_energy_bundle")
                .inputItems(new ItemStack(FinalityCircuitItems.CIRCUIT_FINALITY_1.get(), 6))
                .inputItems(new ItemStack(HonkaiMaterialItems.COMPRESSED_HONKAI_CORE.get(), 32))
                .outputItems(new ItemStack(FinalityComponentItems.ELECTRIC_PUMP_FINALITY_1.get(), 4))
                .duration(1600)
                .EUt(F1_EUT)
                .save(provider);

        Hk3RecipeTypesFinality.SHIPBOARD_ENDGAME_COORDINATION.recipeBuilder("shipboard_coordination_engine")
                .inputItems(new ItemStack(FinalityCircuitItems.CIRCUIT_FINALITY_2.get(), 8))
                .inputItems(new ItemStack(HonkaiMaterialItems.DATA_RESEARCH_PACKAGE.get(), 8))
                .outputItems(new ItemStack(FinalityComponentItems.FIELD_GENERATOR_FINALITY_2.get(), 2))
                .duration(1800)
                .EUt(F2_EUT)
                .save(provider);

        Hk3RecipeTypesFinality.SHIPBOARD_DIVINE_KEY.recipeBuilder("divine_key_signature_frame")
                .inputItems(new ItemStack(FinalityCircuitItems.CIRCUIT_FINALITY_2.get(), 6))
                .inputItems(new ItemStack(HonkaiMaterialItems.ANCIENT_LEGACY.get(), 4))
                .outputItems(new ItemStack(FinalityComponentItems.EMITTER_FINALITY_2.get(), 2))
                .duration(1800)
                .EUt(F2_EUT)
                .save(provider);

        Hk3RecipeTypesFinality.FINALITY_CIVILIZATION_CONSTRUCTION.recipeBuilder("finality_construction_cluster")
                .inputItems(new ItemStack(FinalityCircuitItems.CIRCUIT_FINALITY_3.get(), 8))
                .inputItems(new ItemStack(HonkaiMaterialItems.STABILIZED_HONKAI_CRYSTAL.get(), 128))
                .outputItems(new ItemStack(CasingBlocks.CASING_FINALITY_VOID.get(), 16))
                .duration(2200)
                .EUt(F3_EUT)
                .save(provider);

        // 终焉「统治」机壳：此前缺产出配方，导致 finality_civilization_power_hub / honkai_annihilation_ring /
        // honkai_ultimate_fusion_core 三台控制器无机壳可造（可达性检测报死链）。补基础产线，仅用终焉3电路+稳定结晶，不依赖任何控制器。
        Hk3RecipeTypesFinality.FINALITY_CIVILIZATION_CONSTRUCTION.recipeBuilder("finality_dominion_casing")
                .inputItems(new ItemStack(FinalityCircuitItems.CIRCUIT_FINALITY_3.get(), 8))
                .inputItems(new ItemStack(HonkaiMaterialItems.STABILIZED_HONKAI_CRYSTAL.get(), 128))
                .outputItems(new ItemStack(CasingBlocks.CASING_FINALITY_DOMINION.get(), 16))
                .duration(2200)
                .EUt(F3_EUT)
                .save(provider);

        Hk3RecipeTypesFinality.CIVILIZATION_VALIDATION.recipeBuilder("civilization_validation_key")
                .inputItems(new ItemStack(FinalityCircuitItems.CIRCUIT_FINALITY_3.get(), 6))
                .inputItems(new ItemStack(HonkaiMaterialItems.ANCIENT_LEGACY.get(), 8))
                .outputItems(new ItemStack(HonkaiMaterialItems.DATA_RESEARCH_PACKAGE.get(), 12))
                .duration(2200)
                .EUt(F3_EUT)
                .save(provider);

        Hk3RecipeTypesFinality.FINALITY_ENERGY_DISTRIBUTION.recipeBuilder("finality_energy_regulator")
                .inputItems(new ItemStack(FinalityCircuitItems.CIRCUIT_FINALITY_2.get(), 8))
                .inputItems(new ItemStack(HonkaiMaterialItems.COMPRESSED_HONKAI_CORE.get(), 64))
                .outputItems(new ItemStack(FinalityComponentItems.ELECTRIC_MOTOR_FINALITY_2.get(), 4))
                .duration(1800)
                .EUt(F2_EUT)
                .save(provider);

        Hk3RecipeTypesFinality.FINALITY_ULTIMATE_MATERIAL_FORGE.recipeBuilder("finality_material_batch")
                .inputItems(new ItemStack(FinalityCircuitItems.CIRCUIT_FINALITY_3.get(), 8))
                .inputItems(new ItemStack(HonkaiMaterialItems.RAW_HONKAI_PARTICLE.get(), 4096))
                .outputItems(new ItemStack(HonkaiMaterialItems.STABILIZED_HONKAI_CRYSTAL.get(), 128))
                .duration(2400)
                .EUt(F3_EUT)
                .save(provider);

        Hk3RecipeTypesFinality.FINALITY_HONKAI_ANNIHILATION.recipeBuilder("finality_annihilation_cycle")
                .inputItems(new ItemStack(HonkaiMaterialItems.DENSE_HONKAI_FUEL_ROD.get(), 32))
                .inputFluids(Hk3Materials.LIQUID_HONKAI_ENERGY.getFluid(32768))
                .outputItems(new ItemStack(HonkaiMaterialItems.HONKAI_SUPPRESSANT.get(), 64))
                .duration(2600)
                .EUt(-F3_EUT)
                .save(provider);

        Hk3RecipeTypesFinality.GRADUATION_PERMISSION_VERIFICATION.recipeBuilder("graduation_permission_token")
                .inputItems(new ItemStack(FinalityCircuitItems.CIRCUIT_FINALITY_4.get(), 2))
                .inputItems(new ItemStack(HonkaiMaterialItems.ANCIENT_LEGACY.get(), 8))
                .outputItems(new ItemStack(HonkaiMaterialItems.DATA_RESEARCH_PACKAGE.get(), 16))
                .duration(1800)
                .EUt(F4_EUT)
                .save(provider);

        Hk3RecipeTypesFinality.CIVILIZATION_WONDER_SANCTUM.recipeBuilder("wonder_sanctum_seed")
                .inputItems(new ItemStack(FinalityCircuitItems.CIRCUIT_FINALITY_4.get(), 2))
                .inputItems(new ItemStack(HonkaiMaterialItems.WORLD_BUBBLE_SAMPLE.get(), 16))
                .outputItems(new ItemStack(CasingBlocks.CASING_FINALITY_WONDER.get(), 12))
                .duration(2200)
                .EUt(F4_EUT)
                .save(provider);
    }

    private static void addWonderMachineRecipes(Consumer<FinishedRecipe> provider) {
        Hk3RecipeTypesWonder.HONKAI_ULTIMATE_FUSION.recipeBuilder("ultimate_fusion_core")
                .inputItems(new ItemStack(HonkaiMaterialItems.COMPRESSED_HONKAI_CORE.get(), 128))
                .inputItems(new ItemStack(FinalityCircuitItems.CIRCUIT_FINALITY_4.get(), 2))
                .outputItems(new ItemStack(HonkaiMaterialItems.STABILIZED_HONKAI_CRYSTAL.get(), 256))
                .duration(2600)
                .EUt(F4_EUT)
                .save(provider);

        Hk3RecipeTypesWonder.DIVINE_KEY_GRAND_CATHEDRAL.recipeBuilder("divine_key_cathedral_protocol")
                .inputItems(new ItemStack(FinalityCircuitItems.CIRCUIT_FINALITY_3.get(), 6))
                .inputItems(new ItemStack(HonkaiMaterialItems.ANCIENT_LEGACY.get(), 12))
                .outputItems(new ItemStack(HonkaiMaterialItems.DATA_RESEARCH_PACKAGE.get(), 20))
                .duration(2400)
                .EUt(F3_EUT)
                .save(provider);

        Hk3RecipeTypesWonder.CIVILIZATION_JUDGMENT.recipeBuilder("civilization_judgment_sample")
                .inputItems(new ItemStack(FinalityCircuitItems.CIRCUIT_FINALITY_4.get(), 2))
                .inputItems(new ItemStack(HonkaiMaterialItems.WORLD_BUBBLE_SAMPLE.get(), 16))
                .outputItems(new ItemStack(HonkaiMaterialItems.ANCIENT_LEGACY.get(), 4))
                .duration(2400)
                .EUt(F4_EUT)
                .save(provider);

        Hk3RecipeTypesWonder.CIVILIZATION_MEMORY_ETERNAL.recipeBuilder("memory_eternal_archive")
                .inputItems(new ItemStack(FinalityCircuitItems.CIRCUIT_FINALITY_2.get(), 6))
                .inputItems(new ItemStack(HonkaiMaterialItems.DATA_RESEARCH_PACKAGE.get(), 24))
                .outputItems(new ItemStack(HonkaiMaterialItems.ANCIENT_LEGACY.get(), 3))
                .duration(2200)
                .EUt(F2_EUT)
                .save(provider);

        Hk3RecipeTypesWonder.MYRIAD_REALMS_COMMUNICATION.recipeBuilder("myriad_comm_package")
                .inputItems(new ItemStack(FinalityCircuitItems.CIRCUIT_FINALITY_2.get(), 4))
                .inputItems(new ItemStack(HonkaiMaterialItems.WORLD_BUBBLE_SAMPLE.get(), 8))
                .outputItems(new ItemStack(HonkaiMaterialItems.DATA_RESEARCH_PACKAGE.get(), 12))
                .duration(1800)
                .EUt(F2_EUT)
                .save(provider);

        Hk3RecipeTypesWonder.DESTINY_WEAVING.recipeBuilder("destiny_weaving_kernel")
                .inputItems(new ItemStack(FinalityCircuitItems.CIRCUIT_FINALITY_3.get(), 4))
                .inputItems(new ItemStack(HonkaiMaterialItems.ANCIENT_LEGACY.get(), 6))
                .outputItems(new ItemStack(CasingBlocks.CASING_FINALITY_SANCTUM.get(), 12))
                .duration(2200)
                .EUt(F3_EUT)
                .save(provider);

        Hk3RecipeTypesWonder.CIVILIZATION_EYE_OBSERVATION.recipeBuilder("civilization_eye_projection")
                .inputItems(new ItemStack(FinalityCircuitItems.CIRCUIT_FINALITY_3.get(), 4))
                .inputItems(new ItemStack(HonkaiMaterialItems.WORLD_BUBBLE_SAMPLE.get(), 12))
                .outputItems(new ItemStack(HonkaiMaterialItems.ADVANCED_GAZE_BUFFER_UNIT.get(), 12))
                .duration(2200)
                .EUt(F3_EUT)
                .save(provider);

        Hk3RecipeTypesWonder.CYCLE_NARRATION.recipeBuilder("cycle_narration_record")
                .inputItems(new ItemStack(FinalityCircuitItems.CIRCUIT_FINALITY_2.get(), 4))
                .inputItems(new ItemStack(HonkaiMaterialItems.ANCIENT_LEGACY.get(), 2))
                .inputItems(new ItemStack(HonkaiMaterialItems.WORLD_BUBBLE_SAMPLE.get(), 8))
                .outputItems(new ItemStack(HonkaiMaterialItems.DATA_RESEARCH_PACKAGE.get(), 12))
                .duration(1800)
                .EUt(F2_EUT)
                .save(provider);

        Hk3RecipeTypesWonder.CIVILIZATION_STARSHIP_EXHIBITION.recipeBuilder("starship_exhibition_sign")
                .inputItems(new ItemStack(FinalityCircuitItems.CIRCUIT_FINALITY_3.get(), 4))
                .inputItems(new ItemStack(HonkaiMaterialItems.ANCIENT_LEGACY.get(), 8))
                .outputItems(new ItemStack(CasingBlocks.CASING_FINALITY_HYPERION.get(), 12))
                .duration(2200)
                .EUt(F3_EUT)
                .save(provider);

        Hk3RecipeTypesWonder.PROOF_OF_EXISTENCE.recipeBuilder("proof_of_existence_token")
                .inputItems(new ItemStack(FinalityCircuitItems.CIRCUIT_FINALITY_4.get(), 1))
                .inputItems(new ItemStack(HonkaiMaterialItems.WORLD_BUBBLE_SAMPLE.get(), 10))
                .outputItems(new ItemStack(HonkaiMaterialItems.ANCIENT_LEGACY.get(), 2))
                .duration(2000)
                .EUt(F4_EUT)
                .save(provider);

        Hk3RecipeTypesWonder.ULTIMATE_MEDITATION.recipeBuilder("ultimate_meditation_focus")
                .inputItems(new ItemStack(FinalityCircuitItems.CIRCUIT_FINALITY_3.get(), 2))
                .inputItems(new ItemStack(HonkaiMaterialItems.GAZE_BUFFER_UNIT.get(), 48))
                .inputItems(new ItemStack(HonkaiMaterialItems.STABILIZED_HONKAI_CRYSTAL.get(), 128))
                .outputItems(new ItemStack(HonkaiMaterialItems.ADVANCED_GAZE_BUFFER_UNIT.get(), 16))
                .duration(2000)
                .EUt(F3_EUT)
                .save(provider);

        Hk3RecipeTypesWonder.GRAND_CONVERGENCE.recipeBuilder("grand_convergence_frame")
                .inputItems(new ItemStack(FinalityCircuitItems.CIRCUIT_FINALITY_4.get(), 2))
                .inputItems(new ItemStack(HonkaiMaterialItems.ANCIENT_LEGACY.get(), 12))
                .outputItems(new ItemStack(CasingBlocks.CASING_FINALITY_WONDER.get(), 16))
                .duration(2600)
                .EUt(F4_EUT)
                .save(provider);
    }
}
