package com.sirin.hk3gtl.common.item.finality;


/**
 * 【文件职责】
 * - 注册或实现 FinalityComponentItems 物品行为。
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
 * 终焉 I~IV 八大件（电机/活塞/泵/传送带/机械臂/场发生器/发射器/传感器）。
 * <p>每级 8 个，共 32 个物品。对应 GT 组件体系的终焉阶段扩展。</p>
 *
 * <h3>修改指南</h3>
 * <ul>
 *   <li>新增组件类型：在每级区域内添加字段 + 在 register() 对应位置调用 reg()</li>
 *   <li>注册ID格式：{@code <组件类型>_finality_<级别>}，如 electric_motor_finality_1</li>
 *   <li>贴图路径：{@code assets/hk3gtl/textures/item/<注册ID>.png}</li>
 *   <li>语言Key：{@code item.hk3gtl.<注册ID>}，需同步更新 zh_cn.json / en_us.json</li>
 *   <li>配方中通过 {@code FinalityComponentItems.ELECTRIC_MOTOR_FINALITY_1.get()} 引用</li>
 * </ul>
 *
 * @see AbyssComponentItems 海渊八大件（结构相同）
 * @see ImaginaryComponentItems 虚数八大件（结构相同）
 * @see QuantumComponentItems 量子八大件（结构相同）
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
public class FinalityComponentItems {

    // ── 终焉 I（电机/活塞/泵/传送带/机械臂/场发生器/发射器/传感器）──
    public static RegistryObject<Item> ELECTRIC_MOTOR_WFV;
    public static RegistryObject<Item> ELECTRIC_PISTON_WFV;
    public static RegistryObject<Item> ELECTRIC_PUMP_WFV;
    public static RegistryObject<Item> CONVEYOR_MODULE_WFV;
    public static RegistryObject<Item> ROBOT_ARM_WFV;
    public static RegistryObject<Item> FIELD_GENERATOR_WFV;
    public static RegistryObject<Item> EMITTER_WFV;
    public static RegistryObject<Item> SENSOR_WFV;

    // ── 终焉 II ──
    public static RegistryObject<Item> ELECTRIC_MOTOR_WSV;
    public static RegistryObject<Item> ELECTRIC_PISTON_WSV;
    public static RegistryObject<Item> ELECTRIC_PUMP_WSV;
    public static RegistryObject<Item> CONVEYOR_MODULE_WSV;
    public static RegistryObject<Item> ROBOT_ARM_WSV;
    public static RegistryObject<Item> FIELD_GENERATOR_WSV;
    public static RegistryObject<Item> EMITTER_WSV;
    public static RegistryObject<Item> SENSOR_WSV;

    // ── 终焉 III ──
    public static RegistryObject<Item> ELECTRIC_MOTOR_CIV;
    public static RegistryObject<Item> ELECTRIC_PISTON_CIV;
    public static RegistryObject<Item> ELECTRIC_PUMP_CIV;
    public static RegistryObject<Item> CONVEYOR_MODULE_CIV;
    public static RegistryObject<Item> ROBOT_ARM_CIV;
    public static RegistryObject<Item> FIELD_GENERATOR_CIV;
    public static RegistryObject<Item> EMITTER_CIV;
    public static RegistryObject<Item> SENSOR_CIV;

    // ── 终焉 IV ──
    public static RegistryObject<Item> ELECTRIC_MOTOR_CEV;
    public static RegistryObject<Item> ELECTRIC_PISTON_CEV;
    public static RegistryObject<Item> ELECTRIC_PUMP_CEV;
    public static RegistryObject<Item> CONVEYOR_MODULE_CEV;
    public static RegistryObject<Item> ROBOT_ARM_CEV;
    public static RegistryObject<Item> FIELD_GENERATOR_CEV;
    public static RegistryObject<Item> EMITTER_CEV;
    public static RegistryObject<Item> SENSOR_CEV;

    public static void register() {
        // 终焉 I
        ELECTRIC_MOTOR_WFV = reg("electric_motor_wfv");
        ELECTRIC_PISTON_WFV = reg("electric_piston_wfv");
        ELECTRIC_PUMP_WFV = reg("electric_pump_wfv");
        CONVEYOR_MODULE_WFV = reg("conveyor_module_wfv");
        ROBOT_ARM_WFV = reg("robot_arm_wfv");
        FIELD_GENERATOR_WFV = reg("field_generator_wfv");
        EMITTER_WFV = reg("emitter_wfv");
        SENSOR_WFV = reg("sensor_wfv");

        // 终焉 II
        ELECTRIC_MOTOR_WSV = reg("electric_motor_wsv");
        ELECTRIC_PISTON_WSV = reg("electric_piston_wsv");
        ELECTRIC_PUMP_WSV = reg("electric_pump_wsv");
        CONVEYOR_MODULE_WSV = reg("conveyor_module_wsv");
        ROBOT_ARM_WSV = reg("robot_arm_wsv");
        FIELD_GENERATOR_WSV = reg("field_generator_wsv");
        EMITTER_WSV = reg("emitter_wsv");
        SENSOR_WSV = reg("sensor_wsv");

        // 终焉 III
        ELECTRIC_MOTOR_CIV = reg("electric_motor_civ");
        ELECTRIC_PISTON_CIV = reg("electric_piston_civ");
        ELECTRIC_PUMP_CIV = reg("electric_pump_civ");
        CONVEYOR_MODULE_CIV = reg("conveyor_module_civ");
        ROBOT_ARM_CIV = reg("robot_arm_civ");
        FIELD_GENERATOR_CIV = reg("field_generator_civ");
        EMITTER_CIV = reg("emitter_civ");
        SENSOR_CIV = reg("sensor_civ");

        // 终焉 IV
        ELECTRIC_MOTOR_CEV = reg("electric_motor_cev");
        ELECTRIC_PISTON_CEV = reg("electric_piston_cev");
        ELECTRIC_PUMP_CEV = reg("electric_pump_cev");
        CONVEYOR_MODULE_CEV = reg("conveyor_module_cev");
        ROBOT_ARM_CEV = reg("robot_arm_cev");
        FIELD_GENERATOR_CEV = reg("field_generator_cev");
        EMITTER_CEV = reg("emitter_cev");
        SENSOR_CEV = reg("sensor_cev");
    }

    private static RegistryObject<Item> reg(String name) {
        return Hk3Items.ITEMS.register(name, () -> new com.sirin.hk3gtl.common.item.Hk3ComponentItem(name));
    }
}
