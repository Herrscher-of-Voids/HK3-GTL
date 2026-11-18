package com.sirin.hk3gtl.common.item.finality;

import com.sirin.hk3gtl.common.item.Hk3CircuitItems;
import net.minecraft.world.item.Item;
import net.minecraftforge.registries.RegistryObject;

/**
 * 终焉一~四正式电路 → {@link Hk3CircuitItems}（canonical 形态同 {@link com.sirin.hk3gtl.common.item.abyss.AbyssCircuitItems}）。
 * <p>不注册独立物品，仅为配方/研究代码提供快捷引用。</p>
 *
 * <h3>修改指南</h3>
 * <ul>
 *   <li>此类不注册新物品，实际物品在 {@link Hk3CircuitItems} 中注册</li>
 *   <li>每阶 canonical 形态见 {@code init()} 中第二个参数</li>
 *   <li>配方中可直接用 {@code FinalityCircuitItems.CIRCUIT_FINALITY_1.get()} 快捷引用</li>
 * </ul>
 *
 * @see Hk3CircuitItems#getDetailedCircuit(String, String) 实际数据来源
 */
public class FinalityCircuitItems {

    /** 终焉一·终序判定核 */
    public static RegistryObject<Item> CIRCUIT_WFV;
    /** 终焉二·茧域集成阵 */
    public static RegistryObject<Item> CIRCUIT_WSV;
    /** 终焉三·审判运算体 */
    public static RegistryObject<Item> CIRCUIT_CIV;
    /** 终焉四·裁决主机 */
    public static RegistryObject<Item> CIRCUIT_CEV;

    /** 必须在 Hk3CircuitItems.register() 之后调用 */
    public static void init() {
        CIRCUIT_WFV = Hk3CircuitItems.getDetailedCircuit("wfv", "processor");
        CIRCUIT_WSV = Hk3CircuitItems.getDetailedCircuit("wsv", "assembly");
        CIRCUIT_CIV = Hk3CircuitItems.getDetailedCircuit("civ", "computer");
        CIRCUIT_CEV = Hk3CircuitItems.getDetailedCircuit("cev", "processor_mainframe");
    }
}
