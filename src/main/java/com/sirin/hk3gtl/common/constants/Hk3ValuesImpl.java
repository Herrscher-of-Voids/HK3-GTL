package com.sirin.hk3gtl.common.constants;


/**
 * 【文件职责】
 * - 维护 Hk3ValuesImpl 的核心功能实现。
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
import com.gregtechceu.gtceu.api.GTValues;

/** 中文说明：该处说明已按当前代码行为整理。*/
/**
 * 【变更记录 #2】2026-09-25 03:57:37（第 2 次备注 · 内测5修订71）
 * 删除：单一电路形态或旧电压显示限制。新增：统一系列及电压映射。
 * 修改：安全显示查询统一采用16级标识，避免机器提示残留海渊序号。
 * 用途：保持同级电路可替换、资源与游戏行为一致。
 */
/**
 * 【变更记录 #3】2026-09-30 02:17:47（第3次备注 · 内测5修订107）
 * 删除：本文件可执行代码中的旧电压键及常量引用，不保留旧键注册别名。
 * 新增：16档正式缩写作为唯一电压标识；逐文件映射见logs/voltage-keys-r107。
 * 修改：注册、配方、查询或标签引用按原tier序号一一迁移；数值、层级与资源内容保持原义。
 * 用途：避免显示名与实际注册键不一致；历史备注保留，旧存档不自动改写。
 */
/**
 * 【变更记录 #4】2026-09-30 03:22:21（内测5修订108）
 * 删除：旧配色引用。新增：批准的16档统一RGB色卡。
 * 修改：RGB及字符串兼容回退接入统一色卡。
 * 用途：配色统一；电压数值、注册和配方门槛不变。
 */
public class Hk3ValuesImpl {

    // ═══════════════════════════════════════
    // 中文备注：该处说明已按当前代码行为整理。
    // ═══════════════════════════════════════

    // ── 颜色值 (RGB) ──
    // 含义：每个 tier 的 UI 主色，JEI/Tooltip/外观方块染色会读取
    // 修改影响：调整后所有 tier 相关 UI 显示颜色都会变，建议成套替换以保证配色统一
    private static final int[] FULL_VC = {
            // 原版 0~14
            0xC80000, 0xDCDCDC, 0xFF6400, 0xFFFF1E, 0x808080,
            0xF0F0F5, 0xE99797, 0x7EC3C4, 0x7EB07E, 0xBF74C0,
            0x0B5CFE, 0x914E91, 0x488748, 0x8C0000, 0x2828F5,
            // 批准的HBV至CEV色卡
            Hk3VoltagePalette.main(15), Hk3VoltagePalette.main(16), Hk3VoltagePalette.main(17), Hk3VoltagePalette.main(18), Hk3VoltagePalette.main(19), Hk3VoltagePalette.main(20), Hk3VoltagePalette.main(21), Hk3VoltagePalette.main(22), Hk3VoltagePalette.main(23), Hk3VoltagePalette.main(24), Hk3VoltagePalette.main(25), Hk3VoltagePalette.main(26), Hk3VoltagePalette.main(27), Hk3VoltagePalette.main(28), Hk3VoltagePalette.main(29), Hk3VoltagePalette.main(30)
    };

    // ── 颜色格式字符串（§ 开头的 Minecraft 聊天颜色码） ──
    // 含义：文本型 tier 标签前缀，用于在聊天/Tooltip 中给电压名染色
    // 修改影响：仅影响文本显示；颜色码对照可见 Minecraft 官方 formatting code 文档
    private static final String[] FULL_VCF = {
            // 原版 0~14
            "\u00a78", "\u00a77", "\u00a7b", "\u00a76", "\u00a75",
            "\u00a79", "\u00a7d", "\u00a7c", "\u00a73", "\u00a74",
            "\u00a7a", "\u00a72", "\u00a7e", "\u00a79\u00a7l", "\u00a7c\u00a7l",
            // 批准的HBV至CEV色卡
            Hk3VoltagePalette.legacy(15), Hk3VoltagePalette.legacy(16), Hk3VoltagePalette.legacy(17), Hk3VoltagePalette.legacy(18), Hk3VoltagePalette.legacy(19), Hk3VoltagePalette.legacy(20), Hk3VoltagePalette.legacy(21), Hk3VoltagePalette.legacy(22), Hk3VoltagePalette.legacy(23), Hk3VoltagePalette.legacy(24), Hk3VoltagePalette.legacy(25), Hk3VoltagePalette.legacy(26), Hk3VoltagePalette.legacy(27), Hk3VoltagePalette.legacy(28), Hk3VoltagePalette.legacy(29), Hk3VoltagePalette.legacy(30)
    };

