package com.sirin.hk3gtl.common.item.abyss;



import com.sirin.hk3gtl.common.item.Hk3Items;
import net.minecraft.world.item.Item;
import net.minecraftforge.registries.RegistryObject;

/**
 * 海渊 I~IV 八大件（电机 / 活塞 / 泵 / 传送带 / 机械臂 / 场发生器 / 发射器 / 传感器）。
 *
 * <p>每级 8 个，共 4×8 = 32 个物品。命名规范：{@code <部件>_abyss_<等级>}。
 *
 * <h3>修改指南</h3>
 * <ul>
 *   <li>新增等级：同时补充对应 8 个字段 + {@link #register()} 中的注册调用</li>
 *   <li>贴图路径：{@code assets/hk3gtl/textures/item/abyss/<部件类型>/<注册ID>.png}</li>
 *   <li>语言 Key：{@code item.hk3gtl.<注册ID>}，需同步更新 zh_cn.json / en_us.json</li>
 *   <li>如需特殊属性（堆叠、稀有度），修改 {@link #reg(String)} 或改为独立的注册方法</li>
 *   <li>注册顺序不可依赖，字段保持 static 公开以便配方 / 研究系统引用</li>
 * </ul>
 */
public class AbyssComponentItems {

    // ── 海渊 I（入门级部件，基础机器使用） ──
    /** 海渊 I 电机：提供旋转动力的核心部件。 */
    public static RegistryObject<Item> ELECTRIC_MOTOR_ABYSS_1;
    /** 海渊 I 活塞：提供直线推进的核心部件。 */
    public static RegistryObject<Item> ELECTRIC_PISTON_ABYSS_1;
    /** 海渊 I 泵：液体 / 气体传输的核心部件。 */
    public static RegistryObject<Item> ELECTRIC_PUMP_ABYSS_1;
    /** 海渊 I 传送带模块：物品自动输送。 */
    public static RegistryObject<Item> CONVEYOR_MODULE_ABYSS_1;
    /** 海渊 I 机械臂：物品进出 IO 控制。 */
    public static RegistryObject<Item> ROBOT_ARM_ABYSS_1;
    /** 海渊 I 场发生器：能量场 / 粒子场基础组件。 */
    public static RegistryObject<Item> FIELD_GENERATOR_ABYSS_1;
    /** 海渊 I 发射器：辐射 / 射线类机器的核心。 */
    public static RegistryObject<Item> EMITTER_ABYSS_1;
    /** 海渊 I 传感器：检测 / 扫描类机器的核心。 */
    public static RegistryObject<Item> SENSOR_ABYSS_1;

    // ── 海渊 II（进阶级部件，含义同 I 级） ──
    public static RegistryObject<Item> ELECTRIC_MOTOR_ABYSS_2;
    public static RegistryObject<Item> ELECTRIC_PISTON_ABYSS_2;
    public static RegistryObject<Item> ELECTRIC_PUMP_ABYSS_2;
    public static RegistryObject<Item> CONVEYOR_MODULE_ABYSS_2;
    public static RegistryObject<Item> ROBOT_ARM_ABYSS_2;
    public static RegistryObject<Item> FIELD_GENERATOR_ABYSS_2;
    public static RegistryObject<Item> EMITTER_ABYSS_2;
    public static RegistryObject<Item> SENSOR_ABYSS_2;

    // ── 海渊 III（高阶级部件，含义同 I 级） ──
    public static RegistryObject<Item> ELECTRIC_MOTOR_ABYSS_3;
    public static RegistryObject<Item> ELECTRIC_PISTON_ABYSS_3;
    public static RegistryObject<Item> ELECTRIC_PUMP_ABYSS_3;
    public static RegistryObject<Item> CONVEYOR_MODULE_ABYSS_3;
    public static RegistryObject<Item> ROBOT_ARM_ABYSS_3;
    public static RegistryObject<Item> FIELD_GENERATOR_ABYSS_3;
    public static RegistryObject<Item> EMITTER_ABYSS_3;
    public static RegistryObject<Item> SENSOR_ABYSS_3;

