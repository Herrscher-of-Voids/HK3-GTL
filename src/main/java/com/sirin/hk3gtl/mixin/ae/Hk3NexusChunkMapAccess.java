package com.sirin.hk3gtl.mixin.ae;

import net.minecraft.server.level.ChunkHolder;
import net.minecraft.server.level.ChunkMap;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.gen.Invoker;

@Mixin(ChunkMap.class)
public interface Hk3NexusChunkMapAccess {
    @Invoker("getChunks")
    Iterable<ChunkHolder> hk3gtl$loadedChunks();
}