    // ── 人类可读等级名 ──
    // 含义：GUI/物品 tooltip 上展示的 tier 长描述（含颜色码前缀）
    // 修改影响：改动会改变玩家可见的电压等级名称；原版部分（0~14）沿用 GT 官方称谓，不建议乱动
    private static final String[] FULL_VLVH = {
            // 原版 0~14
            "Primitive", "Basic",
            "\u00a7bAdvanced", "\u00a76Advanced", "\u00a75Advanced",
            "\u00a79Elite", "\u00a7dElite", "\u00a7cElite",
            "\u00a73Ultimate", "\u00a74Epic", "\u00a7aEpic",
            "\u00a72Epic", "\u00a7eEpic",
            "\u00a79\u00a7lLegendary", "\u00a7c\u00a7lMAX",
            // 海渊 15~18
            "\u00a71\u00a7lAbyss", "\u00a71\u00a7lAbyss",
            "\u00a71\u00a7lAbyss", "\u00a71\u00a7lAbyss",
            // 虚数 19~22
            "\u00a73\u00a7lImaginary", "\u00a73\u00a7lImaginary",
            "\u00a73\u00a7lImaginary", "\u00a73\u00a7lImaginary",
            // 量子 23~26
            "\u00a76\u00a7lQuantum", "\u00a76\u00a7lQuantum",
            "\u00a76\u00a7lQuantum", "\u00a76\u00a7lQuantum",
            // 终焉 27~30
            "\u00a74\u00a7lFinality", "\u00a74\u00a7lFinality",
            "\u00a74\u00a7lFinality", "\u00a74\u00a7lFinality"
    };

    // ── 等级后缀 ──
    // 含义：附加在等级名后的数字/序号后缀（如 " II§r"），与 FULL_VLVH 组合使用
    // 修改影响：仅文本层；\u00a7r 表示重置格式，必须保留以避免污染后续文本样式
    private static final String[] FULL_VLVT = {
            // 原版 0~14
            "\u00a7r", "\u00a7r", "\u00a7r", "II\u00a7r", "III\u00a7r",
            "\u00a7r", "II\u00a7r", "III\u00a7r",
            "\u00a7r", "\u00a7r", "II\u00a7r", "III\u00a7r", "IV\u00a7r",
            "\u00a7r", "\u00a7r",
            // 海渊 15~18
            "I\u00a7r", "II\u00a7r", "III\u00a7r", "IV\u00a7r",
            // 虚数 19~22
            "I\u00a7r", "II\u00a7r", "III\u00a7r", "IV\u00a7r",
            // 量子 23~26
            "I\u00a7r", "II\u00a7r", "III\u00a7r", "IV\u00a7r",
            // 终焉 27~30
            "I\u00a7r", "II\u00a7r", "III\u00a7r", "IV\u00a7r"
    };

    // ── 罗马数字 ──
    // 含义：tier 对应的罗马数字（索引 0 为空，便于从 1 起算）
    // 修改影响：仅用于 Tooltip/机器命名展示；若扩展 tier 上限需追加更多罗马数字
    private static final String[] FULL_LVT = {
            "", "I", "II", "III", "IV", "V", "VI", "VII",
            "VIII", "IX", "X", "XI", "XII", "XIII", "XIV",
            "XV", "XVI", "XVII", "XVIII",
            "XIX", "XX", "XXI", "XXII",
            "XXIII", "XXIV", "XXV", "XXVI",
            "XXVII", "XXVIII", "XXIX", "XXX"
    };

