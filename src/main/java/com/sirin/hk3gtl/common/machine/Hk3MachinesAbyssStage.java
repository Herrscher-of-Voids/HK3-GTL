package com.sirin.hk3gtl.common.machine;

import com.sirin.hk3gtl.common.recipe.Hk3IndustrialRecipeTypes;


/** 中文维护备注：历史变更说明已整理；当前实现以代码为准。 */
import com.gregtechceu.gtceu.api.data.RotationState;
import com.gregtechceu.gtceu.api.GTValues;
import com.gregtechceu.gtceu.api.machine.MultiblockMachineDefinition;
import com.gregtechceu.gtceu.api.registry.registrate.GTRegistrate;
import com.mojang.logging.LogUtils;
import com.sirin.hk3gtl.Hk3Gtl;
import com.sirin.hk3gtl.common.block.CasingBlocks;
import com.sirin.hk3gtl.common.constants.Hk3Constants;
import com.sirin.hk3gtl.common.multiblock.pattern.Hk3I02SpectrumPattern;
import com.sirin.hk3gtl.common.recipe.Hk3RecipeTypes;
import net.minecraft.resources.ResourceLocation;
import org.slf4j.Logger;

/** 中文维护备注：历史变更说明已整理；当前实现以代码为准。 */
    /** 中文维护备注：历史变更说明已整理；当前实现以代码为准。 */
/** 中文维护备注：历史变更说明已整理；当前实现以代码为准。 */
/** 中文说明：该处说明已按当前代码行为整理。*/
/**
 * 【变更记录 #3】2026-09-25 02:19:54（内测5修订70）
 * 删除：旧建筑退出四机正式入口，历史文件已归档。
 * 新增：已确认逐格建筑及一致的模板与验收入口。
 * 修改：同步主控坐标、材料或测试夹具，不改配方和研究扣费。
 * 用途：使预览、正式结构及游戏放置相互对应；未将静态验证写作实机通过。
 */
/**
 * 【变更记录 #4】2026-09-27 03:06:43（第 4 次备注 · 内测5修订88）
 * 删除：无，保留历史说明和原有结构几何。
 * 新增：六台采用统一控制器侧面材质的机器，其成型仓室外观同步使用接口机械方块。
 * 修改：接入工业接口机械方块；保留必要能力的全局数量约束。
 * 用途：让多余接口可以封闭，不用填充方块冒充真实仓室能力。
 */
/**
 * 【变更记录 #5】2026-10-01 21:41:57（第5次备注 · 内测5修订151）
 * 删除：内测1—4旧结构相关入口。新增：无替代结构。
 * 修改：删除旧注册与字段；仅调用仍有内测5机器的初始化模块。
 * 用途：落实旧结构全部退役；内测5未审批设备仍待接入，不保留空注册兼容。
 */
/** 【变更记录 #6】2026-10-15 01:12:48（修订156）：I02 接入已批准 V7 精确状态和实际物品接口。 */
public class Hk3MachinesAbyssStage {

    /** 中文变更记录 #2：2026-09-24 18:56:36（内测5修订67）。I02 保留已确认 Pattern，控制器外观与 MAX 液态线统一。 */

    private static final Logger LOGGER = LogUtils.getLogger();
    private static final ResourceLocation OVERLAY = new ResourceLocation(Hk3Constants.MOD_ID, "block/overlay/default_set");

    /** I02 样本光谱分析阵列。 */
    public static MultiblockMachineDefinition I02_SPECTRUM_ANALYSIS_ARRAY;

    private static GTRegistrate reg() {
        return Hk3Gtl.REGISTRATE;
    }

    private static ResourceLocation tex(String name) {
        return new ResourceLocation(Hk3Constants.MOD_ID, "block/casings/" + name);
    }

    public static void init() {


        // 中文维护备注：历史说明已整理；当前实现以代码为准。


        // 中文维护备注：历史说明已整理；当前实现以代码为准。


        // 中文维护备注：历史说明已整理；当前实现以代码为准。


        // 中文维护备注：历史说明已整理；当前实现以代码为准。
        I02_SPECTRUM_ANALYSIS_ARRAY = reg()
                .multiblock("i02_spectrum_analysis_array", com.sirin.hk3gtl.common.machine.research.Hk3SpectrumAnalysisMachine::new)
                .tier(GTValues.MAX)
                .rotationState(RotationState.NON_Y_AXIS)
                .recipeType(Hk3IndustrialRecipeTypes.SPECTRUM_ANALYSIS)
                .appearanceBlock(() -> com.sirin.hk3gtl.common.multiblock.pattern.Hk3StructureBlocks.require("hk3gtl:industrial_port_casing"))
                .pattern(def -> com.sirin.hk3gtl.common.multiblock.pattern.Hk3IndustrialApprovedPatterns.create(def, "i02"))
                // 2026-09-25：光谱棱镜面板使用独立状态贴图；机器功能、接口和配方关联保持不变。
                .workableCasingRenderer(tex("industrial_controller_shell"),
                        new ResourceLocation("hk3gtl", "block/overlay/i02_v2"))
                .tooltips(
                        net.minecraft.network.chat.Component.translatable("hk3gtl.machine.i02_spectrum_analysis_array.tooltip.0"),
                        net.minecraft.network.chat.Component.translatable("hk3gtl.machine.i02_spectrum_analysis_array.tooltip.1"),
                        net.minecraft.network.chat.Component.translatable("hk3gtl.machine.i02_spectrum_analysis_array.tooltip.2"))
                .register();

        LOGGER.info("[HK3GTL] machine registration completed");
    }
}

// 【变更记录 · 修订161】2026-10-17 14:11:55：本轮仅将活动类名、资源与工业配方引用迁移为长期业务命名；历史备注保留，不代表旧逻辑已全部按现行设计重写。
