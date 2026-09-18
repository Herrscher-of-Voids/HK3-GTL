package com.sirin.hk3gtl.api.event;



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
public final class Hk3EventApi {

    /** 工具类，禁止实例化 */
    private Hk3EventApi() {}

    /**
     * 查询玩家是否已触发指定事件。
     *
     * @param player  服务端玩家实例
     * @param eventId 事件 ID，格式如 "abyss_matrix_activated"
     * @return 已触发返回 true
     */
    public static boolean hasTriggered(ServerPlayer player, String eventId) {
        return Hk3EventManager.hasTriggered(player, eventId);
    }
}
