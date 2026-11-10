package com.sirin.hk3gtl.common.recipe.imaginary;


/**
 * 【文件职责】
 * - 负责 ImaginaryCasingRecipes 对应的配方注册与门槛绑定。
 * - 关键调用链：由上层系统入口调用 -> 本文件核心方法 -> 下游模块。
 *
 * 【变更记录】2026-05-19
 * - 删除：
 *   1) 初始归档备注：自 v0.3 基线梳理，无本次 diff。
 * - 新增：
 *   1) 新增统一变更备注块，便于后续维护与审计追踪。
 * - 修改：
 *   1) 未改动业务逻辑，仅补充文件级职责与维护注释模板。
 * - 用途：
 *   1) 帮助维护者快速理解文件职责、变更背景与风险点。
 *
 * 【段内说明】
 * - 复杂方法补充“干什么 / 边界 / 线程侧”精简中文注释。
 */
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

import java.util.List;
import java.util.function.Consumer;
import com.sirin.hk3gtl.common.research.Hk3ElectronicResearch;

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
/**
 * 【变更记录 #1】2026-09-30 02:17:47（第1次备注 · 内测5修订107）
 * 删除：本文件可执行代码中的旧电压键及常量引用，不保留旧键注册别名。
 * 新增：16档正式缩写作为唯一电压标识；逐文件映射见logs/voltage-keys-r107。
 * 修改：注册、配方、查询或标签引用按原tier序号一一迁移；数值、层级与资源内容保持原义。
 * 用途：避免显示名与实际注册键不一致；历史备注保留，旧存档不自动改写。
 */
public class ImaginaryCasingRecipes {

    private static final long IM1_EUT = Hk3Values.VA_LONG[Hk3Tiers.QSV];

    public static void register(Consumer<FinishedRecipe> provider) {
        List<String> research = Hk3ElectronicResearch.requirements(1);

        // 1. 虚数之树机壳：海渊机械机壳 + 魂钢板 + 天命核心 → 32。
        // 用途：虚数之树观测阵列等树系/观测系机器的主体结构。
        GTRecipeTypes.ASSEMBLER_RECIPES.recipeBuilder("hk3gtl_casing_imaginary_tree")
                .inputItems(new ItemStack(CasingBlocks.CASING_ABYSS_MECHANICAL.get(), 512))
                .inputItems(ChemicalHelper.get(TagPrefix.plate, SouliumMaterial.SOULIUM, 2048))
                .inputItems(new ItemStack(HonkaiMaterialItems.SCHICKSAL_IMAGINARY_CORE.get(), 512))
                .circuitMeta(8)
                .outputItems(new ItemStack(CasingBlocks.CASING_IMAGINARY_TREE.get(), 32))
                .duration(3200).EUt(IM1_EUT).save(provider);
        Hk3RecipeResearchGate.bindAll("assembler", "hk3gtl_casing_imaginary_tree", research);

        // 2. 虚数晶格机壳：海渊科研机壳 + 纳米陶瓷 + 逆熵核心 → 32。
        // 用途：虚数电路/研究/数据计算类机器的主体结构。
        GTRecipeTypes.ASSEMBLER_RECIPES.recipeBuilder("hk3gtl_casing_imaginary_lattice")
                .inputItems(new ItemStack(CasingBlocks.CASING_ABYSS_RESEARCH.get(), 512))
                .inputItems(new ItemStack(HonkaiMaterialItems.NANO_CERAMIC.get(), 2048))
                .inputItems(new ItemStack(HonkaiMaterialItems.ANTI_ENTROPY_IMAGINARY_CORE.get(), 512))
                .circuitMeta(8)
                .outputItems(new ItemStack(CasingBlocks.CASING_IMAGINARY_LATTICE.get(), 32))
                .duration(3200).EUt(IM1_EUT).save(provider);
        Hk3RecipeResearchGate.bindAll("assembler", "hk3gtl_casing_imaginary_lattice", research);

        // 3. 虚数核心机壳：海渊能源机壳 + 压缩崩坏核心 + 超导金属氢 → 32。
        // 用途：虚数阶段能源/反应/供给类机器的主体结构。
        GTRecipeTypes.ASSEMBLER_RECIPES.recipeBuilder("hk3gtl_casing_imaginary_core")
                .inputItems(new ItemStack(CasingBlocks.CASING_ABYSS_ENERGY.get(), 512))
                .inputItems(new ItemStack(HonkaiMaterialItems.COMPRESSED_HONKAI_CORE.get(), 2048))
                .inputItems(new ItemStack(HonkaiMaterialItems.SUPERCONDUCTIVE_METAL_HYDROGEN.get(), 512))
                .circuitMeta(8)
                .outputItems(new ItemStack(CasingBlocks.CASING_IMAGINARY_CORE.get(), 32))
                .duration(3200).EUt(IM1_EUT).save(provider);
        Hk3RecipeResearchGate.bindAll("assembler", "hk3gtl_casing_imaginary_core", research);

        // 4. 虚数锚定机壳：强化魂钢机壳 + 相位转移镜 + 逆熵核心 → 32。
        // 用途：锚定/空间固定/相位稳定类机器的主体结构。
        GTRecipeTypes.ASSEMBLER_RECIPES.recipeBuilder("hk3gtl_casing_imaginary_anchor")
                .inputItems(new ItemStack(CasingBlocks.CASING_REINFORCED_SOULIUM.get(), 512))
                .inputItems(new ItemStack(HonkaiMaterialItems.PHASE_TRANSFER_MIRROR.get(), 1024))
                .inputItems(new ItemStack(HonkaiMaterialItems.ANTI_ENTROPY_IMAGINARY_CORE.get(), 512))
                .circuitMeta(8)
                .outputItems(new ItemStack(CasingBlocks.CASING_IMAGINARY_ANCHOR.get(), 32))
                .duration(3200).EUt(IM1_EUT).save(provider);
        Hk3RecipeResearchGate.bindAll("assembler", "hk3gtl_casing_imaginary_anchor", research);

        // 5. 虚数编织机壳：强化魂钢机壳 + 爱因斯坦环形磁铁 + 天命核心 → 32。
        // 用途：物质编织、魂钢超结构等加工类机器的主体结构。
        GTRecipeTypes.ASSEMBLER_RECIPES.recipeBuilder("hk3gtl_casing_imaginary_weave")
                .inputItems(new ItemStack(CasingBlocks.CASING_REINFORCED_SOULIUM.get(), 512))
                .inputItems(new ItemStack(HonkaiMaterialItems.EINSTEIN_RINGMAGNET.get(), 1024))
                .inputItems(new ItemStack(HonkaiMaterialItems.SCHICKSAL_IMAGINARY_CORE.get(), 512))
                .circuitMeta(8)
                .outputItems(new ItemStack(CasingBlocks.CASING_IMAGINARY_WEAVE.get(), 32))
                .duration(3200).EUt(IM1_EUT).save(provider);
        Hk3RecipeResearchGate.bindAll("assembler", "hk3gtl_casing_imaginary_weave", research);
    }
}

// 【变更记录 · 修订163】2026-10-17 15:05:46：移除本类生产配方对旧 R-* 研究的活动绑定，按现行电路平台或功能前级明确绑定 RN 课题；多前置全部保留。输入输出、数量、耗电与时长不变；本轮接线不代表全部工业工艺或百课题已完成实机验收。
