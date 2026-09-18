package com.sirin.hk3gtl.common.recipe.quantum;



import com.gregtechceu.gtceu.common.data.GTRecipeTypes;
import com.sirin.hk3gtl.common.constants.Hk3Tiers;
import com.sirin.hk3gtl.common.constants.Hk3Values;
import com.sirin.hk3gtl.common.item.honkai.HonkaiMaterialItems;
import com.sirin.hk3gtl.common.item.imaginary.ImaginaryComponentItems;
import com.sirin.hk3gtl.common.item.quantum.QuantumCircuitItems;
import com.sirin.hk3gtl.common.item.quantum.QuantumComponentItems;
import com.sirin.hk3gtl.common.research.Hk3RecipeResearchGate;
import net.minecraft.data.recipes.FinishedRecipe;
import net.minecraft.world.item.ItemStack;

import java.util.function.Consumer;

/**
 * 量子 I~IV 八大件组装配方（GT 装配机，研究门控）。
 *
 * <h3>设计</h3>
 * 与虚数八大件一致：海量底层输入 → 单个产出，维持后期产线规模感；每级 8 件共用一个研究节点。
 */
public final class QuantumComponentRecipes {

    private static final long Q1_EUT = Hk3Values.VA_LONG[Hk3Tiers.QUANTUM_1];
    private static final long Q2_EUT = Hk3Values.VA_LONG[Hk3Tiers.QUANTUM_2];
    private static final long Q3_EUT = Hk3Values.VA_LONG[Hk3Tiers.QUANTUM_3];
    private static final long Q4_EUT = Hk3Values.VA_LONG[Hk3Tiers.QUANTUM_4];

    private QuantumComponentRecipes() {}

