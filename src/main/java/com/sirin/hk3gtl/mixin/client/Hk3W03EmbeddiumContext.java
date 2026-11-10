package com.sirin.hk3gtl.mixin.client;

import net.minecraft.core.BlockPos;
import org.spongepowered.asm.mixin.*;
import org.spongepowered.asm.mixin.gen.Invoker;

/** 可选Embeddium上下文桥，不引入运行依赖。 */
@Pseudo
@Mixin(targets="me.jellysquid.mods.sodium.client.render.chunk.compile.pipeline.BlockRenderContext",remap=false)
public interface Hk3W03EmbeddiumContext {
    @Invoker("pos") BlockPos hk3gtl$pos();
}
