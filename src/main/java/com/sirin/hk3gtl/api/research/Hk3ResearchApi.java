package com.sirin.hk3gtl.api.research;


/**
 * 【文件职责】
 * - 维护 Hk3ResearchApi 研究流程与状态。
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
/**
 * 【变更记录 #2】2026-10-31 17:44:19（第2次备注 · 内测5修订189）
 * - 删除：无，保留历史备注及全部查询签名。
 * - 新增：现行查询契约说明。
 * - 修改：校正失效示例；研究查询保持只读委托；RN课题由管理器按玩家当前团队作用域核验研究账本，不以个人持久化标记替代研究权限。
 * - 用途：供外部模组与脚本准确调用兼容查询，不扩充状态写入接口。
 */
public final class Hk3ResearchApi {

    /** 工具类，禁止实例化 */
    private Hk3ResearchApi() {}

    /**
     * 查询玩家是否已完成指定研究节点。
     *
     * @param player     服务端玩家实例
     * @param researchId 研究节点 ID，现行课题如 "RN-HED"
     * @return 已完成返回 true
     */
    public static boolean isResearchCompleted(ServerPlayer player, String researchId) {
        return Hk3ResearchManager.isCompleted(player, researchId);
    }
}
