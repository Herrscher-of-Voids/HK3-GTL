package com.sirin.hk3gtl.common.block;

import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.GlassBlock;
import net.minecraft.world.level.block.SoundType;
import net.minecraft.world.level.block.state.BlockBehaviour;
import net.minecraftforge.registries.RegistryObject;

public class StructureBlocks {

    /** 崩坏能稳定化玻璃 — 透明结构方块，GlassBlock类型（noOcclusion） */
    public static RegistryObject<Block> GLASS_HONKAI_STABILIZED;
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

    }
}
