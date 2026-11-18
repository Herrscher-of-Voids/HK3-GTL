package com.sirin.hk3gtl.common.integration.ae;

import appeng.api.stacks.AEKey;
import appeng.crafting.inv.CraftingSimulationState;
import org.gtlcore.gtlcore.integration.ae2.crafting.ICraftingTreeNode;

public final class Hk3AeCycleMarkers {
    private Hk3AeCycleMarkers() {}

    public static void markReturningInput(ICraftingTreeNode node, CraftingSimulationState state, AEKey key) {
        var flag = (Hk3CraftingCycleFlag) state;
        if (flag.hk3gtl$hasCycles()) return;
        var process = node.gtlcore$getMaxFastParentProcess();
        while (process != null) {
            for (var output : process.getDetails().getOutputs()) {
                if (output.what().equals(key)) {
                    flag.hk3gtl$setHasCycles(true);
                    return;
                }
            }
            process = ((ICraftingTreeNode) process.gtlcore$getMaxFastParentNode()).gtlcore$getMaxFastParentProcess();
        }
    }
}
