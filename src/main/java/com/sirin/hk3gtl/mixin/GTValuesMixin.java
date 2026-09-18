package com.sirin.hk3gtl.mixin;



import com.gregtechceu.gtceu.api.GTValues;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Final;
import org.spongepowered.asm.mixin.Mutable;
import org.spongepowered.asm.mixin.Shadow;

/**
 * GTCEu {@link GTValues} 电压/Tier 数组扩展 Mixin（本模组新增 15~30 级电压的核心）。
 *
 * <p><b>目标类</b>：{@link GTValues}
 * （GTCEu 的全局常量类，所有电压值数组、Tier 数量、短名/彩色名都在这里硬编码）。
 *
 * <p><b>注入目的</b>：GTCEu 原版只定义了 Tier 0~14（ULV ~ MAX）。本模组要扩展到
 * Tier 30，新增 4 个层级共 16 个子 Tier：
 * <ul>
 *   <li>海渊 AB I~IV（15~18）</li>
 *   <li>虚数 IM I~IV（19~22）</li>
 *   <li>量子 QT I~IV（23~26）</li>
 *   <li>终焉 FN I~IV（27~30）</li>
 * </ul>
 * <p>通过在类初始化期（{@code <clinit>}）<b>重写</b> V / VH / VA / VHA / VN / VNF /
 * VOLTAGE_NAMES 这些 static final 数组，让 GTCEu 后续电压查询、tooltip、JEI 和配方匹配
 * 自动看到扩展后的数据。ALL_TIERS 与 TIER_COUNT 刻意保持原版范围，避免 GTCEu 或联动模组
 * 直接遍历全局 tier 时为 Tier 15~30 自动注册总线、仓室和其他残缺部件。
 *
 * <p><b>失效后影响</b>：
 * <ul>
 *   <li>任何 Tier 15+ 的机器/配方都会越界崩溃（{@code V[15]} 抛 AIOOBE）。</li>
 *   <li>JEI / tooltip 无法显示"AB-I、QT-II"等新电压名。</li>
 *   <li>本模组整个高阶科技树直接瘫痪。</li>
 * </ul>
 *
 * <p><b>特殊设计说明</b>：
 * <ul>
 *   <li>只 Shadow <b>确定存在且必须扩展</b>的字段，其他次要字段（{@code VC, VCM, VCF,
 *       VLVH, VLVT, LVT} 等）不触碰，改用 {@code Hk3Values} 工具类对外提供扩展查询，
 *       原因是那些字段在不同 GTCEu 版本中签名/存在性不稳定，强 Shadow 会导致 Mixin
 *       在其他版本 apply 失败。</li>
 *   <li>{@link Mutable} 注解允许我们在静态块里对 Shadow 过来的 {@code static final} 字段
 *       重新赋值；没有 {@code @Mutable} 会被 MixinTransformer 拒绝。</li>
 *   <li>{@code ALL_TIERS} 只保留 0~14，{@code TIER_COUNT} 保持 15：即使 GTCEu 或联动模组
 *       直接遍历全局 tier 集合，也不会生成 Tier 15~30 的总线、仓室或其他衍生机器；
 *       高 Tier 部件继续由本模组自行注册。</li>
 *   <li>但 V/VN/VNF/VOLTAGE_NAMES 等数组仍然扩展到 31 个元素，保证"电压值"本身可查，
 *       满足配方能耗、JEI tooltip 显示需求。</li>
 *   <li>VH/VA/VHA 是 int 数组：超过 {@code Integer.MAX_VALUE} 的 Tier（15+）全部设为
 *       {@code Integer.MAX_VALUE} 作为安全值；真实高精度电压请用 {@code V[]}（long）。</li>
 * </ul>
 *
 * <p><b>修改指南</b>：
 * <ul>
 *   <li>所有电压数组长度必须严格等于 31，否则任何访问 Tier 30 的代码都会越界。</li>
 *   <li>修改某个电压值时，必须<b>同时</b>修改 V / VH / VA / VHA 四个数组的对应位，
 *       它们是强耦合关系（V=真实电压，VH=V/2，VA=扣除线损后的配方电压，VHA=VA/2）。</li>
 *   <li>VN 的短名用于注册 ID（小写化），因此不能出现非法字符；改名会导致旧存档里的
 *       机器找不到实体，仅限模组未发布阶段修改。</li>
 *   <li>VNF 使用 Minecraft 颜色码 {@code §1~§f/§l}，修改颜色时注意 {@code §r} 的位置
 *       以确保 JEI 能正常换行显示。</li>
 *   <li>不要在这里调用任何 GTCEu 的 API；类初始化期过早，大量注册表还没就绪。</li>
 *   <li>Architectury 规则：若要把本 Mixin 下沉到 common，请保证 Fabric 和 Forge
 *       的 mixins.json 都包含它，避免单端未扩展导致客户端/服务器数据不一致。</li>
 *   <li>{@code remap = false}（第三方模组类）。</li>
 * </ul>
 */
