package com.sirin.hk3gtl.common.item.imaginary;



import com.sirin.hk3gtl.common.item.Hk3CircuitItems;
import net.minecraft.world.item.Item;
import net.minecraftforge.registries.RegistryObject;

/**
 * 虚数一~四正式电路 → {@link Hk3CircuitItems}（canonical 形态同 {@link com.sirin.hk3gtl.common.item.abyss.AbyssCircuitItems}）。
 * <p>不注册独立物品，仅为配方/研究代码提供快捷引用。</p>
 *
 * <h3>修改指南</h3>
 * <ul>
 *   <li>此类不注册新物品，实际物品在 {@link Hk3CircuitItems} 中注册</li>
 *   <li>每阶 canonical 形态见 {@code init()} 中第二个参数</li>
 *   <li>配方中可直接用 {@code ImaginaryCircuitItems.CIRCUIT_IMAGINARY_1.get()} 快捷引用</li>
 * </ul>
 *
 * @see Hk3CircuitItems#getDetailedCircuit(String, String) 实际数据来源
 */
public class ImaginaryCircuitItems {

    /** 虚数一·枝序芯元 */
    public static RegistryObject<Item> CIRCUIT_IMAGINARY_1;
    /** 虚数二·树冠集成体 */
    public static RegistryObject<Item> CIRCUIT_IMAGINARY_2;
    /** 虚数三·虚律运算枢 */
    public static RegistryObject<Item> CIRCUIT_IMAGINARY_3;
    /** 虚数四·虚序主脑 */
    public static RegistryObject<Item> CIRCUIT_IMAGINARY_4;

    /** 必须在 Hk3CircuitItems.register() 之后调用 */
    public static void init() {
        CIRCUIT_IMAGINARY_1 = Hk3CircuitItems.getDetailedCircuit("imaginary_1", "processor");
        CIRCUIT_IMAGINARY_2 = Hk3CircuitItems.getDetailedCircuit("imaginary_2", "assembly");
        CIRCUIT_IMAGINARY_3 = Hk3CircuitItems.getDetailedCircuit("imaginary_3", "computer");
        CIRCUIT_IMAGINARY_4 = Hk3CircuitItems.getDetailedCircuit("imaginary_4", "processor_mainframe");
    }
}
