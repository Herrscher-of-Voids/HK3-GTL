package com.sirin.hk3gtl.common.recipe.abyss;



import com.gregtechceu.gtceu.api.data.chemical.ChemicalHelper;
import com.gregtechceu.gtceu.api.data.tag.TagPrefix;
import com.gregtechceu.gtceu.common.data.GTRecipeTypes;
import com.sirin.hk3gtl.common.constants.Hk3Tiers;
import com.sirin.hk3gtl.common.constants.Hk3Values;
import com.sirin.hk3gtl.common.item.abyss.AbyssCircuitItems;
import com.sirin.hk3gtl.common.item.abyss.AbyssComponentItems;
import com.sirin.hk3gtl.common.item.honkai.HonkaiMaterialItems;
import com.sirin.hk3gtl.common.item.soulium.SouliumChainItems;
import com.sirin.hk3gtl.common.material.SouliumMaterial;
import com.sirin.hk3gtl.common.research.Hk3RecipeResearchGate;
import net.minecraft.data.recipes.FinishedRecipe;
import net.minecraft.world.item.ItemStack;

import java.util.function.Consumer;

/**
 * 海渊 II~IV 八大件组装配方。
 *
 * 研究门槛策略：
 * - 不使用 notConsumable 许可物品
 * - 通过 Hk3RecipeResearchGate.bind() 将配方 ID 绑定到研究节点
 * - 机器端：Mixin 拦截配方匹配，检查最近玩家研究状态
 * - JEI 端：根据客户端研究缓存隐藏未解锁配方
 */
/**
 * 海渊 II~IV 八大件组装配方 —— 带研究门槛的升级部件配方。
 *
 * <h3>职责</h3>
 * 注册海渊阶段八大件（马达/活塞/泵/传送带/机械臂/力场/发射器/传感器）的
 * II、III、IV 级配方，每级绑定对应研究节点。
 *
 * <h3>研究门槛机制</h3>
 * 通过 Hk3RecipeResearchGate.bind() 将配方ID与研究节点ID关联。
 * 机器端 Mixin 拦截未完成研究的配方，JEI 端显示"需要研究认知"提示。
 *
 * <h3>修改指南</h3>
 * <ul>
 *   <li>调整电压：修改 AB2/AB3/AB4_EUT 常量</li>
 *   <li>调整研究门槛：修改各方法中的 research 变量（研究节点ID）</li>
 *   <li>新增部件级别：新增方法并调用 buildAndBind</li>
 *   <li>配方ID格式："hk3gtl_{部件类型}_abyss_{级别}"</li>
 *   <li>改输入/输出数量：修改 buildAndBind 内 lambda 的 inputItems/outputItems。</li>
 *   <li>改耗时/电压：修改 lambda 内 duration/EUt；不要用 GTValues.V[15+]。</li>
 *   <li>所有配方走 buildAndBind，保证注册后自动绑定研究门槛。</li>
 * </ul>
 */
public class AbyssComponentRecipes {

    /** 海渊II阶段基准电压 */
    private static final long AB2_EUT = Hk3Values.VA_LONG[Hk3Tiers.ABYSS_2];
    /** 海渊III阶段基准电压 */
    private static final long AB3_EUT = Hk3Values.VA_LONG[Hk3Tiers.ABYSS_3];
    /** 海渊IV阶段基准电压 */
    private static final long AB4_EUT = Hk3Values.VA_LONG[Hk3Tiers.ABYSS_4];

