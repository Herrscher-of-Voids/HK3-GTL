package com.sirin.hk3gtl.mixin.gtceu;

import com.gregtechceu.gtceu.api.machine.multiblock.MultiblockControllerMachine;
import com.gregtechceu.gtceu.api.machine.multiblock.WorkableMultiblockMachine;
import com.sirin.hk3gtl.common.multiblock.loading.Hk3ActiveShells;
import it.unimi.dsi.fastutil.longs.LongSet;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Shadow;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

@Mixin(value = WorkableMultiblockMachine.class, priority = 1300, remap = false)
public abstract class Hk3ActiveShellMixin {
    @Shadow protected LongSet activeBlocks;

    @Inject(method = "updateActiveBlocks", at = @At("HEAD"), cancellable = true, require = 1)
    private void hk3gtl$updateLoadedShells(boolean active, CallbackInfo callback) {
        Hk3ActiveShells.update((MultiblockControllerMachine) (Object) this, activeBlocks, active);
        callback.cancel();
    }

    @Inject(method = "onStructureFormed", at = @At("TAIL"), require = 1)
    private void hk3gtl$restoreActiveShells(CallbackInfo callback) {
        var machine = (WorkableMultiblockMachine) (Object) this;
        Hk3ActiveShells.update(machine, activeBlocks, machine.getRecipeLogic().isWorking());
    }
}
