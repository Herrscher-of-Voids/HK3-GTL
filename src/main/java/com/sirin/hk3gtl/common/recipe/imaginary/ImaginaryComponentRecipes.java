package com.sirin.hk3gtl.common.recipe.imaginary;



import com.gregtechceu.gtceu.api.data.chemical.ChemicalHelper;
import com.gregtechceu.gtceu.api.data.tag.TagPrefix;
import com.gregtechceu.gtceu.common.data.GTRecipeTypes;
import com.sirin.hk3gtl.common.constants.Hk3Tiers;
import com.sirin.hk3gtl.common.constants.Hk3Values;
import com.sirin.hk3gtl.common.item.abyss.AbyssComponentItems;
import com.sirin.hk3gtl.common.item.abyss.AbyssCircuitItems;
import com.sirin.hk3gtl.common.item.imaginary.ImaginaryCircuitItems;
import com.sirin.hk3gtl.common.item.imaginary.ImaginaryComponentItems;
import com.sirin.hk3gtl.common.item.honkai.HonkaiMaterialItems;
import com.sirin.hk3gtl.common.material.SouliumMaterial;
import com.sirin.hk3gtl.common.research.Hk3RecipeResearchGate;
import net.minecraft.data.recipes.FinishedRecipe;
import net.minecraft.world.item.ItemStack;

import java.util.function.Consumer;

/**
 * 虚数 I~IV 八大件组装配方。
 *
 * <h3>职责</h3>
 * 注册虚数阶段八大件（马达/活塞/泵/传送带/机械臂/力场/发射器/传感器）的配方。
 *
 * <h3>设计理念</h3>
 * 针对后期资源溢出，采取“海量输入 → 极少输出”的资源压缩策略。
 * 单个组件动辄需要消耗 256~1024 个底层材料，以此维持后期产线的规模感。
 *
 * <h3>维护说明</h3>
 * <ul>
 *   <li>每个 addImaginaryXComponentRecipes 方法对应一个虚数电压等级。</li>
 *   <li>同一等级的 8 条配方共用同一个 research 变量，改研究门槛只改方法开头。</li>
 *   <li>配方由 buildAndBind 统一注册并绑定研究；不要忘记传入 recipeId。</li>
 *   <li>改输入规模：修改 inputItems 数量，尤其是上一阶组件、电路、核心材料。</li>
 *   <li>改产量：修改 outputItems 第二参数；当前默认每次产出 1 个，维持后期资源压力。</li>
 *   <li>改耗时/电压：调整 IM1_EUT~IM4_EUT 或具体 duration。</li>
 * </ul>
 */
public class ImaginaryComponentRecipes {

    private static final long IM1_EUT = Hk3Values.VA_LONG[Hk3Tiers.IMAGINARY_1];
    private static final long IM2_EUT = Hk3Values.VA_LONG[Hk3Tiers.IMAGINARY_2];
    private static final long IM3_EUT = Hk3Values.VA_LONG[Hk3Tiers.IMAGINARY_3];
    private static final long IM4_EUT = Hk3Values.VA_LONG[Hk3Tiers.IMAGINARY_4];

