package com.sirin.hk3gtl.common.recipe.imaginary;



import com.sirin.hk3gtl.common.constants.Hk3Tiers;
import com.sirin.hk3gtl.common.constants.Hk3Values;
import com.sirin.hk3gtl.common.item.abyss.AbyssCircuitItems;
import com.sirin.hk3gtl.common.item.honkai.HonkaiMaterialItems;
import com.sirin.hk3gtl.common.item.imaginary.ImaginaryCircuitItems;
import com.sirin.hk3gtl.common.material.Hk3Materials;
import com.sirin.hk3gtl.common.recipe.Hk3RecipeTypesImaginary;
import com.sirin.hk3gtl.common.research.Hk3RecipeResearchGate;
import net.minecraft.data.recipes.FinishedRecipe;
import net.minecraft.world.item.ItemStack;

import java.util.function.Consumer;

/**
 * 虚数阶段电路配方（v0.4 双阵营版）。
 *
 * <h3>设计点</h3>
 * <ul>
 *   <li>全部走"虚数电路演算圣堂"专属 RecipeType {@code imaginary_circuit_computation}，
 *       脱离 GT 组装机，强迫玩家建演算圣堂多方块才能造高阶电路。</li>
 *   <li>电路 I/II 只需任一阵营核心（天命或逆熵），鼓励玩家先解锁一条侧支。</li>
 *   <li>电路 III/IV 强制同时投入两阵营核心，激活{@code SCHICKSAL_IMAGINARY_CORE} 与
 *       {@code ANTI_ENTROPY_IMAGINARY_CORE} 这两件原本只出现在物品表里的孤儿物品。</li>
 *   <li>受 {@link com.sirin.hk3gtl.common.machine.imaginary.Hk3ImaginaryAnchor 锚定环境约束}
 *       —— 64 格内无已成型 {@code imaginary_anchor_device} 时整套配方推进速度降至 50%。</li>
 * </ul>
 */
public class ImaginaryCircuitRecipes {

    private static final long IM1_EUT = Hk3Values.VA_LONG[Hk3Tiers.IMAGINARY_1];
    private static final long IM2_EUT = Hk3Values.VA_LONG[Hk3Tiers.IMAGINARY_2];
    private static final long IM3_EUT = Hk3Values.VA_LONG[Hk3Tiers.IMAGINARY_3];
    private static final long IM4_EUT = Hk3Values.VA_LONG[Hk3Tiers.IMAGINARY_4];

    /** RecipeType 路径名，注册研究门槛用。 */
    private static final String RT = "imaginary_circuit_computation";

