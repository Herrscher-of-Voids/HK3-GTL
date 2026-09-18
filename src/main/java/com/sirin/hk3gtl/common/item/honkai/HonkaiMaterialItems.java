package com.sirin.hk3gtl.common.item.honkai;



import com.sirin.hk3gtl.common.item.Hk3Items;
import net.minecraft.world.item.Item;
import net.minecraftforge.registries.RegistryObject;

/**
 * 崩坏能体系材料物品注册。包括崩坏能加工链、虚数核心、特殊合金、P2研究提交物等。
 *
 * <h3>修改指南</h3>
 * <ul>
 *   <li>新增物品：声明 RegistryObject 字段 → 在 {@link #register()} 中注册</li>
 *   <li>修改堆叠数：在 {@code new Item.Properties()} 后链式调用 {@code .stacksTo(N)}</li>
 *   <li>贴图路径：{@code assets/hk3gtl/textures/item/<注册ID>.png}</li>
 *   <li>语言Key：{@code item.hk3gtl.<注册ID>}，需同步更新 zh_cn.json / en_us.json</li>
 *   <li>配方引用：在 Hk3RecipeAdder 中通过 {@code HonkaiMaterialItems.XXX.get()} 引用</li>
 * </ul>
 */
public class HonkaiMaterialItems {

    // ── 崩坏能加工链（从低级到高级）──
    /** 原始崩坏粒子 — 崩坏能加工链起始原料 */
    public static RegistryObject<Item> RAW_HONKAI_PARTICLE;
    /** 崩坏能结晶 — 初级能量载体 */
    public static RegistryObject<Item> HONKAI_ENERGY_CRYSTAL;
    /** 稳定化崩坏结晶 — 经稳定处理的中级载体 */
    public static RegistryObject<Item> STABILIZED_HONKAI_CRYSTAL;
    /** 压缩崩坏核心 — 高密度能量单元 */
    public static RegistryObject<Item> COMPRESSED_HONKAI_CORE;
    /** 崩坏燃料棒 — 反应堆燃料 */
    public static RegistryObject<Item> HONKAI_FUEL_ROD;
    /** 致密崩坏燃料棒 — 高效反应堆燃料 */
    public static RegistryObject<Item> DENSE_HONKAI_FUEL_ROD;
    /** 崩坏抑制剂 — 控制崩坏反应的稳定剂 */
    public static RegistryObject<Item> HONKAI_SUPPRESSANT;
    /** 凝视缓冲单元 — 信号处理组件 */
    public static RegistryObject<Item> GAZE_BUFFER_UNIT;
    /** 高级凝视缓冲单元 — 高级信号处理组件 */
    public static RegistryObject<Item> ADVANCED_GAZE_BUFFER_UNIT;

    // ── 虚数核心 ──
    /** 天命虚数核心 — 天命阵营特有核心 */
    public static RegistryObject<Item> SCHICKSAL_IMAGINARY_CORE;
    /** 逆熵虚数核心 — 逆熵阵营特有核心 */
    public static RegistryObject<Item> ANTI_ENTROPY_IMAGINARY_CORE;

    // ── 特殊合金与组件 ──
    /** 流体合金 — 特殊合金中间产物 */
    public static RegistryObject<Item> FLUID_ALLOY;
    /** 流体合金块 — 大批量流体合金 */
    public static RegistryObject<Item> FLUID_ALLOY_BLOCK;
    /** 纳米陶瓷 — 耐高温结构材料 */
    public static RegistryObject<Item> NANO_CERAMIC;
    /** 相位转移镜 — 虚数能量操控组件 */
    public static RegistryObject<Item> PHASE_TRANSFER_MIRROR;
    /** 爱因斯坦环形磁铁 — 高级电磁组件 */
    public static RegistryObject<Item> EINSTEIN_RINGMAGNET;
    /** 超导金属氢 — 极端条件材料 */
    public static RegistryObject<Item> SUPERCONDUCTIVE_METAL_HYDROGEN;

