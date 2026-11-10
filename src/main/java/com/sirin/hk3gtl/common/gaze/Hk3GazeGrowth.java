package com.sirin.hk3gtl.common.gaze;


/**
 * 【文件职责】
 * - 维护 Hk3GazeGrowth 的核心功能实现。
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
import net.minecraft.server.level.ServerPlayer;

/**
 * 注视增长修正器：统一处理增长侧的抑制规则，避免在事件/研究代码里重复乘法逻辑。
 */
/**
 * 【变更记录 #1】2026-09-30 15:49:23（第1次编号备注 · 内测5修订109）
 * 删除：过期的计算或无运行依据的分支；保留历史备注。
 * 新增／修改：取消仅凭净化控制器旁置的增长减免；保留缓冲增长减半，不把稳定锚s当作增长减免。
 * 用途：统一注视与研究联动，服务端判定；不新增结构或贴图。
 */
public final class Hk3GazeGrowth {

    private Hk3GazeGrowth() {}

    /**
     * 对注视变化量做统一修正：
     * - 负值（降低注视）原样返回
     * - 不再把旁置净化控制器当作抑制设施；研究锚只影响压力公式
     * - 缓冲单元激活期间再降低 50%
     */
    public static int adjustGrowth(ServerPlayer player, int amount, String reason) {
        return Hk3GazeRules.growth(amount, Hk3GazeManager.isBufferActive(player));
    }
}