    public static void addImaginaryIComponentRecipes(Consumer<FinishedRecipe> provider) {
        String research = "R-IM-001"; // 预留节点

        // 虚数I马达：海渊IV马达 + 魂钢细丝 + 压缩核心 + 虚数I电路 → 1。
        // 用途：所有虚数I运动/物流类组件的基础。
        buildAndBind(provider, "hk3gtl_motor_imaginary_1", research, b -> b
                .inputItems(new ItemStack(AbyssComponentItems.ELECTRIC_MOTOR_ABYSS_4.get(), 256))
                .inputItems(ChemicalHelper.get(TagPrefix.wireFine, SouliumMaterial.SOULIUM, 8192))
                .inputItems(new ItemStack(HonkaiMaterialItems.COMPRESSED_HONKAI_CORE.get(), 512))
                .inputItems(new ItemStack(ImaginaryCircuitItems.CIRCUIT_IMAGINARY_1.get(), 128))
                .outputItems(new ItemStack(ImaginaryComponentItems.ELECTRIC_MOTOR_IMAGINARY_1.get(), 1))
                .duration(2000).EUt(IM1_EUT));

        // 虚数I活塞：海渊IV活塞 + 魂钢板 + 虚数I马达 → 1。
        // 用途：虚数I机械臂和需要线性驱动的控制器。
        buildAndBind(provider, "hk3gtl_piston_imaginary_1", research, b -> b
                .inputItems(new ItemStack(AbyssComponentItems.ELECTRIC_PISTON_ABYSS_4.get(), 256))
                .inputItems(ChemicalHelper.get(TagPrefix.plate, SouliumMaterial.SOULIUM, 2048))
                .inputItems(new ItemStack(ImaginaryComponentItems.ELECTRIC_MOTOR_IMAGINARY_1.get(), 256))
                .outputItems(new ItemStack(ImaginaryComponentItems.ELECTRIC_PISTON_IMAGINARY_1.get(), 1))
                .duration(2000).EUt(IM1_EUT));

        // 虚数I泵：海渊IV泵 + 魂钢环 + 虚数I马达 → 1。
        // 用途：虚数流体/相位纯化相关机器。
        buildAndBind(provider, "hk3gtl_pump_imaginary_1", research, b -> b
                .inputItems(new ItemStack(AbyssComponentItems.ELECTRIC_PUMP_ABYSS_4.get(), 256))
                .inputItems(ChemicalHelper.get(TagPrefix.ring, SouliumMaterial.SOULIUM, 2048))
                .inputItems(new ItemStack(ImaginaryComponentItems.ELECTRIC_MOTOR_IMAGINARY_1.get(), 256))
                .outputItems(new ItemStack(ImaginaryComponentItems.ELECTRIC_PUMP_IMAGINARY_1.get(), 1))
                .duration(2000).EUt(IM1_EUT));

        // 虚数I传送带：海渊IV传送带 + 魂钢板 + 虚数I马达 → 1。
        // 用途：虚数物流与装配链。
        buildAndBind(provider, "hk3gtl_conveyor_imaginary_1", research, b -> b
                .inputItems(new ItemStack(AbyssComponentItems.CONVEYOR_MODULE_ABYSS_4.get(), 256))
                .inputItems(ChemicalHelper.get(TagPrefix.plate, SouliumMaterial.SOULIUM, 2048))
                .inputItems(new ItemStack(ImaginaryComponentItems.ELECTRIC_MOTOR_IMAGINARY_1.get(), 512))
                .outputItems(new ItemStack(ImaginaryComponentItems.CONVEYOR_MODULE_IMAGINARY_1.get(), 1))
                .duration(2000).EUt(IM1_EUT));

        // 机械臂: 128 海渊4机械臂 + 128 虚数1马达 + 128 虚数1活塞 + 128 虚数1电路 -> 1 虚数1机械臂
        buildAndBind(provider, "hk3gtl_robot_arm_imaginary_1", research, b -> b
                .inputItems(new ItemStack(AbyssComponentItems.ROBOT_ARM_ABYSS_4.get(), 128))
                .inputItems(new ItemStack(ImaginaryComponentItems.ELECTRIC_MOTOR_IMAGINARY_1.get(), 128))
                .inputItems(new ItemStack(ImaginaryComponentItems.ELECTRIC_PISTON_IMAGINARY_1.get(), 128))
                .inputItems(new ItemStack(ImaginaryCircuitItems.CIRCUIT_IMAGINARY_1.get(), 128))
                .outputItems(new ItemStack(ImaginaryComponentItems.ROBOT_ARM_IMAGINARY_1.get(), 1))
                .duration(2400).EUt(IM1_EUT));

        // 力场: 128 海渊4力场 + 1024 天命/逆熵虚数核心 + 256 压缩崩坏核心 + 128 虚数1电路 -> 1 虚数1力场
        buildAndBind(provider, "hk3gtl_field_gen_imaginary_1", research, b -> b
                .inputItems(new ItemStack(AbyssComponentItems.FIELD_GENERATOR_ABYSS_4.get(), 128))
                .inputItems(new ItemStack(HonkaiMaterialItems.SCHICKSAL_IMAGINARY_CORE.get(), 512))
                .inputItems(new ItemStack(HonkaiMaterialItems.ANTI_ENTROPY_IMAGINARY_CORE.get(), 512))
                .inputItems(new ItemStack(HonkaiMaterialItems.COMPRESSED_HONKAI_CORE.get(), 256))
                .inputItems(new ItemStack(ImaginaryCircuitItems.CIRCUIT_IMAGINARY_1.get(), 128))
                .outputItems(new ItemStack(ImaginaryComponentItems.FIELD_GENERATOR_IMAGINARY_1.get(), 1))
                .duration(2400).EUt(IM1_EUT));

        // 发射器: 128 海渊4发射器 + 1024 纳米陶瓷 + 256 压缩核心 + 128 虚数1电路 -> 1 虚数1发射器
        buildAndBind(provider, "hk3gtl_emitter_imaginary_1", research, b -> b
                .inputItems(new ItemStack(AbyssComponentItems.EMITTER_ABYSS_4.get(), 128))
                .inputItems(new ItemStack(HonkaiMaterialItems.NANO_CERAMIC.get(), 1024))
                .inputItems(new ItemStack(HonkaiMaterialItems.COMPRESSED_HONKAI_CORE.get(), 256))
                .inputItems(new ItemStack(ImaginaryCircuitItems.CIRCUIT_IMAGINARY_1.get(), 128))
                .outputItems(new ItemStack(ImaginaryComponentItems.EMITTER_IMAGINARY_1.get(), 1))
                .duration(2400).EUt(IM1_EUT));

        // 传感器: 128 海渊4传感器 + 512 相位转移镜面 + 256 压缩核心 + 128 虚数1电路 -> 1 虚数1传感器
        buildAndBind(provider, "hk3gtl_sensor_imaginary_1", research, b -> b
                .inputItems(new ItemStack(AbyssComponentItems.SENSOR_ABYSS_4.get(), 128))
                .inputItems(new ItemStack(HonkaiMaterialItems.PHASE_TRANSFER_MIRROR.get(), 512))
                .inputItems(new ItemStack(HonkaiMaterialItems.COMPRESSED_HONKAI_CORE.get(), 256))
                .inputItems(new ItemStack(ImaginaryCircuitItems.CIRCUIT_IMAGINARY_1.get(), 128))
                .outputItems(new ItemStack(ImaginaryComponentItems.SENSOR_IMAGINARY_1.get(), 1))
                .duration(2400).EUt(IM1_EUT));
    }

