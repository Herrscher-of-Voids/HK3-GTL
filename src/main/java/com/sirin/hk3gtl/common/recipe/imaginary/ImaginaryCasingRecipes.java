package com.sirin.hk3gtl.common.recipe.imaginary;



import com.gregtechceu.gtceu.api.data.chemical.ChemicalHelper;
import com.gregtechceu.gtceu.api.data.tag.TagPrefix;
import com.gregtechceu.gtceu.common.data.GTRecipeTypes;
import com.sirin.hk3gtl.common.block.CasingBlocks;
import com.sirin.hk3gtl.common.constants.Hk3Tiers;
import com.sirin.hk3gtl.common.constants.Hk3Values;
import com.sirin.hk3gtl.common.item.honkai.HonkaiMaterialItems;
import com.sirin.hk3gtl.common.material.SouliumMaterial;
import com.sirin.hk3gtl.common.research.Hk3RecipeResearchGate;
import net.minecraft.data.recipes.FinishedRecipe;
import net.minecraft.world.item.ItemStack;

import java.util.function.Consumer;

/**
 * 虚数阶段（5种）多方块机器机壳配方。
 *
 * <h3>维护说明</h3>
 * <ul>
 *   <li>全部使用 GT 组装机，配方 ID 为 {@code hk3gtl_casing_imaginary_*}。</li>
 *   <li>输入侧是海渊机壳 + 虚数阶段材料；输出侧是对应虚数机壳。</li>
 *   <li>修改结构材料成本：改每条配方的第一个 inputItems（海渊机壳数量）。</li>
 *   <li>修改虚数材料成本：改核心/纳米陶瓷/相位镜等 inputItems 数量。</li>
 *   <li>修改产量：改 outputItems 第二参数；修改耗时/耗电：改 duration / EUt。</li>
 *   <li>所有虚数机壳当前统一绑定 {@code R-IM-001}，要分层解锁就在 bind 的 research 变量处拆分。</li>
 * </ul>
 */
public class ImaginaryCasingRecipes {

    private static final long IM1_EUT = Hk3Values.VA_LONG[Hk3Tiers.IMAGINARY_1];

    public static void register(Consumer<FinishedRecipe> provider) {
        String research = "R-IM-001";

        // 1. 虚数之树机壳：海渊机械机壳 + 魂钢板 + 天命核心 → 32。
        // 用途：虚数之树观测阵列等树系/观测系机器的主体结构。
        GTRecipeTypes.ASSEMBLER_RECIPES.recipeBuilder("hk3gtl_casing_imaginary_tree")
                .inputItems(new ItemStack(CasingBlocks.CASING_ABYSS_MECHANICAL.get(), 512))
                .inputItems(ChemicalHelper.get(TagPrefix.plate, SouliumMaterial.SOULIUM, 2048))
                .inputItems(new ItemStack(HonkaiMaterialItems.SCHICKSAL_IMAGINARY_CORE.get(), 512))
                .circuitMeta(8)
                .outputItems(new ItemStack(CasingBlocks.CASING_IMAGINARY_TREE.get(), 32))
                .duration(3200).EUt(IM1_EUT).save(provider);
        Hk3RecipeResearchGate.bind("assembler", "hk3gtl_casing_imaginary_tree", research);

        // 2. 虚数晶格机壳：海渊科研机壳 + 纳米陶瓷 + 逆熵核心 → 32。
        // 用途：虚数电路/研究/数据计算类机器的主体结构。
        GTRecipeTypes.ASSEMBLER_RECIPES.recipeBuilder("hk3gtl_casing_imaginary_lattice")
                .inputItems(new ItemStack(CasingBlocks.CASING_ABYSS_RESEARCH.get(), 512))
                .inputItems(new ItemStack(HonkaiMaterialItems.NANO_CERAMIC.get(), 2048))
                .inputItems(new ItemStack(HonkaiMaterialItems.ANTI_ENTROPY_IMAGINARY_CORE.get(), 512))
                .circuitMeta(8)
                .outputItems(new ItemStack(CasingBlocks.CASING_IMAGINARY_LATTICE.get(), 32))
                .duration(3200).EUt(IM1_EUT).save(provider);
        Hk3RecipeResearchGate.bind("assembler", "hk3gtl_casing_imaginary_lattice", research);

        // 3. 虚数核心机壳：海渊能源机壳 + 压缩崩坏核心 + 超导金属氢 → 32。
        // 用途：虚数阶段能源/反应/供给类机器的主体结构。
        GTRecipeTypes.ASSEMBLER_RECIPES.recipeBuilder("hk3gtl_casing_imaginary_core")
                .inputItems(new ItemStack(CasingBlocks.CASING_ABYSS_ENERGY.get(), 512))
                .inputItems(new ItemStack(HonkaiMaterialItems.COMPRESSED_HONKAI_CORE.get(), 2048))
                .inputItems(new ItemStack(HonkaiMaterialItems.SUPERCONDUCTIVE_METAL_HYDROGEN.get(), 512))
                .circuitMeta(8)
                .outputItems(new ItemStack(CasingBlocks.CASING_IMAGINARY_CORE.get(), 32))
                .duration(3200).EUt(IM1_EUT).save(provider);
        Hk3RecipeResearchGate.bind("assembler", "hk3gtl_casing_imaginary_core", research);

        // 4. 虚数锚定机壳：强化魂钢机壳 + 相位转移镜 + 逆熵核心 → 32。
        // 用途：锚定/空间固定/相位稳定类机器的主体结构。
        GTRecipeTypes.ASSEMBLER_RECIPES.recipeBuilder("hk3gtl_casing_imaginary_anchor")
                .inputItems(new ItemStack(CasingBlocks.CASING_REINFORCED_SOULIUM.get(), 512))
                .inputItems(new ItemStack(HonkaiMaterialItems.PHASE_TRANSFER_MIRROR.get(), 1024))
                .inputItems(new ItemStack(HonkaiMaterialItems.ANTI_ENTROPY_IMAGINARY_CORE.get(), 512))
                .circuitMeta(8)
                .outputItems(new ItemStack(CasingBlocks.CASING_IMAGINARY_ANCHOR.get(), 32))
                .duration(3200).EUt(IM1_EUT).save(provider);
        Hk3RecipeResearchGate.bind("assembler", "hk3gtl_casing_imaginary_anchor", research);

        // 5. 虚数编织机壳：强化魂钢机壳 + 爱因斯坦环形磁铁 + 天命核心 → 32。
        // 用途：物质编织、魂钢超结构等加工类机器的主体结构。
        GTRecipeTypes.ASSEMBLER_RECIPES.recipeBuilder("hk3gtl_casing_imaginary_weave")
                .inputItems(new ItemStack(CasingBlocks.CASING_REINFORCED_SOULIUM.get(), 512))
                .inputItems(new ItemStack(HonkaiMaterialItems.EINSTEIN_RINGMAGNET.get(), 1024))
                .inputItems(new ItemStack(HonkaiMaterialItems.SCHICKSAL_IMAGINARY_CORE.get(), 512))
                .circuitMeta(8)
                .outputItems(new ItemStack(CasingBlocks.CASING_IMAGINARY_WEAVE.get(), 32))
                .duration(3200).EUt(IM1_EUT).save(provider);
        Hk3RecipeResearchGate.bind("assembler", "hk3gtl_casing_imaginary_weave", research);
    }
}
