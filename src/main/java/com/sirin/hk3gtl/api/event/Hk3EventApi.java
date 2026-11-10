package com.sirin.hk3gtl.api.event;


/**
 * 【文件职责】
 * - 处理 Hk3EventApi 相关事件分发与触发。
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
import com.sirin.hk3gtl.common.event.Hk3EventManager;
import net.minecraft.server.level.ServerPlayer;

/**
 * 事件系统的公开 API 门面。
 *
 * <p>职责：为外部模组 / KubeJS 脚本提供只读的事件状态查询入口，
 * 内部委托给 {@link Hk3EventManager}。</p>
 *
 * <p>实现类：{@link Hk3EventManager}（common.event 包）</p>
 *
 * <h3>修改指南</h3>
 * <ul>
 *   <li>新增查询方法时在此类添加静态方法并委托给 Hk3EventManager</li>
 *   <li>不要在此类中放置任何状态变更逻辑</li>
 * </ul>
 */
/**
 * 【变更记录 #2】2026-10-31 17:44:19（第2次备注 · 内测5修订189）
 * - 删除：无，保留历史备注及全部查询签名。
 * - 新增：现行查询契约说明。
 * - 修改：校正失效示例；事件查询只读取既有触发标记，不触发事件、不授予研究；写入及研究桥接由事件服务负责。
 * - 用途：供外部模组与脚本准确调用兼容查询，不扩充状态写入接口。
 */
public final class Hk3EventApi {

    /** 工具类，禁止实例化 */
    private Hk3EventApi() {}

    /**
     * 查询玩家是否已触发指定事件。
     *
     * @param player  服务端玩家实例
     * @param eventId 事件 ID，如 "E-MS-001"
     * @return 已触发返回 true
     */
    public static boolean hasTriggered(ServerPlayer player, String eventId) {
        return Hk3EventManager.hasTriggered(player, eventId);
    }
}
