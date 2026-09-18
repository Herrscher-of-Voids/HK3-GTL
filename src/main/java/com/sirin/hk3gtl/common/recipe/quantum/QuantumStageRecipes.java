package com.sirin.hk3gtl.common.recipe.quantum;

import com.sirin.hk3gtl.common.block.CasingBlocks;
import com.sirin.hk3gtl.common.constants.Hk3Tiers;
import com.sirin.hk3gtl.common.constants.Hk3Values;
import com.sirin.hk3gtl.common.item.abyss.AbyssComponentItems;
import com.sirin.hk3gtl.common.item.finality.FinalityCircuitItems;
import com.sirin.hk3gtl.common.item.honkai.HonkaiMaterialItems;
import com.sirin.hk3gtl.common.item.imaginary.ImaginaryCircuitItems;
import com.sirin.hk3gtl.common.item.quantum.QuantumCircuitItems;
import com.sirin.hk3gtl.common.item.quantum.QuantumComponentItems;
import com.sirin.hk3gtl.common.material.Hk3Materials;
import com.sirin.hk3gtl.common.recipe.Hk3RecipeTypesQuantum;
import com.sirin.hk3gtl.common.research.Hk3RecipeResearchGate;
import net.minecraft.data.recipes.FinishedRecipe;
import net.minecraft.world.item.ItemStack;

import java.util.function.Consumer;


public final class QuantumStageRecipes {

    private static final long Q1_EUT = Hk3Values.VA_LONG[Hk3Tiers.QUANTUM_1];
    private static final long Q2_EUT = Hk3Values.VA_LONG[Hk3Tiers.QUANTUM_2];
    private static final long Q3_EUT = Hk3Values.VA_LONG[Hk3Tiers.QUANTUM_3];

    private QuantumStageRecipes() {}

    public static void register(Consumer<FinishedRecipe> provider) {
        QuantumCasingRecipes.register(provider);
        addQuantumCircuitRecipes(provider);
        addQuantumMachineRecipes(provider);
    }

    private static void addQuantumCircuitRecipes(Consumer<FinishedRecipe> provider) {
        Hk3RecipeTypesQuantum.QUANTUM_ENTANGLEMENT_COMPUTING.recipeBuilder("quantum_circuit_1_synthesis")
                .inputItems(new ItemStack(ImaginaryCircuitItems.CIRCUIT_IMAGINARY_4.get(), 32))
                .inputItems(new ItemStack(AbyssComponentItems.FIELD_GENERATOR_ABYSS_4.get(), 16))
                .inputItems(new ItemStack(HonkaiMaterialItems.ADVANCED_GAZE_BUFFER_UNIT.get(), 32))
                .inputFluids(Hk3Materials.LIQUID_HONKAI_ENERGY.getFluid(18432))
                .outputItems(new ItemStack(QuantumCircuitItems.CIRCUIT_QUANTUM_1.get(), 4))
                .duration(1800)
                .EUt(Q1_EUT)
                .save(provider);
        Hk3RecipeResearchGate.bind("quantum_entanglement_computing", "quantum_circuit_1_synthesis", "R-QT-001");

        Hk3RecipeTypesQuantum.QUANTUM_SUPERCONDUCTOR_LATTICE.recipeBuilder("quantum_circuit_2_synthesis")
                .inputItems(new ItemStack(QuantumCircuitItems.CIRCUIT_QUANTUM_1.get(), 64))
                .inputItems(new ItemStack(HonkaiMaterialItems.SUPERCONDUCTIVE_METAL_HYDROGEN.get(), 128))
                .inputItems(new ItemStack(HonkaiMaterialItems.EINSTEIN_RINGMAGNET.get(), 32))
                .inputFluids(Hk3Materials.LIQUID_HONKAI_ENERGY.getFluid(36864))
                .outputItems(new ItemStack(QuantumCircuitItems.CIRCUIT_QUANTUM_2.get(), 4))
                .duration(2200)
                .EUt(Q2_EUT)
                .save(provider);
        Hk3RecipeResearchGate.bind("quantum_superconductor_lattice", "quantum_circuit_2_synthesis", "R-QT-007");

        Hk3RecipeTypesQuantum.QUANTUM_THOUGHT_FORGING.recipeBuilder("quantum_circuit_3_synthesis")
                .inputItems(new ItemStack(QuantumCircuitItems.CIRCUIT_QUANTUM_2.get(), 64))
                .inputItems(new ItemStack(HonkaiMaterialItems.WORLD_BUBBLE_SAMPLE.get(), 16))
                .inputItems(new ItemStack(HonkaiMaterialItems.COMPRESSED_HONKAI_CORE.get(), 64))
                .inputFluids(Hk3Materials.LIQUID_HONKAI_ENERGY.getFluid(65536))
                .outputItems(new ItemStack(QuantumCircuitItems.CIRCUIT_QUANTUM_3.get(), 2))
                .duration(2600)
                .EUt(Q2_EUT)
                .save(provider);
        Hk3RecipeResearchGate.bind("quantum_thought_forging", "quantum_circuit_3_synthesis", "R-QT-010");

        Hk3RecipeTypesQuantum.QUANTUM_PRECISION_ASSEMBLY.recipeBuilder("quantum_circuit_4_synthesis")
                .inputItems(new ItemStack(QuantumCircuitItems.CIRCUIT_QUANTUM_3.get(), 64))
                .inputItems(new ItemStack(HonkaiMaterialItems.ANCIENT_LEGACY.get(), 8))
                .inputItems(new ItemStack(HonkaiMaterialItems.STABILIZED_HONKAI_CRYSTAL.get(), 512))
                .inputFluids(Hk3Materials.LIQUID_HONKAI_ENERGY.getFluid(98304))
                .outputItems(new ItemStack(QuantumCircuitItems.CIRCUIT_QUANTUM_4.get(), 2))
                .duration(3200)
                .EUt(Q3_EUT)
                .save(provider);
        Hk3RecipeResearchGate.bind("quantum_precision_assembly", "quantum_circuit_4_synthesis", "R-QT-011");
    }

