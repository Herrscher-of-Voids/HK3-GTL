package com.sirin.hk3gtl.mixin;


/**
 * 【文件职责】
 * - 处理 GTValuesMixin 的 Mixin 注入逻辑。
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
 *   1) 删除 ALL_TIERS 仅含 0~14、TIER_COUNT 固定为 15 的容量限制；该限制会令 GTValues 的全局 tier 集合与扩展电压数组长度不一致。
 * - 新增：
 *   1) 将 ALL_TIERS 扩展为 0~30，并将 TIER_COUNT 改为 31，使高阶电压索引、GT 数组容量和按 tier 分配的定义数组保持一致。
 * - 修改：
 *   1) GTCEu 自动注册仍通过 GTMachines/GTCovers 的 tiersBetween(..., MAX/OpV) 过滤，因 ALL_TIERS 已排序且上限为原版 MAX/OpV，迭代会在 14 或 13 停止，不会自动注册 15~30 总线、仓室或盖子。
 *   2) 更新本文件的边界说明，明确区分“全局 tier 容量”与“GT 原生自动注册 tier 集合”。
 * - 用途：
 *   1) 为 Tier 15~30 提供可索引的 GT 全局 tier 容量，同时保留 GT 原生机器注册边界；本模组高阶部件仍由自身注册逻辑负责。
 *   2) 关键风险是任何新增 GT 注册代码不得直接遍历 ALL_TIERS，否则会重新生成 15~30 的残缺部件。
 *
 * 【变更记录 #3】2026-07-19 02:29:49（第 3 次备注 · 内测三第 29 次更新）
 * - 删除：
 *   1) 回退 revision 28 对 ALL_TIERS 0~30 与 TIER_COUNT 31 的扩展，取消第三方代码直接遍历高阶 tier 的潜在注册风险。
 * - 新增：
 *   1) 恢复“电压数据扩展、自动注册集合不扩展”的边界说明；不新增任何机器、总线或仓室。
 * - 修改：
 *   1) ALL_TIERS 恢复为 0~14，TIER_COUNT 恢复为 15；V/VH/VA/VHA/VN/VNF/VOLTAGE_NAMES 继续保持 31 项供 Tier 15~30 配方与显示查询。
 * - 用途：
 *   1) 保留 hk3gtl 高阶电压能力，同时从全局 tier 集合层阻止 GTCEu 或联动模组为 Tier 15~30 自动注册残缺部件。
 *
 * 【段内说明】
 * - 复杂方法补充“干什么 / 边界 / 线程侧”精简中文注释。
 */
import com.gregtechceu.gtceu.api.GTValues;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Final;
import org.spongepowered.asm.mixin.Mutable;
import org.spongepowered.asm.mixin.Shadow;

/** 中文说明：该处说明已按当前代码行为整理。*/
@Mixin(value = GTValues.class, remap = false)
/**
 * 【变更记录 #4】2026-09-25 03:57:37（第 4 次备注 · 内测5修订71）
 * 删除：单一电路形态或旧电压显示限制。新增：统一系列及电压映射。
 * 修改：VNF和英文全称接入HBV至CEV；VN注册键与电压数值保持稳定。
 * 用途：保持同级电路可替换、资源与游戏行为一致。
 */
/**
 * 【变更记录 #5】2026-09-30 02:17:47（第5次备注 · 内测5修订107）
 * 删除：本文件可执行代码中的旧电压键及常量引用，不保留旧键注册别名。
 * 新增：16档正式缩写作为唯一电压标识；逐文件映射见logs/voltage-keys-r107。
 * 修改：注册、配方、查询或标签引用按原tier序号一一迁移；数值、层级与资源内容保持原义。
 * 用途：避免显示名与实际注册键不一致；历史备注保留，旧存档不自动改写。
 */
/**
 * 【变更记录 #6】2026-09-30 03:22:21（内测5修订108）
 * 删除：旧配色引用。新增：批准的16档统一RGB色卡。
 * 修改：VC保存精确RGB；传统VNF使用最近的Minecraft16色，避免不支持的格式码。
 * 用途：配色统一；电压数值、注册和配方门槛不变。
 */
public class GTValuesMixin {