    public static void addImaginaryIIComponentRecipes(Consumer<FinishedRecipe> provider) {
        String research = "R-IM-002"; // 预留节点

        buildAndBind(provider, "hk3gtl_motor_imaginary_2", research, b -> b
                .inputItems(new ItemStack(ImaginaryComponentItems.ELECTRIC_MOTOR_IMAGINARY_1.get(), 256))
                .inputItems(new ItemStack(HonkaiMaterialItems.SUPERCONDUCTIVE_METAL_HYDROGEN.get(), 2048))
                .inputItems(new ItemStack(HonkaiMaterialItems.COMPRESSED_HONKAI_CORE.get(), 1024))
                .inputItems(new ItemStack(ImaginaryCircuitItems.CIRCUIT_IMAGINARY_2.get(), 128))
                .outputItems(new ItemStack(ImaginaryComponentItems.ELECTRIC_MOTOR_IMAGINARY_2.get(), 1))
                .duration(3000).EUt(IM2_EUT));

        buildAndBind(provider, "hk3gtl_piston_imaginary_2", research, b -> b
                .inputItems(new ItemStack(ImaginaryComponentItems.ELECTRIC_PISTON_IMAGINARY_1.get(), 256))
                .inputItems(new ItemStack(HonkaiMaterialItems.NANO_CERAMIC.get(), 2048))
                .inputItems(new ItemStack(ImaginaryComponentItems.ELECTRIC_MOTOR_IMAGINARY_2.get(), 256))
                .outputItems(new ItemStack(ImaginaryComponentItems.ELECTRIC_PISTON_IMAGINARY_2.get(), 1))
                .duration(3000).EUt(IM2_EUT));

        buildAndBind(provider, "hk3gtl_pump_imaginary_2", research, b -> b
                .inputItems(new ItemStack(ImaginaryComponentItems.ELECTRIC_PUMP_IMAGINARY_1.get(), 256))
                .inputItems(new ItemStack(HonkaiMaterialItems.NANO_CERAMIC.get(), 2048))
                .inputItems(new ItemStack(ImaginaryComponentItems.ELECTRIC_MOTOR_IMAGINARY_2.get(), 256))
                .outputItems(new ItemStack(ImaginaryComponentItems.ELECTRIC_PUMP_IMAGINARY_2.get(), 1))
                .duration(3000).EUt(IM2_EUT));

        buildAndBind(provider, "hk3gtl_conveyor_imaginary_2", research, b -> b
                .inputItems(new ItemStack(ImaginaryComponentItems.CONVEYOR_MODULE_IMAGINARY_1.get(), 256))
                .inputItems(new ItemStack(HonkaiMaterialItems.NANO_CERAMIC.get(), 2048))
                .inputItems(new ItemStack(ImaginaryComponentItems.ELECTRIC_MOTOR_IMAGINARY_2.get(), 512))
                .outputItems(new ItemStack(ImaginaryComponentItems.CONVEYOR_MODULE_IMAGINARY_2.get(), 1))
                .duration(3000).EUt(IM2_EUT));

        buildAndBind(provider, "hk3gtl_robot_arm_imaginary_2", research, b -> b
                .inputItems(new ItemStack(ImaginaryComponentItems.ROBOT_ARM_IMAGINARY_1.get(), 128))
                .inputItems(new ItemStack(ImaginaryComponentItems.ELECTRIC_MOTOR_IMAGINARY_2.get(), 128))
                .inputItems(new ItemStack(ImaginaryComponentItems.ELECTRIC_PISTON_IMAGINARY_2.get(), 128))
                .inputItems(new ItemStack(ImaginaryCircuitItems.CIRCUIT_IMAGINARY_2.get(), 128))
                .outputItems(new ItemStack(ImaginaryComponentItems.ROBOT_ARM_IMAGINARY_2.get(), 1))
                .duration(3200).EUt(IM2_EUT));

        buildAndBind(provider, "hk3gtl_field_gen_imaginary_2", research, b -> b
                .inputItems(new ItemStack(ImaginaryComponentItems.FIELD_GENERATOR_IMAGINARY_1.get(), 128))
                .inputItems(new ItemStack(HonkaiMaterialItems.EINSTEIN_RINGMAGNET.get(), 512))
                .inputItems(new ItemStack(HonkaiMaterialItems.COMPRESSED_HONKAI_CORE.get(), 512))
                .inputItems(new ItemStack(ImaginaryCircuitItems.CIRCUIT_IMAGINARY_2.get(), 128))
                .outputItems(new ItemStack(ImaginaryComponentItems.FIELD_GENERATOR_IMAGINARY_2.get(), 1))
                .duration(3200).EUt(IM2_EUT));

        buildAndBind(provider, "hk3gtl_emitter_imaginary_2", research, b -> b
                .inputItems(new ItemStack(ImaginaryComponentItems.EMITTER_IMAGINARY_1.get(), 128))
                .inputItems(new ItemStack(HonkaiMaterialItems.PHASE_TRANSFER_MIRROR.get(), 512))
                .inputItems(new ItemStack(HonkaiMaterialItems.COMPRESSED_HONKAI_CORE.get(), 512))
                .inputItems(new ItemStack(ImaginaryCircuitItems.CIRCUIT_IMAGINARY_2.get(), 128))
                .outputItems(new ItemStack(ImaginaryComponentItems.EMITTER_IMAGINARY_2.get(), 1))
                .duration(3200).EUt(IM2_EUT));

        buildAndBind(provider, "hk3gtl_sensor_imaginary_2", research, b -> b
                .inputItems(new ItemStack(ImaginaryComponentItems.SENSOR_IMAGINARY_1.get(), 128))
                .inputItems(new ItemStack(HonkaiMaterialItems.ADVANCED_GAZE_BUFFER_UNIT.get(), 512))
                .inputItems(new ItemStack(HonkaiMaterialItems.COMPRESSED_HONKAI_CORE.get(), 512))
                .inputItems(new ItemStack(ImaginaryCircuitItems.CIRCUIT_IMAGINARY_2.get(), 128))
                .outputItems(new ItemStack(ImaginaryComponentItems.SENSOR_IMAGINARY_2.get(), 1))
                .duration(3200).EUt(IM2_EUT));
    }