    /**
     * 海渊II级八大件配方（绑定研究节点 R-AB-011）。
     * 输入主要消耗海渊I八大件、魂钢材料、稳定崩坏晶体和海渊II电路。
     */
    public static void addAbyssIIComponentRecipes(Consumer<FinishedRecipe> provider) {
        String research = "R-AB-011";

        buildAndBind(provider, "hk3gtl_motor_abyss_2", research, b -> b
                .inputItems(new ItemStack(AbyssComponentItems.ELECTRIC_MOTOR_ABYSS_1.get(), 256))
                .inputItems(ChemicalHelper.get(TagPrefix.wireFine, SouliumMaterial.SOULIUM, 8192))
                .inputItems(new ItemStack(HonkaiMaterialItems.STABILIZED_HONKAI_CRYSTAL.get(), 512))
                .inputItems(new ItemStack(AbyssCircuitItems.CIRCUIT_ABYSS_2.get(), 128))
                .outputItems(new ItemStack(AbyssComponentItems.ELECTRIC_MOTOR_ABYSS_2.get(), 2))
                .duration(1600).EUt(AB2_EUT));

        buildAndBind(provider, "hk3gtl_piston_abyss_2", research, b -> b
                .inputItems(new ItemStack(AbyssComponentItems.ELECTRIC_PISTON_ABYSS_1.get(), 256))
                .inputItems(ChemicalHelper.get(TagPrefix.plate, SouliumMaterial.SOULIUM, 2048))
                .inputItems(new ItemStack(AbyssComponentItems.ELECTRIC_MOTOR_ABYSS_2.get(), 256))
                .outputItems(new ItemStack(AbyssComponentItems.ELECTRIC_PISTON_ABYSS_2.get(), 2))
                .duration(1600).EUt(AB2_EUT));

        buildAndBind(provider, "hk3gtl_pump_abyss_2", research, b -> b
                .inputItems(new ItemStack(AbyssComponentItems.ELECTRIC_PUMP_ABYSS_1.get(), 256))
                .inputItems(ChemicalHelper.get(TagPrefix.ring, SouliumMaterial.SOULIUM, 2048))
                .inputItems(new ItemStack(AbyssComponentItems.ELECTRIC_MOTOR_ABYSS_2.get(), 256))
                .outputItems(new ItemStack(AbyssComponentItems.ELECTRIC_PUMP_ABYSS_2.get(), 2))
                .duration(1600).EUt(AB2_EUT));

        buildAndBind(provider, "hk3gtl_conveyor_abyss_2", research, b -> b
                .inputItems(new ItemStack(AbyssComponentItems.CONVEYOR_MODULE_ABYSS_1.get(), 256))
                .inputItems(ChemicalHelper.get(TagPrefix.plate, SouliumMaterial.SOULIUM, 2048))
                .inputItems(new ItemStack(AbyssComponentItems.ELECTRIC_MOTOR_ABYSS_2.get(), 512))
                .outputItems(new ItemStack(AbyssComponentItems.CONVEYOR_MODULE_ABYSS_2.get(), 2))
                .duration(1600).EUt(AB2_EUT));

        buildAndBind(provider, "hk3gtl_robot_arm_abyss_2", research, b -> b
                .inputItems(new ItemStack(AbyssComponentItems.ROBOT_ARM_ABYSS_1.get(), 128))
                .inputItems(new ItemStack(AbyssComponentItems.ELECTRIC_MOTOR_ABYSS_2.get(), 128))
                .inputItems(new ItemStack(AbyssComponentItems.ELECTRIC_PISTON_ABYSS_2.get(), 128))
                .inputItems(new ItemStack(AbyssCircuitItems.CIRCUIT_ABYSS_2.get(), 128))
                .outputItems(new ItemStack(AbyssComponentItems.ROBOT_ARM_ABYSS_2.get(), 2))
                .duration(1600).EUt(AB2_EUT));

        buildAndBind(provider, "hk3gtl_field_gen_abyss_2", research, b -> b
                .inputItems(new ItemStack(AbyssComponentItems.FIELD_GENERATOR_ABYSS_1.get(), 128))
                .inputItems(ChemicalHelper.get(TagPrefix.frameGt, SouliumMaterial.SOULIUM, 512))
                .inputItems(new ItemStack(HonkaiMaterialItems.STABILIZED_HONKAI_CRYSTAL.get(), 1024))
                .inputItems(new ItemStack(AbyssCircuitItems.CIRCUIT_ABYSS_2.get(), 128))
                .outputItems(new ItemStack(AbyssComponentItems.FIELD_GENERATOR_ABYSS_2.get(), 2))
                .duration(1600).EUt(AB2_EUT));

        buildAndBind(provider, "hk3gtl_emitter_abyss_2", research, b -> b
                .inputItems(new ItemStack(AbyssComponentItems.EMITTER_ABYSS_1.get(), 128))
                .inputItems(ChemicalHelper.get(TagPrefix.rod, SouliumMaterial.SOULIUM, 1024))
                .inputItems(new ItemStack(HonkaiMaterialItems.STABILIZED_HONKAI_CRYSTAL.get(), 512))
                .inputItems(new ItemStack(AbyssCircuitItems.CIRCUIT_ABYSS_2.get(), 128))
                .outputItems(new ItemStack(AbyssComponentItems.EMITTER_ABYSS_2.get(), 2))
                .duration(1600).EUt(AB2_EUT));

        buildAndBind(provider, "hk3gtl_sensor_abyss_2", research, b -> b
                .inputItems(new ItemStack(AbyssComponentItems.SENSOR_ABYSS_1.get(), 128))
                .inputItems(ChemicalHelper.get(TagPrefix.plate, SouliumMaterial.SOULIUM, 1024))
                .inputItems(new ItemStack(HonkaiMaterialItems.STABILIZED_HONKAI_CRYSTAL.get(), 512))
                .inputItems(new ItemStack(AbyssCircuitItems.CIRCUIT_ABYSS_2.get(), 128))
                .outputItems(new ItemStack(AbyssComponentItems.SENSOR_ABYSS_2.get(), 2))
                .duration(1600).EUt(AB2_EUT));
    }