    // ── 远古遗物 ──
    /** 远古遗产 — 前文明遗留物 */
    public static RegistryObject<Item> ANCIENT_LEGACY;
    /** 远古意志 — 前文明意志载体 */
    public static RegistryObject<Item> ANCIENT_WILL;

    // ── P2 研究提交物 ──
    /** 数据研究包 — 用于研究系统提交 */
    public static RegistryObject<Item> DATA_RESEARCH_PACKAGE;
    /** 世界泡样本 — 稀有研究材料，堆叠上限16 */
    public static RegistryObject<Item> WORLD_BUBBLE_SAMPLE;

    public static void register() {
        RAW_HONKAI_PARTICLE = Hk3Items.ITEMS.register("raw_honkai_particle",
                () -> new Item(new Item.Properties()));
        HONKAI_ENERGY_CRYSTAL = Hk3Items.ITEMS.register("honkai_energy_crystal",
                () -> new Item(new Item.Properties()));
        STABILIZED_HONKAI_CRYSTAL = Hk3Items.ITEMS.register("stabilized_honkai_crystal",
                () -> new Item(new Item.Properties()));
        COMPRESSED_HONKAI_CORE = Hk3Items.ITEMS.register("compressed_honkai_core",
                () -> new Item(new Item.Properties()));
        HONKAI_FUEL_ROD = Hk3Items.ITEMS.register("honkai_fuel_rod",
                () -> new Item(new Item.Properties()));
        DENSE_HONKAI_FUEL_ROD = Hk3Items.ITEMS.register("dense_honkai_fuel_rod",
                () -> new Item(new Item.Properties()));
        HONKAI_SUPPRESSANT = Hk3Items.ITEMS.register("honkai_suppressant",
                () -> new Item(new Item.Properties()));
        GAZE_BUFFER_UNIT = Hk3Items.ITEMS.register("gaze_buffer_unit",
                () -> new GazeBufferUnitItem(new Item.Properties()));
        ADVANCED_GAZE_BUFFER_UNIT = Hk3Items.ITEMS.register("advanced_gaze_buffer_unit",
                () -> new Item(new Item.Properties()));
        SCHICKSAL_IMAGINARY_CORE = Hk3Items.ITEMS.register("schicksal_imaginary_core",
                () -> new Item(new Item.Properties()));
        ANTI_ENTROPY_IMAGINARY_CORE = Hk3Items.ITEMS.register("anti_entropy_imaginary_core",
                () -> new Item(new Item.Properties()));
        FLUID_ALLOY = Hk3Items.ITEMS.register("fluid_alloy",
                () -> new Item(new Item.Properties()));
        FLUID_ALLOY_BLOCK = Hk3Items.ITEMS.register("fluid_alloy_block",
                () -> new Item(new Item.Properties()));
        NANO_CERAMIC = Hk3Items.ITEMS.register("nano_ceramic",
                () -> new Item(new Item.Properties()));
        PHASE_TRANSFER_MIRROR = Hk3Items.ITEMS.register("phase_transfer_mirror",
                () -> new Item(new Item.Properties()));
        EINSTEIN_RINGMAGNET = Hk3Items.ITEMS.register("einstein_ringmagnet",
                () -> new Item(new Item.Properties()));
        SUPERCONDUCTIVE_METAL_HYDROGEN = Hk3Items.ITEMS.register("superconductive_metal_hydrogen",
                () -> new Item(new Item.Properties()));
        ANCIENT_LEGACY = Hk3Items.ITEMS.register("ancient_legacy",
                () -> new Item(new Item.Properties()));
        ANCIENT_WILL = Hk3Items.ITEMS.register("ancient_will",
                () -> new Item(new Item.Properties()));

        DATA_RESEARCH_PACKAGE = Hk3Items.ITEMS.register("data_research_package",
                () -> new Item(new Item.Properties()));
        WORLD_BUBBLE_SAMPLE = Hk3Items.ITEMS.register("world_bubble_sample",
                () -> new Item(new Item.Properties().stacksTo(16)));
    }
}
