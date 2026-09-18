package com.sirin.hk3gtl.common.item.abyss;



import com.sirin.hk3gtl.common.item.Hk3CircuitItems;
import net.minecraft.world.item.Item;
import net.minecraftforge.registries.RegistryObject;

/**
 * 海渊一~四正式电路 → {@link Hk3CircuitItems}（canonical：阶1 processor、阶2 assembly、阶3 computer、阶4 processor_mainframe）。
 * <p>不注册独立物品，仅为配方/研究代码提供向后兼容的快捷引用。</p>
 *
 * <h3>修改指南</h3>
 * <ul>
 *   <li>此类不注册新物品，实际物品在 {@link Hk3CircuitItems#registerDetailedCircuits()} 中注册</li>
 *   <li>如需更改每阶 canonical 形态，修改 {@code init()} 中各 {@link Hk3CircuitItems#getDetailedCircuit} 的第二个参数</li>
 *   <li>新增海渊 V 等更高级别：先在 Hk3CircuitItems.DETAILED_CIRCUIT_TIERS 中添加，再在此补充别名</li>
 *   <li>配方中可直接用 {@code AbyssCircuitItems.CIRCUIT_ABYSS_1.get()} 快捷引用</li>
 * </ul>
 *
 * @see Hk3CircuitItems#getDetailedCircuit(String, String) 实际数据来源
 */
public class AbyssCircuitItems {

    /** 海渊一·演算核心（canonical：abyss_1_processor） */
    public static RegistryObject<Item> CIRCUIT_ABYSS_1;
    /** 海渊二·演算矩阵（canonical：abyss_2_assembly） */
    public static RegistryObject<Item> CIRCUIT_ABYSS_2;
    /** 海渊三·智算中枢（canonical：abyss_3_computer） */
    public static RegistryObject<Item> CIRCUIT_ABYSS_3;
    /** 海渊四·统御主机（canonical：abyss_4_processor_mainframe） */
    public static RegistryObject<Item> CIRCUIT_ABYSS_4;

    /** 必须在 Hk3CircuitItems.register() 之后调用 */
    public static void init() {
        CIRCUIT_ABYSS_1 = Hk3CircuitItems.getDetailedCircuit("abyss_1", "processor");
        CIRCUIT_ABYSS_2 = Hk3CircuitItems.getDetailedCircuit("abyss_2", "assembly");
        CIRCUIT_ABYSS_3 = Hk3CircuitItems.getDetailedCircuit("abyss_3", "computer");
        CIRCUIT_ABYSS_4 = Hk3CircuitItems.getDetailedCircuit("abyss_4", "processor_mainframe");
    }
}
