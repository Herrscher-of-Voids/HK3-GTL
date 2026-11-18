package com.sirin.hk3gtl.mixin.ae;

import appeng.crafting.CraftingCalculation;
import appeng.crafting.CraftingPlan;
import appeng.crafting.inv.CraftingSimulationState;
import com.sirin.hk3gtl.common.integration.ae.Hk3CraftingCycleFlag;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Unique;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

@Mixin(value = CraftingSimulationState.class, remap = false)
public abstract class Hk3CraftingCycleStateMixin implements Hk3CraftingCycleFlag {
    @Unique private boolean hk3gtl$hasCycles;

    @Override
    public boolean hk3gtl$hasCycles() {
        return hk3gtl$hasCycles;
    }

    @Override
    public void hk3gtl$setHasCycles(boolean value) {
        hk3gtl$hasCycles = value;
    }

    @Inject(method = "applyDiff", at = @At("TAIL"))
    private void hk3gtl$propagateCommittedCycle(CraftingSimulationState parent, CallbackInfo ci) {
        if (hk3gtl$hasCycles) ((Hk3CraftingCycleFlag) parent).hk3gtl$setHasCycles(true);
    }

    @Inject(method = "buildCraftingPlan", at = @At("RETURN"))
    private static void hk3gtl$copyCycleToPlan(CraftingSimulationState state, CraftingCalculation calculation,
                                            long amount, CallbackInfoReturnable<CraftingPlan> ci) {
        ((Hk3CraftingCycleFlag) (Object) ci.getReturnValue())
                .hk3gtl$setHasCycles(((Hk3CraftingCycleFlag) state).hk3gtl$hasCycles());
    }
}
