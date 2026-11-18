package com.sirin.hk3gtl.mixin.client;

import com.sirin.hk3gtl.client.farview.Hk3FarViewRenderer;
import net.minecraft.client.renderer.LevelRenderer;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

@Mixin(LevelRenderer.class)
public abstract class Hk3FarFrameMixin {
    @Inject(method="renderLevel",at=@At("HEAD"))
    private void hk3gtl$frame(CallbackInfo ci){Hk3FarViewRenderer.nativeFrame();}
}