    /** 量子 I：以虚数 IV 八大件为基底 + 量子 I 电路 + 基础材料。研究 R-QT-001。 */
    public static void addQuantumIComponentRecipes(Consumer<FinishedRecipe> provider) {
        String research = "R-QT-001";

        buildAndBind(provider, "hk3gtl_motor_quantum_1", research, b -> b
                .inputItems(new ItemStack(ImaginaryComponentItems.ELECTRIC_MOTOR_IMAGINARY_4.get(), 128))
                .inputItems(new ItemStack(HonkaiMaterialItems.SUPERCONDUCTIVE_METAL_HYDROGEN.get(), 4096))
                .inputItems(new ItemStack(HonkaiMaterialItems.COMPRESSED_HONKAI_CORE.get(), 512))
                .inputItems(new ItemStack(QuantumCircuitItems.CIRCUIT_QUANTUM_1.get(), 64))
                .outputItems(new ItemStack(QuantumComponentItems.ELECTRIC_MOTOR_QUANTUM_1.get(), 1))
                .duration(3000).EUt(Q1_EUT));

        buildAndBind(provider, "hk3gtl_piston_quantum_1", research, b -> b
                .inputItems(new ItemStack(ImaginaryComponentItems.ELECTRIC_PISTON_IMAGINARY_4.get(), 128))
                .inputItems(new ItemStack(HonkaiMaterialItems.NANO_CERAMIC.get(), 2048))
                .inputItems(new ItemStack(QuantumComponentItems.ELECTRIC_MOTOR_QUANTUM_1.get(), 128))
                .outputItems(new ItemStack(QuantumComponentItems.ELECTRIC_PISTON_QUANTUM_1.get(), 1))
                .duration(3000).EUt(Q1_EUT));

        buildAndBind(provider, "hk3gtl_pump_quantum_1", research, b -> b
                .inputItems(new ItemStack(ImaginaryComponentItems.ELECTRIC_PUMP_IMAGINARY_4.get(), 128))
                .inputItems(new ItemStack(HonkaiMaterialItems.NANO_CERAMIC.get(), 2048))
                .inputItems(new ItemStack(QuantumComponentItems.ELECTRIC_MOTOR_QUANTUM_1.get(), 128))
                .outputItems(new ItemStack(QuantumComponentItems.ELECTRIC_PUMP_QUANTUM_1.get(), 1))
                .duration(3000).EUt(Q1_EUT));

        buildAndBind(provider, "hk3gtl_conveyor_quantum_1", research, b -> b
                .inputItems(new ItemStack(ImaginaryComponentItems.CONVEYOR_MODULE_IMAGINARY_4.get(), 128))
                .inputItems(new ItemStack(HonkaiMaterialItems.NANO_CERAMIC.get(), 2048))
                .inputItems(new ItemStack(QuantumComponentItems.ELECTRIC_MOTOR_QUANTUM_1.get(), 256))
                .outputItems(new ItemStack(QuantumComponentItems.CONVEYOR_MODULE_QUANTUM_1.get(), 1))
                .duration(3000).EUt(Q1_EUT));

        buildAndBind(provider, "hk3gtl_robot_arm_quantum_1", research, b -> b
                .inputItems(new ItemStack(ImaginaryComponentItems.ROBOT_ARM_IMAGINARY_4.get(), 64))
                .inputItems(new ItemStack(QuantumComponentItems.ELECTRIC_MOTOR_QUANTUM_1.get(), 64))
                .inputItems(new ItemStack(QuantumComponentItems.ELECTRIC_PISTON_QUANTUM_1.get(), 64))
                .inputItems(new ItemStack(QuantumCircuitItems.CIRCUIT_QUANTUM_1.get(), 64))
                .outputItems(new ItemStack(QuantumComponentItems.ROBOT_ARM_QUANTUM_1.get(), 1))
                .duration(3400).EUt(Q1_EUT));

        buildAndBind(provider, "hk3gtl_field_gen_quantum_1", research, b -> b
                .inputItems(new ItemStack(ImaginaryComponentItems.FIELD_GENERATOR_IMAGINARY_4.get(), 64))
                .inputItems(new ItemStack(HonkaiMaterialItems.EINSTEIN_RINGMAGNET.get(), 512))
                .inputItems(new ItemStack(HonkaiMaterialItems.COMPRESSED_HONKAI_CORE.get(), 256))
                .inputItems(new ItemStack(QuantumCircuitItems.CIRCUIT_QUANTUM_1.get(), 64))
                .outputItems(new ItemStack(QuantumComponentItems.FIELD_GENERATOR_QUANTUM_1.get(), 1))
                .duration(3400).EUt(Q1_EUT));

        buildAndBind(provider, "hk3gtl_emitter_quantum_1", research, b -> b
                .inputItems(new ItemStack(ImaginaryComponentItems.EMITTER_IMAGINARY_4.get(), 64))
                .inputItems(new ItemStack(HonkaiMaterialItems.PHASE_TRANSFER_MIRROR.get(), 512))
                .inputItems(new ItemStack(HonkaiMaterialItems.COMPRESSED_HONKAI_CORE.get(), 256))
                .inputItems(new ItemStack(QuantumCircuitItems.CIRCUIT_QUANTUM_1.get(), 64))
                .outputItems(new ItemStack(QuantumComponentItems.EMITTER_QUANTUM_1.get(), 1))
                .duration(3400).EUt(Q1_EUT));

        buildAndBind(provider, "hk3gtl_sensor_quantum_1", research, b -> b
                .inputItems(new ItemStack(ImaginaryComponentItems.SENSOR_IMAGINARY_4.get(), 64))
                .inputItems(new ItemStack(HonkaiMaterialItems.WORLD_BUBBLE_SAMPLE.get(), 64))
                .inputItems(new ItemStack(HonkaiMaterialItems.COMPRESSED_HONKAI_CORE.get(), 256))
                .inputItems(new ItemStack(QuantumCircuitItems.CIRCUIT_QUANTUM_1.get(), 64))
                .outputItems(new ItemStack(QuantumComponentItems.SENSOR_QUANTUM_1.get(), 1))
                .duration(3400).EUt(Q1_EUT));
    }

