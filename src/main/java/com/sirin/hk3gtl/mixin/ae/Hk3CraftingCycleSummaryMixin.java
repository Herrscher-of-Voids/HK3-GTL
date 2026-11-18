package com.sirin.hk3gtl.mixin.ae;

import appeng.api.networking.IGrid;
import appeng.api.networking.crafting.ICraftingPlan;
import appeng.api.networking.security.IActionSource;
import appeng.menu.me.crafting.CraftingPlanSummary;
import com.llamalad7.mixinextras.injector.ModifyExpressionValue;
import com.sirin.hk3gtl.common.integration.ae.Hk3CraftingCycleFlag;
import com.sirin.hk3gtl.common.integration.ae.nexus.crafting.Hk3NexusPlanSummary;
import org.gtlcore.gtlcore.integration.ae2.graph.GraphSummaryContext;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Unique;
import org.spongepowered.asm.mixin.injection.At;

import java.math.BigInteger;

@Mixin(value = CraftingPlanSummary.class, remap = false)
public abstract class Hk3CraftingCycleSummaryMixin implements Hk3CraftingCycleFlag {
    @Unique private boolean hk3gtl$hasCycles;

    @Override
    public boolean hk3gtl$hasCycles() { return hk3gtl$hasCycles; }

    @Override
    public void hk3gtl$setHasCycles(boolean value) { hk3gtl$hasCycles = value; }

    @ModifyExpressionValue(method = "fromJob", at = @At(value = "NEW", target = "appeng/menu/me/crafting/CraftingPlanSummary"))
    private static CraftingPlanSummary hk3gtl$copyCycle(CraftingPlanSummary summary,
            IGrid grid, IActionSource source, ICraftingPlan plan) {
        ((Hk3CraftingCycleFlag) summary).hk3gtl$setHasCycles(
                plan instanceof Hk3CraftingCycleFlag cycle && cycle.hk3gtl$hasCycles());
        var graph = GraphSummaryContext.graphPlan(plan);
        return graph == null ? summary : Hk3NexusPlanSummary.fromGraph(summary,
                BigInteger.valueOf(graph.graph().amount()), graph.exactBytes());
    }
}
