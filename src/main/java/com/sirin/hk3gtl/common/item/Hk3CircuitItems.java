package com.sirin.hk3gtl.common.item;



import net.minecraft.world.item.Item;
import net.minecraftforge.registries.RegistryObject;

import java.util.Collections;
import java.util.LinkedHashMap;
import java.util.Map;

/**
 * 电路物品统一注册中心，包含两类电路：
 * <ol>
 *   <li>崩坏能电路板（ULV~MAX，共15级） — 注册ID格式：{@code honkai_circuit_<tier>}</li>
 *   <li>细分电路物品 64 个注册ID（4体系×4阶×4形态）；玩法上仅 16 档 canonical（每阶固定一种形态：processor→assembly→computer→processor_mainframe），其余为归档占位</li>
 * </ol>
 *
 * <h3>修改指南</h3>
 * <ul>
 *   <li>新增崩坏能电路等级：在 {@link #HONKAI_CIRCUIT_TIERS} 数组中添加tier名</li>
 *   <li>新增细分电路阶段：在 {@link #DETAILED_CIRCUIT_TIERS} 数组中添加</li>
 *   <li>新增电路形态：在 {@link #DETAILED_CIRCUIT_TYPES} 数组中添加</li>
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

    /**
     * 细分电路的阶段名（4体系 × 4级），注册ID前缀。
     * 体系顺序：海渊(abyss) → 虚数(imaginary) → 量子(quantum) → 终焉(finality)
     */
    private static final String[] DETAILED_CIRCUIT_TIERS = {
            "abyss_1", "abyss_2", "abyss_3", "abyss_4",
            "imaginary_1", "imaginary_2", "imaginary_3", "imaginary_4",
            "quantum_1", "quantum_2", "quantum_3", "quantum_4",
            "finality_1", "finality_2", "finality_3", "finality_4"
    };

    /** 电路形态名（处理器/集成/计算机/主机），注册ID后缀 */
    private static final String[] DETAILED_CIRCUIT_TYPES = {
            "processor", "assembly", "computer", "processor_mainframe"
    };

    private static final Map<String, RegistryObject<Item>> MUTABLE_HONKAI_CIRCUITS = new LinkedHashMap<>();
    private static final Map<String, RegistryObject<Item>> MUTABLE_DETAILED_CIRCUITS = new LinkedHashMap<>();

    /** 崩坏能电路只读视图，Key=tier名（如"lv"），用 {@link #getHonkaiCircuit} 访问 */
    public static final Map<String, RegistryObject<Item>> HONKAI_CIRCUITS =
            Collections.unmodifiableMap(MUTABLE_HONKAI_CIRCUITS);

    /** 细分电路只读视图，Key="{tier}_{type}"（如"abyss_1_processor"），用 {@link #getDetailedCircuit} 访问 */
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

    /** 按阶段+形态获取细分电路，如 getDetailedCircuit("abyss_1", "processor") */
    public static RegistryObject<Item> getDetailedCircuit(String tier, String type) {
        return MUTABLE_DETAILED_CIRCUITS.get(tier + "_" + type);
    }

    private static void registerHonkaiCircuits() {
        for (String tier : HONKAI_CIRCUIT_TIERS) {
            String id = "honkai_circuit_" + tier;
            MUTABLE_HONKAI_CIRCUITS.put(tier, registerItem(id));
        }
    }

    private static void registerDetailedCircuits() {
        for (String tier : DETAILED_CIRCUIT_TIERS) {
            for (String type : DETAILED_CIRCUIT_TYPES) {
                String id = tier + "_" + type;
                MUTABLE_DETAILED_CIRCUITS.put(id, registerItem(id));
            }
        }
    }

    private static RegistryObject<Item> registerItem(String id) {
        return Hk3Items.ITEMS.register(id, () -> new Item(new Item.Properties()));
    }
}