    /** 量子 II：以量子 I 组件 + 量子 II 电路 + 材料升级。研究 R-QT-007。 */
    public static void addQuantumIIComponentRecipes(Consumer<FinishedRecipe> provider) {
        String research = "R-QT-007";

        buildAndBind(provider, "hk3gtl_motor_quantum_2", research, b -> b
                .inputItems(new ItemStack(QuantumComponentItems.ELECTRIC_MOTOR_QUANTUM_1.get(), 256))
                .inputItems(new ItemStack(HonkaiMaterialItems.SUPERCONDUCTIVE_METAL_HYDROGEN.get(), 8192))
                .inputItems(new ItemStack(HonkaiMaterialItems.STABILIZED_HONKAI_CRYSTAL.get(), 1024))
                .inputItems(new ItemStack(QuantumCircuitItems.CIRCUIT_QUANTUM_2.get(), 128))
                .outputItems(new ItemStack(QuantumComponentItems.ELECTRIC_MOTOR_QUANTUM_2.get(), 1))
                .duration(4000).EUt(Q2_EUT));

        buildAndBind(provider, "hk3gtl_piston_quantum_2", research, b -> b
                .inputItems(new ItemStack(QuantumComponentItems.ELECTRIC_PISTON_QUANTUM_1.get(), 256))
                .inputItems(new ItemStack(HonkaiMaterialItems.NANO_CERAMIC.get(), 4096))
                .inputItems(new ItemStack(QuantumComponentItems.ELECTRIC_MOTOR_QUANTUM_2.get(), 256))
                .outputItems(new ItemStack(QuantumComponentItems.ELECTRIC_PISTON_QUANTUM_2.get(), 1))
                .duration(4000).EUt(Q2_EUT));

        buildAndBind(provider, "hk3gtl_pump_quantum_2", research, b -> b
                .inputItems(new ItemStack(QuantumComponentItems.ELECTRIC_PUMP_QUANTUM_1.get(), 256))
                .inputItems(new ItemStack(HonkaiMaterialItems.NANO_CERAMIC.get(), 4096))
                .inputItems(new ItemStack(QuantumComponentItems.ELECTRIC_MOTOR_QUANTUM_2.get(), 256))
                .outputItems(new ItemStack(QuantumComponentItems.ELECTRIC_PUMP_QUANTUM_2.get(), 1))
                .duration(4000).EUt(Q2_EUT));

        buildAndBind(provider, "hk3gtl_conveyor_quantum_2", research, b -> b
                .inputItems(new ItemStack(QuantumComponentItems.CONVEYOR_MODULE_QUANTUM_1.get(), 256))
                .inputItems(new ItemStack(HonkaiMaterialItems.NANO_CERAMIC.get(), 4096))
                .inputItems(new ItemStack(QuantumComponentItems.ELECTRIC_MOTOR_QUANTUM_2.get(), 512))
                .outputItems(new ItemStack(QuantumComponentItems.CONVEYOR_MODULE_QUANTUM_2.get(), 1))
                .duration(4000).EUt(Q2_EUT));

        buildAndBind(provider, "hk3gtl_robot_arm_quantum_2", research, b -> b
                .inputItems(new ItemStack(QuantumComponentItems.ROBOT_ARM_QUANTUM_1.get(), 128))
                .inputItems(new ItemStack(QuantumComponentItems.ELECTRIC_MOTOR_QUANTUM_2.get(), 128))
                .inputItems(new ItemStack(QuantumComponentItems.ELECTRIC_PISTON_QUANTUM_2.get(), 128))
                .inputItems(new ItemStack(QuantumCircuitItems.CIRCUIT_QUANTUM_2.get(), 128))
                .outputItems(new ItemStack(QuantumComponentItems.ROBOT_ARM_QUANTUM_2.get(), 1))
                .duration(4400).EUt(Q2_EUT));

        buildAndBind(provider, "hk3gtl_field_gen_quantum_2", research, b -> b
                .inputItems(new ItemStack(QuantumComponentItems.FIELD_GENERATOR_QUANTUM_1.get(), 128))
                .inputItems(new ItemStack(HonkaiMaterialItems.EINSTEIN_RINGMAGNET.get(), 1024))
                .inputItems(new ItemStack(HonkaiMaterialItems.COMPRESSED_HONKAI_CORE.get(), 512))
                .inputItems(new ItemStack(QuantumCircuitItems.CIRCUIT_QUANTUM_2.get(), 128))
                .outputItems(new ItemStack(QuantumComponentItems.FIELD_GENERATOR_QUANTUM_2.get(), 1))
                .duration(4400).EUt(Q2_EUT));

        buildAndBind(provider, "hk3gtl_emitter_quantum_2", research, b -> b
                .inputItems(new ItemStack(QuantumComponentItems.EMITTER_QUANTUM_1.get(), 128))
                .inputItems(new ItemStack(HonkaiMaterialItems.PHASE_TRANSFER_MIRROR.get(), 1024))
                .inputItems(new ItemStack(HonkaiMaterialItems.COMPRESSED_HONKAI_CORE.get(), 512))
                .inputItems(new ItemStack(QuantumCircuitItems.CIRCUIT_QUANTUM_2.get(), 128))
                .outputItems(new ItemStack(QuantumComponentItems.EMITTER_QUANTUM_2.get(), 1))
                .duration(4400).EUt(Q2_EUT));

        buildAndBind(provider, "hk3gtl_sensor_quantum_2", research, b -> b
                .inputItems(new ItemStack(QuantumComponentItems.SENSOR_QUANTUM_1.get(), 128))
                .inputItems(new ItemStack(HonkaiMaterialItems.WORLD_BUBBLE_SAMPLE.get(), 128))
                .inputItems(new ItemStack(HonkaiMaterialItems.COMPRESSED_HONKAI_CORE.get(), 512))
                .inputItems(new ItemStack(QuantumCircuitItems.CIRCUIT_QUANTUM_2.get(), 128))
                .outputItems(new ItemStack(QuantumComponentItems.SENSOR_QUANTUM_2.get(), 1))
                .duration(4400).EUt(Q2_EUT));
    }

