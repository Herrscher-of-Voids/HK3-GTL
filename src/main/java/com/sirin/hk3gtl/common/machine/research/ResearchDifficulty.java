package com.sirin.hk3gtl.common.machine.research;



import com.sirin.hk3gtl.common.constants.Hk3Constants;
import com.sirin.hk3gtl.common.research.Hk3ResearchNode;

/**
 * 研究矩阵难度曲线计算器（平衡档：{@code 2^(tier-15)} 指数）。
 *
 * <h3>难度系数</h3>
 * <p>以 tier 15（海渊 I 入口）为基准 1.0×，每升 1 级难度翻倍：</p>
 * <table>
 *   <tr><th>Tier</th><th>代表节点</th><th>难度系数</th><th>耗时</th><th>额外能耗</th></tr>
 *   <tr><td>15.0</td><td>R-AB-001/004</td><td>1.00×</td><td>20s</td><td>1 MEU/t</td></tr>
 *   <tr><td>16.0</td><td>R-AB-011</td><td>2.00×</td><td>40s</td><td>2 MEU/t</td></tr>
 *   <tr><td>17.0</td><td>R-AB-017</td><td>4.00×</td><td>80s</td><td>4 MEU/t</td></tr>
 *   <tr><td>18.0</td><td>R-AB-021</td><td>8.00×</td><td>160s</td><td>8 MEU/t</td></tr>
 *   <tr><td>18.5</td><td>R-AB-024 (认证)</td><td>11.31×</td><td>~226s</td><td>~11.3 MEU/t</td></tr>
 * </table>
 *
 * <h3>修改指南</h3>
 * <ul>
 *   <li>换指数基数：修改 {@link #difficultyFactor} 中的 {@code Math.pow(2, ...)}
 *       （例如改为 1.5 会让曲线更温和）</li>
 *   <li>换 tier 基准：改 {@link #TIER_BASELINE}（当前为 15 = 海渊 I 入口）</li>
 *   <li>改耗时上限：{@link #durationTicks} 末尾可叠加 {@code Math.min(MAX_TICKS, ...)}</li>
 *   <li>不同类型的节点想要不同曲线：在 {@link #difficultyFactor} 里根据 {@code node.type()} 分支</li>
 * </ul>
 *
 * <h3>为什么用 2^(tier-15)</h3>
 * 项目电压体系本身就是 tier 每升 1 级能耗 ×4（V[16]/V[15] = 4），玩家供电能力倍增。
 * 研究难度跟随一半倍率（×2），既能体现阶段递进感，又不至于让终局节点变成数小时挂机。
 */
public final class ResearchDifficulty {

    /** 难度曲线的 tier 基准点（海渊 I 入口）。低于此 tier 的节点难度固定为 1.0× */
    private static final double TIER_BASELINE = 15.0;

    private ResearchDifficulty() {}

    /**
     * 计算该节点的难度系数 {@code 2^(tier-15)}；tier ≤ 15 时一律返回 1.0。
     * 自动完成型节点（事件触发即完成）返回 0.0，表示无需走研究矩阵流程。
     */
    public static double difficultyFactor(Hk3ResearchNode node) {
        if (node == null || node.isAutoComplete()) return 0.0;
        double delta = node.tier() - TIER_BASELINE;
        if (delta <= 0) return 1.0;
        return Math.pow(2.0, delta);
    }

    /**
     * 该节点需要的总 tick 数。
     * 公式：{@code BASE_DURATION × difficulty}；最小 1 tick 防止 tier 过低时立即完成。
     */
    public static int durationTicks(Hk3ResearchNode node) {
        double factor = difficultyFactor(node);
        int ticks = (int) Math.max(1.0, Hk3Constants.RESEARCH_MATRIX_BASE_DURATION_TICKS * factor);
        return ticks;
    }

    /**
     * 该节点研究过程中每 tick 的额外能耗（EU/t）。叠加在 IDLE 之上。
     * 公式：{@code BASE_EXTRA × difficulty}。
     */
    public static long extraEutPerTick(Hk3ResearchNode node) {
        double factor = difficultyFactor(node);
        if (factor <= 0) return 0L;
        return (long) Math.max(1.0, Hk3Constants.RESEARCH_MATRIX_BASE_EXTRA_EUT * factor);
    }

    /** 仅供 GUI 展示：难度系数字符串（保留 2 位小数） */
    public static String formatDifficulty(Hk3ResearchNode node) {
        return String.format("%.2f", difficultyFactor(node));
    }
}
