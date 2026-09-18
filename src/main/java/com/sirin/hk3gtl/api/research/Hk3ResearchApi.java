package com.sirin.hk3gtl.api.research;



import com.sirin.hk3gtl.common.research.Hk3ResearchManager;
import net.minecraft.server.level.ServerPlayer;

/**
 * 研究系统的公开 API 门面。
 *
 * <p>职责：为外部模组 / KubeJS 脚本提供只读的研究状态查询入口，
 * 内部委托给 {@link Hk3ResearchManager}。</p>
 *
 * <p>实现类：{@link Hk3ResearchManager}（common.research 包）</p>
 *
 * <h3>修改指南</h3>
 * <ul>
 *   <li>新增查询方法时在此类添加静态方法并委托给 Hk3ResearchManager</li>
 *   <li>不要在此类中放置状态变更或提交逻辑</li>
 * </ul>
 */
public final class Hk3ResearchApi {

    /** 工具类，禁止实例化 */
    private Hk3ResearchApi() {}

    /**
     * 查询玩家是否已完成指定研究节点。
     *
     * @param player     服务端玩家实例
     * @param researchId 研究节点 ID，格式如 "R-AB-001"
     * @return 已完成返回 true
     */
    public static boolean isResearchCompleted(ServerPlayer player, String researchId) {
        return Hk3ResearchManager.isCompleted(player, researchId);
    }
}