    /** 量子 III：以量子 II 组件 + 量子 III 电路 + 材料升级。研究 R-QT-010。 */
    public static void addQuantumIIIComponentRecipes(Consumer<FinishedRecipe> provider) {
        String research = "R-QT-010";

        buildAndBind(provider, "hk3gtl_motor_quantum_3", research, b -> b
                .inputItems(new ItemStack(QuantumComponentItems.ELECTRIC_MOTOR_QUANTUM_2.get(), 256))
                .inputItems(new ItemStack(HonkaiMaterialItems.SUPERCONDUCTIVE_METAL_HYDROGEN.get(), 16384))
                .inputItems(new ItemStack(HonkaiMaterialItems.STABILIZED_HONKAI_CRYSTAL.get(), 2048))
                .inputItems(new ItemStack(QuantumCircuitItems.CIRCUIT_QUANTUM_3.get(), 128))
                .outputItems(new ItemStack(QuantumComponentItems.ELECTRIC_MOTOR_QUANTUM_3.get(), 1))
                .duration(5200).EUt(Q3_EUT));

        buildAndBind(provider, "hk3gtl_piston_quantum_3", research, b -> b
                .inputItems(new ItemStack(QuantumComponentItems.ELECTRIC_PISTON_QUANTUM_2.get(), 256))
                .inputItems(new ItemStack(HonkaiMaterialItems.FLUID_ALLOY_BLOCK.get(), 2048))
                .inputItems(new ItemStack(QuantumComponentItems.ELECTRIC_MOTOR_QUANTUM_3.get(), 256))
                .outputItems(new ItemStack(QuantumComponentItems.ELECTRIC_PISTON_QUANTUM_3.get(), 1))
                .duration(5200).EUt(Q3_EUT));

        buildAndBind(provider, "hk3gtl_pump_quantum_3", research, b -> b
                .inputItems(new ItemStack(QuantumComponentItems.ELECTRIC_PUMP_QUANTUM_2.get(), 256))
                .inputItems(new ItemStack(HonkaiMaterialItems.FLUID_ALLOY_BLOCK.get(), 2048))
                .inputItems(new ItemStack(QuantumComponentItems.ELECTRIC_MOTOR_QUANTUM_3.get(), 256))
                .outputItems(new ItemStack(QuantumComponentItems.ELECTRIC_PUMP_QUANTUM_3.get(), 1))
                .duration(5200).EUt(Q3_EUT));

        buildAndBind(provider, "hk3gtl_conveyor_quantum_3", research, b -> b
                .inputItems(new ItemStack(QuantumComponentItems.CONVEYOR_MODULE_QUANTUM_2.get(), 256))
                .inputItems(new ItemStack(HonkaiMaterialItems.FLUID_ALLOY_BLOCK.get(), 2048))
                .inputItems(new ItemStack(QuantumComponentItems.ELECTRIC_MOTOR_QUANTUM_3.get(), 512))
                .outputItems(new ItemStack(QuantumComponentItems.CONVEYOR_MODULE_QUANTUM_3.get(), 1))
                .duration(5200).EUt(Q3_EUT));

        buildAndBind(provider, "hk3gtl_robot_arm_quantum_3", research, b -> b
                .inputItems(new ItemStack(QuantumComponentItems.ROBOT_ARM_QUANTUM_2.get(), 128))
                .inputItems(new ItemStack(QuantumComponentItems.ELECTRIC_MOTOR_QUANTUM_3.get(), 128))
                .inputItems(new ItemStack(QuantumComponentItems.ELECTRIC_PISTON_QUANTUM_3.get(), 128))
                .inputItems(new ItemStack(QuantumCircuitItems.CIRCUIT_QUANTUM_3.get(), 128))
                .outputItems(new ItemStack(QuantumComponentItems.ROBOT_ARM_QUANTUM_3.get(), 1))
                .duration(5600).EUt(Q3_EUT));

        buildAndBind(provider, "hk3gtl_field_gen_quantum_3", research, b -> b
                .inputItems(new ItemStack(QuantumComponentItems.FIELD_GENERATOR_QUANTUM_2.get(), 128))
                .inputItems(new ItemStack(HonkaiMaterialItems.EINSTEIN_RINGMAGNET.get(), 2048))
                .inputItems(new ItemStack(HonkaiMaterialItems.ANCIENT_LEGACY.get(), 256))
                .inputItems(new ItemStack(QuantumCircuitItems.CIRCUIT_QUANTUM_3.get(), 128))
                .outputItems(new ItemStack(QuantumComponentItems.FIELD_GENERATOR_QUANTUM_3.get(), 1))
                .duration(5600).EUt(Q3_EUT));

        buildAndBind(provider, "hk3gtl_emitter_quantum_3", research, b -> b
                .inputItems(new ItemStack(QuantumComponentItems.EMITTER_QUANTUM_2.get(), 128))
                .inputItems(new ItemStack(HonkaiMaterialItems.PHASE_TRANSFER_MIRROR.get(), 2048))
                .inputItems(new ItemStack(HonkaiMaterialItems.ANCIENT_LEGACY.get(), 256))
                .inputItems(new ItemStack(QuantumCircuitItems.CIRCUIT_QUANTUM_3.get(), 128))
                .outputItems(new ItemStack(QuantumComponentItems.EMITTER_QUANTUM_3.get(), 1))
                .duration(5600).EUt(Q3_EUT));

        buildAndBind(provider, "hk3gtl_sensor_quantum_3", research, b -> b
                .inputItems(new ItemStack(QuantumComponentItems.SENSOR_QUANTUM_2.get(), 128))
                .inputItems(new ItemStack(HonkaiMaterialItems.WORLD_BUBBLE_SAMPLE.get(), 256))
                .inputItems(new ItemStack(HonkaiMaterialItems.ANCIENT_LEGACY.get(), 256))
                .inputItems(new ItemStack(QuantumCircuitItems.CIRCUIT_QUANTUM_3.get(), 128))
                .outputItems(new ItemStack(QuantumComponentItems.SENSOR_QUANTUM_3.get(), 1))
                .duration(5600).EUt(Q3_EUT));
    }