    /**
     * 海渊III级八大件配方（绑定研究节点 R-AB-015）。
     * 输入主要消耗海渊II八大件、定向魂钢构件、稳定崩坏晶体和海渊III电路。
     */
    public static void addAbyssIIIComponentRecipes(Consumer<FinishedRecipe> provider) {
        String research = "R-AB-015";

        buildAndBind(provider, "hk3gtl_motor_abyss_3", research, b -> b
                .inputItems(new ItemStack(AbyssComponentItems.ELECTRIC_MOTOR_ABYSS_2.get(), 256))
                .inputItems(ChemicalHelper.get(TagPrefix.wireFine, SouliumMaterial.SOULIUM, 16384))
                .inputItems(new ItemStack(HonkaiMaterialItems.STABILIZED_HONKAI_CRYSTAL.get(), 1024))
                .inputItems(new ItemStack(AbyssCircuitItems.CIRCUIT_ABYSS_3.get(), 128))
                .outputItems(new ItemStack(AbyssComponentItems.ELECTRIC_MOTOR_ABYSS_3.get(), 2))
                .duration(2000).EUt(AB3_EUT));

        buildAndBind(provider, "hk3gtl_piston_abyss_3", research, b -> b
                .inputItems(new ItemStack(AbyssComponentItems.ELECTRIC_PISTON_ABYSS_2.get(), 256))
                .inputItems(new ItemStack(SouliumChainItems.ORIENTED_SOULIUM_COMPONENT.get(), 1024))
                .inputItems(new ItemStack(AbyssComponentItems.ELECTRIC_MOTOR_ABYSS_3.get(), 256))
                .outputItems(new ItemStack(AbyssComponentItems.ELECTRIC_PISTON_ABYSS_3.get(), 2))
                .duration(2000).EUt(AB3_EUT));

        buildAndBind(provider, "hk3gtl_pump_abyss_3", research, b -> b
                .inputItems(new ItemStack(AbyssComponentItems.ELECTRIC_PUMP_ABYSS_2.get(), 256))
                .inputItems(new ItemStack(SouliumChainItems.ORIENTED_SOULIUM_COMPONENT.get(), 1024))
                .inputItems(new ItemStack(AbyssComponentItems.ELECTRIC_MOTOR_ABYSS_3.get(), 256))
                .outputItems(new ItemStack(AbyssComponentItems.ELECTRIC_PUMP_ABYSS_3.get(), 2))
                .duration(2000).EUt(AB3_EUT));

        buildAndBind(provider, "hk3gtl_conveyor_abyss_3", research, b -> b
                .inputItems(new ItemStack(AbyssComponentItems.CONVEYOR_MODULE_ABYSS_2.get(), 256))
                .inputItems(new ItemStack(SouliumChainItems.ORIENTED_SOULIUM_COMPONENT.get(), 1024))
                .inputItems(new ItemStack(AbyssComponentItems.ELECTRIC_MOTOR_ABYSS_3.get(), 512))
                .outputItems(new ItemStack(AbyssComponentItems.CONVEYOR_MODULE_ABYSS_3.get(), 2))
                .duration(2000).EUt(AB3_EUT));

        buildAndBind(provider, "hk3gtl_robot_arm_abyss_3", research, b -> b
                .inputItems(new ItemStack(AbyssComponentItems.ROBOT_ARM_ABYSS_2.get(), 128))
                .inputItems(new ItemStack(AbyssComponentItems.ELECTRIC_MOTOR_ABYSS_3.get(), 128))
                .inputItems(new ItemStack(AbyssComponentItems.ELECTRIC_PISTON_ABYSS_3.get(), 128))
                .inputItems(new ItemStack(AbyssCircuitItems.CIRCUIT_ABYSS_3.get(), 128))
                .outputItems(new ItemStack(AbyssComponentItems.ROBOT_ARM_ABYSS_3.get(), 2))
                .duration(2000).EUt(AB3_EUT));

        buildAndBind(provider, "hk3gtl_field_gen_abyss_3", research, b -> b
                .inputItems(new ItemStack(AbyssComponentItems.FIELD_GENERATOR_ABYSS_2.get(), 128))
                .inputItems(new ItemStack(SouliumChainItems.ORIENTED_SOULIUM_COMPONENT.get(), 512))
                .inputItems(new ItemStack(HonkaiMaterialItems.STABILIZED_HONKAI_CRYSTAL.get(), 2048))
                .inputItems(new ItemStack(AbyssCircuitItems.CIRCUIT_ABYSS_3.get(), 128))
                .outputItems(new ItemStack(AbyssComponentItems.FIELD_GENERATOR_ABYSS_3.get(), 2))
                .duration(2000).EUt(AB3_EUT));

        buildAndBind(provider, "hk3gtl_emitter_abyss_3", research, b -> b
                .inputItems(new ItemStack(AbyssComponentItems.EMITTER_ABYSS_2.get(), 128))
                .inputItems(new ItemStack(SouliumChainItems.ORIENTED_SOULIUM_COMPONENT.get(), 512))
                .inputItems(new ItemStack(HonkaiMaterialItems.STABILIZED_HONKAI_CRYSTAL.get(), 1024))
                .inputItems(new ItemStack(AbyssCircuitItems.CIRCUIT_ABYSS_3.get(), 128))
                .outputItems(new ItemStack(AbyssComponentItems.EMITTER_ABYSS_3.get(), 2))
                .duration(2000).EUt(AB3_EUT));

        buildAndBind(provider, "hk3gtl_sensor_abyss_3", research, b -> b
                .inputItems(new ItemStack(AbyssComponentItems.SENSOR_ABYSS_2.get(), 128))
                .inputItems(new ItemStack(SouliumChainItems.ORIENTED_SOULIUM_COMPONENT.get(), 512))
                .inputItems(new ItemStack(HonkaiMaterialItems.STABILIZED_HONKAI_CRYSTAL.get(), 1024))
                .inputItems(new ItemStack(AbyssCircuitItems.CIRCUIT_ABYSS_3.get(), 128))
                .outputItems(new ItemStack(AbyssComponentItems.SENSOR_ABYSS_3.get(), 2))
                .duration(2000).EUt(AB3_EUT));
    }

