package com.sirin.hk3gtl.mixin.gtceu;

import com.gregtechceu.gtceu.api.machine.multiblock.MultiblockControllerMachine;
import com.sirin.hk3gtl.common.multiblock.build.Hk3UniversalTerminalBuilder;
import com.sirin.hk3gtl.common.farview.Hk3FarViewCapture;
import com.sirin.hk3gtl.common.multiblock.loading.Hk3MultiblockLoading;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

/** 所有GT主控共用主线程分批世界读取；专用巨构核验沿用原实现。 */
@Mixin(value = MultiblockControllerMachine.class, remap = false, priority = 1300)
public abstract class Hk3UniversalBuildCheckMixin {
    @Inject(method = "asyncCheckPattern", at = @At("HEAD"), cancellable = true)
    private void hk3gtl$queueBatchCheck(long periodID, CallbackInfo callback) {
        var controller=(MultiblockControllerMachine)(Object)this;
        if(!Hk3MultiblockLoading.managed(controller))return;
        callback.cancel();
        if((controller.getHolder().getOffset()+periodID)%4L==0L)Hk3MultiblockLoading.queue(controller);
    }

    @Inject(method = "onUnload", at = @At("HEAD"))
    private void hk3gtl$releaseBuildOnUnload(CallbackInfo callback) {
        Hk3MultiblockLoading.unloaded((MultiblockControllerMachine)(Object)this);
        Hk3FarViewCapture.cancel((MultiblockControllerMachine)(Object)this);
        Hk3UniversalTerminalBuilder.controllerUnloaded((MultiblockControllerMachine)(Object)this);
    }

    @Inject(method = "onPartUnload", at = @At("HEAD"))
    private void hk3gtl$releaseMissingParts(CallbackInfo callback) {
        Hk3MultiblockLoading.invalidated((MultiblockControllerMachine)(Object)this);
    }

    @Inject(method = "onStructureFormed", at = @At("RETURN"))
    private void hk3gtl$observeFormedStructure(CallbackInfo callback) {
        Hk3FarViewCapture.formed((MultiblockControllerMachine)(Object)this);
    }

    @Inject(method = "onStructureInvalid", at = @At("HEAD"))
    private void hk3gtl$cancelFarViewCapture(CallbackInfo callback) {
        Hk3MultiblockLoading.invalidated((MultiblockControllerMachine)(Object)this);
        Hk3FarViewCapture.cancel((MultiblockControllerMachine)(Object)this);
    }

    @Inject(method = "onStructureFormed", at = @At("HEAD"), cancellable = true)
    private void hk3gtl$rejectStaleFormation(CallbackInfo callback) {
        if (Hk3UniversalTerminalBuilder.isBuilding((MultiblockControllerMachine)(Object)this)) callback.cancel();
    }
}
