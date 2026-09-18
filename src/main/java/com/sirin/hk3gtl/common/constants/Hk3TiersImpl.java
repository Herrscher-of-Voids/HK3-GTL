package com.sirin.hk3gtl.common.constants;



import com.gregtechceu.gtceu.api.GTValues;

/**
 * 扩展电压等级常量与查询方法的实现类。
 *
 * <p>职责：定义 hk3gtl 新增的 16 个电压等级（Tier 15~30），提供索引常量、
 * 电压 key、显示名数组和基础查询方法。</p>
 *
 * <h3>等级划分（每阶段 4 级）</h3>
 * <table>
 *   <tr><th>阶段</th><th>索引范围</th><th>中文名</th></tr>
 *   <tr><td>海渊 (Abyss)</td><td>15~18</td><td>海渊 I~IV</td></tr>
 *   <tr><td>虚数 (Imaginary)</td><td>19~22</td><td>虚数 I~IV</td></tr>
 *   <tr><td>量子 (Quantum)</td><td>23~26</td><td>量子 I~IV</td></tr>
 *   <tr><td>终焉 (Finality)</td><td>27~30</td><td>终焉 I~IV</td></tr>
 * </table>
 *
 * <h3>修改指南 (Where to modify data)</h3>
 * <ul>
 *   <li>新增等级：追加索引常量 → 更新 ALL_NEW_TIERS → 同步更新 VOLTAGE_KEYS / VOLTAGE_NAMES_ZH / VOLTAGE_NAMES_EN</li>
 *   <li>修改等级范围：同步更新 {@link Hk3ValuesImpl} 中所有 31 元素数组</li>
 *   <li>修改电压值：由于直接引用 {@link GTValues#VEX}，如需修改具体EU数值，需通过 Mixin 修改 GT 原版数组，或重写 {@link #voltage(int)} 方法</li>
 *   <li>GTValues.ALL_TIERS / TIER_COUNT 保持原版 0~14 / 15；扩展等级只通过本类常量和 Hk3Values 查询，不参与 GT 自动注册</li>
 * </ul>
 *
 * @see Hk3Tiers 公开入口类
 * @see Hk3ValuesImpl 完整的数值数组和安全 getter
 */
public class Hk3TiersImpl {

    // ═══════════════════════════════════════
    //  Tier 索引常量
    //  每个常量对应 GTValues 数组中的下标位置
    // ═══════════════════════════════════════

    /** 海渊 I，tier 索引 15，电压约 8,053,063,680 EU/t */
    public static final int ABYSS_1     = 15;
    /** 海渊 II，tier 索引 16，电压约 32,212,254,720 EU/t */
    public static final int ABYSS_2     = 16;
    /** 海渊 III，tier 索引 17，电压约 128,849,018,880 EU/t */
    public static final int ABYSS_3     = 17;
    /** 海渊 IV，tier 索引 18，电压约 515,396,075,520 EU/t */
    public static final int ABYSS_4     = 18;
    /** 虚数 I，tier 索引 19，电压约 2,061,584,302,080 EU/t */
    public static final int IMAGINARY_1 = 19;
    /** 虚数 II，tier 索引 20，电压约 8,246,337,208,320 EU/t */
    public static final int IMAGINARY_2 = 20;
    /** 虚数 III，tier 索引 21，电压约 32,985,348,833,280 EU/t */
    public static final int IMAGINARY_3 = 21;
    /** 虚数 IV，tier 索引 22，电压约 131,941,395,333,120 EU/t */
    public static final int IMAGINARY_4 = 22;
    /** 量子 I，tier 索引 23，电压约 527,765,581,332,480 EU/t */
    public static final int QUANTUM_1   = 23;
    /** 量子 II，tier 索引 24，电压约 2,111,062,325,329,920 EU/t */
    public static final int QUANTUM_2   = 24;
    /** 量子 III，tier 索引 25，电压约 8,444,249,301,319,680 EU/t */
    public static final int QUANTUM_3   = 25;
    /** 量子 IV，tier 索引 26，电压约 33,776,997,205,278,720 EU/t */
    public static final int QUANTUM_4   = 26;
    /** 终焉 I，tier 索引 27，电压约 135,107,988,821,114,880 EU/t */
    public static final int FINALITY_1  = 27;
    /** 终焉 II，tier 索引 28，电压约 540,431,955,284,459,520 EU/t */
    public static final int FINALITY_2  = 28;
    /** 终焉 III，tier 索引 29，电压约 2,161,727,821,137,838,080 EU/t */
    public static final int FINALITY_3  = 29;
    /** 终焉 IV，tier 索引 30，电压为 Long.MAX_VALUE（溢出上限） */
    public static final int FINALITY_4  = 30;

