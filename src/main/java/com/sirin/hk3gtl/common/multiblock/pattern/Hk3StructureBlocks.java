package com.sirin.hk3gtl.common.multiblock.pattern;

import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.level.block.Block;

public final class Hk3StructureBlocks {
    private Hk3StructureBlocks() {}

    public static Block require(String name) {
        ResourceLocation id = new ResourceLocation(name);
        if (!BuiltInRegistries.BLOCK.containsKey(id)) {
            throw new IllegalStateException("Missing approved structure material: " + id);
        }
        return BuiltInRegistries.BLOCK.get(id);
    }
}
