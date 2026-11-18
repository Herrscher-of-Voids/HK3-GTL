package com.sirin.hk3gtl.mixin;

import com.sirin.hk3gtl.client.compat.Hk3JeiLifecyclePlugin;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Pseudo;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

 







@Pseudo
@Mixin(targets = "net.yiran.jcrj.CopyItemHandler", remap = false)
public abstract class JeiCopyItemHandlerMixin {
    @Inject(method = "onKeyInput(Lnet/minecraftforge/client/event/ScreenEvent$KeyPressed$Pre;)V",
            at = @At("HEAD"), cancellable = true, remap = false)
    private static void hk3gtl$guardJeiLifecycle(CallbackInfo callback) {
        if (!Hk3JeiLifecyclePlugin.isRuntimeAvailable()) callback.cancel();
    }
}
