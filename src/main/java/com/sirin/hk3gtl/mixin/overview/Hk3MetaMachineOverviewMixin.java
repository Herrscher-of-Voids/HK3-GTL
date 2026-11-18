package com.sirin.hk3gtl.mixin.overview;

import com.gregtechceu.gtceu.api.machine.MetaMachine;
import com.sirin.hk3gtl.common.overview.Hk3MachineOverviewHooks;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

 





@Mixin(value = MetaMachine.class, remap = false)
public abstract class Hk3MetaMachineOverviewMixin {
    @Inject(method = "onLoad", at = @At("RETURN"))
    private void hk3gtl$overviewLoaded(CallbackInfo ci) { Hk3MachineOverviewHooks.loaded((MetaMachine) (Object) this); }

    @Inject(method = "onUnload", at = @At("RETURN"))
    private void hk3gtl$overviewUnloaded(CallbackInfo ci) { Hk3MachineOverviewHooks.unloaded((MetaMachine) (Object) this); }
}