    // ── long 版 VA（解决 int 溢出） ──
    // 含义：每个 tier 的"配方电压"（通常为 V[tier] 的 3/4~相关倍数），决定配方计算时的耗电/加速
    // 为什么需要 long：tier 15 之后数值会超过 int 上限（~21 亿），必须用 long 存储
    // 最后一项取 Long.MAX_VALUE 作为封顶，防止超级终焉档位下溢出
    // 修改影响：直接影响高 tier 机器的配方电压计算与平衡，改动需全局回归测试
    public static final long[] VA_LONG = {
            7L, 30L, 120L, 480L, 1920L, 7680L, 30720L, 122880L, 491520L,
            1966080L, 7864320L, 31457280L, 125829120L, 503316480L, 2013265920L,
            8053063680L,                    // 海渊 I  (15)
            32212254720L,                   // 海渊 II (16)
            128849018880L,                  // 海渊 III(17)
            515396075520L,                  // 海渊 IV (18)
            2061584302080L,                 // 虚数 I  (19)
            8246337208320L,                 // 虚数 II (20)
            32985348833280L,               // 虚数 III(21)
            131941395333120L,              // 虚数 IV (22)
            527765581332480L,              // 量子 I  (23)
            2111062325329920L,             // 量子 II (24)
            8444249301319680L,             // 量子 III(25)
            33776997205278720L,            // 量子 IV (26)
            135107988821114880L,           // 终焉 I  (27)
            540431955284459520L,           // 终焉 II (28)
            2161727821137838080L,          // 终焉 III(29)
            Long.MAX_VALUE                  // 终焉 IV (30)
    };

    // ═══════════════════════════════════════
    //  安全 Getter 方法
    // 中文备注：该处说明已按当前代码行为整理。
    // ═══════════════════════════════════════

    /**
     * 安全获取指定 tier 的 UI 主色（RGB）。
     * 修改要点：越界返回 0xFFFFFF 白色兜底；扩展 tier 上限需同步调整上界判断
     */
    public static int getVC(int tier) {
        if (tier < 0 || tier > 30) return 0xFFFFFF;
        // Mixin 后 GTValues.VC 已扩展到 31
        if (tier >= 15) return Hk3VoltagePalette.main(tier);
        if (tier < GTValues.VC.length) return GTValues.VC[tier];
        // Fallback
        return FULL_VC[tier];
    }

    /**
     * 安全获取指定 tier 的颜色格式字符串（§ 前缀）。
     * 修改要点：刻意不读 GTValues.VCF 以规避字段可能缺失；越界返回空串
     */
    public static String getVCF(int tier) {
        if (tier < 0 || tier > 30) return "";
        // 不直接引用 GTValues.VCF（编译期可能不存在）
        // 统一使用本类数组
        return tier >= 15 ? Hk3VoltagePalette.legacy(tier) : FULL_VCF[tier];
    }

    /** 中文说明：该处说明已按当前代码行为整理。*/
    public static String getVNF(int tier) {
        if (tier < 0 || tier > 30) return "\u00a7rUnknown";
        if (tier < GTValues.VNF.length) return GTValues.VNF[tier];
        return getVCF(tier) + getVN(tier);
    }

    /** 中文说明：该处说明已按当前代码行为整理。*/
    public static String getVN(int tier) {
        if (tier < 0 || tier > 30) return "???";
        if (tier >= 15) return Hk3Tiers.VOLTAGE_SYMBOLS[tier - 15];
        if (tier < GTValues.VN.length) return GTValues.VN[tier];
        // Fallback — 不应该触发（Mixin 已扩展 VN）
        String[] fallbackVN = {
                "HBV", "HCV", "HRV", "HDV",
                "QSV", "QCV", "QEV", "QAV",
                "IMV", "ICV", "IRV", "IWV",
                "WFV", "WSV", "CIV", "CEV"
        };
        return fallbackVN[tier - 15];
    }

    /** 中文说明：该处说明已按当前代码行为整理。*/
    public static String getVoltageName(int tier) {
        if (tier < 0 || tier > 30) return "Unknown Voltage";
        if (tier >= 15) return Hk3Tiers.VOLTAGE_NAMES_EN[tier - 15];
        if (tier < GTValues.VOLTAGE_NAMES.length) return GTValues.VOLTAGE_NAMES[tier];
        String[] fallbackNames = {
                Hk3Tiers.VOLTAGE_NAMES_EN[0], Hk3Tiers.VOLTAGE_NAMES_EN[1],
                Hk3Tiers.VOLTAGE_NAMES_EN[2], Hk3Tiers.VOLTAGE_NAMES_EN[3],
                Hk3Tiers.VOLTAGE_NAMES_EN[4], Hk3Tiers.VOLTAGE_NAMES_EN[5],
                Hk3Tiers.VOLTAGE_NAMES_EN[6], Hk3Tiers.VOLTAGE_NAMES_EN[7],
                Hk3Tiers.VOLTAGE_NAMES_EN[8], Hk3Tiers.VOLTAGE_NAMES_EN[9],
                Hk3Tiers.VOLTAGE_NAMES_EN[10], Hk3Tiers.VOLTAGE_NAMES_EN[11],
                Hk3Tiers.VOLTAGE_NAMES_EN[12], Hk3Tiers.VOLTAGE_NAMES_EN[13],
                Hk3Tiers.VOLTAGE_NAMES_EN[14], Hk3Tiers.VOLTAGE_NAMES_EN[15]
        };
        return fallbackNames[tier - 15];
    }

