package com.sirin.hk3gtl.common.item.imaginary;


/**
 * 【文件职责】
 * - 注册或实现 ImaginaryCircuitItems 物品行为。
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
/**
 * 【变更记录 #1】2026-09-30 02:17:47（第1次备注 · 内测5修订107）
 * 删除：本文件可执行代码中的旧电压键及常量引用，不保留旧键注册别名。
 * 新增：16档正式缩写作为唯一电压标识；逐文件映射见logs/voltage-keys-r107。
 * 修改：注册、配方、查询或标签引用按原tier序号一一迁移；数值、层级与资源内容保持原义。
 * 用途：避免显示名与实际注册键不一致；历史备注保留，旧存档不自动改写。
 */
public class ImaginaryCircuitItems {

    /** 虚数一·枝序芯元 */
    public static RegistryObject<Item> CIRCUIT_QSV;
    /** 虚数二·树冠集成体 */
    public static RegistryObject<Item> CIRCUIT_QCV;
    /** 虚数三·虚律运算枢 */
    public static RegistryObject<Item> CIRCUIT_QEV;
    /** 虚数四·虚序主脑 */
    public static RegistryObject<Item> CIRCUIT_QAV;

    /** 必须在 Hk3CircuitItems.register() 之后调用 */
    public static void init() {
        CIRCUIT_QSV = Hk3CircuitItems.getDetailedCircuit("qsv", "processor");
        CIRCUIT_QCV = Hk3CircuitItems.getDetailedCircuit("qcv", "assembly");
        CIRCUIT_QEV = Hk3CircuitItems.getDetailedCircuit("qev", "computer");
        CIRCUIT_QAV = Hk3CircuitItems.getDetailedCircuit("qav", "processor_mainframe");
    }
}
