package com.sirin.hk3gtl.common.item.abyss;


/**
 * 【文件职责】
 * - 注册或实现 AbyssComponentItems 物品行为。
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

/** 中文说明：该处说明已按当前代码行为整理。*/
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
public class AbyssComponentItems {

    // ── 海渊 I（入门级部件，基础机器使用） ──
    /** 海渊 I 电机：提供旋转动力的核心部件。 */
    public static RegistryObject<Item> ELECTRIC_MOTOR_HBV;
    /** 海渊 I 活塞：提供直线推进的核心部件。 */
    public static RegistryObject<Item> ELECTRIC_PISTON_HBV;
    /** 海渊 I 泵：液体 / 气体传输的核心部件。 */
    public static RegistryObject<Item> ELECTRIC_PUMP_HBV;
    /** 海渊 I 传送带模块：物品自动输送。 */
    public static RegistryObject<Item> CONVEYOR_MODULE_HBV;
    /** 海渊 I 机械臂：物品进出 IO 控制。 */
    public static RegistryObject<Item> ROBOT_ARM_HBV;
    /** 海渊 I 场发生器：能量场 / 粒子场基础组件。 */
    public static RegistryObject<Item> FIELD_GENERATOR_HBV;
    /** 海渊 I 发射器：辐射 / 射线类机器的核心。 */
    public static RegistryObject<Item> EMITTER_HBV;
    /** 海渊 I 传感器：检测 / 扫描类机器的核心。 */
    public static RegistryObject<Item> SENSOR_HBV;

    // ── 海渊 II（进阶级部件，含义同 I 级） ──
    public static RegistryObject<Item> ELECTRIC_MOTOR_HCV;
    public static RegistryObject<Item> ELECTRIC_PISTON_HCV;
    public static RegistryObject<Item> ELECTRIC_PUMP_HCV;
    public static RegistryObject<Item> CONVEYOR_MODULE_HCV;
    public static RegistryObject<Item> ROBOT_ARM_HCV;
    public static RegistryObject<Item> FIELD_GENERATOR_HCV;
    public static RegistryObject<Item> EMITTER_HCV;
    public static RegistryObject<Item> SENSOR_HCV;

    // ── 海渊 III（高阶级部件，含义同 I 级） ──
    public static RegistryObject<Item> ELECTRIC_MOTOR_HRV;
    public static RegistryObject<Item> ELECTRIC_PISTON_HRV;
    public static RegistryObject<Item> ELECTRIC_PUMP_HRV;
    public static RegistryObject<Item> CONVEYOR_MODULE_HRV;
    public static RegistryObject<Item> ROBOT_ARM_HRV;
    public static RegistryObject<Item> FIELD_GENERATOR_HRV;
    public static RegistryObject<Item> EMITTER_HRV;
    public static RegistryObject<Item> SENSOR_HRV;

    // ── 海渊 IV（顶级部件，含义同 I 级） ──
    public static RegistryObject<Item> ELECTRIC_MOTOR_HDV;
    public static RegistryObject<Item> ELECTRIC_PISTON_HDV;
    public static RegistryObject<Item> ELECTRIC_PUMP_HDV;
    public static RegistryObject<Item> CONVEYOR_MODULE_HDV;
    public static RegistryObject<Item> ROBOT_ARM_HDV;
    public static RegistryObject<Item> FIELD_GENERATOR_HDV;
    public static RegistryObject<Item> EMITTER_HDV;
    public static RegistryObject<Item> SENSOR_HDV;

    /**
     * 统一注册入口：在 {@link Hk3Items#ITEMS} 中注册全部 32 个部件。
     * 由 mod 主类在 DeferredRegister 注册阶段调用。
     */
    public static void register() {
        // 海渊 I
        ELECTRIC_MOTOR_HBV = reg("electric_motor_hbv");
        ELECTRIC_PISTON_HBV = reg("electric_piston_hbv");
        ELECTRIC_PUMP_HBV = reg("electric_pump_hbv");
        CONVEYOR_MODULE_HBV = reg("conveyor_module_hbv");
        ROBOT_ARM_HBV = reg("robot_arm_hbv");
        FIELD_GENERATOR_HBV = reg("field_generator_hbv");
        EMITTER_HBV = reg("emitter_hbv");
        SENSOR_HBV = reg("sensor_hbv");

        // 海渊 II
        ELECTRIC_MOTOR_HCV = reg("electric_motor_hcv");
        ELECTRIC_PISTON_HCV = reg("electric_piston_hcv");
        ELECTRIC_PUMP_HCV = reg("electric_pump_hcv");
        CONVEYOR_MODULE_HCV = reg("conveyor_module_hcv");
        ROBOT_ARM_HCV = reg("robot_arm_hcv");
        FIELD_GENERATOR_HCV = reg("field_generator_hcv");
        EMITTER_HCV = reg("emitter_hcv");
        SENSOR_HCV = reg("sensor_hcv");

        // 海渊 III
        ELECTRIC_MOTOR_HRV = reg("electric_motor_hrv");
        ELECTRIC_PISTON_HRV = reg("electric_piston_hrv");
        ELECTRIC_PUMP_HRV = reg("electric_pump_hrv");
        CONVEYOR_MODULE_HRV = reg("conveyor_module_hrv");
        ROBOT_ARM_HRV = reg("robot_arm_hrv");
        FIELD_GENERATOR_HRV = reg("field_generator_hrv");
        EMITTER_HRV = reg("emitter_hrv");
        SENSOR_HRV = reg("sensor_hrv");

        // 海渊 IV
        ELECTRIC_MOTOR_HDV = reg("electric_motor_hdv");
        ELECTRIC_PISTON_HDV = reg("electric_piston_hdv");
        ELECTRIC_PUMP_HDV = reg("electric_pump_hdv");
        CONVEYOR_MODULE_HDV = reg("conveyor_module_hdv");
        ROBOT_ARM_HDV = reg("robot_arm_hdv");
        FIELD_GENERATOR_HDV = reg("field_generator_hdv");
        EMITTER_HDV = reg("emitter_hdv");
        SENSOR_HDV = reg("sensor_hdv");
    }

    /** 中文说明：该处说明已按当前代码行为整理。*/
    private static RegistryObject<Item> reg(String name) {
        return Hk3Items.ITEMS.register(name, () -> new com.sirin.hk3gtl.common.item.Hk3ComponentItem(name));
    }
}
