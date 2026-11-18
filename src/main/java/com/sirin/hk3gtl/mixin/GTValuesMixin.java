package com.sirin.hk3gtl.mixin;




























import com.gregtechceu.gtceu.api.GTValues;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Final;
import org.spongepowered.asm.mixin.Mutable;
import org.spongepowered.asm.mixin.Shadow;

@Mixin(value = GTValues.class, remap = false)



















public class GTValuesMixin {

    // ═══════════════════════════════════════
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
