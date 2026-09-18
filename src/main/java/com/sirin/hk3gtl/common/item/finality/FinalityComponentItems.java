package com.sirin.hk3gtl.common.item.finality;



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
public class FinalityComponentItems {

    // ── 终焉 I（电机/活塞/泵/传送带/机械臂/场发生器/发射器/传感器）──
    public static RegistryObject<Item> ELECTRIC_MOTOR_FINALITY_1;
    public static RegistryObject<Item> ELECTRIC_PISTON_FINALITY_1;
    public static RegistryObject<Item> ELECTRIC_PUMP_FINALITY_1;
    public static RegistryObject<Item> CONVEYOR_MODULE_FINALITY_1;
    public static RegistryObject<Item> ROBOT_ARM_FINALITY_1;
    public static RegistryObject<Item> FIELD_GENERATOR_FINALITY_1;
    public static RegistryObject<Item> EMITTER_FINALITY_1;
    public static RegistryObject<Item> SENSOR_FINALITY_1;

    // ── 终焉 II ──
    public static RegistryObject<Item> ELECTRIC_MOTOR_FINALITY_2;
    public static RegistryObject<Item> ELECTRIC_PISTON_FINALITY_2;
    public static RegistryObject<Item> ELECTRIC_PUMP_FINALITY_2;
    public static RegistryObject<Item> CONVEYOR_MODULE_FINALITY_2;
    public static RegistryObject<Item> ROBOT_ARM_FINALITY_2;
    public static RegistryObject<Item> FIELD_GENERATOR_FINALITY_2;
    public static RegistryObject<Item> EMITTER_FINALITY_2;
    public static RegistryObject<Item> SENSOR_FINALITY_2;

    // ── 终焉 III ──
    public static RegistryObject<Item> ELECTRIC_MOTOR_FINALITY_3;
    public static RegistryObject<Item> ELECTRIC_PISTON_FINALITY_3;
    public static RegistryObject<Item> ELECTRIC_PUMP_FINALITY_3;
    public static RegistryObject<Item> CONVEYOR_MODULE_FINALITY_3;
    public static RegistryObject<Item> ROBOT_ARM_FINALITY_3;
    public static RegistryObject<Item> FIELD_GENERATOR_FINALITY_3;
    public static RegistryObject<Item> EMITTER_FINALITY_3;
    public static RegistryObject<Item> SENSOR_FINALITY_3;

    // ── 终焉 IV ──
    public static RegistryObject<Item> ELECTRIC_MOTOR_FINALITY_4;
    public static RegistryObject<Item> ELECTRIC_PISTON_FINALITY_4;
    public static RegistryObject<Item> ELECTRIC_PUMP_FINALITY_4;
    public static RegistryObject<Item> CONVEYOR_MODULE_FINALITY_4;
    public static RegistryObject<Item> ROBOT_ARM_FINALITY_4;
    public static RegistryObject<Item> FIELD_GENERATOR_FINALITY_4;
    public static RegistryObject<Item> EMITTER_FINALITY_4;
    public static RegistryObject<Item> SENSOR_FINALITY_4;

    public static void register() {
        // 终焉 I
        ELECTRIC_MOTOR_FINALITY_1 = reg("electric_motor_finality_1");
        ELECTRIC_PISTON_FINALITY_1 = reg("electric_piston_finality_1");
        ELECTRIC_PUMP_FINALITY_1 = reg("electric_pump_finality_1");
        CONVEYOR_MODULE_FINALITY_1 = reg("conveyor_module_finality_1");
        ROBOT_ARM_FINALITY_1 = reg("robot_arm_finality_1");
        FIELD_GENERATOR_FINALITY_1 = reg("field_generator_finality_1");
        EMITTER_FINALITY_1 = reg("emitter_finality_1");
        SENSOR_FINALITY_1 = reg("sensor_finality_1");

        // 终焉 II
        ELECTRIC_MOTOR_FINALITY_2 = reg("electric_motor_finality_2");
        ELECTRIC_PISTON_FINALITY_2 = reg("electric_piston_finality_2");
        ELECTRIC_PUMP_FINALITY_2 = reg("electric_pump_finality_2");
        CONVEYOR_MODULE_FINALITY_2 = reg("conveyor_module_finality_2");
        ROBOT_ARM_FINALITY_2 = reg("robot_arm_finality_2");
        FIELD_GENERATOR_FINALITY_2 = reg("field_generator_finality_2");
        EMITTER_FINALITY_2 = reg("emitter_finality_2");
        SENSOR_FINALITY_2 = reg("sensor_finality_2");

        // 终焉 III
        ELECTRIC_MOTOR_FINALITY_3 = reg("electric_motor_finality_3");
        ELECTRIC_PISTON_FINALITY_3 = reg("electric_piston_finality_3");
        ELECTRIC_PUMP_FINALITY_3 = reg("electric_pump_finality_3");
        CONVEYOR_MODULE_FINALITY_3 = reg("conveyor_module_finality_3");
        ROBOT_ARM_FINALITY_3 = reg("robot_arm_finality_3");
        FIELD_GENERATOR_FINALITY_3 = reg("field_generator_finality_3");
        EMITTER_FINALITY_3 = reg("emitter_finality_3");
        SENSOR_FINALITY_3 = reg("sensor_finality_3");

        // 终焉 IV
        ELECTRIC_MOTOR_FINALITY_4 = reg("electric_motor_finality_4");
        ELECTRIC_PISTON_FINALITY_4 = reg("electric_piston_finality_4");
        ELECTRIC_PUMP_FINALITY_4 = reg("electric_pump_finality_4");
        CONVEYOR_MODULE_FINALITY_4 = reg("conveyor_module_finality_4");
        ROBOT_ARM_FINALITY_4 = reg("robot_arm_finality_4");
        FIELD_GENERATOR_FINALITY_4 = reg("field_generator_finality_4");
        EMITTER_FINALITY_4 = reg("emitter_finality_4");
        SENSOR_FINALITY_4 = reg("sensor_finality_4");
    }

    private static RegistryObject<Item> reg(String name) {
        return Hk3Items.ITEMS.register(name, () -> new Item(new Item.Properties()));
    }
}
