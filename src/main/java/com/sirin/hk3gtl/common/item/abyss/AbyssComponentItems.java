package com.sirin.hk3gtl.common.item.abyss;

import com.sirin.hk3gtl.common.item.Hk3Items;
import net.minecraft.world.item.Item;
import net.minecraftforge.registries.RegistryObject;

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

    private static RegistryObject<Item> reg(String name) {
        return Hk3Items.ITEMS.register(name, () -> new com.sirin.hk3gtl.common.item.Hk3ComponentItem(name));
    }
}
