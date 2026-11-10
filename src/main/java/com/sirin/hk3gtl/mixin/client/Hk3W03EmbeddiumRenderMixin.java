package com.sirin.hk3gtl.mixin.client;

import org.spongepowered.asm.mixin.*;
import org.spongepowered.asm.mixin.injection.*;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

/** 增强版3.5的实际区块编译入口，避免动态环与原静态环重叠。 */
@Pseudo
@Mixin(targets="me.jellysquid.mods.sodium.client.render.chunk.compile.pipeline.BlockRenderer",remap=false)
public abstract class Hk3W03EmbeddiumRenderMixin {
    @Inject(method="renderModel",at=@At("HEAD"),cancellable=true,remap=false)
    private void hk3gtl$c9(@Coerce Object context,@Coerce Object buffers,CallbackInfo ci){
        if(com.sirin.hk3gtl.client.wonder.Hk3W03FieldScenes.hidden(((Hk3W03EmbeddiumContext)context).hk3gtl$pos()))ci.cancel();
    }
}