    // ═══════════════════════════════════════
    // 中文备注：该处说明已按当前代码行为整理。
    //  通过 @Shadow 让 Mixin 能引用它们，再通过 @Mutable 允许我们重新赋值。
    // ═══════════════════════════════════════

    /** 真实电压值数组（long）；索引 = Tier；单位 EU/t。原版长度 15，扩展到 31。 */
    @Shadow @Final @Mutable
    public static long[] V;

    /** V / 2 的 int 版本（部分老代码用）；Tier 15+ 用 Integer.MAX_VALUE 占位避免溢出。 */
    @Shadow @Final @Mutable
    public static int[] VH;

    /** 配方实际消耗电压（V 扣除线损后的值）；int 数组。 */
    @Shadow @Final @Mutable
    public static int[] VA;

    /** VA / 2 的 int 数组；同样 Tier 15+ 用 Integer.MAX_VALUE 占位。 */
    @Shadow @Final @Mutable
    public static int[] VHA;

    /** 电压短名（用于注册 ID，小写化后作为方块 ID 前缀），如 "LV"、"HV"、"AB-I"。 */
    @Shadow @Final @Mutable
    public static String[] VN;

    /** 带颜色格式的显示名（Tooltip / JEI 展示用），含 Minecraft §颜色码。 */
    @Shadow @Final @Mutable
    public static String[] VNF;

    /** 扩展RGB色表，不扩大自动注册的tier集合。 */
    @Shadow @Final @Mutable
    public static int[] VC;

    /** 中文说明：该处说明已按当前代码行为整理。*/
    @Shadow @Final @Mutable
    public static String[] VOLTAGE_NAMES;

    /** GT 自动注册使用的 Tier 索引数组；刻意保持 0~14，避免生成 Tier 15+ 衍生机器。 */
    @Shadow @Final @Mutable
    public static int[] ALL_TIERS;

    /** GT 自动注册 Tier 数量；与 ALL_TIERS.length 一致，保持 15。 */
    @Shadow @Final @Mutable
    public static int TIER_COUNT;

