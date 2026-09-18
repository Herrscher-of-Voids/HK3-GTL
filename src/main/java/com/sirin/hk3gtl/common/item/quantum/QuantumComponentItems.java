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
    public static RegistryObject<Item> ELECTRIC_MOTOR_QUANTUM_1;
    public static RegistryObject<Item> ELECTRIC_PISTON_QUANTUM_1;
    public static RegistryObject<Item> ELECTRIC_PUMP_QUANTUM_1;
    public static RegistryObject<Item> CONVEYOR_MODULE_QUANTUM_1;
    public static RegistryObject<Item> ROBOT_ARM_QUANTUM_1;
    public static RegistryObject<Item> FIELD_GENERATOR_QUANTUM_1;
    public static RegistryObject<Item> EMITTER_QUANTUM_1;
    public static RegistryObject<Item> SENSOR_QUANTUM_1;

    // ── 量子 II ──
    public static RegistryObject<Item> ELECTRIC_MOTOR_QUANTUM_2;
    public static RegistryObject<Item> ELECTRIC_PISTON_QUANTUM_2;
    public static RegistryObject<Item> ELECTRIC_PUMP_QUANTUM_2;
    public static RegistryObject<Item> CONVEYOR_MODULE_QUANTUM_2;
    public static RegistryObject<Item> ROBOT_ARM_QUANTUM_2;
    public static RegistryObject<Item> FIELD_GENERATOR_QUANTUM_2;
    public static RegistryObject<Item> EMITTER_QUANTUM_2;
    public static RegistryObject<Item> SENSOR_QUANTUM_2;

    // ── 量子 III ──
    public static RegistryObject<Item> ELECTRIC_MOTOR_QUANTUM_3;
    public static RegistryObject<Item> ELECTRIC_PISTON_QUANTUM_3;
    public static RegistryObject<Item> ELECTRIC_PUMP_QUANTUM_3;
    public static RegistryObject<Item> CONVEYOR_MODULE_QUANTUM_3;
    public static RegistryObject<Item> ROBOT_ARM_QUANTUM_3;
    public static RegistryObject<Item> FIELD_GENERATOR_QUANTUM_3;
    public static RegistryObject<Item> EMITTER_QUANTUM_3;
    public static RegistryObject<Item> SENSOR_QUANTUM_3;

    // ── 量子 IV ──
    public static RegistryObject<Item> ELECTRIC_MOTOR_QUANTUM_4;
    public static RegistryObject<Item> ELECTRIC_PISTON_QUANTUM_4;
    public static RegistryObject<Item> ELECTRIC_PUMP_QUANTUM_4;
    public static RegistryObject<Item> CONVEYOR_MODULE_QUANTUM_4;
    public static RegistryObject<Item> ROBOT_ARM_QUANTUM_4;
    public static RegistryObject<Item> FIELD_GENERATOR_QUANTUM_4;
    public static RegistryObject<Item> EMITTER_QUANTUM_4;
    public static RegistryObject<Item> SENSOR_QUANTUM_4;

    public static void register() {
        // 量子 I
        ELECTRIC_MOTOR_QUANTUM_1 = reg("electric_motor_quantum_1");
        ELECTRIC_PISTON_QUANTUM_1 = reg("electric_piston_quantum_1");
        ELECTRIC_PUMP_QUANTUM_1 = reg("electric_pump_quantum_1");
        CONVEYOR_MODULE_QUANTUM_1 = reg("conveyor_module_quantum_1");
        ROBOT_ARM_QUANTUM_1 = reg("robot_arm_quantum_1");
        FIELD_GENERATOR_QUANTUM_1 = reg("field_generator_quantum_1");
        EMITTER_QUANTUM_1 = reg("emitter_quantum_1");
        SENSOR_QUANTUM_1 = reg("sensor_quantum_1");

        // 量子 II
        ELECTRIC_MOTOR_QUANTUM_2 = reg("electric_motor_quantum_2");
        ELECTRIC_PISTON_QUANTUM_2 = reg("electric_piston_quantum_2");
        ELECTRIC_PUMP_QUANTUM_2 = reg("electric_pump_quantum_2");
        CONVEYOR_MODULE_QUANTUM_2 = reg("conveyor_module_quantum_2");
        ROBOT_ARM_QUANTUM_2 = reg("robot_arm_quantum_2");
        FIELD_GENERATOR_QUANTUM_2 = reg("field_generator_quantum_2");
        EMITTER_QUANTUM_2 = reg("emitter_quantum_2");
        SENSOR_QUANTUM_2 = reg("sensor_quantum_2");

        // 量子 III
        ELECTRIC_MOTOR_QUANTUM_3 = reg("electric_motor_quantum_3");
        ELECTRIC_PISTON_QUANTUM_3 = reg("electric_piston_quantum_3");
        ELECTRIC_PUMP_QUANTUM_3 = reg("electric_pump_quantum_3");
        CONVEYOR_MODULE_QUANTUM_3 = reg("conveyor_module_quantum_3");
        ROBOT_ARM_QUANTUM_3 = reg("robot_arm_quantum_3");
        FIELD_GENERATOR_QUANTUM_3 = reg("field_generator_quantum_3");
        EMITTER_QUANTUM_3 = reg("emitter_quantum_3");
        SENSOR_QUANTUM_3 = reg("sensor_quantum_3");

        // 量子 IV
        ELECTRIC_MOTOR_QUANTUM_4 = reg("electric_motor_quantum_4");
        ELECTRIC_PISTON_QUANTUM_4 = reg("electric_piston_quantum_4");
        ELECTRIC_PUMP_QUANTUM_4 = reg("electric_pump_quantum_4");
        CONVEYOR_MODULE_QUANTUM_4 = reg("conveyor_module_quantum_4");
        ROBOT_ARM_QUANTUM_4 = reg("robot_arm_quantum_4");
        FIELD_GENERATOR_QUANTUM_4 = reg("field_generator_quantum_4");
        EMITTER_QUANTUM_4 = reg("emitter_quantum_4");
        SENSOR_QUANTUM_4 = reg("sensor_quantum_4");
    }

    private static RegistryObject<Item> reg(String name) {
        return Hk3Items.ITEMS.register(name, () -> new Item(new Item.Properties()));
    }
}
