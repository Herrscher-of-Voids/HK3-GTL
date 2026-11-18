package com.sirin.hk3gtl.mixin.client;

import com.sirin.hk3gtl.client.farview.Hk3FarViewRenderer;
import it.unimi.dsi.fastutil.longs.LongOpenHashSet;
import it.unimi.dsi.fastutil.longs.LongSet;
import me.jellysquid.mods.sodium.client.render.chunk.RenderSection;
import net.minecraft.core.BlockPos;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Pseudo;
import org.spongepowered.asm.mixin.Unique;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

@Pseudo
@Mixin(targets="me.jellysquid.mods.sodium.client.render.chunk.lists.VisibleChunkCollector",remap=false)
public abstract class Hk3FarEmbeddiumVisibilityMixin implements Hk3FarViewRenderer.NativeVisibility {
    @Unique private final LongSet hk3gtl$visible=new LongOpenHashSet();

    @Inject(method="visit",at=@At("HEAD"),remap=false)
    private void hk3gtl$section(RenderSection section,boolean visible,CallbackInfo ci){
        if(visible)hk3gtl$visible.add(BlockPos.asLong(section.getChunkX(),section.getChunkY(),section.getChunkZ()));
    }

    @Override public boolean hk3gtl$visible(int x,int y,int z){return hk3gtl$visible.contains(BlockPos.asLong(x,y,z));}
}