    private static void addQuantumMachineRecipes(Consumer<FinishedRecipe> provider) {
        Hk3RecipeTypesQuantum.QUANTUM_ENTANGLEMENT_COMPUTING.recipeBuilder("quantum_sensor_pack")
                .inputItems(new ItemStack(QuantumCircuitItems.CIRCUIT_QUANTUM_1.get(), 16))
                .inputItems(new ItemStack(HonkaiMaterialItems.COMPRESSED_HONKAI_CORE.get(), 8))
                .outputItems(new ItemStack(QuantumComponentItems.SENSOR_QUANTUM_1.get(), 4))
                .duration(1200)
                .EUt(Q1_EUT)
                .save(provider);

        Hk3RecipeTypesQuantum.THOUSAND_REALMS_TRANSIT.recipeBuilder("quantum_transport_pack")
                .inputItems(new ItemStack(QuantumCircuitItems.CIRCUIT_QUANTUM_1.get(), 12))
                .inputItems(new ItemStack(HonkaiMaterialItems.WORLD_BUBBLE_SAMPLE.get(), 4))
                .outputItems(new ItemStack(QuantumComponentItems.CONVEYOR_MODULE_QUANTUM_1.get(), 4))
                .duration(1200)
                .EUt(Q1_EUT)
                .save(provider);

        Hk3RecipeTypesQuantum.WORLD_BUBBLE_MELTDOWN.recipeBuilder("world_bubble_reforming")
                .inputItems(new ItemStack(HonkaiMaterialItems.RAW_HONKAI_PARTICLE.get(), 2048))
                .inputFluids(Hk3Materials.LIQUID_HONKAI_ENERGY.getFluid(18432))
                .outputItems(new ItemStack(HonkaiMaterialItems.WORLD_BUBBLE_SAMPLE.get(), 2))
                .duration(1800)
                .EUt(Q2_EUT)
                .save(provider);

        // 注意：输入只用基础材料（结晶 + 压缩核心），不得用 circuit_quantum_2 / einstein_ringmagnet，
        // 否则与「circuit_2 / einstein 都需要超导金属氢」形成回收环（superconductive ↔ circuit_2 / einstein）。
        Hk3RecipeTypesQuantum.QUANTUM_SUPERCONDUCTOR_LATTICE.recipeBuilder("quantum_hydrogen_lattice")
                .inputItems(new ItemStack(HonkaiMaterialItems.HONKAI_ENERGY_CRYSTAL.get(), 512))
                .inputItems(new ItemStack(HonkaiMaterialItems.COMPRESSED_HONKAI_CORE.get(), 16))
                .outputItems(new ItemStack(HonkaiMaterialItems.SUPERCONDUCTIVE_METAL_HYDROGEN.get(), 64))
                .duration(1400)
                .EUt(Q2_EUT)
                .save(provider);

        Hk3RecipeTypesQuantum.HONKAI_WIRELESS_TRANSIT.recipeBuilder("wireless_energy_compression")
                .inputItems(new ItemStack(HonkaiMaterialItems.HONKAI_ENERGY_CRYSTAL.get(), 512))
                .inputFluids(Hk3Materials.LIQUID_HONKAI_ENERGY.getFluid(9216))
                .outputItems(new ItemStack(HonkaiMaterialItems.COMPRESSED_HONKAI_CORE.get(), 16))
                .duration(1000)
                .EUt(Q1_EUT)
                .save(provider);

        Hk3RecipeTypesQuantum.QUANTUM_THOUGHT_FORGING.recipeBuilder("quantum_robotic_logic_arm")
                .inputItems(new ItemStack(QuantumCircuitItems.CIRCUIT_QUANTUM_2.get(), 16))
                .inputItems(new ItemStack(QuantumComponentItems.ELECTRIC_MOTOR_QUANTUM_1.get(), 32))
                .outputItems(new ItemStack(QuantumComponentItems.ROBOT_ARM_QUANTUM_2.get(), 4))
                .duration(1600)
                .EUt(Q2_EUT)
                .save(provider);

        // 注意：不得输入 ancient_legacy，否则与 quantum_trade_contract(data→ancient_legacy) 形成
        // ancient_legacy ↔ data_research_package 回收环。改用压缩核心作基底。
        Hk3RecipeTypesQuantum.DIVINE_KEY_DISPLAY.recipeBuilder("legacy_observation_package")
                .inputItems(new ItemStack(QuantumCircuitItems.CIRCUIT_QUANTUM_2.get(), 12))
                .inputItems(new ItemStack(HonkaiMaterialItems.COMPRESSED_HONKAI_CORE.get(), 16))
                .outputItems(new ItemStack(HonkaiMaterialItems.DATA_RESEARCH_PACKAGE.get(), 8))
                .duration(1200)
                .EUt(Q2_EUT)
                .save(provider);

        Hk3RecipeTypesQuantum.QUANTUM_CIVILIZATION_TRADE.recipeBuilder("quantum_trade_contract")
                .inputItems(new ItemStack(QuantumCircuitItems.CIRCUIT_QUANTUM_2.get(), 8))
                .inputItems(new ItemStack(HonkaiMaterialItems.DATA_RESEARCH_PACKAGE.get(), 8))
                .outputItems(new ItemStack(HonkaiMaterialItems.ANCIENT_LEGACY.get(), 2))
                .duration(1200)
                .EUt(Q2_EUT)
                .save(provider);

        Hk3RecipeTypesQuantum.QUANTUM_HONKAI_FUSION.recipeBuilder("quantum_crystal_fusion")
                .inputItems(new ItemStack(HonkaiMaterialItems.HONKAI_ENERGY_CRYSTAL.get(), 1024))
                .inputItems(new ItemStack(HonkaiMaterialItems.COMPRESSED_HONKAI_CORE.get(), 32))
                .outputItems(new ItemStack(HonkaiMaterialItems.STABILIZED_HONKAI_CRYSTAL.get(), 64))
                .duration(2200)
                .EUt(Q2_EUT)
                .save(provider);

        Hk3RecipeTypesQuantum.FINALITY_PRESSURE_BUFFERING.recipeBuilder("buffer_array_supply")
                .inputItems(new ItemStack(QuantumCircuitItems.CIRCUIT_QUANTUM_3.get(), 4))
                .inputItems(new ItemStack(HonkaiMaterialItems.GAZE_BUFFER_UNIT.get(), 32))
                .inputItems(new ItemStack(HonkaiMaterialItems.COMPRESSED_HONKAI_CORE.get(), 16))
                .outputItems(new ItemStack(HonkaiMaterialItems.ADVANCED_GAZE_BUFFER_UNIT.get(), 8))
                .duration(1000)
                .EUt(Q2_EUT)
                .save(provider);

        Hk3RecipeTypesQuantum.WONDER_CONSTRUCTION_SIMULATION.recipeBuilder("wonder_casing_projection")
                .inputItems(new ItemStack(QuantumCircuitItems.CIRCUIT_QUANTUM_3.get(), 8))
                .inputItems(new ItemStack(HonkaiMaterialItems.WORLD_BUBBLE_SAMPLE.get(), 8))
                .outputItems(new ItemStack(CasingBlocks.CASING_FINALITY_WONDER.get(), 8))
                .duration(1200)
                .EUt(Q3_EUT)
                .save(provider);

        Hk3RecipeTypesQuantum.QUANTUM_PRECISION_ASSEMBLY.recipeBuilder("finality_seed_chip")
                .inputItems(new ItemStack(QuantumCircuitItems.CIRCUIT_QUANTUM_3.get(), 16))
                .inputItems(new ItemStack(HonkaiMaterialItems.STABILIZED_HONKAI_CRYSTAL.get(), 64))
                .outputItems(new ItemStack(FinalityCircuitItems.CIRCUIT_FINALITY_1.get(), 2))
                .duration(1600)
                .EUt(Q3_EUT)
                .save(provider);
    }
}
