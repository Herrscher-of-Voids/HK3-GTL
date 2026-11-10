package com.sirin.hk3gtl.common.item.imaginary;


/**
 * 【文件职责】
 * - 注册或实现 ImaginaryComponentItems 物品行为。
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
import com.sirin.hk3gtl.common.item.Hk3Items;
import net.minecraft.world.item.Item;
import net.minecraftforge.registries.RegistryObject;

/**
 * 虚数 I~IV 八大件（电机/活塞/泵/传送带/机械臂/场发生器/发射器/传感器）。
 * <p>每级 8 个，共 32 个物品。对应 GT 组件体系的虚数阶段扩展。</p>
 *
 * <h3>修改指南</h3>
 * <ul>
 *   <li>新增组件类型：在每级区域内添加字段 + 在 register() 对应位置调用 reg()</li>
 *   <li>注册ID格式：{@code <组件类型>_imaginary_<级别>}，如 electric_motor_imaginary_1</li>
 *   <li>贴图路径：{@code assets/hk3gtl/textures/item/<注册ID>.png}</li>
 *   <li>语言Key：{@code item.hk3gtl.<注册ID>}，需同步更新 zh_cn.json / en_us.json</li>
 *   <li>配方中通过 {@code ImaginaryComponentItems.ELECTRIC_MOTOR_IMAGINARY_1.get()} 引用</li>
 * </ul>
 *
 * @see AbyssComponentItems 海渊八大件（结构相同）
 * @see QuantumComponentItems 量子八大件（结构相同）
 * @see FinalityComponentItems 终焉八大件（结构相同）
 */
/**
 * 【变更记录 #1】2026-09-28 01:24:51（第 1 次编号备注 · 内测5修订92）
 * 删除：无，保留注册ID、字段和历史备注。
 * 新增：八大件共用的电压名称显示实现。
 * 修改：普通Item改为Hk3ComponentItem，显示当前电压缩写及其文字颜色。
 * 用途：统一部件命名；不改配方、属性或贴图，贴图电压配色留待负责人另审。
 */
/**
 * 【变更记录 #2】2026-09-30 02:17:47（第2次备注 · 内测5修订107）
 * 删除：本文件可执行代码中的旧电压键及常量引用，不保留旧键注册别名。
 * 新增：16档正式缩写作为唯一电压标识；逐文件映射见logs/voltage-keys-r107。
 * 修改：注册、配方、查询或标签引用按原tier序号一一迁移；数值、层级与资源内容保持原义。
 * 用途：避免显示名与实际注册键不一致；历史备注保留，旧存档不自动改写。
 */
public class ImaginaryComponentItems {

    // ── 虚数 I（电机/活塞/泵/传送带/机械臂/场发生器/发射器/传感器）──
    public static RegistryObject<Item> ELECTRIC_MOTOR_QSV;
    public static RegistryObject<Item> ELECTRIC_PISTON_QSV;
    public static RegistryObject<Item> ELECTRIC_PUMP_QSV;
    public static RegistryObject<Item> CONVEYOR_MODULE_QSV;
    public static RegistryObject<Item> ROBOT_ARM_QSV;
    public static RegistryObject<Item> FIELD_GENERATOR_QSV;
    public static RegistryObject<Item> EMITTER_QSV;
    public static RegistryObject<Item> SENSOR_QSV;

    // ── 虚数 II ──
    public static RegistryObject<Item> ELECTRIC_MOTOR_QCV;
    public static RegistryObject<Item> ELECTRIC_PISTON_QCV;
    public static RegistryObject<Item> ELECTRIC_PUMP_QCV;
    public static RegistryObject<Item> CONVEYOR_MODULE_QCV;
    public static RegistryObject<Item> ROBOT_ARM_QCV;
    public static RegistryObject<Item> FIELD_GENERATOR_QCV;
    public static RegistryObject<Item> EMITTER_QCV;
    public static RegistryObject<Item> SENSOR_QCV;

