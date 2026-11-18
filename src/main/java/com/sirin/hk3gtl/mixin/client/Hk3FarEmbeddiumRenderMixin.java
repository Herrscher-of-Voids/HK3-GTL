package com.sirin.hk3gtl.mixin.client;

import com.sirin.hk3gtl.client.farview.Hk3FarViewRenderer;
import com.llamalad7.mixinextras.injector.wrapoperation.Operation;
import com.llamalad7.mixinextras.injector.wrapoperation.WrapOperation;
import me.jellysquid.mods.sodium.client.render.chunk.lists.SortedRenderLists;
import me.jellysquid.mods.sodium.client.render.chunk.lists.VisibleChunkCollector;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Pseudo;
import org.spongepowered.asm.mixin.Shadow;
import org.spongepowered.asm.mixin.Unique;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

@Pseudo
@Mixin(targets="me.jellysquid.mods.sodium.client.render.chunk.RenderSectionManager",remap=false)
public abstract class Hk3FarEmbeddiumRenderMixin implements Hk3FarViewRenderer.NativeVisibility {
    @Shadow public abstract boolean isSectionBuilt(int x,int y,int z);
    @Unique private Hk3FarViewRenderer.NativeVisibility hk3gtl$visibility=(x,y,z)->false;

    @WrapOperation(method="createTerrainRenderList",at=@At(value="INVOKE",target="Lme/jellysquid/mods/sodium/client/render/chunk/lists/VisibleChunkCollector;createRenderLists()Lme/jellysquid/mods/sodium/client/render/chunk/lists/SortedRenderLists;"),remap=false)
    private SortedRenderLists hk3gtl$lists(VisibleChunkCollector collector,Operation<SortedRenderLists> original){
        hk3gtl$visibility=(Hk3FarViewRenderer.NativeVisibility)collector;
        return original.call(collector);
    }

    @Inject(method="renderLayer",at=@At("HEAD"),remap=false)
    private void hk3gtl$layer(CallbackInfo ci){Hk3FarViewRenderer.nativeVisibility(this);}

    @Override public boolean hk3gtl$visible(int x,int y,int z){
        return isSectionBuilt(x,y,z)&&hk3gtl$visibility.hk3gtl$visible(x,y,z);
    }
}
