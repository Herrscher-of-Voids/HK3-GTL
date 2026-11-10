package com.sirin.hk3gtl.common.item.abyss;


/**
 * 【文件职责】
 * - 注册或实现 AbyssCircuitItems 物品行为。
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
 */
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
/**
 * 【变更记录 #1】2026-09-30 02:17:47（第1次备注 · 内测5修订107）
 * 删除：本文件可执行代码中的旧电压键及常量引用，不保留旧键注册别名。
 * 新增：16档正式缩写作为唯一电压标识；逐文件映射见logs/voltage-keys-r107。
 * 修改：注册、配方、查询或标签引用按原tier序号一一迁移；数值、层级与资源内容保持原义。
 * 用途：避免显示名与实际注册键不一致；历史备注保留，旧存档不自动改写。
 */
public class AbyssCircuitItems {

    /** 海渊一·演算核心（canonical：abyss_1_processor） */
    public static RegistryObject<Item> CIRCUIT_HBV;
    /** 海渊二·演算矩阵（canonical：abyss_2_assembly） */
    public static RegistryObject<Item> CIRCUIT_HCV;
    /** 海渊三·智算中枢（canonical：abyss_3_computer） */
    public static RegistryObject<Item> CIRCUIT_HRV;
    /** 海渊四·统御主机（canonical：abyss_4_processor_mainframe） */
    public static RegistryObject<Item> CIRCUIT_HDV;

    /** 必须在 Hk3CircuitItems.register() 之后调用 */
    public static void init() {
        CIRCUIT_HBV = Hk3CircuitItems.getDetailedCircuit("hbv", "processor");
        CIRCUIT_HCV = Hk3CircuitItems.getDetailedCircuit("hcv", "assembly");
        CIRCUIT_HRV = Hk3CircuitItems.getDetailedCircuit("hrv", "computer");
        CIRCUIT_HDV = Hk3CircuitItems.getDetailedCircuit("hdv", "processor_mainframe");
    }
}