    /**
     * 安全获取人类可读等级名（含颜色前缀，如 "§bAdvanced"）。
     * 修改要点：直接读 FULL_VLVH；不依赖 GTValues，改动仅影响文本显示
     */
    public static String getVLVH(int tier) {
        if (tier < 0 || tier > 30) return "Unknown";
        return tier >= 15 ? Hk3VoltagePalette.legacy(tier) + Hk3Tiers.VOLTAGE_SYMBOLS[tier - 15] : FULL_VLVH[tier];
    }

    /**
     * 安全获取等级后缀（如 " II§r"）。
     * 修改要点：与 getVLVH 配合使用，末尾 §r 不可省略
     */
    public static String getVLVT(int tier) {
        if (tier < 0 || tier > 30) return "";
        return tier >= 15 ? "§r" : FULL_VLVT[tier];
    }

    /**
     * 安全获取 tier 对应的罗马数字。
     * 修改要点：仅字面量查表；扩 tier 需同步扩 FULL_LVT
     */
    public static String getLVT(int tier) {
        if (tier < 0 || tier > 30) return "";
        return FULL_LVT[tier];
    }

    /**
     * 获取 long 版配方电压（解决 Tier 15+ 的 int 溢出问题）。
     * 修改要点：所有高 tier 配方计算必须走此方法，禁止直接用 GTValues.VA[tier]（int 型会溢出）
     */
    public static long getVA(int tier) {
        if (tier < 0 || tier > 30) return 0L;
        return VA_LONG[tier];
    }

    /** 中文说明：该处说明已按当前代码行为整理。*/
    public static long getV(int tier) {
        if (tier < 0 || tier > 30) return 0L;
        if (tier < GTValues.V.length) return GTValues.V[tier];
        // Fallback: VEX 原版就有 31 个元素
        return GTValues.VEX[tier];
    }

    /**
     * 获取 tier 对应电压值的一半（常用于 overclock 计算）。
     */
    public static long getVH(int tier) {
        return getV(tier) / 2;
    }

    /**
     * 判断是否为扩展 tier（15~30）。
     * 修改要点：是否进入"本模组新增"电压段的总闸；新增阶段时应同步扩上界
     */
    public static boolean isExtendedTier(int tier) {
        return tier >= 15 && tier <= 30;
    }

    /** 是否为海渊阶段（15~18）。修改要点：阶段区段边界变更需同步修改 getPhaseName */
    public static boolean isAbyssTier(int tier) {
        return tier >= 15 && tier <= 18;
    }

    /** 是否为虚数阶段（19~22）。修改要点：阶段区段边界变更需同步修改 getPhaseName */
    public static boolean isImaginaryTier(int tier) {
        return tier >= 19 && tier <= 22;
    }

    /** 是否为量子阶段（23~26）。修改要点：阶段区段边界变更需同步修改 getPhaseName */
    public static boolean isQuantumTier(int tier) {
        return tier >= 23 && tier <= 26;
    }

    /** 是否为终焉阶段（27~30）。修改要点：阶段区段边界变更需同步修改 getPhaseName */
    public static boolean isFinalityTier(int tier) {
        return tier >= 27 && tier <= 30;
    }

    /**
     * 获取 tier 所属阶段英文名。
     * 修改要点：与 isXxxTier 判定一致；新增阶段需同步添加分支
     */
    public static String getPhaseName(int tier) {
        if (tier <= 14) return "Original";
        if (tier <= 18) return "Abyss";
        if (tier <= 22) return "Imaginary";
        if (tier <= 26) return "Quantum";
        if (tier <= 30) return "Finality";
        return "Unknown";
    }

    /**
     * 获取 tier 所属阶段中文名。
     * 修改要点：与 getPhaseName 保持分段一致；中文名用于本地化 tooltip/成就显示
     */
    public static String getPhaseNameCN(int tier) {
        if (tier <= 14) return "原版";
        if (tier <= 18) return "海渊";
        if (tier <= 22) return "虚数";
        if (tier <= 26) return "量子";
        if (tier <= 30) return "终焉";
        return "未知";
    }
}