    /** 量子 IV：以量子 III 组件 + 量子 IV 电路 + 顶级材料。研究 R-QT-011。 */
    public static void addQuantumIVComponentRecipes(Consumer<FinishedRecipe> provider) {
        String research = "R-QT-011";

        buildAndBind(provider, "hk3gtl_motor_quantum_4", research, b -> b
                .inputItems(new ItemStack(QuantumComponentItems.ELECTRIC_MOTOR_QUANTUM_3.get(), 256))
                .inputItems(new ItemStack(HonkaiMaterialItems.SUPERCONDUCTIVE_METAL_HYDROGEN.get(), 32768))
                .inputItems(new ItemStack(HonkaiMaterialItems.DENSE_HONKAI_FUEL_ROD.get(), 512))
                .inputItems(new ItemStack(QuantumCircuitItems.CIRCUIT_QUANTUM_4.get(), 128))
                .outputItems(new ItemStack(QuantumComponentItems.ELECTRIC_MOTOR_QUANTUM_4.get(), 1))
                .duration(6400).EUt(Q4_EUT));

        buildAndBind(provider, "hk3gtl_piston_quantum_4", research, b -> b
                .inputItems(new ItemStack(QuantumComponentItems.ELECTRIC_PISTON_QUANTUM_3.get(), 256))
                .inputItems(new ItemStack(HonkaiMaterialItems.FLUID_ALLOY_BLOCK.get(), 4096))
                .inputItems(new ItemStack(QuantumComponentItems.ELECTRIC_MOTOR_QUANTUM_4.get(), 256))
                .outputItems(new ItemStack(QuantumComponentItems.ELECTRIC_PISTON_QUANTUM_4.get(), 1))
                .duration(6400).EUt(Q4_EUT));

        buildAndBind(provider, "hk3gtl_pump_quantum_4", research, b -> b
                .inputItems(new ItemStack(QuantumComponentItems.ELECTRIC_PUMP_QUANTUM_3.get(), 256))
                .inputItems(new ItemStack(HonkaiMaterialItems.FLUID_ALLOY_BLOCK.get(), 4096))
                .inputItems(new ItemStack(QuantumComponentItems.ELECTRIC_MOTOR_QUANTUM_4.get(), 256))
                .outputItems(new ItemStack(QuantumComponentItems.ELECTRIC_PUMP_QUANTUM_4.get(), 1))
                .duration(6400).EUt(Q4_EUT));

        buildAndBind(provider, "hk3gtl_conveyor_quantum_4", research, b -> b
                .inputItems(new ItemStack(QuantumComponentItems.CONVEYOR_MODULE_QUANTUM_3.get(), 256))
                .inputItems(new ItemStack(HonkaiMaterialItems.FLUID_ALLOY_BLOCK.get(), 4096))
                .inputItems(new ItemStack(QuantumComponentItems.ELECTRIC_MOTOR_QUANTUM_4.get(), 512))
                .outputItems(new ItemStack(QuantumComponentItems.CONVEYOR_MODULE_QUANTUM_4.get(), 1))
                .duration(6400).EUt(Q4_EUT));

        buildAndBind(provider, "hk3gtl_robot_arm_quantum_4", research, b -> b
                .inputItems(new ItemStack(QuantumComponentItems.ROBOT_ARM_QUANTUM_3.get(), 128))
                .inputItems(new ItemStack(QuantumComponentItems.ELECTRIC_MOTOR_QUANTUM_4.get(), 128))
                .inputItems(new ItemStack(QuantumComponentItems.ELECTRIC_PISTON_QUANTUM_4.get(), 128))
                .inputItems(new ItemStack(QuantumCircuitItems.CIRCUIT_QUANTUM_4.get(), 128))
                .outputItems(new ItemStack(QuantumComponentItems.ROBOT_ARM_QUANTUM_4.get(), 1))
                .duration(6800).EUt(Q4_EUT));

        buildAndBind(provider, "hk3gtl_field_gen_quantum_4", research, b -> b
                .inputItems(new ItemStack(QuantumComponentItems.FIELD_GENERATOR_QUANTUM_3.get(), 128))
                .inputItems(new ItemStack(HonkaiMaterialItems.ANCIENT_LEGACY.get(), 512))
                .inputItems(new ItemStack(HonkaiMaterialItems.DENSE_HONKAI_FUEL_ROD.get(), 512))
                .inputItems(new ItemStack(QuantumCircuitItems.CIRCUIT_QUANTUM_4.get(), 128))
                .outputItems(new ItemStack(QuantumComponentItems.FIELD_GENERATOR_QUANTUM_4.get(), 1))
                .duration(6800).EUt(Q4_EUT));

        buildAndBind(provider, "hk3gtl_emitter_quantum_4", research, b -> b
                .inputItems(new ItemStack(QuantumComponentItems.EMITTER_QUANTUM_3.get(), 128))
                .inputItems(new ItemStack(HonkaiMaterialItems.ANCIENT_WILL.get(), 512))
                .inputItems(new ItemStack(HonkaiMaterialItems.DENSE_HONKAI_FUEL_ROD.get(), 512))
                .inputItems(new ItemStack(QuantumCircuitItems.CIRCUIT_QUANTUM_4.get(), 128))
                .outputItems(new ItemStack(QuantumComponentItems.EMITTER_QUANTUM_4.get(), 1))
                .duration(6800).EUt(Q4_EUT));

        buildAndBind(provider, "hk3gtl_sensor_quantum_4", research, b -> b
                .inputItems(new ItemStack(QuantumComponentItems.SENSOR_QUANTUM_3.get(), 128))
                .inputItems(new ItemStack(HonkaiMaterialItems.ANCIENT_WILL.get(), 512))
                .inputItems(new ItemStack(HonkaiMaterialItems.DENSE_HONKAI_FUEL_ROD.get(), 512))
                .inputItems(new ItemStack(QuantumCircuitItems.CIRCUIT_QUANTUM_4.get(), 128))
                .outputItems(new ItemStack(QuantumComponentItems.SENSOR_QUANTUM_4.get(), 1))
                .duration(6800).EUt(Q4_EUT));
    }

    @FunctionalInterface
    interface RecipeConfigurator {
        com.gregtechceu.gtceu.data.recipe.builder.GTRecipeBuilder configure(
                com.gregtechceu.gtceu.data.recipe.builder.GTRecipeBuilder builder);
    }

    private static void buildAndBind(Consumer<FinishedRecipe> provider,
                                     String recipeId, String researchId,
                                     RecipeConfigurator configurator) {
        configurator.configure(GTRecipeTypes.ASSEMBLER_RECIPES.recipeBuilder(recipeId))
                .save(provider);
        Hk3RecipeResearchGate.bind("assembler", recipeId, researchId);
    }
}
