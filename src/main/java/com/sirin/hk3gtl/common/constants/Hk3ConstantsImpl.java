package com.sirin.hk3gtl.common.constants;


/**
 * 【文件职责】
 * - 维护 Hk3ConstantsImpl 的核心功能实现。
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
/** 中文说明：该处说明已按当前代码行为整理。*/
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
