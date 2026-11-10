package com.sirin.hk3gtl.common.event;


/**
 * 【文件职责】
 * - 处理 Hk3EventManager 相关事件分发与触发。
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

import javax.annotation.Nullable;

/**
 * 事件管理器的公开门面类。
 *
 * <h3>职责</h3>
 * 监听玩家行为并触发一次性里程碑（E-MS-xxx）和多方块首次建成（E-FB-xxx）事件。
 * 事件状态存储在玩家 {@code persistentData} 中，key 格式为 {@code "hk3gtl_evt_" + eventId}。
 *
 * <h3>核心入口</h3>
 * <ul>
 *   <li>{@code onPlayerTick} — 每秒扫描玩家背包，检查里程碑触发条件</li>
 *   <li>{@code onMultiblockFormed} — 由 {@code Hk3WorkableMultiblockMachine} 在成型后调用</li>
 *   <li>{@code hasTriggered} — 外部查询某事件是否已触发</li>
 * </ul>
 *
 * <h3>与研究系统的桥接</h3>
 * 事件触发后通过 {@code Hk3ResearchManager.onEventTriggered} 自动通知研究系统。
 *
 * @see Hk3EventManagerImpl
 * @see Hk3EventService 脚本/彩蛋等任意入口触发一次性事件
 * @see com.sirin.hk3gtl.common.research.Hk3ResearchManager
 */
public class Hk3EventManager extends Hk3EventManagerImpl {

    /**
     * 与服务端事件存储、研究/叙事桥接、客户端同步对齐的通用触发入口。
     */
    public static boolean tryTriggerFirstTime(ServerPlayer player, String eventId, @Nullable String eventChatLangKey) {
        return Hk3EventService.tryTriggerFirstTime(player, eventId, eventChatLangKey);
    }
}