    /**
     * 静态初始化块：在 {@link GTValues} 类首次被加载时执行，用新数组直接覆盖原值。
     * <p>时机关键：{@code <clinit>} 早于 GTCEu 任何注册逻辑，因此后续所有对这些字段的读取
     * 都能看到扩展后的数据，且不会触发并发问题（类初始化天然线程安全）。
     */
    static {
        // ═══════════════════════════════════════
        //  V[] - 电压值（15 → 31 个元素）
        // ═══════════════════════════════════════
        V = new long[] {
                8L, 32L, 128L, 512L, 2048L,                           // ULV ~ EV    (0~4)
                8192L, 32768L, 131072L, 524288L, 2097152L,             // IV ~ UHV    (5~9)
                8388608L, 33554432L, 134217728L, 536870912L,           // UEV ~ OpV   (10~13)
                2147483648L,                                            // MAX         (14)
                8589934592L,                                            // 海渊 I      (15)
                34359738368L,                                           // 海渊 II     (16)
                137438953472L,                                          // 海渊 III    (17)
                549755813888L,                                          // 海渊 IV     (18)
                2199023255552L,                                         // 虚数 I      (19)
                8796093022208L,                                         // 虚数 II     (20)
                35184372088832L,                                        // 虚数 III    (21)
                140737488355328L,                                       // 虚数 IV     (22)
                562949953421312L,                                       // 量子 I      (23)
                2251799813685248L,                                      // 量子 II     (24)
                9007199254740992L,                                      // 量子 III    (25)
                36028797018963968L,                                     // 量子 IV     (26)
                144115188075855872L,                                    // 终焉 I      (27)
                576460752303423488L,                                    // 终焉 II     (28)
                2305843009213693952L,                                   // 终焉 III    (29)
                Long.MAX_VALUE                                          // 终焉 IV     (30)
        };

        // ═══════════════════════════════════════
        //  VH[] - 电压值 / 2
        //  注意：Tier 15+ 超过 int 范围，用 Integer.MAX_VALUE
        // ═══════════════════════════════════════
        VH = new int[] {
                4, 16, 64, 256, 1024, 4096, 16384, 65536, 262144,
                1048576, 4194304, 16777216, 67108864, 268435456, 1073741824,
                Integer.MAX_VALUE, Integer.MAX_VALUE, Integer.MAX_VALUE, Integer.MAX_VALUE,
                Integer.MAX_VALUE, Integer.MAX_VALUE, Integer.MAX_VALUE, Integer.MAX_VALUE,
                Integer.MAX_VALUE, Integer.MAX_VALUE, Integer.MAX_VALUE, Integer.MAX_VALUE,
                Integer.MAX_VALUE, Integer.MAX_VALUE, Integer.MAX_VALUE, Integer.MAX_VALUE
        };

        // ═══════════════════════════════════════
        //  VA[] - 配方用电压（扣除线损）
        // ═══════════════════════════════════════
        VA = new int[] {
                7, 30, 120, 480, 1920, 7680, 30720, 122880, 491520,
                1966080, 7864320, 31457280, 125829120, 503316480, 2013265920,
                Integer.MAX_VALUE, Integer.MAX_VALUE, Integer.MAX_VALUE, Integer.MAX_VALUE,
                Integer.MAX_VALUE, Integer.MAX_VALUE, Integer.MAX_VALUE, Integer.MAX_VALUE,
                Integer.MAX_VALUE, Integer.MAX_VALUE, Integer.MAX_VALUE, Integer.MAX_VALUE,
                Integer.MAX_VALUE, Integer.MAX_VALUE, Integer.MAX_VALUE, Integer.MAX_VALUE
        };

        // ═══════════════════════════════════════
        //  VHA[] - 配方用电压 / 2
        // ═══════════════════════════════════════
        VHA = new int[] {
                3, 15, 60, 240, 960, 3840, 15360, 61440, 245760,
                983040, 3932160, 15728640, 62914560, 251658240, 1006632960,
                Integer.MAX_VALUE, Integer.MAX_VALUE, Integer.MAX_VALUE, Integer.MAX_VALUE,
                Integer.MAX_VALUE, Integer.MAX_VALUE, Integer.MAX_VALUE, Integer.MAX_VALUE,
                Integer.MAX_VALUE, Integer.MAX_VALUE, Integer.MAX_VALUE, Integer.MAX_VALUE,
                Integer.MAX_VALUE, Integer.MAX_VALUE, Integer.MAX_VALUE, Integer.MAX_VALUE
        };

        // ═══════════════════════════════════════
        //  VN[] - 短名（注册ID用）
        // ═══════════════════════════════════════
        VN = new String[] {
                "ULV", "LV", "MV", "HV", "EV", "IV", "LuV", "ZPM", "UV",
                "UHV", "UEV", "UIV", "UXV", "OpV", "MAX",
                "HBV", "HCV", "HRV", "HDV",
                "QSV", "QCV", "QEV", "QAV",
                "IMV", "ICV", "IRV", "IWV",
                "WFV", "WSV", "CIV", "CEV"
        };

        // ═══════════════════════════════════════
        //  VNF[] - 带颜色格式的显示名（JEI / Tooltip）
        // ═══════════════════════════════════════
        VNF = new String[] {
                // 原版 0~14
                "\u00a78ULV",
                "\u00a77LV",
                "\u00a7bMV",
                "\u00a76HV",
                "\u00a75EV",
                "\u00a79IV",
                "\u00a7dLuV",
                "\u00a7cZPM",
                "\u00a73UV",
                "\u00a74UHV",
                "\u00a7aUEV",
                "\u00a72UIV",
                "\u00a7eUXV",
                "\u00a79\u00a7lOpV",
                "\u00a7c\u00a7lMAX",
                // 海渊 15~18 — 深蓝 + 粗体
                "\u00a71\u00a7lHBV",
                "\u00a71\u00a7lHCV",
                "\u00a71\u00a7lHRV",
                "\u00a71\u00a7lHDV",
                // 虚数 19~22 — 深青 + 粗体
                "\u00a73\u00a7lQSV",
                "\u00a73\u00a7lQCV",
                "\u00a73\u00a7lQEV",
                "\u00a73\u00a7lQAV",
                // 量子 23~26 — 金色 + 粗体
                "\u00a76\u00a7lIMV",
                "\u00a76\u00a7lICV",
                "\u00a76\u00a7lIRV",
                "\u00a76\u00a7lIWV",
                // 终焉 27~30 — 深红 + 粗体
                "\u00a74\u00a7lWFV",
                "\u00a74\u00a7lWSV",
                "\u00a74\u00a7lCIV",
                "\u00a74\u00a7lCEV"
        };

        // ═══════════════════════════════════════
        //  VOLTAGE_NAMES[] - 完整英文名
        // ═══════════════════════════════════════
        VOLTAGE_NAMES = new String[] {
                "Ultra Low Voltage", "Low Voltage", "Medium Voltage",
                "High Voltage", "Extreme Voltage", "Insane Voltage",
                "Ludicrous Voltage", "ZPM Voltage", "Ultimate Voltage",
                "Ultra High Voltage", "Ultra Excessive Voltage",
                "Ultra Immense Voltage", "Ultra Extreme Voltage",
                "Overpowered Voltage", "Maximum Voltage",
                com.sirin.hk3gtl.common.constants.Hk3Tiers.VOLTAGE_NAMES_EN[0], com.sirin.hk3gtl.common.constants.Hk3Tiers.VOLTAGE_NAMES_EN[1],
                com.sirin.hk3gtl.common.constants.Hk3Tiers.VOLTAGE_NAMES_EN[2], com.sirin.hk3gtl.common.constants.Hk3Tiers.VOLTAGE_NAMES_EN[3],
                com.sirin.hk3gtl.common.constants.Hk3Tiers.VOLTAGE_NAMES_EN[4], com.sirin.hk3gtl.common.constants.Hk3Tiers.VOLTAGE_NAMES_EN[5],
                com.sirin.hk3gtl.common.constants.Hk3Tiers.VOLTAGE_NAMES_EN[6], com.sirin.hk3gtl.common.constants.Hk3Tiers.VOLTAGE_NAMES_EN[7],
                com.sirin.hk3gtl.common.constants.Hk3Tiers.VOLTAGE_NAMES_EN[8], com.sirin.hk3gtl.common.constants.Hk3Tiers.VOLTAGE_NAMES_EN[9],
                com.sirin.hk3gtl.common.constants.Hk3Tiers.VOLTAGE_NAMES_EN[10], com.sirin.hk3gtl.common.constants.Hk3Tiers.VOLTAGE_NAMES_EN[11],
                com.sirin.hk3gtl.common.constants.Hk3Tiers.VOLTAGE_NAMES_EN[12], com.sirin.hk3gtl.common.constants.Hk3Tiers.VOLTAGE_NAMES_EN[13],
                com.sirin.hk3gtl.common.constants.Hk3Tiers.VOLTAGE_NAMES_EN[14], com.sirin.hk3gtl.common.constants.Hk3Tiers.VOLTAGE_NAMES_EN[15]
        };

        // ═══════════════════════════════════════
        //  ALL_TIERS[] & TIER_COUNT
        //  只保留 0-14，避免 GTCEu 或联动模组自动为 15-30 注册总线/仓室。
        //  电压和名称数组仍扩展到 31 项，支持高阶配方与显示。
        // ═══════════════════════════════════════
        ALL_TIERS = new int[] {
                0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14
        };
        TIER_COUNT = 15;
        // 注册、显示与英文全称共同使用现行16级定义，原版tier集合不扩张。
        VC = java.util.Arrays.copyOf(VC, 31);
        for (int index = 0; index < 16; index++) {
            VC[15 + index] = com.sirin.hk3gtl.common.constants.Hk3VoltagePalette.main(15 + index);
            int tier = 15 + index;
            VN[tier] = com.sirin.hk3gtl.common.constants.Hk3Tiers.VOLTAGE_SYMBOLS[index];
            String color = com.sirin.hk3gtl.common.constants.Hk3VoltagePalette.legacy(tier);
            VNF[tier] = color + com.sirin.hk3gtl.common.constants.Hk3Tiers.VOLTAGE_SYMBOLS[index];
            VOLTAGE_NAMES[tier] = com.sirin.hk3gtl.common.constants.Hk3Tiers.VOLTAGE_NAMES_EN[index];
        }
    }
}
