package com.sirin.hk3gtl.common.item.imaginary;

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
