package com.sirin.hk3gtl.common.dimension.melon;

import com.sirin.hk3gtl.common.block.Hk3Blocks;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.state.BlockBehaviour;
import net.minecraftforge.registries.RegistryObject;

public final class Hk3MelonBlocks {
    public static RegistryObject<Block> MELON_RIND;
    public static RegistryObject<Block> SEED_SAND;

    private Hk3MelonBlocks() {}

    public static void register() {
        MELON_RIND = Hk3Blocks.registerBlock("melon_rind",
                () -> new Block(BlockBehaviour.Properties.copy(Blocks.MELON).strength(1.2F)));
        SEED_SAND = Hk3Blocks.registerBlock("seed_sand",
                () -> new Block(BlockBehaviour.Properties.copy(Blocks.BLACK_CONCRETE_POWDER)));
    }
}
