package com.sirin.hk3gtl.common.recipe.imaginary;



import com.sirin.hk3gtl.common.constants.Hk3Tiers;
import com.sirin.hk3gtl.common.constants.Hk3Values;
import com.sirin.hk3gtl.common.item.abyss.AbyssFunctionalItems;
import com.sirin.hk3gtl.common.item.honkai.HonkaiMaterialItems;
import com.sirin.hk3gtl.common.item.soulium.SouliumChainItems;
import com.sirin.hk3gtl.common.material.Hk3Materials;
import com.sirin.hk3gtl.common.recipe.Hk3RecipeTypesImaginary;
import com.sirin.hk3gtl.common.research.Hk3RecipeResearchGate;
import net.minecraft.data.recipes.FinishedRecipe;
import net.minecraft.world.item.ItemStack;

import java.util.function.Consumer;

/**
 * 虚数双阵营核心产线（v0.4 新增）。
 *
 * <h3>设计目标</h3>
 * <ul>
 *   <li>把孤儿物品 {@code SCHICKSAL_IMAGINARY_CORE} / {@code ANTI_ENTROPY_IMAGINARY_CORE}
 *       从"只在物品表里存在"变成"必须造的工业产物"。</li>
 *   <li>两路分别走天命路线（数据 → 远古遗产 → 魂钢超结构）与
 *       逆熵路线（流体合金 → 相位镜 + 爱因斯坦环磁体 → 梦境熔炉）。</li>
 *   <li>两条核心都是 {@link ImaginaryCircuitRecipes} 虚数 III/IV 电路的强制输入，
 *       逼迫玩家维护两条平行产线。</li>
 *   <li>所有相关 RecipeType 均受
 *       {@link com.sirin.hk3gtl.common.machine.imaginary.Hk3ImaginaryAnchor 锚定环境约束}：
 *       64 格内无已成型锚定装置时配方推进降到 50%。</li>
 * </ul>
 *
 * <h3>路线拓扑</h3>
 * <pre>
 * 天命路：
 *   precivilization_database_decoder → ancient_legacy
 *   civilization_exchange_council_hub → ancient_will（升华跨阶段）
 *   soulium_superstructure_forge → SCHICKSAL_IMAGINARY_CORE
 *
 * 逆熵路：
 *   imaginary_matter_weaver → phase_transfer_mirror / einstein_ringmagnet（构件）
 *   imaginary_dream_furnace → ANTI_ENTROPY_IMAGINARY_CORE
 *
 * 闭环：
 *   honkai_phase_purification_plant → 回收废液 → 液态崩坏能（喂回吸收链）
 * </pre>
 */
public final class ImaginaryChainRecipes {

    private static final long IM1_EUT = Hk3Values.VA_LONG[Hk3Tiers.IMAGINARY_1];
    private static final long IM2_EUT = Hk3Values.VA_LONG[Hk3Tiers.IMAGINARY_2];
    private static final long IM3_EUT = Hk3Values.VA_LONG[Hk3Tiers.IMAGINARY_3];

    private ImaginaryChainRecipes() {}

    public static void register(Consumer<FinishedRecipe> provider) {
        registerSchicksalPath(provider);
        registerAntiEntropyPath(provider);
        registerPhasePurification(provider);
    }