@Mixin(value = GTValues.class, remap = false)
public class GTValuesMixin {

    // ═══════════════════════════════════════
    //  Shadow 字段：这些都是 GTValues 原类的 public static final 数组/常量，
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

    /** 完整英文电压名（"Low Voltage"、"Abyss I Voltage" 等），用于语言文件 fallback。 */
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
                "AB-I", "AB-II", "AB-III", "AB-IV",
                "IM-I", "IM-II", "IM-III", "IM-IV",
                "QT-I", "QT-II", "QT-III", "QT-IV",
                "FN-I", "FN-II", "FN-III", "FN-IV"
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
                "\u00a71\u00a7lAB-\u00a7r\u00a71\u00a7lI",
                "\u00a71\u00a7lAB-\u00a7r\u00a71\u00a7lII",
                "\u00a71\u00a7lAB-\u00a7r\u00a71\u00a7lIII",
                "\u00a71\u00a7lAB-\u00a7r\u00a71\u00a7lIV",
                // 虚数 19~22 — 深青 + 粗体
                "\u00a73\u00a7lIM-\u00a7r\u00a73\u00a7lI",
                "\u00a73\u00a7lIM-\u00a7r\u00a73\u00a7lII",
                "\u00a73\u00a7lIM-\u00a7r\u00a73\u00a7lIII",
                "\u00a73\u00a7lIM-\u00a7r\u00a73\u00a7lIV",
                // 量子 23~26 — 金色 + 粗体
                "\u00a76\u00a7lQT-\u00a7r\u00a76\u00a7lI",
                "\u00a76\u00a7lQT-\u00a7r\u00a76\u00a7lII",
                "\u00a76\u00a7lQT-\u00a7r\u00a76\u00a7lIII",
                "\u00a76\u00a7lQT-\u00a7r\u00a76\u00a7lIV",
                // 终焉 27~30 — 深红 + 粗体
                "\u00a74\u00a7lFN-\u00a7r\u00a74\u00a7lI",
                "\u00a74\u00a7lFN-\u00a7r\u00a74\u00a7lII",
                "\u00a74\u00a7lFN-\u00a7r\u00a74\u00a7lIII",
                "\u00a74\u00a7lFN-\u00a7r\u00a74\u00a7lIV"
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
                "Abyss I Voltage", "Abyss II Voltage",
                "Abyss III Voltage", "Abyss IV Voltage",
                "Imaginary I Voltage", "Imaginary II Voltage",
                "Imaginary III Voltage", "Imaginary IV Voltage",
                "Quantum I Voltage", "Quantum II Voltage",
                "Quantum III Voltage", "Quantum IV Voltage",
                "Finality I Voltage", "Finality II Voltage",
                "Finality III Voltage", "Finality IV Voltage"
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
    }
}
