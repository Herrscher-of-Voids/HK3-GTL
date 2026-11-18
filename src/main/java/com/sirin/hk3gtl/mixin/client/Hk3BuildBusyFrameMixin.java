package com.sirin.hk3gtl.mixin.client;

import com.sirin.hk3gtl.client.Hk3BuildFrameFeedback;
import net.minecraft.client.Minecraft;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Unique;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

/** 只计每帧真正执行任务的时间，在交换缓冲与限帧等待前结束。 */
@Mixin(Minecraft.class)
public abstract class Hk3BuildBusyFrameMixin {
    @Unique private long hk3gtl$busyFrameStart;

    @Inject(method="runTick(Z)V",at=@At("HEAD"))
    private void hk3gtl$beginBusyFrame(boolean render,CallbackInfo callback) {
        hk3gtl$busyFrameStart=System.nanoTime();
    }

    @Inject(method="runTick(Z)V",at=@At(value="INVOKE",target="Lcom/mojang/blaze3d/platform/Window;updateDisplay()V"))
    private void hk3gtl$finishBusyFrame(boolean render,CallbackInfo callback) {
        Hk3BuildFrameFeedback.recordFrame(System.nanoTime()-hk3gtl$busyFrameStart);
    }
}