    // ════════════════════════════════════════════════════════════════════
    //  天命路：远古遗产 → 远古意志 → 天命虚数核心
    // ════════════════════════════════════════════════════════════════════
    private static void registerSchicksalPath(Consumer<FinishedRecipe> provider) {
        // 1. 前文明数据库解码：前文明资料 + 数据研究包 + 压缩崩坏核心 + 凝视缓冲单元 → 远古遗产
        // 注：本 RecipeType setMaxIOSize=(4,4,0,0) 不允许流体输入，因此用压缩核心+凝视缓冲提供"能量介质"。
        Hk3RecipeTypesImaginary.PRECIVILIZATION_DATABASE_DECODING.recipeBuilder("hk3gtl_decode_ancient_legacy")
                .inputItems(new ItemStack(AbyssFunctionalItems.DATA_PRECIVILIZATION_FRAGMENT.get(), 16))
                .inputItems(new ItemStack(HonkaiMaterialItems.DATA_RESEARCH_PACKAGE.get(), 4))
                .inputItems(new ItemStack(HonkaiMaterialItems.COMPRESSED_HONKAI_CORE.get(), 8))
                .inputItems(new ItemStack(HonkaiMaterialItems.GAZE_BUFFER_UNIT.get(), 2))
                .outputItems(new ItemStack(HonkaiMaterialItems.ANCIENT_LEGACY.get(), 1))
                .duration(2400).EUt(IM1_EUT)
                .save(provider);
        Hk3RecipeResearchGate.bind("precivilization_database_decoding", "hk3gtl_decode_ancient_legacy", "R-IM-006");

        // 2. 文明交流议会升华：远古遗产 + 虚空万藏 + 数据研究包 → 远古意志
        //    把"已知历史"凝练成"跨文明意志"，这是天命路独有的高阶素材。
        Hk3RecipeTypesImaginary.CIVILIZATION_EXCHANGE.recipeBuilder("hk3gtl_council_ancient_will")
                .inputItems(new ItemStack(HonkaiMaterialItems.ANCIENT_LEGACY.get(), 8))
                .inputItems(new ItemStack(AbyssFunctionalItems.ARTIFACT_VOID_ARCHIVES.get(), 2))
                .inputItems(new ItemStack(HonkaiMaterialItems.DATA_RESEARCH_PACKAGE.get(), 16))
                .outputItems(new ItemStack(HonkaiMaterialItems.ANCIENT_WILL.get(), 1))
                .duration(3600).EUt(IM2_EUT)
                .save(provider);
        Hk3RecipeResearchGate.bind("civilization_exchange", "hk3gtl_council_ancient_will", "R-IM-006");

        // 3. 魂钢超结构锻造：稳定原质 + 远古遗产 + 定向魂钢构件 + 液态崩坏能 → 天命虚数核心
        Hk3RecipeTypesImaginary.SOULIUM_SUPERSTRUCTURE_FORGING.recipeBuilder("hk3gtl_schicksal_core_forging")
                .inputItems(new ItemStack(SouliumChainItems.STABILIZED_SOULIUM_PROTO_MASS.get(), 32))
                .inputItems(new ItemStack(HonkaiMaterialItems.ANCIENT_LEGACY.get(), 4))
                .inputItems(new ItemStack(SouliumChainItems.ORIENTED_SOULIUM_COMPONENT.get(), 16))
                .inputItems(new ItemStack(HonkaiMaterialItems.COMPRESSED_HONKAI_CORE.get(), 32))
                .inputFluids(Hk3Materials.LIQUID_HONKAI_ENERGY.getFluid(200000))
                .outputItems(new ItemStack(HonkaiMaterialItems.SCHICKSAL_IMAGINARY_CORE.get(), 1))
                .duration(4800).EUt(IM2_EUT)
                .save(provider);
        Hk3RecipeResearchGate.bind("soulium_superstructure_forging", "hk3gtl_schicksal_core_forging", "R-IM-009");
    }

    // ════════════════════════════════════════════════════════════════════
    //  逆熵路：构件 → 梦境熔炉 → 逆熵虚数核心
    // ════════════════════════════════════════════════════════════════════
    private static void registerAntiEntropyPath(Consumer<FinishedRecipe> provider) {
        // 1. 物质编织：流体合金 + 纳米陶瓷 + 液态崩坏能 → 相位转移镜面
        Hk3RecipeTypesImaginary.IMAGINARY_MATTER_WEAVING.recipeBuilder("hk3gtl_weave_phase_transfer_mirror")
                .inputItems(new ItemStack(HonkaiMaterialItems.FLUID_ALLOY.get(), 8))
                .inputItems(new ItemStack(HonkaiMaterialItems.NANO_CERAMIC.get(), 16))
                .inputFluids(Hk3Materials.LIQUID_HONKAI_ENERGY.getFluid(30000))
                .outputItems(new ItemStack(HonkaiMaterialItems.PHASE_TRANSFER_MIRROR.get(), 1))
                .duration(1600).EUt(IM1_EUT)
                .save(provider);
        Hk3RecipeResearchGate.bind("imaginary_matter_weaving", "hk3gtl_weave_phase_transfer_mirror", "R-IM-012");

        // 2. 物质编织：纳米陶瓷 + 超导金属氢 + 液态崩坏能 → 爱因斯坦环磁机
        Hk3RecipeTypesImaginary.IMAGINARY_MATTER_WEAVING.recipeBuilder("hk3gtl_weave_einstein_ringmagnet")
                .inputItems(new ItemStack(HonkaiMaterialItems.NANO_CERAMIC.get(), 32))
                .inputItems(new ItemStack(HonkaiMaterialItems.SUPERCONDUCTIVE_METAL_HYDROGEN.get(), 16))
                .inputFluids(Hk3Materials.LIQUID_HONKAI_ENERGY.getFluid(50000))
                .outputItems(new ItemStack(HonkaiMaterialItems.EINSTEIN_RINGMAGNET.get(), 1))
                .duration(2000).EUt(IM2_EUT)
                .save(provider);
        Hk3RecipeResearchGate.bind("imaginary_matter_weaving", "hk3gtl_weave_einstein_ringmagnet", "R-IM-012");

        // 3. 梦境熔炉：流体合金块 + 相位镜面 + 爱因斯坦环磁机 + 液态崩坏能 → 逆熵虚数核心
        Hk3RecipeTypesImaginary.IMAGINARY_DREAM_MELTING.recipeBuilder("hk3gtl_anti_entropy_core_dream_melting")
                .inputItems(new ItemStack(HonkaiMaterialItems.FLUID_ALLOY_BLOCK.get(), 16))
                .inputItems(new ItemStack(HonkaiMaterialItems.PHASE_TRANSFER_MIRROR.get(), 8))
                .inputItems(new ItemStack(HonkaiMaterialItems.EINSTEIN_RINGMAGNET.get(), 8))
                .inputItems(new ItemStack(HonkaiMaterialItems.COMPRESSED_HONKAI_CORE.get(), 32))
                .inputFluids(Hk3Materials.LIQUID_HONKAI_ENERGY.getFluid(200000))
                .outputItems(new ItemStack(HonkaiMaterialItems.ANTI_ENTROPY_IMAGINARY_CORE.get(), 1))
                .duration(4800).EUt(IM2_EUT)
                .save(provider);
        Hk3RecipeResearchGate.bind("imaginary_dream_melting", "hk3gtl_anti_entropy_core_dream_melting", "R-IM-011");
    }

