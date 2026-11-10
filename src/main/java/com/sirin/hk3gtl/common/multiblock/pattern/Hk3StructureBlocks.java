package com.sirin.hk3gtl.common.multiblock.pattern;

import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.level.block.Block;

/** 中文说明：该处备注已按当前代码行为整理，不使用问号占位。*/
public final class Hk3StructureBlocks {
    private Hk3StructureBlocks() {}

    /** 中文说明：该处说明已按当前代码行为整理。*/
    public static Block require(String name) {
        ResourceLocation id = new ResourceLocation(name);
        if (!BuiltInRegistries.BLOCK.containsKey(id)) {
            throw new IllegalStateException("Missing approved structure material: " + id);
        }
        return BuiltInRegistries.BLOCK.get(id);
    }
}
