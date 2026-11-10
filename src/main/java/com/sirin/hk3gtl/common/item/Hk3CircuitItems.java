package com.sirin.hk3gtl.common.item;


/**
 * 【文件职责】
 * - 注册或实现 Hk3CircuitItems 物品行为。
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
 *
 * 【变更记录 #2】2026-07-19 21:49:23（第 2 次备注 · revision 35）
 * - 删除：
 *   1) 删除公开字段直接持有可变 LinkedHashMap 的写入口，外部代码不能再通过 put、remove、clear 改写电路注册结果。
 *   2) 未删除任何电路注册 ID、查询方法或注册流程，物品注册数量与顺序保持不变。
 * - 新增：
 *   1) 新增两个私有可变注册 Map，限定为本类注册期写入。
 *   2) 公开同名 Map 改为不可变视图，继续支持创造栏按原顺序遍历 values，非法外部写入会被拒绝。
 * - 修改：
 *   1) 注册和查询方法改为访问私有可变 Map；外部已有查询方法及只读遍历调用无需改变。
 *   2) 可变状态的所有权由公开共享改为类内封装，避免外部误改导致配方引用、桥接别名与创造栏内容不一致。
 * - 用途：
 *   1) 本文件仍负责注册 15 个崩坏能电路和 64 个细分电路，并为配方、桥接类及创造栏提供稳定引用。
 *   2) 关键风险点是 Forge 注册期顺序；不可变视图是动态视图，不会阻断注册期后续写入或改变迭代顺序。
 */
import net.minecraft.world.item.Item;
import net.minecraftforge.registries.RegistryObject;

import java.util.Collections;
import java.util.LinkedHashMap;
import java.util.Map;

/**
 * 电路物品统一注册中心，包含两类电路：
 * <ol>
 *   <li>崩坏能电路板（ULV~MAX，共15级） — 注册ID格式：{@code honkai_circuit_<tier>}</li>
 *   <li>细分电路物品：仅注册 {@link Hk3CircuitCatalog#ENTRIES} 中的52个正式ID</li>
 * </ol>
 *
 * <h3>修改指南</h3>
 * <ul>
 *   <li>新增崩坏能电路等级：在 {@link #HONKAI_CIRCUIT_TIERS} 数组中添加tier名</li>
 *   <li>新增细分电路：在 {@link Hk3CircuitCatalog#ENTRIES} 中添加正式目录项</li>
 *   <li>获取引用：{@link #getHonkaiCircuit(String)} / {@link #getDetailedCircuit(String, String)}</li>
 *   <li>电路标签：{@code data/forge/tags/items/circuits/<tier>.json}，每级只含本级电路</li>
 *   <li>贴图路径：{@code assets/hk3gtl/textures/item/<注册ID>.png}</li>
 * </ul>
 *
 * @see AbyssCircuitItems 海渊电路桥接别名
 * @see ImaginaryCircuitItems 虚数电路桥接别名
 * @see QuantumCircuitItems 量子电路桥接别名
 * @see FinalityCircuitItems 终焉电路桥接别名
 */
/**
 * 【变更记录 #3】2026-09-25 03:57:37（第 3 次备注 · 内测5修订71）
 * 删除：单一电路形态或旧电压显示限制。新增：统一系列及电压映射。
 * 修改：注册12种交叠系列电路，保留既有16种正式引用。
 * 用途：保持同级电路可替换、资源与游戏行为一致。
 */
/**
 * 【变更记录 #4】2026-09-26 01:52:49（第 4 次备注 · 内测5修订74）
 * 删除：普通Item缺失电压提示的注册方式。新增：正式电路等级的只读传参。
 * 修改：28个目录电路与15个崩坏能电路改用Hk3CircuitItem，其他占位物不猜测等级。
 * 用途：把电压显示移到tooltip，保留注册键、系列映射及同级标签。
 */