    /**
     * 海渊IV级八大件配方（绑定研究节点 R-AB-021）。
     * 输入主要消耗海渊III八大件、定向魂钢构件、压缩崩坏核心和海渊IV电路。
     */
    public static void addAbyssIVComponentRecipes(Consumer<FinishedRecipe> provider) {
        String research = "R-AB-021";

        buildAndBind(provider, "hk3gtl_motor_abyss_4", research, b -> b
                .inputItems(new ItemStack(AbyssComponentItems.ELECTRIC_MOTOR_ABYSS_3.get(), 256))
                .inputItems(ChemicalHelper.get(TagPrefix.wireFine, SouliumMaterial.SOULIUM, 32768))
                .inputItems(new ItemStack(HonkaiMaterialItems.COMPRESSED_HONKAI_CORE.get(), 128))
                .inputItems(new ItemStack(AbyssCircuitItems.CIRCUIT_ABYSS_4.get(), 128))
                .outputItems(new ItemStack(AbyssComponentItems.ELECTRIC_MOTOR_ABYSS_4.get(), 2))
                .duration(2400).EUt(AB4_EUT));

        buildAndBind(provider, "hk3gtl_piston_abyss_4", research, b -> b
                .inputItems(new ItemStack(AbyssComponentItems.ELECTRIC_PISTON_ABYSS_3.get(), 256))
                .inputItems(new ItemStack(SouliumChainItems.ORIENTED_SOULIUM_COMPONENT.get(), 2048))
                .inputItems(new ItemStack(AbyssComponentItems.ELECTRIC_MOTOR_ABYSS_4.get(), 256))
                .outputItems(new ItemStack(AbyssComponentItems.ELECTRIC_PISTON_ABYSS_4.get(), 2))
                .duration(2400).EUt(AB4_EUT));

        buildAndBind(provider, "hk3gtl_pump_abyss_4", research, b -> b
                .inputItems(new ItemStack(AbyssComponentItems.ELECTRIC_PUMP_ABYSS_3.get(), 256))
                .inputItems(new ItemStack(SouliumChainItems.ORIENTED_SOULIUM_COMPONENT.get(), 2048))
                .inputItems(new ItemStack(AbyssComponentItems.ELECTRIC_MOTOR_ABYSS_4.get(), 256))
                .outputItems(new ItemStack(AbyssComponentItems.ELECTRIC_PUMP_ABYSS_4.get(), 2))
                .duration(2400).EUt(AB4_EUT));

        buildAndBind(provider, "hk3gtl_conveyor_abyss_4", research, b -> b
                .inputItems(new ItemStack(AbyssComponentItems.CONVEYOR_MODULE_ABYSS_3.get(), 256))
                .inputItems(new ItemStack(SouliumChainItems.ORIENTED_SOULIUM_COMPONENT.get(), 2048))
                .inputItems(new ItemStack(AbyssComponentItems.ELECTRIC_MOTOR_ABYSS_4.get(), 512))
                .outputItems(new ItemStack(AbyssComponentItems.CONVEYOR_MODULE_ABYSS_4.get(), 2))
                .duration(2400).EUt(AB4_EUT));

        buildAndBind(provider, "hk3gtl_robot_arm_abyss_4", research, b -> b
                .inputItems(new ItemStack(AbyssComponentItems.ROBOT_ARM_ABYSS_3.get(), 128))
                .inputItems(new ItemStack(AbyssComponentItems.ELECTRIC_MOTOR_ABYSS_4.get(), 128))
                .inputItems(new ItemStack(AbyssComponentItems.ELECTRIC_PISTON_ABYSS_4.get(), 128))
                .inputItems(new ItemStack(AbyssCircuitItems.CIRCUIT_ABYSS_4.get(), 128))
                .outputItems(new ItemStack(AbyssComponentItems.ROBOT_ARM_ABYSS_4.get(), 2))
                .duration(2400).EUt(AB4_EUT));

        buildAndBind(provider, "hk3gtl_field_gen_abyss_4", research, b -> b
                .inputItems(new ItemStack(AbyssComponentItems.FIELD_GENERATOR_ABYSS_3.get(), 128))
                .inputItems(new ItemStack(SouliumChainItems.ORIENTED_SOULIUM_COMPONENT.get(), 1024))
                .inputItems(new ItemStack(HonkaiMaterialItems.COMPRESSED_HONKAI_CORE.get(), 256))
                .inputItems(new ItemStack(AbyssCircuitItems.CIRCUIT_ABYSS_4.get(), 128))
                .outputItems(new ItemStack(AbyssComponentItems.FIELD_GENERATOR_ABYSS_4.get(), 2))
                .duration(2400).EUt(AB4_EUT));

        buildAndBind(provider, "hk3gtl_emitter_abyss_4", research, b -> b
                .inputItems(new ItemStack(AbyssComponentItems.EMITTER_ABYSS_3.get(), 128))
                .inputItems(new ItemStack(SouliumChainItems.ORIENTED_SOULIUM_COMPONENT.get(), 1024))
                .inputItems(new ItemStack(HonkaiMaterialItems.COMPRESSED_HONKAI_CORE.get(), 128))
                .inputItems(new ItemStack(AbyssCircuitItems.CIRCUIT_ABYSS_4.get(), 128))
                .outputItems(new ItemStack(AbyssComponentItems.EMITTER_ABYSS_4.get(), 2))
                .duration(2400).EUt(AB4_EUT));

        buildAndBind(provider, "hk3gtl_sensor_abyss_4", research, b -> b
                .inputItems(new ItemStack(AbyssComponentItems.SENSOR_ABYSS_3.get(), 128))
                .inputItems(new ItemStack(SouliumChainItems.ORIENTED_SOULIUM_COMPONENT.get(), 1024))
                .inputItems(new ItemStack(HonkaiMaterialItems.COMPRESSED_HONKAI_CORE.get(), 128))
                .inputItems(new ItemStack(AbyssCircuitItems.CIRCUIT_ABYSS_4.get(), 128))
                .outputItems(new ItemStack(AbyssComponentItems.SENSOR_ABYSS_4.get(), 2))
                .duration(2400).EUt(AB4_EUT));
    }

    /** 配方构建器函数式接口，用于 buildAndBind 的链式配置 */
    @FunctionalInterface
    interface RecipeConfigurator {
        com.gregtechceu.gtceu.data.recipe.builder.GTRecipeBuilder configure(
                com.gregtechceu.gtceu.data.recipe.builder.GTRecipeBuilder builder);
    }

    /**
     * 构建 GT 组装机配方并注册研究门槛绑定。
     * @param recipeId   配方ID，同时用于研究门槛映射
     * @param researchId 绑定的研究节点ID
     */
    private static void buildAndBind(Consumer<FinishedRecipe> provider,
                                     String recipeId, String researchId,
                                     RecipeConfigurator configurator) {
        // 统一构建入口：
        // 1. 创建 GT 组装机配方；
        // 2. 让调用方 lambda 填输入、输出、耗时、电压；
        // 3. 保存配方；
        // 4. 将 recipeId 绑定到研究节点，确保 JEI/机器执行门槛一致。
        configurator.configure(GTRecipeTypes.ASSEMBLER_RECIPES.recipeBuilder(recipeId))
                .save(provider);
        Hk3RecipeResearchGate.bind("assembler", recipeId, researchId);
    }
}
