package com.sirin.hk3gtl.mixin.overview;

import com.gregtechceu.gtceu.api.machine.multiblock.MultiblockControllerMachine;
import com.sirin.hk3gtl.common.overview.Hk3MachineOverviewHooks;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

/**
 * 观察GT多方块实际成型/失效完成后的状态，不执行匹配或读写结构。
 */
@Mixin(value = MultiblockControllerMachine.class, remap = false)
public abstract class Hk3MultiblockOverviewMixin {
    @Inject(method = {"onStructureFormed", "onStructureInvalid"}, at = @At("RETURN"))
    private void hk3gtl$overviewStructureChanged(CallbackInfo ci) {
        Hk3MachineOverviewHooks.changed((MultiblockControllerMachine) (Object) this);
    }
}