    // ── 海渊 IV（顶级部件，含义同 I 级） ──
    public static RegistryObject<Item> ELECTRIC_MOTOR_ABYSS_4;
    public static RegistryObject<Item> ELECTRIC_PISTON_ABYSS_4;
    public static RegistryObject<Item> ELECTRIC_PUMP_ABYSS_4;
    public static RegistryObject<Item> CONVEYOR_MODULE_ABYSS_4;
    public static RegistryObject<Item> ROBOT_ARM_ABYSS_4;
    public static RegistryObject<Item> FIELD_GENERATOR_ABYSS_4;
    public static RegistryObject<Item> EMITTER_ABYSS_4;
    public static RegistryObject<Item> SENSOR_ABYSS_4;

    /**
     * 统一注册入口：在 {@link Hk3Items#ITEMS} 中注册全部 32 个部件。
     * 由 mod 主类在 DeferredRegister 注册阶段调用。
     */
    public static void register() {
        // 海渊 I
        ELECTRIC_MOTOR_ABYSS_1 = reg("electric_motor_abyss_1");
        ELECTRIC_PISTON_ABYSS_1 = reg("electric_piston_abyss_1");
        ELECTRIC_PUMP_ABYSS_1 = reg("electric_pump_abyss_1");
        CONVEYOR_MODULE_ABYSS_1 = reg("conveyor_module_abyss_1");
        ROBOT_ARM_ABYSS_1 = reg("robot_arm_abyss_1");
        FIELD_GENERATOR_ABYSS_1 = reg("field_generator_abyss_1");
        EMITTER_ABYSS_1 = reg("emitter_abyss_1");
        SENSOR_ABYSS_1 = reg("sensor_abyss_1");

        // 海渊 II
        ELECTRIC_MOTOR_ABYSS_2 = reg("electric_motor_abyss_2");
        ELECTRIC_PISTON_ABYSS_2 = reg("electric_piston_abyss_2");
        ELECTRIC_PUMP_ABYSS_2 = reg("electric_pump_abyss_2");
        CONVEYOR_MODULE_ABYSS_2 = reg("conveyor_module_abyss_2");
        ROBOT_ARM_ABYSS_2 = reg("robot_arm_abyss_2");
        FIELD_GENERATOR_ABYSS_2 = reg("field_generator_abyss_2");
        EMITTER_ABYSS_2 = reg("emitter_abyss_2");
        SENSOR_ABYSS_2 = reg("sensor_abyss_2");

        // 海渊 III
        ELECTRIC_MOTOR_ABYSS_3 = reg("electric_motor_abyss_3");
        ELECTRIC_PISTON_ABYSS_3 = reg("electric_piston_abyss_3");
        ELECTRIC_PUMP_ABYSS_3 = reg("electric_pump_abyss_3");
        CONVEYOR_MODULE_ABYSS_3 = reg("conveyor_module_abyss_3");
        ROBOT_ARM_ABYSS_3 = reg("robot_arm_abyss_3");
        FIELD_GENERATOR_ABYSS_3 = reg("field_generator_abyss_3");
        EMITTER_ABYSS_3 = reg("emitter_abyss_3");
        SENSOR_ABYSS_3 = reg("sensor_abyss_3");

        // 海渊 IV
        ELECTRIC_MOTOR_ABYSS_4 = reg("electric_motor_abyss_4");
        ELECTRIC_PISTON_ABYSS_4 = reg("electric_piston_abyss_4");
        ELECTRIC_PUMP_ABYSS_4 = reg("electric_pump_abyss_4");
        CONVEYOR_MODULE_ABYSS_4 = reg("conveyor_module_abyss_4");
        ROBOT_ARM_ABYSS_4 = reg("robot_arm_abyss_4");
        FIELD_GENERATOR_ABYSS_4 = reg("field_generator_abyss_4");
        EMITTER_ABYSS_4 = reg("emitter_abyss_4");
        SENSOR_ABYSS_4 = reg("sensor_abyss_4");
    }

    /**
     * 统一的物品注册工厂方法。
     * 所有部件均使用默认 Item.Properties，如需自定义堆叠 / 稀有度请改此方法或新增重载。
     */
    private static RegistryObject<Item> reg(String name) {
        return Hk3Items.ITEMS.register(name, () -> new Item(new Item.Properties()));
    }
}