/**
 * 【变更记录 #5】2026-09-30 02:17:47（第5次备注 · 内测5修订107）
 * 删除：本文件可执行代码中的旧电压键及常量引用，不保留旧键注册别名。
 * 新增：16档正式缩写作为唯一电压标识；逐文件映射见logs/voltage-keys-r107。
 * 修改：注册、配方、查询或标签引用按原tier序号一一迁移；数值、层级与资源内容保持原义。
 * 用途：避免显示名与实际注册键不一致；历史备注保留，旧存档不自动改写。
 */
/** 【变更记录 #6】2026-11-04 23:10:59（第6次备注 · 内测5修订202）：删除旧16阶×4形态组合数组、嵌套注册及非primary补注册；新增目录外ID注册拒绝；修改细分电路仅注册正式目录52项，保留15个崩坏能电路及桥接查询；用途：移除48个无等级占位，历史备注仅保留原时点记录。 */
public final class Hk3CircuitItems {

    /** 崩坏能电路板等级名（ULV~MAX），修改此数组可增减电路等级数量 */
    private static final String[] HONKAI_CIRCUIT_TIERS = {
            "ulv", "lv", "mv", "hv", "ev",
            "iv", "luv", "zpm", "uv", "uhv",
            "uev", "uiv", "uxv", "opv", "max"
    };

    private static final Map<String, RegistryObject<Item>> MUTABLE_HONKAI_CIRCUITS = new LinkedHashMap<>();
    private static final Map<String, RegistryObject<Item>> MUTABLE_DETAILED_CIRCUITS = new LinkedHashMap<>();

    /** 崩坏能电路只读视图，Key=tier名（如"lv"），用 {@link #getHonkaiCircuit} 访问 */
    public static final Map<String, RegistryObject<Item>> HONKAI_CIRCUITS =
            Collections.unmodifiableMap(MUTABLE_HONKAI_CIRCUITS);

    /** 52个正式细分电路的只读视图，Key为目录ID（如"hbv_processor"）。 */
    public static final Map<String, RegistryObject<Item>> DETAILED_CIRCUITS =
            Collections.unmodifiableMap(MUTABLE_DETAILED_CIRCUITS);

    private Hk3CircuitItems() {
    }

    public static void register() {
        registerHonkaiCircuits();
        registerDetailedCircuits();
    }

    /** 按tier名获取崩坏能电路，如 getHonkaiCircuit("lv") */
    public static RegistryObject<Item> getHonkaiCircuit(String tier) {
        return MUTABLE_HONKAI_CIRCUITS.get(tier);
    }

    /** 按阶段+形态获取正式细分电路，如 getDetailedCircuit("hbv", "processor")；非目录ID返回null。 */
    public static RegistryObject<Item> getDetailedCircuit(String tier, String type) {
        return MUTABLE_DETAILED_CIRCUITS.get(tier + "_" + type);
    }

    private static void registerHonkaiCircuits() {
        for (String tier : HONKAI_CIRCUIT_TIERS)
            MUTABLE_HONKAI_CIRCUITS.put(tier, registerItem("honkai_circuit_" + tier));
    }

    private static void registerDetailedCircuits() {
        for (var entry : Hk3CircuitCatalog.ENTRIES)
            MUTABLE_DETAILED_CIRCUITS.put(entry.id(), registerItem(entry.id()));
    }

    private static RegistryObject<Item> registerItem(String id) {
        int tier = Hk3CircuitCatalog.tier(new net.minecraft.resources.ResourceLocation("hk3gtl", id));
        for (int i = 0; i < HONKAI_CIRCUIT_TIERS.length; i++) {
            if (id.equals("honkai_circuit_" + HONKAI_CIRCUIT_TIERS[i])) tier = i;
        }
        if (tier < 0) throw new IllegalArgumentException("非正式电路ID: " + id);
        final int displayTier = tier;
        return Hk3Items.ITEMS.register(id, () -> new Hk3CircuitItem(displayTier));
    }
}
