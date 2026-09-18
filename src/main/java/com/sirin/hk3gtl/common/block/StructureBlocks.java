package com.sirin.hk3gtl.common.block;



import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.GlassBlock;
import net.minecraft.world.level.block.SoundType;
import net.minecraft.world.level.block.state.BlockBehaviour;
import net.minecraftforge.registries.RegistryObject;

/**
 * P2 海渊阶段结构方块：玻璃、线圈、冷却构件、通讯阵列、数据柱。
 * <p>来源：设计文档 §2.1 基础功能方块。用于多方块机器结构搭建。</p>
 *
 * <h3>修改指南</h3>
 * <ul>
 *   <li>新增结构方块：声明 RegistryObject 字段 → 在 {@link #register()} 中调用 {@link Hk3Blocks#registerBlock}</li>
 *   <li>修改方块硬度/爆炸抗性：调整 {@link #structureProperties()} 或 {@link #glassProperties()} 中的 strength(硬度, 抗性)</li>
 *   <li>玻璃类方块需要 {@code .noOcclusion()} 以支持透明渲染</li>
 *   <li>方块贴图：{@code assets/hk3gtl/textures/block/<注册ID>.png}（16x16 PNG）</li>
 *   <li>方块状态：{@code assets/hk3gtl/blockstates/<注册ID>.json}</li>
 *   <li>语言Key：{@code block.hk3gtl.<注册ID>}，需同步更新 zh_cn.json / en_us.json</li>
 * </ul>
 */
public class StructureBlocks {

    /** 崩坏能稳定化玻璃 — 透明结构方块，GlassBlock类型（noOcclusion） */
    public static RegistryObject<Block> GLASS_HONKAI_STABILIZED;
    /** 海渊通量线圈 — 能量传输结构组件 */
    public static RegistryObject<Block> COIL_ABYSS_FLUX;
    /** 海渊冷却构件 — 散热结构组件 */
    public static RegistryObject<Block> STRUCTURE_ABYSS_COOLING_UNIT;
    /** 通讯阵列 — 数据传输结构组件 */
    public static RegistryObject<Block> STRUCTURE_COMMUNICATION_ARRAY;
    /** 数据柱 — 数据存储结构组件 */
    public static RegistryObject<Block> STRUCTURE_DATA_PILLAR;

    /**
     * 金属结构方块通用属性。
     * 修改硬度：第一个参数；修改爆炸抗性：第二个参数
     */
    private static BlockBehaviour.Properties structureProperties() {
        return BlockBehaviour.Properties.of()
                .strength(5.0f, 10.0f)
                .sound(SoundType.METAL)
                .requiresCorrectToolForDrops();
    }

    /**
     * 玻璃方块通用属性。noOcclusion() 使方块透明渲染。
     * 修改硬度：第一个参数；修改爆炸抗性：第二个参数
     */
    private static BlockBehaviour.Properties glassProperties() {
        return BlockBehaviour.Properties.of()
                .strength(3.0f, 8.0f)
                .sound(SoundType.GLASS)
                .noOcclusion()
                .requiresCorrectToolForDrops();
    }

    public static void register() {
        GLASS_HONKAI_STABILIZED = Hk3Blocks.registerBlock("glass_honkai_stabilized",
                () -> new GlassBlock(glassProperties()));

        COIL_ABYSS_FLUX = Hk3Blocks.registerBlock("coil_abyss_flux",
                () -> new Block(structureProperties()));

        STRUCTURE_ABYSS_COOLING_UNIT = Hk3Blocks.registerBlock("structure_abyss_cooling_unit",
                () -> new Block(structureProperties()));

        STRUCTURE_COMMUNICATION_ARRAY = Hk3Blocks.registerBlock("structure_communication_array",
                () -> new Block(structureProperties()));

        STRUCTURE_DATA_PILLAR = Hk3Blocks.registerBlock("structure_data_pillar",
                () -> new Block(structureProperties()));
    }
}
