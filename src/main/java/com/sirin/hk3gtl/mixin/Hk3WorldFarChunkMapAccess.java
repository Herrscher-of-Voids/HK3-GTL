package com.sirin.hk3gtl.mixin;

import net.minecraft.nbt.CompoundTag;
import net.minecraft.server.level.ChunkMap;
import net.minecraft.world.level.ChunkPos;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.gen.Invoker;

import java.util.Optional;
import java.util.concurrent.CompletableFuture;

@Mixin(ChunkMap.class)
public interface Hk3WorldFarChunkMapAccess {
    @Invoker("readChunk") CompletableFuture<Optional<CompoundTag>> hk3gtl$readChunk(ChunkPos pos);
}
