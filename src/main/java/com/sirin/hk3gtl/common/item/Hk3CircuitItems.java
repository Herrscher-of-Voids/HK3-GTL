package com.sirin.hk3gtl.common.item;

/**
 * 
 * - 注册或实现 Hk3CircuitItems 物品行为。
 *
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