    public static void addImaginaryIIIComponentRecipes(Consumer<FinishedRecipe> provider) {
        String research = "R-IM-003";

        buildAndBind(provider, "hk3gtl_motor_imaginary_3", research, b -> b
                .inputItems(new ItemStack(ImaginaryComponentItems.ELECTRIC_MOTOR_IMAGINARY_2.get(), 256))
                .inputItems(new ItemStack(HonkaiMaterialItems.SUPERCONDUCTIVE_METAL_HYDROGEN.get(), 4096))
                .inputItems(new ItemStack(HonkaiMaterialItems.COMPRESSED_HONKAI_CORE.get(), 2048))
                .inputItems(new ItemStack(ImaginaryCircuitItems.CIRCUIT_IMAGINARY_3.get(), 128))
                .outputItems(new ItemStack(ImaginaryComponentItems.ELECTRIC_MOTOR_IMAGINARY_3.get(), 1))
                .duration(4000).EUt(IM3_EUT));

        buildAndBind(provider, "hk3gtl_piston_imaginary_3", research, b -> b
                .inputItems(new ItemStack(ImaginaryComponentItems.ELECTRIC_PISTON_IMAGINARY_2.get(), 256))
                .inputItems(new ItemStack(HonkaiMaterialItems.NANO_CERAMIC.get(), 4096))
                .inputItems(new ItemStack(ImaginaryComponentItems.ELECTRIC_MOTOR_IMAGINARY_3.get(), 256))
                .outputItems(new ItemStack(ImaginaryComponentItems.ELECTRIC_PISTON_IMAGINARY_3.get(), 1))
                .duration(4000).EUt(IM3_EUT));

        buildAndBind(provider, "hk3gtl_pump_imaginary_3", research, b -> b
                .inputItems(new ItemStack(ImaginaryComponentItems.ELECTRIC_PUMP_IMAGINARY_2.get(), 256))
                .inputItems(new ItemStack(HonkaiMaterialItems.NANO_CERAMIC.get(), 4096))
                .inputItems(new ItemStack(ImaginaryComponentItems.ELECTRIC_MOTOR_IMAGINARY_3.get(), 256))
                .outputItems(new ItemStack(ImaginaryComponentItems.ELECTRIC_PUMP_IMAGINARY_3.get(), 1))
                .duration(4000).EUt(IM3_EUT));

        buildAndBind(provider, "hk3gtl_conveyor_imaginary_3", research, b -> b
                .inputItems(new ItemStack(ImaginaryComponentItems.CONVEYOR_MODULE_IMAGINARY_2.get(), 256))
                .inputItems(new ItemStack(HonkaiMaterialItems.NANO_CERAMIC.get(), 4096))
                .inputItems(new ItemStack(ImaginaryComponentItems.ELECTRIC_MOTOR_IMAGINARY_3.get(), 512))
                .outputItems(new ItemStack(ImaginaryComponentItems.CONVEYOR_MODULE_IMAGINARY_3.get(), 1))
                .duration(4000).EUt(IM3_EUT));

        buildAndBind(provider, "hk3gtl_robot_arm_imaginary_3", research, b -> b
                .inputItems(new ItemStack(ImaginaryComponentItems.ROBOT_ARM_IMAGINARY_2.get(), 128))
                .inputItems(new ItemStack(ImaginaryComponentItems.ELECTRIC_MOTOR_IMAGINARY_3.get(), 128))
                .inputItems(new ItemStack(ImaginaryComponentItems.ELECTRIC_PISTON_IMAGINARY_3.get(), 128))
                .inputItems(new ItemStack(ImaginaryCircuitItems.CIRCUIT_IMAGINARY_3.get(), 128))
                .outputItems(new ItemStack(ImaginaryComponentItems.ROBOT_ARM_IMAGINARY_3.get(), 1))
                .duration(4400).EUt(IM3_EUT));

        buildAndBind(provider, "hk3gtl_field_gen_imaginary_3", research, b -> b
                .inputItems(new ItemStack(ImaginaryComponentItems.FIELD_GENERATOR_IMAGINARY_2.get(), 128))
                .inputItems(new ItemStack(HonkaiMaterialItems.EINSTEIN_RINGMAGNET.get(), 1024))
                .inputItems(new ItemStack(HonkaiMaterialItems.COMPRESSED_HONKAI_CORE.get(), 1024))
                .inputItems(new ItemStack(ImaginaryCircuitItems.CIRCUIT_IMAGINARY_3.get(), 128))
                .outputItems(new ItemStack(ImaginaryComponentItems.FIELD_GENERATOR_IMAGINARY_3.get(), 1))
                .duration(4400).EUt(IM3_EUT));

        buildAndBind(provider, "hk3gtl_emitter_imaginary_3", research, b -> b
                .inputItems(new ItemStack(ImaginaryComponentItems.EMITTER_IMAGINARY_2.get(), 128))
                .inputItems(new ItemStack(HonkaiMaterialItems.PHASE_TRANSFER_MIRROR.get(), 1024))
                .inputItems(new ItemStack(HonkaiMaterialItems.COMPRESSED_HONKAI_CORE.get(), 1024))
                .inputItems(new ItemStack(ImaginaryCircuitItems.CIRCUIT_IMAGINARY_3.get(), 128))
                .outputItems(new ItemStack(ImaginaryComponentItems.EMITTER_IMAGINARY_3.get(), 1))
                .duration(4400).EUt(IM3_EUT));

        buildAndBind(provider, "hk3gtl_sensor_imaginary_3", research, b -> b
                .inputItems(new ItemStack(ImaginaryComponentItems.SENSOR_IMAGINARY_2.get(), 128))
                .inputItems(new ItemStack(HonkaiMaterialItems.ADVANCED_GAZE_BUFFER_UNIT.get(), 1024))
                .inputItems(new ItemStack(HonkaiMaterialItems.COMPRESSED_HONKAI_CORE.get(), 1024))
                .inputItems(new ItemStack(ImaginaryCircuitItems.CIRCUIT_IMAGINARY_3.get(), 128))
                .outputItems(new ItemStack(ImaginaryComponentItems.SENSOR_IMAGINARY_3.get(), 1))
                .duration(4400).EUt(IM3_EUT));
    }

