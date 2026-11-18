package com.sirin.hk3gtl.mixin.overview;

import com.gregtechceu.gtceu.api.machine.MetaMachine;
import com.sirin.hk3gtl.common.overview.Hk3MachineOverviewHooks;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

/**
 * 观察GT机器加载/卸载；卸载不会删除已登记位置或重新推断归属。
 */
@Mixin(value = MetaMachine.class, remap = false)
public abstract class Hk3MetaMachineOverviewMixin {
    @Inject(method = "onLoad", at = @At("RETURN"))
    private void hk3gtl$overviewLoaded(CallbackInfo ci) { Hk3MachineOverviewHooks.loaded((MetaMachine) (Object) this); }

    @Inject(method = "onUnload", at = @At("RETURN"))
    private void hk3gtl$overviewUnloaded(CallbackInfo ci) { Hk3MachineOverviewHooks.unloaded((MetaMachine) (Object) this); }
}
