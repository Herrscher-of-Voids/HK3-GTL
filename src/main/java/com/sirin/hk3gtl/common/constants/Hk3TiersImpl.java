package com.sirin.hk3gtl.common.constants;


/**
 * 【文件职责】
 * - 维护 Hk3TiersImpl 的核心功能实现。
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
 * 【变更记录 #2】2026-07-19 02:11:46（第 2 次备注 · 内测三第 28 次更新）
 * - 删除：
 *   1) 删除“禁止扩展 GTValues.ALL_TIERS/TIER_COUNT”的过期维护限制，该限制已不符合 31 级全局 tier 容量需求。
 * - 新增：
 *   1) 新增全局 tier 可扩展、原生机器注册仍受 tiersBetween(..., MAX/OpV) 限制的维护说明。
 * - 修改：
 *   1) 仅修正文档约束，不改变本类 15~30 常量与查询方法；实际 GTValues 字段修改位于 GTValuesMixin。
 * - 用途：
 *   1) 防止维护者误把全局 tier 容量与 GT 自动注册范围混为一谈，避免未来回退到数组长度不一致的状态。
 *
 * 【变更记录 #3】2026-07-19 02:29:49（第 3 次备注 · 内测三第 29 次更新）
 * - 删除：
 *   1) 回退 revision 28 关于 GTValues.ALL_TIERS/TIER_COUNT 已扩展到 0~30/31 的维护说明。
 * - 新增：
 *   1) 恢复扩展 tier 与 GT 自动注册 tier 集合隔离的说明。
 * - 修改：
 *   1) 仅修正文档契约；本类 15~30 常量、名称和电压查询逻辑均不回退。
 * - 用途：
 *   1) 确保高阶配方继续可用，同时阻止 GTCEu 和联动模组通过全局 tier 集合批量创建高阶总线与仓室。
 *
 * 【段内说明】
 * - 复杂方法补充“干什么 / 边界 / 线程侧”精简中文注释。
 */
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
 *   <tr><td>HBV—HDV</td><td>15~18</td><td>崩能压—致密压</td></tr>
 *   <tr><td>QSV—QAV</td><td>19~22</td><td>叠态压—锚定压</td></tr>
 *   <tr><td>IMV—IWV</td><td>23~26</td><td>虚数压—织界压</td></tr>
 *   <tr><td>WFV—CEV</td><td>27~30</td><td>构界压—恒续压</td></tr>
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
/**
 * 【变更记录 #4】2026-09-30 02:17:47（第4次备注 · 内测5修订107）
 * 删除：本文件可执行代码中的旧电压键及常量引用，不保留旧键注册别名。
 * 新增：16档正式缩写作为唯一电压标识；逐文件映射见logs/voltage-keys-r107。
 * 修改：注册、配方、查询或标签引用按原tier序号一一迁移；数值、层级与资源内容保持原义。
 * 用途：避免显示名与实际注册键不一致；历史备注保留，旧存档不自动改写。
 */
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

    /**
     * 全部 16 级新 tier 索引数组，按阶段顺序排列。
     * <p>用于批量遍历扩展等级，如注册总线、生成配方等。</p>
     */
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

    /**
     * 中文显示名数组，索引 0 对应 tier 15。
     * <p>用于 GUI、聊天消息等中文环境下的等级显示。</p>
     */
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

    /**
     * 英文显示名数组，索引 0 对应 tier 15。
     * <p>用于 en_us 语言环境和日志输出。</p>
     */
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
