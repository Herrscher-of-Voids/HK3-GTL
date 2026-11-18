package com.sirin.hk3gtl.mixin.gtlcore;

import appeng.menu.me.crafting.CraftingPlanSummaryEntry;
import com.llamalad7.mixinextras.sugar.Local;
import com.sirin.hk3gtl.common.integration.ae.nexus.crafting.Hk3NexusPlanSummary;
import org.gtlcore.gtlcore.integration.ae2.graph.AeGraphPlan;
import org.gtlcore.gtlcore.integration.ae2.graph.GraphPlanSummary;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;

@Mixin(value = GraphPlanSummary.class, remap = false)
public abstract class Hk3GraphPlanSummaryMixin {
    @Inject(method = "entries", at = @At("RETURN"), cancellable = true)
    private static void hk3gtl$exactEntries(AeGraphPlan plan,
            CallbackInfoReturnable<List<CraftingPlanSummaryEntry>> cir, @Local(name = "groups") Map<?, ?> groups) {
        var projected = cir.getReturnValue().iterator();
        List<CraftingPlanSummaryEntry> entries = new ArrayList<>(groups.size());
        for (Object value : groups.values()) {
            var group = (Hk3GraphPlanGroupAccess) value;
            entries.add(Hk3NexusPlanSummary.exactEntry(projected.next(), group.hk3gtl$missing(),
                    group.hk3gtl$stored(), group.hk3gtl$crafted(), group.hk3gtl$runs()));
        }
        cir.setReturnValue(entries);
    }
}
