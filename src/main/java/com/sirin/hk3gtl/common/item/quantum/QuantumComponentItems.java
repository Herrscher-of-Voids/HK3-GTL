package com.sirin.hk3gtl.common.item.quantum;

import com.sirin.hk3gtl.common.item.Hk3Items;
import net.minecraft.world.item.Item;
import net.minecraftforge.registries.RegistryObject;

/**
 * 量子 I~IV 八大件（电机/活塞/泵/传送带/机械臂/场发生器/发射器/传感器）。
 * <p>每级 8 个，共 32 个物品。对应 GT 组件体系的量子阶段扩展。</p>
 *
 * <h3>修改指南</h3>
 * <ul>
 *   <li>新增组件类型：在每级区域内添加字段 + 在 register() 对应位置调用 reg()</li>
 *   <li>注册ID格式：{@code <组件类型>_quantum_<级别>}，如 electric_motor_quantum_1</li>
 *   <li>贴图路径：{@code assets/hk3gtl/textures/item/<注册ID>.png}</li>
 *   <li>语言Key：{@code item.hk3gtl.<注册ID>}，需同步更新 zh_cn.json / en_us.json</li>
 *   <li>配方中通过 {@code QuantumComponentItems.ELECTRIC_MOTOR_QUANTUM_1.get()} 引用</li>
 * </ul>
 *
 * @see AbyssComponentItems 海渊八大件（结构相同）
 * @see ImaginaryComponentItems 虚数八大件（结构相同）
 * @see FinalityComponentItems 终焉八大件（结构相同）
 */
public class QuantumComponentItems {

    // ── 量子 I（电机/活塞/泵/传送带/机械臂/场发生器/发射器/传感器）──
    public static RegistryObject<Item> ELECTRIC_MOTOR_IMV;
    public static RegistryObject<Item> ELECTRIC_PISTON_IMV;
    public static RegistryObject<Item> ELECTRIC_PUMP_IMV;
    public static RegistryObject<Item> CONVEYOR_MODULE_IMV;
    public static RegistryObject<Item> ROBOT_ARM_IMV;
    public static RegistryObject<Item> FIELD_GENERATOR_IMV;
    public static RegistryObject<Item> EMITTER_IMV;
    public static RegistryObject<Item> SENSOR_IMV;

    // ── 量子 II ──
    public static RegistryObject<Item> ELECTRIC_MOTOR_ICV;
    public static RegistryObject<Item> ELECTRIC_PISTON_ICV;
    public static RegistryObject<Item> ELECTRIC_PUMP_ICV;
    public static RegistryObject<Item> CONVEYOR_MODULE_ICV;
    public static RegistryObject<Item> ROBOT_ARM_ICV;
    public static RegistryObject<Item> FIELD_GENERATOR_ICV;
    public static RegistryObject<Item> EMITTER_ICV;
    public static RegistryObject<Item> SENSOR_ICV;

    // ── 量子 III ──
    public static RegistryObject<Item> ELECTRIC_MOTOR_IRV;
    public static RegistryObject<Item> ELECTRIC_PISTON_IRV;
    public static RegistryObject<Item> ELECTRIC_PUMP_IRV;
    public static RegistryObject<Item> CONVEYOR_MODULE_IRV;
    public static RegistryObject<Item> ROBOT_ARM_IRV;
    public static RegistryObject<Item> FIELD_GENERATOR_IRV;
    public static RegistryObject<Item> EMITTER_IRV;
    public static RegistryObject<Item> SENSOR_IRV;

    // ── 量子 IV ──
    public static RegistryObject<Item> ELECTRIC_MOTOR_IWV;
    public static RegistryObject<Item> ELECTRIC_PISTON_IWV;
    public static RegistryObject<Item> ELECTRIC_PUMP_IWV;
    public static RegistryObject<Item> CONVEYOR_MODULE_IWV;
    public static RegistryObject<Item> ROBOT_ARM_IWV;
    public static RegistryObject<Item> FIELD_GENERATOR_IWV;
    public static RegistryObject<Item> EMITTER_IWV;
    public static RegistryObject<Item> SENSOR_IWV;

    public static void register() {
        // 量子 I
        ELECTRIC_MOTOR_IMV = reg("electric_motor_imv");
        ELECTRIC_PISTON_IMV = reg("electric_piston_imv");
        ELECTRIC_PUMP_IMV = reg("electric_pump_imv");
        CONVEYOR_MODULE_IMV = reg("conveyor_module_imv");
        ROBOT_ARM_IMV = reg("robot_arm_imv");
        FIELD_GENERATOR_IMV = reg("field_generator_imv");
        EMITTER_IMV = reg("emitter_imv");
        SENSOR_IMV = reg("sensor_imv");

        // 量子 II
        ELECTRIC_MOTOR_ICV = reg("electric_motor_icv");
        ELECTRIC_PISTON_ICV = reg("electric_piston_icv");
        ELECTRIC_PUMP_ICV = reg("electric_pump_icv");
        CONVEYOR_MODULE_ICV = reg("conveyor_module_icv");
        ROBOT_ARM_ICV = reg("robot_arm_icv");
        FIELD_GENERATOR_ICV = reg("field_generator_icv");
        EMITTER_ICV = reg("emitter_icv");
        SENSOR_ICV = reg("sensor_icv");

        // 量子 III
        ELECTRIC_MOTOR_IRV = reg("electric_motor_irv");
        ELECTRIC_PISTON_IRV = reg("electric_piston_irv");
        ELECTRIC_PUMP_IRV = reg("electric_pump_irv");
        CONVEYOR_MODULE_IRV = reg("conveyor_module_irv");
        ROBOT_ARM_IRV = reg("robot_arm_irv");
        FIELD_GENERATOR_IRV = reg("field_generator_irv");
        EMITTER_IRV = reg("emitter_irv");
        SENSOR_IRV = reg("sensor_irv");

        // 量子 IV
        ELECTRIC_MOTOR_IWV = reg("electric_motor_iwv");
        ELECTRIC_PISTON_IWV = reg("electric_piston_iwv");
        ELECTRIC_PUMP_IWV = reg("electric_pump_iwv");
        CONVEYOR_MODULE_IWV = reg("conveyor_module_iwv");
        ROBOT_ARM_IWV = reg("robot_arm_iwv");
        FIELD_GENERATOR_IWV = reg("field_generator_iwv");
        EMITTER_IWV = reg("emitter_iwv");
        SENSOR_IWV = reg("sensor_iwv");
    }

    private static RegistryObject<Item> reg(String name) {
        return Hk3Items.ITEMS.register(name, () -> new com.sirin.hk3gtl.common.item.Hk3ComponentItem(name));
    }
}