    /**
     * 全部 16 级新 tier 索引数组，按阶段顺序排列。
     * <p>用于批量遍历扩展等级，如注册总线、生成配方等。</p>
     */
    public static final int[] ALL_NEW_TIERS = {
            ABYSS_1, ABYSS_2, ABYSS_3, ABYSS_4,
            IMAGINARY_1, IMAGINARY_2, IMAGINARY_3, IMAGINARY_4,
            QUANTUM_1, QUANTUM_2, QUANTUM_3, QUANTUM_4,
            FINALITY_1, FINALITY_2, FINALITY_3, FINALITY_4
    };

    /**
     * 电压 key 数组，索引 0 对应 tier 15。
     * <p>用于物品 ID、标签路径、KubeJS 脚本中的字符串标识。
     * 例：tier 15 → "abyss_1"，tier 23 → "quantum_1"</p>
     * <p>访问方式：{@code VOLTAGE_KEYS[tier - ABYSS_1]}</p>
     */
    public static final String[] VOLTAGE_KEYS = {
            "abyss_1", "abyss_2", "abyss_3", "abyss_4",
            "imaginary_1", "imaginary_2", "imaginary_3", "imaginary_4",
            "quantum_1", "quantum_2", "quantum_3", "quantum_4",
            "finality_1", "finality_2", "finality_3", "finality_4"
    };

    /**
     * 中文显示名数组，索引 0 对应 tier 15。
     * <p>用于 GUI、聊天消息等中文环境下的等级显示。</p>
     */
    public static final String[] VOLTAGE_NAMES_ZH = {
            "海渊 I", "海渊 II", "海渊 III", "海渊 IV",
            "虚数 I", "虚数 II", "虚数 III", "虚数 IV",
            "量子 I", "量子 II", "量子 III", "量子 IV",
            "终焉 I", "终焉 II", "终焉 III", "终焉 IV"
    };

    /**
     * 英文显示名数组，索引 0 对应 tier 15。
     * <p>用于 en_us 语言环境和日志输出。</p>
     */
    public static final String[] VOLTAGE_NAMES_EN = {
            "Abyss I", "Abyss II", "Abyss III", "Abyss IV",
            "Imaginary I", "Imaginary II", "Imaginary III", "Imaginary IV",
            "Quantum I", "Quantum II", "Quantum III", "Quantum IV",
            "Finality I", "Finality II", "Finality III", "Finality IV"
    };

    /**
     * 获取指定 tier 的基础电压值，直接引用 GTValues.VEX。
     *
     * <p>⚠ 注意：tier 15+ 返回值超出 int 范围，必须用 long 接收。</p>
     *
     * @param tier tier 索引 (15~30)
     * @return 电压值（单位：EU/t）
     */
    public static long voltage(int tier) {
        return GTValues.VEX[tier];
    }

    /**
     * 获取指定 tier 的配方用电压（考虑线损）。
     *
     * <p>对于 MAX (tier 14) 及以下使用 GTValues.VA（含线损补偿），
     * MAX 以上暂时使用 VEX（无线损概念）。</p>
     *
     * <p>⚠ 注意：tier 15+ 返回值超出 int 范围，禁止用 int 接收。</p>
     *
     * @param tier tier 索引
     * @return 配方用电压值（单位：EU/t）
     */
    public static long voltageAdjusted(int tier) {
        if (tier <= GTValues.MAX) {
            return GTValues.VA[tier];
        }
        return GTValues.VEX[tier];
    }

    /**
     * 根据 tier 索引获取电压 key 字符串。
     *
     * @param tier tier 索引 (15~30)
     * @return 电压 key，如 "abyss_1"
     * @throws IllegalArgumentException tier 超出 [15, 30] 范围
     */
    public static String voltageKey(int tier) {
        if (tier < ABYSS_1 || tier > FINALITY_4) {
            throw new IllegalArgumentException("Invalid HK3 tier: " + tier);
        }
        return VOLTAGE_KEYS[tier - ABYSS_1];
    }

    /**
     * 根据 tier 索引获取中文显示名。
     *
     * @param tier tier 索引 (15~30)
     * @return 中文显示名，如 "海渊 I"
     * @throws IllegalArgumentException tier 超出 [15, 30] 范围
     */
    public static String voltageNameZh(int tier) {
        if (tier < ABYSS_1 || tier > FINALITY_4) {
            throw new IllegalArgumentException("Invalid HK3 tier: " + tier);
        }
        return VOLTAGE_NAMES_ZH[tier - ABYSS_1];
    }
}
