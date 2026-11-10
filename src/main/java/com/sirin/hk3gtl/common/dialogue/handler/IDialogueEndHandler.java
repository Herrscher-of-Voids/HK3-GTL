package com.sirin.hk3gtl.common.dialogue.handler;


/**
 * 【文件职责】
 * - 维护 IDialogueEndHandler 的核心功能实现。
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
 * 对话结束回调接口。
 * <p>
 * 不同对话在结束时执行不同的服务端逻辑（如毕业标记、传送等）。
 */
@FunctionalInterface
public interface IDialogueEndHandler {

    /**
     * 对话正常结束时调用（服务端主线程）。
     *
     * @param player     对话参与的玩家
     * @param dialogueId 对话ID
     * @param extraData  附加数据（由启动时传入）
     */
    void onDialogueEnd(ServerPlayer player, String dialogueId, int extraData);
}