    public static void register(Consumer<FinishedRecipe> provider) {
        // ── 虚数 I 电路：单阵营路线，二选一 ────────────────────────────────
        Hk3RecipeTypesImaginary.IMAGINARY_CIRCUIT_COMPUTATION.recipeBuilder("hk3gtl_circuit_imaginary_1_schicksal")
                .inputItems(new ItemStack(AbyssCircuitItems.CIRCUIT_ABYSS_4.get(), 256))
                .inputItems(new ItemStack(HonkaiMaterialItems.NANO_CERAMIC.get(), 1024))
                .inputItems(new ItemStack(HonkaiMaterialItems.COMPRESSED_HONKAI_CORE.get(), 512))
                .inputItems(new ItemStack(HonkaiMaterialItems.SCHICKSAL_IMAGINARY_CORE.get(), 64))
                .inputFluids(Hk3Materials.LIQUID_HONKAI_ENERGY.getFluid(100000))
                .outputItems(new ItemStack(ImaginaryCircuitItems.CIRCUIT_IMAGINARY_1.get(), 1))
                .duration(2000).EUt(IM1_EUT)
                .save(provider);
        Hk3RecipeResearchGate.bind(RT, "hk3gtl_circuit_imaginary_1_schicksal", "R-IM-001");

        Hk3RecipeTypesImaginary.IMAGINARY_CIRCUIT_COMPUTATION.recipeBuilder("hk3gtl_circuit_imaginary_1_anti_entropy")
                .inputItems(new ItemStack(AbyssCircuitItems.CIRCUIT_ABYSS_4.get(), 256))
                .inputItems(new ItemStack(HonkaiMaterialItems.NANO_CERAMIC.get(), 1024))
                .inputItems(new ItemStack(HonkaiMaterialItems.COMPRESSED_HONKAI_CORE.get(), 512))
                .inputItems(new ItemStack(HonkaiMaterialItems.ANTI_ENTROPY_IMAGINARY_CORE.get(), 64))
                .inputFluids(Hk3Materials.LIQUID_HONKAI_ENERGY.getFluid(100000))
                .outputItems(new ItemStack(ImaginaryCircuitItems.CIRCUIT_IMAGINARY_1.get(), 1))
                .duration(2000).EUt(IM1_EUT)
                .save(provider);
        Hk3RecipeResearchGate.bind(RT, "hk3gtl_circuit_imaginary_1_anti_entropy", "R-IM-001");

        // ── 虚数 II 电路：单阵营路线，二选一 ───────────────────────────────
        Hk3RecipeTypesImaginary.IMAGINARY_CIRCUIT_COMPUTATION.recipeBuilder("hk3gtl_circuit_imaginary_2_schicksal")
                .inputItems(new ItemStack(ImaginaryCircuitItems.CIRCUIT_IMAGINARY_1.get(), 128))
                .inputItems(new ItemStack(HonkaiMaterialItems.SUPERCONDUCTIVE_METAL_HYDROGEN.get(), 2048))
                .inputItems(new ItemStack(HonkaiMaterialItems.SCHICKSAL_IMAGINARY_CORE.get(), 256))
                .inputFluids(Hk3Materials.LIQUID_HONKAI_ENERGY.getFluid(250000))
                .outputItems(new ItemStack(ImaginaryCircuitItems.CIRCUIT_IMAGINARY_2.get(), 1))
                .duration(3000).EUt(IM2_EUT)
                .save(provider);
        Hk3RecipeResearchGate.bind(RT, "hk3gtl_circuit_imaginary_2_schicksal", "R-IM-002");

        Hk3RecipeTypesImaginary.IMAGINARY_CIRCUIT_COMPUTATION.recipeBuilder("hk3gtl_circuit_imaginary_2_anti_entropy")
                .inputItems(new ItemStack(ImaginaryCircuitItems.CIRCUIT_IMAGINARY_1.get(), 128))
                .inputItems(new ItemStack(HonkaiMaterialItems.SUPERCONDUCTIVE_METAL_HYDROGEN.get(), 2048))
                .inputItems(new ItemStack(HonkaiMaterialItems.ANTI_ENTROPY_IMAGINARY_CORE.get(), 256))
                .inputFluids(Hk3Materials.LIQUID_HONKAI_ENERGY.getFluid(250000))
                .outputItems(new ItemStack(ImaginaryCircuitItems.CIRCUIT_IMAGINARY_2.get(), 1))
                .duration(3000).EUt(IM2_EUT)
                .save(provider);
        Hk3RecipeResearchGate.bind(RT, "hk3gtl_circuit_imaginary_2_anti_entropy", "R-IM-002");

        // ── 虚数 III 电路：强制双阵营核心 ──────────────────────────────────
        Hk3RecipeTypesImaginary.IMAGINARY_CIRCUIT_COMPUTATION.recipeBuilder("hk3gtl_circuit_imaginary_3")
                .inputItems(new ItemStack(ImaginaryCircuitItems.CIRCUIT_IMAGINARY_2.get(), 128))
                .inputItems(new ItemStack(HonkaiMaterialItems.EINSTEIN_RINGMAGNET.get(), 1024))
                .inputItems(new ItemStack(HonkaiMaterialItems.ANCIENT_LEGACY.get(), 256))
                .inputItems(new ItemStack(HonkaiMaterialItems.SCHICKSAL_IMAGINARY_CORE.get(), 256))
                .inputItems(new ItemStack(HonkaiMaterialItems.ANTI_ENTROPY_IMAGINARY_CORE.get(), 256))
                .inputFluids(Hk3Materials.LIQUID_HONKAI_ENERGY.getFluid(500000))
                .outputItems(new ItemStack(ImaginaryCircuitItems.CIRCUIT_IMAGINARY_3.get(), 1))
                .duration(4000).EUt(IM3_EUT)
                .save(provider);
        Hk3RecipeResearchGate.bind(RT, "hk3gtl_circuit_imaginary_3", "R-IM-003");

        // ── 虚数 IV 电路：强制双阵营核心 + 远古意志 ───────────────────────
        Hk3RecipeTypesImaginary.IMAGINARY_CIRCUIT_COMPUTATION.recipeBuilder("hk3gtl_circuit_imaginary_4")
                .inputItems(new ItemStack(ImaginaryCircuitItems.CIRCUIT_IMAGINARY_3.get(), 128))
                .inputItems(new ItemStack(HonkaiMaterialItems.ANCIENT_WILL.get(), 256))
                .inputItems(new ItemStack(HonkaiMaterialItems.FLUID_ALLOY_BLOCK.get(), 1024))
                .inputItems(new ItemStack(HonkaiMaterialItems.SCHICKSAL_IMAGINARY_CORE.get(), 512))
                .inputItems(new ItemStack(HonkaiMaterialItems.ANTI_ENTROPY_IMAGINARY_CORE.get(), 512))
                .inputFluids(Hk3Materials.LIQUID_HONKAI_ENERGY.getFluid(1000000))
                .outputItems(new ItemStack(ImaginaryCircuitItems.CIRCUIT_IMAGINARY_4.get(), 1))
                .duration(5000).EUt(IM4_EUT)
                .save(provider);
        Hk3RecipeResearchGate.bind(RT, "hk3gtl_circuit_imaginary_4", "R-IM-004");
    }
}