    public static void addImaginaryIVComponentRecipes(Consumer<FinishedRecipe> provider) {
        String research = "R-IM-004";

        buildAndBind(provider, "hk3gtl_motor_imaginary_4", research, b -> b
                .inputItems(new ItemStack(ImaginaryComponentItems.ELECTRIC_MOTOR_IMAGINARY_3.get(), 256))
                .inputItems(new ItemStack(HonkaiMaterialItems.SUPERCONDUCTIVE_METAL_HYDROGEN.get(), 8192))
                .inputItems(new ItemStack(HonkaiMaterialItems.DENSE_HONKAI_FUEL_ROD.get(), 512))
                .inputItems(new ItemStack(ImaginaryCircuitItems.CIRCUIT_IMAGINARY_4.get(), 128))
                .outputItems(new ItemStack(ImaginaryComponentItems.ELECTRIC_MOTOR_IMAGINARY_4.get(), 1))
                .duration(5000).EUt(IM4_EUT));

        buildAndBind(provider, "hk3gtl_piston_imaginary_4", research, b -> b
                .inputItems(new ItemStack(ImaginaryComponentItems.ELECTRIC_PISTON_IMAGINARY_3.get(), 256))
                .inputItems(new ItemStack(HonkaiMaterialItems.FLUID_ALLOY_BLOCK.get(), 1024))
                .inputItems(new ItemStack(ImaginaryComponentItems.ELECTRIC_MOTOR_IMAGINARY_4.get(), 256))
                .outputItems(new ItemStack(ImaginaryComponentItems.ELECTRIC_PISTON_IMAGINARY_4.get(), 1))
                .duration(5000).EUt(IM4_EUT));

        buildAndBind(provider, "hk3gtl_pump_imaginary_4", research, b -> b
                .inputItems(new ItemStack(ImaginaryComponentItems.ELECTRIC_PUMP_IMAGINARY_3.get(), 256))
                .inputItems(new ItemStack(HonkaiMaterialItems.FLUID_ALLOY_BLOCK.get(), 1024))
                .inputItems(new ItemStack(ImaginaryComponentItems.ELECTRIC_MOTOR_IMAGINARY_4.get(), 256))
                .outputItems(new ItemStack(ImaginaryComponentItems.ELECTRIC_PUMP_IMAGINARY_4.get(), 1))
                .duration(5000).EUt(IM4_EUT));

        buildAndBind(provider, "hk3gtl_conveyor_imaginary_4", research, b -> b
                .inputItems(new ItemStack(ImaginaryComponentItems.CONVEYOR_MODULE_IMAGINARY_3.get(), 256))
                .inputItems(new ItemStack(HonkaiMaterialItems.FLUID_ALLOY_BLOCK.get(), 1024))
                .inputItems(new ItemStack(ImaginaryComponentItems.ELECTRIC_MOTOR_IMAGINARY_4.get(), 512))
                .outputItems(new ItemStack(ImaginaryComponentItems.CONVEYOR_MODULE_IMAGINARY_4.get(), 1))
                .duration(5000).EUt(IM4_EUT));

        buildAndBind(provider, "hk3gtl_robot_arm_imaginary_4", research, b -> b
                .inputItems(new ItemStack(ImaginaryComponentItems.ROBOT_ARM_IMAGINARY_3.get(), 128))
                .inputItems(new ItemStack(ImaginaryComponentItems.ELECTRIC_MOTOR_IMAGINARY_4.get(), 128))
                .inputItems(new ItemStack(ImaginaryComponentItems.ELECTRIC_PISTON_IMAGINARY_4.get(), 128))
                .inputItems(new ItemStack(ImaginaryCircuitItems.CIRCUIT_IMAGINARY_4.get(), 128))
                .outputItems(new ItemStack(ImaginaryComponentItems.ROBOT_ARM_IMAGINARY_4.get(), 1))
                .duration(5400).EUt(IM4_EUT));

        buildAndBind(provider, "hk3gtl_field_gen_imaginary_4", research, b -> b
                .inputItems(new ItemStack(ImaginaryComponentItems.FIELD_GENERATOR_IMAGINARY_3.get(), 128))
                .inputItems(new ItemStack(HonkaiMaterialItems.ANCIENT_LEGACY.get(), 512))
                .inputItems(new ItemStack(HonkaiMaterialItems.DENSE_HONKAI_FUEL_ROD.get(), 512))
                .inputItems(new ItemStack(ImaginaryCircuitItems.CIRCUIT_IMAGINARY_4.get(), 128))
                .outputItems(new ItemStack(ImaginaryComponentItems.FIELD_GENERATOR_IMAGINARY_4.get(), 1))
                .duration(5400).EUt(IM4_EUT));

        buildAndBind(provider, "hk3gtl_emitter_imaginary_4", research, b -> b
                .inputItems(new ItemStack(ImaginaryComponentItems.EMITTER_IMAGINARY_3.get(), 128))
                .inputItems(new ItemStack(HonkaiMaterialItems.ANCIENT_WILL.get(), 512))
                .inputItems(new ItemStack(HonkaiMaterialItems.DENSE_HONKAI_FUEL_ROD.get(), 512))
                .inputItems(new ItemStack(ImaginaryCircuitItems.CIRCUIT_IMAGINARY_4.get(), 128))
                .outputItems(new ItemStack(ImaginaryComponentItems.EMITTER_IMAGINARY_4.get(), 1))
                .duration(5400).EUt(IM4_EUT));

        buildAndBind(provider, "hk3gtl_sensor_imaginary_4", research, b -> b
                .inputItems(new ItemStack(ImaginaryComponentItems.SENSOR_IMAGINARY_3.get(), 128))
                .inputItems(new ItemStack(HonkaiMaterialItems.ANCIENT_WILL.get(), 512))
                .inputItems(new ItemStack(HonkaiMaterialItems.DENSE_HONKAI_FUEL_ROD.get(), 512))
                .inputItems(new ItemStack(ImaginaryCircuitItems.CIRCUIT_IMAGINARY_4.get(), 128))
                .outputItems(new ItemStack(ImaginaryComponentItems.SENSOR_IMAGINARY_4.get(), 1))
                .duration(5400).EUt(IM4_EUT));
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
