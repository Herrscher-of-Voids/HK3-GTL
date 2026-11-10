package com.sirin.hk3gtl.common.recipe.soulium;


/**
 * 【文件职责】
 * - 负责 SouliumRecipes 对应的配方注册与门槛绑定。
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
import com.sirin.hk3gtl.common.constants.Hk3Tiers;
import com.sirin.hk3gtl.common.constants.Hk3Values;
import com.sirin.hk3gtl.common.item.honkai.HonkaiMaterialItems;
import com.sirin.hk3gtl.common.material.Hk3Materials;
import com.sirin.hk3gtl.common.material.SouliumMaterial;
import net.minecraft.data.recipes.FinishedRecipe;
import net.minecraft.world.item.ItemStack;

import java.util.function.Consumer;

/**
 * 魂钢产业链配方 —— 海渊闭环的材料主线。
 *
 * <h3>职责</h3>
 * <ul>
 *   <li>启动线：魂钢冶铸中心只负责前驱体和少量低效魂钢锭，避免首台海渊设备死锁</li>
 *   <li>工业线：海渊深熔精炼联合体负责纳米活化 / 原质稳定，海渊精密装配工坊负责批量凝锭</li>
 *   <li>加工线：板材/框架/细线/箔材保留 GT 标准机路线，作为早期手工加工；后续由海渊精密装配工坊承接批量路线</li>
 * </ul>
 *
 * <h3>修改指南</h3>
 * <ul>
 *   <li>调整电压：修改 ABYSS_1_EUT</li>
 *   <li>冶铸启动配方使用 SOULIUM_SMELTING_RECIPES；批量链使用 ABYSS_VACUUM_SMELTING / ABYSS_PRECISION_ASSEMBLY</li>
 *   <li>加工配方使用 GT 标准机类型（BENDER/ASSEMBLER/WIREMILL），配方ID需加 "hk3gtl_" 前缀</li>
 *   <li>所有魂钢配方 EU/t 必须高于 MAX（Tier 14），避免 int 溢出</li>
 * </ul>
 */
/**
 * 【变更记录 #1】2026-09-30 02:17:47（第1次备注 · 内测5修订107）
 * 删除：本文件可执行代码中的旧电压键及常量引用，不保留旧键注册别名。
 * 新增：16档正式缩写作为唯一电压标识；逐文件映射见logs/voltage-keys-r107。
 * 修改：注册、配方、查询或标签引用按原tier序号一一迁移；数值、层级与资源内容保持原义。
 * 用途：避免显示名与实际注册键不一致；历史备注保留，旧存档不自动改写。
 */
/**
 * 【历史退役记录 · 修订160】2026-10-17 13:52:26：三类旧执行器已退役，
 * 总入口停止调用；现行L3使用I09–I16八步。旧私有实现于修订162完整移出活动源码。
 */
/**
 * 【变更记录 #2】2026-10-17 14:38:40（第2次备注 · 内测5修订162）
 * 删除：已停用的retiredSouliumSmeltingRecipes及其六条旧生产配方、旧研究绑定和专用常量。
 * 新增：无。修改：本类仅保留GT标准机中的板、框架、细线、箔材后处理。
 * 用途：退役结构不留死配方实现；现行魂钢生产仍归I09–I16，不改挂设备或补造启动配方。
 * 追溯：原文件保存在logs/retired-recipes-r162/before的同相对路径。
 */
public class SouliumRecipes {

    /** 海渊I阶段基准电压（EU/t） */
    private static final long HBV_EUT = Hk3Values.VA_LONG[Hk3Tiers.HBV];

    /** 注册魂钢加工配方（使用 GT 标准机：弯曲机/组装机/线材厂） */
    public static void addSouliumProcessingRecipes(Consumer<FinishedRecipe> provider) {
        GTRecipeTypes.BENDER_RECIPES.recipeBuilder("hk3gtl_soulium_plate")
                .inputItems(ChemicalHelper.get(TagPrefix.ingot, SouliumMaterial.SOULIUM, 128))
                .circuitMeta(1)
                .outputItems(ChemicalHelper.get(TagPrefix.plate, SouliumMaterial.SOULIUM, 64))
                .duration(240)
                .EUt(HBV_EUT)
                .save(provider);

        GTRecipeTypes.ASSEMBLER_RECIPES.recipeBuilder("hk3gtl_soulium_frame")
                .inputItems(ChemicalHelper.get(TagPrefix.plate, SouliumMaterial.SOULIUM, 1024))
                .inputItems(ChemicalHelper.get(TagPrefix.ingot, SouliumMaterial.SOULIUM, 512))
                .inputItems(new ItemStack(HonkaiMaterialItems.HONKAI_ENERGY_CRYSTAL.get(), 512))
                .outputItems(ChemicalHelper.get(TagPrefix.frameGt, SouliumMaterial.SOULIUM, 32))
                .duration(600)
                .EUt(HBV_EUT)
                .save(provider);

        GTRecipeTypes.WIREMILL_RECIPES.recipeBuilder("hk3gtl_soulium_fine_wire")
                .inputItems(ChemicalHelper.get(TagPrefix.ingot, SouliumMaterial.SOULIUM, 256))
                .inputFluids(Hk3Materials.LIQUID_HONKAI_ENERGY.getFluid(2304))
                .outputItems(ChemicalHelper.get(TagPrefix.wireFine, SouliumMaterial.SOULIUM, 512))
                .duration(400)
                .EUt(HBV_EUT)
                .save(provider);

        GTRecipeTypes.BENDER_RECIPES.recipeBuilder("hk3gtl_soulium_foil")
                .inputItems(ChemicalHelper.get(TagPrefix.plate, SouliumMaterial.SOULIUM, 256))
                .circuitMeta(10)
                .inputFluids(Hk3Materials.LIQUID_HONKAI_ENERGY.getFluid(1152))
                .outputItems(ChemicalHelper.get(TagPrefix.foil, SouliumMaterial.SOULIUM, 256))
                .duration(300)
                .EUt(HBV_EUT)
                .save(provider);
    }
}
