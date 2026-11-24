package com.sirin.hk3gtl.mixin.gtlcore;

import org.gtlcore.gtlcore.config.ConfigHolder;
import org.gtlcore.gtlcore.integration.ae2.graph.CraftingEngineRouter;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

@Mixin(value = CraftingEngineRouter.class, remap = false)
public abstract class Hk3GraphPlannerBudgetMixin {
    @Inject(method = "planningBudget", at = @At("HEAD"))
    private static void hk3gtl$raiseMemoryBudget(int requested, CallbackInfoReturnable<?> cir) {
        var ae = ConfigHolder.INSTANCE.ae;
        ae.ae2GraphPlannerMemoryMiB = Math.max(ae.ae2GraphPlannerMemoryMiB, 256);
        ae.ae2GraphGlobalMemoryMiB = Math.max(ae.ae2GraphGlobalMemoryMiB, 768);
    }
}
