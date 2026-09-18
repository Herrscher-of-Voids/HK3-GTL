package com.sirin.hk3gtl.common.constants;



/**
 * 模组全局常量定义 —— 所有跨模块共享的配置值集中在此。
 *
 * <h3>职责</h3>
 * 提供模组ID、数值公式参数、毕业条件等不变常量。
 * Hk3Constants 继承本类，外部统一通过 Hk3Constants.XXX 引用。
 *
 * <h3>修改指南</h3>
 * <ul>
 *   <li>新增全局常量：直接在本类中添加 public static final 字段</li>
 *   <li>修改毕业条件：调整 GRADUATION_WONDER_COUNT / GRADUATION_RESEARCH_COUNT</li>
 *   <li>调整注视度机制参数：修改 GAZE_MAX / RESEARCH_SPEED_FLOOR / GAZE_DECAY_DIVISOR</li>
 *   <li>禁止硬编码数值——所有模块应引用此处常量</li>
 * </ul>
 */
public class Hk3ConstantsImpl {

    /** 模组ID，用于所有注册（方块/物品/网络通道/资源路径等） */
    public static final String MOD_ID = "hk3gtl";

    /** 模组显示名（用于日志、GUI 标题等） */
    public static final String MOD_NAME = "Honkai 3rd GTL";

    /** 崩坏能与EU换算比：1崩坏能 = 1000 EU。修改此值会影响所有能量转换逻辑 */
    public static final long HONKAI_TO_EU_RATIO = 1000L;

    /** 注视度最小值（下限钳制） */
    public static final int GAZE_MIN = 0;

    /** 注视度最大值（上限钳制）。调大则注视度系统范围扩大 */
    public static final int GAZE_MAX = 1000;

    /** 研究速度衰减下限：注视度达到最高时的最低速度倍率（0.3 = 30%速度） */
    public static final double RESEARCH_SPEED_FLOOR = 0.3;

    /** 注视度衰减公式分母。值越大衰减越慢。公式：speed = max(FLOOR, 1 - gaze/DIVISOR) */
    public static final double GAZE_DECAY_DIVISOR = 2000.0;

    /** 休伯利安号最大挂接模块数。修改此值影响休伯利安号多方块的模块上限 */
    public static final int HYPERION_MAX_MODULES = 10;

    /** 毕业必检奇观数量：玩家必须建造至少这么多奇观才能触发毕业 */
    public static final int GRADUATION_WONDER_COUNT = 10;

    /** 毕业必需研究节点数量：玩家必须完成至少这么多研究才能触发毕业 */
    public static final int GRADUATION_RESEARCH_COUNT = 43;

    // ═══════════════════════════════════════
    //  研究矩阵机器（Hk3ResearchMatrixMachine）运行期常量
    // ═══════════════════════════════════════

    /**
     * 研究矩阵待机每 tick 固定能耗（EU/t）。即使未在研究，结构成型后也持续消耗。
     * 修改影响：调低会削弱"耗电大户"定位，调高会逼死低 tier 发电；
     * 默认 21 亿 EU/t ≈ 略低于 MAX 电压单相，一个海渊 I 电压单相可完全供电。
     */
    public static final long RESEARCH_MATRIX_IDLE_EUT_PER_TICK = 2_100_000_000L;

    /**
     * 研究基础耗时（tick）。实际耗时 = 基础耗时 × 2^(tier-15)。
     * 修改影响：直接改变研究推进节奏。400 tick = 20 秒，作为 tier 15 基线。
     */
    public static final int RESEARCH_MATRIX_BASE_DURATION_TICKS = 400;

    /**
     * 研究过程中额外能耗基线（EU/t）。实际 = 基线 × 2^(tier-15)。
     * 修改影响：仅改变研究中能耗增量，不影响待机能耗。基线 1M/t 对 tier15 几乎无感，
     * 对 tier18.5 的终点节点达到 ~11M/t 增量，与 IDLE 叠加后仍在海渊电压范围内可供电。
     */
    public static final long RESEARCH_MATRIX_BASE_EXTRA_EUT = 1_000_000L;

    /**
     * 玩家调用 /submit 时找研究矩阵的半径（方块）。
     * 超出此距离不触发启动；玩家必须亲自站在矩阵附近。
     */
    public static final int RESEARCH_MATRIX_SEARCH_RADIUS = 64;
}
