package com.sirin.hk3gtl.mixin;

import net.minecraft.server.level.ChunkMap;
import net.minecraft.world.level.chunk.ChunkAccess;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.gen.Invoker;

@Mixin(ChunkMap.class)
public interface Hk3ChunkMapSaveAccess {
    @Invoker("save") boolean hk3gtl$save(ChunkAccess chunk);
}