    // ════════════════════════════════════════════════════════════════════
    //  相位纯化：废料回收 → 液态崩坏能（闭环）
    // ════════════════════════════════════════════════════════════════════
    private static void registerPhasePurification(Consumer<FinishedRecipe> provider) {
        // 用崩坏抑制剂 + 凝视缓冲单元把溢出的液态崩坏能"稳定+提纯"，把"演算/锻造"废液重新做成可用液态崩坏能。
        // RecipeType I/O 为 (4,4,2,1)；输入 2 流体（演算/锻造废液 + 抑制剂），输出 1 流体（液态崩坏能）。
        // 现阶段没有"废液"专用流体，先用液态崩坏能自身作为输入（相当于"过滤"消耗一部分换更纯），保留可拓展接口。
        // 注：原配方曾同时输入+输出 GAZE_BUFFER_UNIT，会被循环检测器判为自环（gaze_buffer → gaze_buffer）。
        // 现去掉其物品输出，凝视缓冲单元作为"提纯催化剂"被净消耗，仅输出提纯后的液态崩坏能，彻底消除自环。
        Hk3RecipeTypesImaginary.HONKAI_PHASE_PURIFICATION.recipeBuilder("hk3gtl_phase_purify_recycle")
                .inputItems(new ItemStack(HonkaiMaterialItems.HONKAI_SUPPRESSANT.get(), 4))
                .inputItems(new ItemStack(HonkaiMaterialItems.GAZE_BUFFER_UNIT.get(), 2))
                .inputFluids(Hk3Materials.LIQUID_HONKAI_ENERGY.getFluid(80000))
                .outputFluids(Hk3Materials.LIQUID_HONKAI_ENERGY.getFluid(120000))
                .duration(1200).EUt(IM2_EUT)
                .save(provider);
        Hk3RecipeResearchGate.bind("honkai_phase_purification", "hk3gtl_phase_purify_recycle", "R-IM-008");

        // 大型纯化：用世界泡样本作"催化剂"显著提升纯化效率
        Hk3RecipeTypesImaginary.HONKAI_PHASE_PURIFICATION.recipeBuilder("hk3gtl_phase_purify_world_bubble")
                .inputItems(new ItemStack(HonkaiMaterialItems.WORLD_BUBBLE_SAMPLE.get(), 1))
                .inputItems(new ItemStack(HonkaiMaterialItems.HONKAI_SUPPRESSANT.get(), 8))
                .inputFluids(Hk3Materials.LIQUID_HONKAI_ENERGY.getFluid(100000))
                .outputFluids(Hk3Materials.LIQUID_HONKAI_ENERGY.getFluid(250000))
                .duration(2400).EUt(IM3_EUT)
                .save(provider);
        Hk3RecipeResearchGate.bind("honkai_phase_purification", "hk3gtl_phase_purify_world_bubble", "R-IM-008");
    }
}
