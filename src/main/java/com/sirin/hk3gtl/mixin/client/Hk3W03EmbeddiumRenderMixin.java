package com.sirin.hk3gtl.mixin.client;

import org.spongepowered.asm.mixin.*;
import org.spongepowered.asm.mixin.injection.*;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

@Pseudo
@Mixin(targets="me.jellysquid.mods.sodium.client.render.chunk.compile.pipeline.BlockRenderer",remap=false)
public abstract class Hk3W03EmbeddiumRenderMixin {
    @Inject(method="renderModel",at=@At("HEAD"),cancellable=true,remap=false)
    private void hk3gtl$c9(@Coerce Object context,@Coerce Object buffers,CallbackInfo ci){
        var block=(Hk3W03EmbeddiumContext)context;
        if(com.sirin.hk3gtl.client.wonder.Hk3W03FieldScenes.hidden(block.hk3gtl$pos(),block.hk3gtl$state())
                ||com.sirin.hk3gtl.client.wonder.Hk3W08FieldScenes.hidden(block.hk3gtl$pos(),block.hk3gtl$state())
                ||com.sirin.hk3gtl.client.wonder.Hk3W10FieldScenes.hidden(block.hk3gtl$pos(),block.hk3gtl$state())
                ||com.sirin.hk3gtl.client.wonder.Hk3W12FieldScenes.hidden(block.hk3gtl$pos(),block.hk3gtl$state())
                ||com.sirin.hk3gtl.client.wonder.Hk3W11FieldScenes.hidden(block.hk3gtl$pos(),block.hk3gtl$state())
                ||com.sirin.hk3gtl.client.wonder.Hk3W13FieldScenes.hidden(block.hk3gtl$pos(),block.hk3gtl$state())
                ||com.sirin.hk3gtl.client.wonder.Hk3WonderFxScenes.hidden(block.hk3gtl$pos(),block.hk3gtl$state()))ci.cancel();
    }
}
