package com.sirin.hk3gtl.common.recipe.quantum;

import com.gregtechceu.gtceu.common.data.GTRecipeTypes;
import com.sirin.hk3gtl.common.block.CasingBlocks;
import com.sirin.hk3gtl.common.constants.Hk3Tiers;
import com.sirin.hk3gtl.common.constants.Hk3Values;
import com.sirin.hk3gtl.common.item.honkai.HonkaiMaterialItems;
import com.sirin.hk3gtl.common.item.imaginary.ImaginaryCircuitItems;
import com.sirin.hk3gtl.common.material.Hk3Materials;
import com.sirin.hk3gtl.common.research.Hk3RecipeResearchGate;
import net.minecraft.data.recipes.FinishedRecipe;
import net.minecraft.world.item.ItemStack;

import java.util.List;
import java.util.function.Consumer;
import com.sirin.hk3gtl.common.research.Hk3ElectronicResearch;

/**
 * 【文件职责】
 * - 注册量子阶段 5 种机壳的组装机配方，供量子/终焉控制器建造消耗。
 * - 调用链：QuantumStageRecipes.register -> QuantumCasingRecipes.register。
 *
 * 【变更记录】2026-05-19
 * - 删除：无。
 * - 新增：
 *   1) 量子纠缠/之海/世界泡/通量/舰载机壳各 1 条组装配方（32 个/批）。
 * - 修改：无。
 * - 用途：
 *   1) 打破 AdvancedControllerRecipes 对量子机壳的需求与“无机壳来源”死锁。
 *   2) 输入为虚数机壳 + 虚数 IV 电路 + 阶段材料，避免控制器↔机壳直接配方回圈。
 */
/**
 * 【变更记录 #2】2026-09-25 03:59:11（第 2 次备注 · 内测5修订71）
 * 删除：单一电路形态或旧电压显示限制。新增：统一系列及电压映射。
 * 修改：电路输入使用本等级标签，允许不同系列替代；输出、材料成本及研究门槛保持明确。
 * 用途：保持同级电路可替换、资源与游戏行为一致。
 */
/**
 * 【变更记录 #3】2026-09-30 02:17:47（第3次备注 · 内测5修订107）
 * 删除：本文件可执行代码中的旧电压键及常量引用，不保留旧键注册别名。
 * 新增：16档正式缩写作为唯一电压标识；逐文件映射见logs/voltage-keys-r107。
 * 修改：注册、配方、查询或标签引用按原tier序号一一迁移；数值、层级与资源内容保持原义。
 * 用途：避免显示名与实际注册键不一致；历史备注保留，旧存档不自动改写。
 */
public final class QuantumCasingRecipes {

    private static final long Q1_EUT = Hk3Values.VA_LONG[Hk3Tiers.IMV];

    private QuantumCasingRecipes() {}

    public static void register(Consumer<FinishedRecipe> provider) {
        List<String> research = Hk3ElectronicResearch.requirements(2);

        GTRecipeTypes.ASSEMBLER_RECIPES.recipeBuilder("hk3gtl_casing_quantum_entangle")
                .inputItems(new ItemStack(CasingBlocks.CASING_IMAGINARY_LATTICE.get(), 256))
                .inputItems(com.sirin.hk3gtl.common.item.Hk3CircuitCatalog.tag(22), 32)
                .inputItems(new ItemStack(HonkaiMaterialItems.EINSTEIN_RINGMAGNET.get(), 256))
                .circuitMeta(8)
                .outputItems(new ItemStack(CasingBlocks.CASING_QUANTUM_ENTANGLE.get(), 32))
                .duration(3200).EUt(Q1_EUT).save(provider);
        Hk3RecipeResearchGate.bindAll("assembler", "hk3gtl_casing_quantum_entangle", research);

        GTRecipeTypes.ASSEMBLER_RECIPES.recipeBuilder("hk3gtl_casing_quantum_sea")
                .inputItems(new ItemStack(CasingBlocks.CASING_IMAGINARY_TREE.get(), 256))
                .inputItems(com.sirin.hk3gtl.common.item.Hk3CircuitCatalog.tag(22), 32)
                .inputItems(new ItemStack(HonkaiMaterialItems.WORLD_BUBBLE_SAMPLE.get(), 64))
                .inputFluids(Hk3Materials.LIQUID_HONKAI_ENERGY.getFluid(18432))
                .circuitMeta(8)
                .outputItems(new ItemStack(CasingBlocks.CASING_QUANTUM_SEA.get(), 32))
                .duration(3200).EUt(Q1_EUT).save(provider);
        Hk3RecipeResearchGate.bindAll("assembler", "hk3gtl_casing_quantum_sea", research);

        GTRecipeTypes.ASSEMBLER_RECIPES.recipeBuilder("hk3gtl_casing_quantum_bubble")
                .inputItems(new ItemStack(CasingBlocks.CASING_IMAGINARY_ANCHOR.get(), 256))
                .inputItems(com.sirin.hk3gtl.common.item.Hk3CircuitCatalog.tag(22), 32)
                .inputItems(new ItemStack(HonkaiMaterialItems.WORLD_BUBBLE_SAMPLE.get(), 128))
                .circuitMeta(8)
                .outputItems(new ItemStack(CasingBlocks.CASING_QUANTUM_BUBBLE.get(), 32))
                .duration(3200).EUt(Q1_EUT).save(provider);
        Hk3RecipeResearchGate.bindAll("assembler", "hk3gtl_casing_quantum_bubble", research);

        GTRecipeTypes.ASSEMBLER_RECIPES.recipeBuilder("hk3gtl_casing_quantum_flux")
                .inputItems(new ItemStack(CasingBlocks.CASING_IMAGINARY_CORE.get(), 256))
                .inputItems(com.sirin.hk3gtl.common.item.Hk3CircuitCatalog.tag(22), 32)
                .inputItems(new ItemStack(HonkaiMaterialItems.SUPERCONDUCTIVE_METAL_HYDROGEN.get(), 256))
                .circuitMeta(8)
                .outputItems(new ItemStack(CasingBlocks.CASING_QUANTUM_FLUX.get(), 32))
                .duration(3200).EUt(Q1_EUT).save(provider);
        Hk3RecipeResearchGate.bindAll("assembler", "hk3gtl_casing_quantum_flux", research);

        GTRecipeTypes.ASSEMBLER_RECIPES.recipeBuilder("hk3gtl_casing_quantum_shipboard")
                .inputItems(new ItemStack(CasingBlocks.CASING_IMAGINARY_WEAVE.get(), 256))
                .inputItems(com.sirin.hk3gtl.common.item.Hk3CircuitCatalog.tag(22), 32)
                .inputItems(new ItemStack(HonkaiMaterialItems.COMPRESSED_HONKAI_CORE.get(), 512))
                .circuitMeta(8)
                .outputItems(new ItemStack(CasingBlocks.CASING_QUANTUM_SHIPBOARD.get(), 32))
                .duration(3200).EUt(Q1_EUT).save(provider);
        Hk3RecipeResearchGate.bindAll("assembler", "hk3gtl_casing_quantum_shipboard", research);
    }
}

// 【变更记录 · 修订163】2026-10-17 15:05:46：移除本类生产配方对旧 R-* 研究的活动绑定，按现行电路平台或功能前级明确绑定 RN 课题；多前置全部保留。输入输出、数量、耗电与时长不变；本轮接线不代表全部工业工艺或百课题已完成实机验收。
