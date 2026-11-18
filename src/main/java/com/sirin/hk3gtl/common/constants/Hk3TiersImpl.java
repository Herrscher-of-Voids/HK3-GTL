package com.sirin.hk3gtl.common.constants;

 






















import com.gregtechceu.gtceu.api.GTValues;

/** 新增tier为15~30；不扩展GT自动注册使用的ALL_TIERS。 */
 






public class Hk3TiersImpl {

    // ═══════════════════════════════════════
    //  Tier 索引常量
    //  每个常量对应 GTValues 数组中的下标位置
    // ═══════════════════════════════════════

    /** HBV，tier 索引 15，电压约 8,053,063,680 EU/t */
    public static final int HBV     = 15;
    /** HCV，tier 索引 16，电压约 32,212,254,720 EU/t */
    public static final int HCV     = 16;
    /** HRV，tier 索引 17，电压约 128,849,018,880 EU/t */
    public static final int HRV     = 17;
    /** HDV，tier 索引 18，电压约 515,396,075,520 EU/t */
    public static final int HDV     = 18;
    /** QSV，tier 索引 19，电压约 2,061,584,302,080 EU/t */
    public static final int QSV = 19;
    /** QCV，tier 索引 20，电压约 8,246,337,208,320 EU/t */
    public static final int QCV = 20;
    /** QEV，tier 索引 21，电压约 32,985,348,833,280 EU/t */
    public static final int QEV = 21;
    /** QAV，tier 索引 22，电压约 131,941,395,333,120 EU/t */
    public static final int QAV = 22;
    /** IMV，tier 索引 23，电压约 527,765,581,332,480 EU/t */
    public static final int IMV   = 23;
    /** ICV，tier 索引 24，电压约 2,111,062,325,329,920 EU/t */
    public static final int ICV   = 24;
    /** IRV，tier 索引 25，电压约 8,444,249,301,319,680 EU/t */
    public static final int IRV   = 25;
    /** IWV，tier 索引 26，电压约 33,776,997,205,278,720 EU/t */
    public static final int IWV   = 26;
    /** WFV，tier 索引 27，电压约 135,107,988,821,114,880 EU/t */
    public static final int WFV  = 27;
    /** WSV，tier 索引 28，电压约 540,431,955,284,459,520 EU/t */
    public static final int WSV  = 28;
    /** CIV，tier 索引 29，电压约 2,161,727,821,137,838,080 EU/t */
    public static final int CIV  = 29;
    /** CEV，tier 索引 30，电压为 Long.MAX_VALUE（溢出上限） */
    public static final int CEV  = 30;

    public static final int[] ALL_NEW_TIERS = {
            HBV, HCV, HRV, HDV,
            QSV, QCV, QEV, QAV,
            IMV, ICV, IRV, IWV,
            WFV, WSV, CIV, CEV
    };

    /**
     * 电压 key 数组，索引 0 对应 tier 15。
     * <p>用于物品 ID、标签路径、KubeJS 脚本中的字符串标识。
     * 例：tier 15 → "hbv"，tier 23 → "imv"</p>
     * <p>访问方式：{@code VOLTAGE_KEYS[tier - HBV]}</p>
     */
    public static final String[] VOLTAGE_KEYS = {
            "hbv", "hcv", "hrv", "hdv",
            "qsv", "qcv", "qev", "qav",
            "imv", "icv", "irv", "iwv",
            "wfv", "wsv", "civ", "cev"
    };

    /** 内测5已确认的显示标识；与注册短键按tier一一对应，电压数值不变。 */
    public static final String[] VOLTAGE_SYMBOLS = {
            "HBV", "HCV", "HRV", "HDV",
            "QSV", "QCV", "QEV", "QAV",
            "IMV", "ICV", "IRV", "IWV",
            "WFV", "WSV", "CIV", "CEV"
    };

    public static final String[] VOLTAGE_NAMES_ZH = {
            "崩能压", "约束压", "谐振压", "致密压",
            "叠态压", "相干压", "纠缠压", "锚定压",
            "虚数压", "耦合压", "重构压", "织界压",
            "构界压", "稳界压", "统合压", "恒续压"
    };

    public static final String[] VOLTAGE_NAMES_EN = {
            "Honkai-Based Voltage", "Honkai-Containment Voltage", "Honkai-Resonance Voltage", "Honkai-Densification Voltage",
            "Quantum-Superposition Voltage", "Quantum-Coherence Voltage", "Quantum-Entanglement Voltage", "Quantum-Anchoring Voltage",
            "Imaginary-Medium Voltage", "Imaginary-Coupling Voltage", "Imaginary-Reconstruction Voltage", "Imaginary-Weaving Voltage",
            "World-Fabrication Voltage", "World-Stabilization Voltage", "Civilization-Integration Voltage", "Civilization-Endurance Voltage"
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
     * @return 电压 key，如 "hbv"
     * @throws IllegalArgumentException tier 超出 [15, 30] 范围
     */
    public static String voltageKey(int tier) {
        if (tier < HBV || tier > CEV) {
            throw new IllegalArgumentException("Invalid HK3 tier: " + tier);
        }
        return VOLTAGE_KEYS[tier - HBV];
    }

    /**
     * 根据 tier 索引获取中文显示名。
     *
     * @param tier tier 索引 (15~30)
     * @return 中文显示名，如 "HBV"
     * @throws IllegalArgumentException tier 超出 [15, 30] 范围
     */
    public static String voltageNameZh(int tier) {
        if (tier < HBV || tier > CEV) {
            throw new IllegalArgumentException("Invalid HK3 tier: " + tier);
        }
        return VOLTAGE_NAMES_ZH[tier - HBV];
    }
}
