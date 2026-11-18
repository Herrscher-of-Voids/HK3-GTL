package com.sirin.hk3gtl.mixin.gtlcore;

import com.gregtechceu.gtceu.api.machine.feature.multiblock.IWorkableMultiController;
import com.gregtechceu.gtceu.api.machine.multiblock.MultiblockControllerMachine;
import com.sirin.hk3gtl.common.multiblock.loading.Hk3ActiveShells;
import it.unimi.dsi.fastutil.longs.LongSet;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Pseudo;
import org.spongepowered.asm.mixin.Shadow;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

@Pseudo
@Mixin(targets = "org.gtlcore.gtlcore.api.machine.multiblock.MolecularAssemblerMultiblockMachineBase",
        priority = 1300, remap = false)
public abstract class Hk3MolecularActiveShellMixin {
    @Shadow protected LongSet activeBlocks;

    @Inject(method = "updateActiveBlocks", at = @At("HEAD"), cancellable = true, require = 1)
    private void hk3gtl$updateLoadedShells(boolean active, CallbackInfo callback) {
        Hk3ActiveShells.update((MultiblockControllerMachine) (Object) this, activeBlocks, active, 3);
        callback.cancel();
    }

    @Inject(method = "onStructureFormed", at = @At("TAIL"), require = 1)
    private void hk3gtl$restoreActiveShells(CallbackInfo callback) {
        var machine = (MultiblockControllerMachine) (Object) this;
        boolean active = ((IWorkableMultiController) this).getRecipeLogic().isWorking();
        Hk3ActiveShells.update(machine, activeBlocks, active, 3);
    }
}
