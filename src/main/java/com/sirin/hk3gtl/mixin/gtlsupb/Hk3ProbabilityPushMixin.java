package com.sirin.hk3gtl.mixin.gtlsupb;

import appeng.api.crafting.IPatternDetails;
import appeng.api.stacks.KeyCounter;
import com.sirin.hk3gtl.common.integration.ae.exact.Hk3ProbabilityAssemblyAccess;
import com.sirin.hk3gtl.common.integration.ae.exact.Hk3ProbabilityOrderService;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Pseudo;
import org.spongepowered.asm.mixin.Shadow;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

@Pseudo
@Mixin(targets = {
        "com.gtlsupb.gtlsupb.common.machine.hatch.PatternAssemblyPartMachine",
        "com.gtlsupb.gtlsupb.common.machine.multiblock.part.PatternAssemblyPartMachine"
}, remap = false)
abstract class Hk3ProbabilityPushMixin implements Hk3ProbabilityAssemblyAccess {
    @Shadow public int patternScale;
    @Shadow public int patternDivScale;

    @Override
    public boolean hk3gtl$hasUnitScale() {
        return patternScale == 1 && patternDivScale == 1;
    }

    @Inject(method = "pushPattern", at = @At("HEAD"), cancellable = true)
    private void hk3gtl$exclusivePush(IPatternDetails pattern, KeyCounter[] contents, CallbackInfoReturnable<Boolean> result) {
        if (Hk3ProbabilityOrderService.blocksPush(this)) result.setReturnValue(false);
    }
}
