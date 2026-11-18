package com.sirin.hk3gtl.mixin.client;

import com.llamalad7.mixinextras.injector.wrapoperation.Operation;
import com.llamalad7.mixinextras.injector.wrapoperation.WrapOperation;
import com.sirin.hk3gtl.client.farview.Hk3FarViewRenderer;
import net.minecraft.client.renderer.LevelRenderer;
import net.minecraft.client.renderer.chunk.ChunkRenderDispatcher;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;

@Mixin(LevelRenderer.class)
public abstract class Hk3FarNativeRenderMixin {
    @WrapOperation(method="renderChunkLayer",at=@At(value="INVOKE",target="Lnet/minecraft/client/renderer/chunk/ChunkRenderDispatcher$RenderChunk;getCompiledChunk()Lnet/minecraft/client/renderer/chunk/ChunkRenderDispatcher$CompiledChunk;"),require=0)
    private ChunkRenderDispatcher.CompiledChunk hk3gtl$visible(ChunkRenderDispatcher.RenderChunk chunk,Operation<ChunkRenderDispatcher.CompiledChunk> original){
        var compiled=original.call(chunk);
        if(compiled!=ChunkRenderDispatcher.CompiledChunk.UNCOMPILED)Hk3FarViewRenderer.nativeSection(chunk.getOrigin());
        return compiled;
    }
}
