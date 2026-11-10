package com.sirin.hk3gtl.api.stage;


/**
 * 【文件职责】
 * - 维护 Hk3StageApi 的核心功能实现。
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
import com.sirin.hk3gtl.common.constants.Hk3Tiers;
import com.sirin.hk3gtl.common.constants.Hk3Values;

/**
 * 阶段/电压等级系统的公开 API 门面。
 *
 * <p>职责：为外部模组 / KubeJS 脚本提供扩展电压等级的只读查询入口，
 * 内部委托给 {@link Hk3Tiers} 和 {@link Hk3Values}。</p>
 *
 * <p>实现类：{@link Hk3Tiers}（常量与索引）、{@link Hk3Values}（数值与显示）</p>
 *
 * <h3>修改指南</h3>
 * <ul>
 *   <li>新增查询方法时在此类添加静态方法并委托给对应实现</li>
 *   <li>注意：tier 15~30 的电压值为 long 类型，禁止用 int 接收</li>
 * </ul>
 */
/**
 * 【变更记录 #2】2026-10-31 17:44:19（第2次备注 · 内测5修订189）
 * - 删除：无，保留历史备注及全部查询签名。
 * - 新增：现行查询契约说明。
 * - 修改：校正失效示例；阶段查询返回现行电压键及长整型配方电压；电压键越界抛出异常，配方电压越界返回零。
 * - 用途：供外部模组与脚本准确调用兼容查询，不扩充状态写入接口。
 */
public final class Hk3StageApi {

    /** 工具类，禁止实例化 */
    private Hk3StageApi() {}

    /**
     * 判断 tier 是否属于扩展等级（15~30）。
     *
     * @param tier tier 索引
     * @return 在 [15, 30] 范围内返回 true
     */
    public static boolean isExtendedTier(int tier) {
        return Hk3Values.isExtendedTier(tier);
    }

    /**
     * 获取 tier 对应的电压 key（用于物品 ID、标签等）。
     *
     * @param tier tier 索引 (15~30)
     * @return 电压 key，如 "hbv"、"imv"
     * @throws IllegalArgumentException tier 超出 [15, 30] 范围
     */
    public static String getVoltageKey(int tier) {
        return Hk3Tiers.voltageKey(tier);
    }

    /**
     * 获取 tier 对应的中文阶段名。
     *
     * @param tier tier 索引
     * @return 中文阶段名，如 "海渊"、"虚数"、"量子"、"终焉"
     */
    public static String getPhaseNameCn(int tier) {
        return Hk3Values.getPhaseNameCN(tier);
    }

    /**
     * 获取 tier 对应的配方用电压（long 类型，避免 int 溢出）。
     *
     * @param tier tier 索引 (0~30)
     * @return 配方用电压值（EU/t），tier 15+ 超出 int 范围
     */
    public static long getRecipeVoltage(int tier) {
        return Hk3Values.getVA(tier);
    }
}
