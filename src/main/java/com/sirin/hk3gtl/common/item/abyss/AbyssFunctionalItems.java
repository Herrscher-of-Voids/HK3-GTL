package com.sirin.hk3gtl.common.item.abyss;


/**
 * 【文件职责】
 * - 注册或实现 AbyssFunctionalItems 物品行为。
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
public class AbyssFunctionalItems {

    // ── 前文明 / 数据类 ──
    /** 虚空万藏 — 前文明遗物，唯一物品（stacksTo=1） */
    public static RegistryObject<Item> ARTIFACT_VOID_ARCHIVES;
    /** 前文明数据碎片 — 研究系统提交材料 */
    public static RegistryObject<Item> DATA_PRECIVILIZATION_FRAGMENT;

    // ── 功能性中间件（用于多方块机器合成）──
    /** 海渊能量调制器 — 能量系统核心组件 */
    public static RegistryObject<Item> ABYSS_ENERGY_MODULATOR;
    /** 海渊数据核心 — 数据处理核心 */
    public static RegistryObject<Item> ABYSS_DATA_CORE;
    /** 海渊稳定框架 — 结构稳定性组件 */
    public static RegistryObject<Item> ABYSS_STABLE_FRAME;
    /** 海渊反应堆核心 — 高级反应堆组件 */
    public static RegistryObject<Item> ABYSS_REACTOR_CORE;
    /** 海渊测量阵列 — 精密测量组件 */
    public static RegistryObject<Item> ABYSS_MEASUREMENT_ARRAY;
    /** 反应堆稳定器 — 反应堆安全组件 */
    public static RegistryObject<Item> REACTOR_STABILIZER;

    public static void register() {
        ARTIFACT_VOID_ARCHIVES = Hk3Items.ITEMS.register("artifact_void_archives",
                () -> new Item(new Item.Properties().stacksTo(1)));

        DATA_PRECIVILIZATION_FRAGMENT = Hk3Items.ITEMS.register("data_precivilization_fragment",
                () -> new Item(new Item.Properties()));

        ABYSS_ENERGY_MODULATOR = Hk3Items.ITEMS.register("abyss_energy_modulator",
                () -> new Item(new Item.Properties()));

        ABYSS_DATA_CORE = Hk3Items.ITEMS.register("abyss_data_core",
                () -> new Item(new Item.Properties()));

        ABYSS_STABLE_FRAME = Hk3Items.ITEMS.register("abyss_stable_frame",
                () -> new Item(new Item.Properties()));

        ABYSS_REACTOR_CORE = Hk3Items.ITEMS.register("abyss_reactor_core",
                () -> new Item(new Item.Properties()));

        ABYSS_MEASUREMENT_ARRAY = Hk3Items.ITEMS.register("abyss_measurement_array",
                () -> new Item(new Item.Properties()));

        REACTOR_STABILIZER = Hk3Items.ITEMS.register("reactor_stabilizer",
                () -> new Item(new Item.Properties()));
    }
}
