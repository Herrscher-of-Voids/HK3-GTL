package com.sirin.hk3gtl.common.block;



import net.minecraft.core.registries.Registries;
import net.minecraft.world.level.block.entity.BlockEntityType;
import net.minecraftforge.registries.DeferredRegister;
import net.minecraftforge.registries.RegistryObject;


import com.sirin.hk3gtl.common.constants.Hk3Constants;

public final class Hk3BlockEntities {

    public static final DeferredRegister<BlockEntityType<?>> BE_TYPES =
            DeferredRegister.create(Registries.BLOCK_ENTITY_TYPE, Hk3Constants.MOD_ID);

    private Hk3BlockEntities() {}
}