    // ── 虚数 III ──
    public static RegistryObject<Item> ELECTRIC_MOTOR_QEV;
    public static RegistryObject<Item> ELECTRIC_PISTON_QEV;
    public static RegistryObject<Item> ELECTRIC_PUMP_QEV;
    public static RegistryObject<Item> CONVEYOR_MODULE_QEV;
    public static RegistryObject<Item> ROBOT_ARM_QEV;
    public static RegistryObject<Item> FIELD_GENERATOR_QEV;
    public static RegistryObject<Item> EMITTER_QEV;
    public static RegistryObject<Item> SENSOR_QEV;

    // ── 虚数 IV ──
    public static RegistryObject<Item> ELECTRIC_MOTOR_QAV;
    public static RegistryObject<Item> ELECTRIC_PISTON_QAV;
    public static RegistryObject<Item> ELECTRIC_PUMP_QAV;
    public static RegistryObject<Item> CONVEYOR_MODULE_QAV;
    public static RegistryObject<Item> ROBOT_ARM_QAV;
    public static RegistryObject<Item> FIELD_GENERATOR_QAV;
    public static RegistryObject<Item> EMITTER_QAV;
    public static RegistryObject<Item> SENSOR_QAV;

    public static void register() {
        // 虚数 I
        ELECTRIC_MOTOR_QSV = reg("electric_motor_qsv");
        ELECTRIC_PISTON_QSV = reg("electric_piston_qsv");
        ELECTRIC_PUMP_QSV = reg("electric_pump_qsv");
        CONVEYOR_MODULE_QSV = reg("conveyor_module_qsv");
        ROBOT_ARM_QSV = reg("robot_arm_qsv");
        FIELD_GENERATOR_QSV = reg("field_generator_qsv");
        EMITTER_QSV = reg("emitter_qsv");
        SENSOR_QSV = reg("sensor_qsv");

        // 虚数 II
        ELECTRIC_MOTOR_QCV = reg("electric_motor_qcv");
        ELECTRIC_PISTON_QCV = reg("electric_piston_qcv");
        ELECTRIC_PUMP_QCV = reg("electric_pump_qcv");
        CONVEYOR_MODULE_QCV = reg("conveyor_module_qcv");
        ROBOT_ARM_QCV = reg("robot_arm_qcv");
        FIELD_GENERATOR_QCV = reg("field_generator_qcv");
        EMITTER_QCV = reg("emitter_qcv");
        SENSOR_QCV = reg("sensor_qcv");

        // 虚数 III
        ELECTRIC_MOTOR_QEV = reg("electric_motor_qev");
        ELECTRIC_PISTON_QEV = reg("electric_piston_qev");
        ELECTRIC_PUMP_QEV = reg("electric_pump_qev");
        CONVEYOR_MODULE_QEV = reg("conveyor_module_qev");
        ROBOT_ARM_QEV = reg("robot_arm_qev");
        FIELD_GENERATOR_QEV = reg("field_generator_qev");
        EMITTER_QEV = reg("emitter_qev");
        SENSOR_QEV = reg("sensor_qev");

        // 虚数 IV
        ELECTRIC_MOTOR_QAV = reg("electric_motor_qav");
        ELECTRIC_PISTON_QAV = reg("electric_piston_qav");
        ELECTRIC_PUMP_QAV = reg("electric_pump_qav");
        CONVEYOR_MODULE_QAV = reg("conveyor_module_qav");
        ROBOT_ARM_QAV = reg("robot_arm_qav");
        FIELD_GENERATOR_QAV = reg("field_generator_qav");
        EMITTER_QAV = reg("emitter_qav");
        SENSOR_QAV = reg("sensor_qav");
    }

    private static RegistryObject<Item> reg(String name) {
        return Hk3Items.ITEMS.register(name, () -> new com.sirin.hk3gtl.common.item.Hk3ComponentItem(name));
    }
}
