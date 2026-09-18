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
    public static RegistryObject<Item> ELECTRIC_MOTOR_IMAGINARY_1;
    public static RegistryObject<Item> ELECTRIC_PISTON_IMAGINARY_1;
    public static RegistryObject<Item> ELECTRIC_PUMP_IMAGINARY_1;
    public static RegistryObject<Item> CONVEYOR_MODULE_IMAGINARY_1;
    public static RegistryObject<Item> ROBOT_ARM_IMAGINARY_1;
    public static RegistryObject<Item> FIELD_GENERATOR_IMAGINARY_1;
    public static RegistryObject<Item> EMITTER_IMAGINARY_1;
    public static RegistryObject<Item> SENSOR_IMAGINARY_1;

    // ── 虚数 II ──
    public static RegistryObject<Item> ELECTRIC_MOTOR_IMAGINARY_2;
    public static RegistryObject<Item> ELECTRIC_PISTON_IMAGINARY_2;
    public static RegistryObject<Item> ELECTRIC_PUMP_IMAGINARY_2;
    public static RegistryObject<Item> CONVEYOR_MODULE_IMAGINARY_2;
    public static RegistryObject<Item> ROBOT_ARM_IMAGINARY_2;
    public static RegistryObject<Item> FIELD_GENERATOR_IMAGINARY_2;
    public static RegistryObject<Item> EMITTER_IMAGINARY_2;
    public static RegistryObject<Item> SENSOR_IMAGINARY_2;

    // ── 虚数 III ──
    public static RegistryObject<Item> ELECTRIC_MOTOR_IMAGINARY_3;
    public static RegistryObject<Item> ELECTRIC_PISTON_IMAGINARY_3;
    public static RegistryObject<Item> ELECTRIC_PUMP_IMAGINARY_3;
    public static RegistryObject<Item> CONVEYOR_MODULE_IMAGINARY_3;
    public static RegistryObject<Item> ROBOT_ARM_IMAGINARY_3;
    public static RegistryObject<Item> FIELD_GENERATOR_IMAGINARY_3;
    public static RegistryObject<Item> EMITTER_IMAGINARY_3;
    public static RegistryObject<Item> SENSOR_IMAGINARY_3;

    // ── 虚数 IV ──
    public static RegistryObject<Item> ELECTRIC_MOTOR_IMAGINARY_4;
    public static RegistryObject<Item> ELECTRIC_PISTON_IMAGINARY_4;
    public static RegistryObject<Item> ELECTRIC_PUMP_IMAGINARY_4;
    public static RegistryObject<Item> CONVEYOR_MODULE_IMAGINARY_4;
    public static RegistryObject<Item> ROBOT_ARM_IMAGINARY_4;
    public static RegistryObject<Item> FIELD_GENERATOR_IMAGINARY_4;
    public static RegistryObject<Item> EMITTER_IMAGINARY_4;
    public static RegistryObject<Item> SENSOR_IMAGINARY_4;

    public static void register() {
        // 虚数 I
        ELECTRIC_MOTOR_IMAGINARY_1 = reg("electric_motor_imaginary_1");
        ELECTRIC_PISTON_IMAGINARY_1 = reg("electric_piston_imaginary_1");
        ELECTRIC_PUMP_IMAGINARY_1 = reg("electric_pump_imaginary_1");
        CONVEYOR_MODULE_IMAGINARY_1 = reg("conveyor_module_imaginary_1");
        ROBOT_ARM_IMAGINARY_1 = reg("robot_arm_imaginary_1");
        FIELD_GENERATOR_IMAGINARY_1 = reg("field_generator_imaginary_1");
        EMITTER_IMAGINARY_1 = reg("emitter_imaginary_1");
        SENSOR_IMAGINARY_1 = reg("sensor_imaginary_1");

        // 虚数 II
        ELECTRIC_MOTOR_IMAGINARY_2 = reg("electric_motor_imaginary_2");
        ELECTRIC_PISTON_IMAGINARY_2 = reg("electric_piston_imaginary_2");
        ELECTRIC_PUMP_IMAGINARY_2 = reg("electric_pump_imaginary_2");
        CONVEYOR_MODULE_IMAGINARY_2 = reg("conveyor_module_imaginary_2");
        ROBOT_ARM_IMAGINARY_2 = reg("robot_arm_imaginary_2");
        FIELD_GENERATOR_IMAGINARY_2 = reg("field_generator_imaginary_2");
        EMITTER_IMAGINARY_2 = reg("emitter_imaginary_2");
        SENSOR_IMAGINARY_2 = reg("sensor_imaginary_2");

        // 虚数 III
        ELECTRIC_MOTOR_IMAGINARY_3 = reg("electric_motor_imaginary_3");
        ELECTRIC_PISTON_IMAGINARY_3 = reg("electric_piston_imaginary_3");
        ELECTRIC_PUMP_IMAGINARY_3 = reg("electric_pump_imaginary_3");
        CONVEYOR_MODULE_IMAGINARY_3 = reg("conveyor_module_imaginary_3");
        ROBOT_ARM_IMAGINARY_3 = reg("robot_arm_imaginary_3");
        FIELD_GENERATOR_IMAGINARY_3 = reg("field_generator_imaginary_3");
        EMITTER_IMAGINARY_3 = reg("emitter_imaginary_3");
        SENSOR_IMAGINARY_3 = reg("sensor_imaginary_3");

        // 虚数 IV
        ELECTRIC_MOTOR_IMAGINARY_4 = reg("electric_motor_imaginary_4");
        ELECTRIC_PISTON_IMAGINARY_4 = reg("electric_piston_imaginary_4");
        ELECTRIC_PUMP_IMAGINARY_4 = reg("electric_pump_imaginary_4");
        CONVEYOR_MODULE_IMAGINARY_4 = reg("conveyor_module_imaginary_4");
        ROBOT_ARM_IMAGINARY_4 = reg("robot_arm_imaginary_4");
        FIELD_GENERATOR_IMAGINARY_4 = reg("field_generator_imaginary_4");
        EMITTER_IMAGINARY_4 = reg("emitter_imaginary_4");
        SENSOR_IMAGINARY_4 = reg("sensor_imaginary_4");
    }

    private static RegistryObject<Item> reg(String name) {
        return Hk3Items.ITEMS.register(name, () -> new Item(new Item.Properties()));
    }
}
