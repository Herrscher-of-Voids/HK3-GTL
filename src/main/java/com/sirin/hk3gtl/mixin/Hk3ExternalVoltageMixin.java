package com.sirin.hk3gtl.mixin;

import com.gregtechceu.gtceu.api.machine.multiblock.WorkableElectricMultiblockMachine;
import com.sirin.hk3gtl.common.recipe.power.Hk3PowerPorts;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

import java.util.Arrays;

@Mixin(value = WorkableElectricMultiblockMachine.class, priority = 1200, remap = false)
public abstract class Hk3ExternalVoltageMixin {
    @Inject(method = "getTier", at = @At("RETURN"), cancellable = true, require = 1)
    private void hk3gtl$inputTier(CallbackInfoReturnable<Integer> callback) {
        var machine = (WorkableElectricMultiblockMachine) (Object) this;
        if (!machine.isFormed() || !Hk3PowerPorts.usesExtendedVoltage(machine.getRecipeType())
                && Arrays.stream(machine.getRecipeTypes()).noneMatch(Hk3PowerPorts::usesExtendedVoltage)) return;
        int original = callback.getReturnValueI();
        int extended = Hk3PowerPorts.inputTier(machine, original);
        if (extended > original) callback.setReturnValue(extended);
    }
}
