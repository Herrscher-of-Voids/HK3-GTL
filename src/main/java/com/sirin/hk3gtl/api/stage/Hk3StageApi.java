package com.sirin.hk3gtl.api.stage;



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
     * @return 电压 key，如 "abyss_1"、"quantum_3"
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
