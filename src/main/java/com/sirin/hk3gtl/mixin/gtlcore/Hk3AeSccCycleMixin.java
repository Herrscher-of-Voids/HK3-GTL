package com.sirin.hk3gtl.mixin.gtlcore;

import appeng.crafting.inv.ChildCraftingSimulationState;
import appeng.crafting.inv.CraftingSimulationState;
import com.llamalad7.mixinextras.injector.wrapoperation.Operation;
import com.llamalad7.mixinextras.injector.wrapoperation.WrapOperation;
import com.sirin.hk3gtl.common.integration.ae.Hk3AeCycleMarkers;
import com.sirin.hk3gtl.common.integration.ae.Hk3CraftingCycleFlag;
import org.gtlcore.gtlcore.integration.ae2.crafting.ICraftingTreeNode;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;

@Mixin(targets = "org.gtlcore.gtlcore.integration.ae2.crafting.compiled.MaxFastExecutor", remap = false)
public abstract class Hk3AeSccCycleMixin {
    @WrapOperation(method = "tryExecuteScc", at = @At(value = "INVOKE",
            target = "Lappeng/crafting/inv/ChildCraftingSimulationState;applyDiff(Lappeng/crafting/inv/CraftingSimulationState;)V"),
            require = 1, expect = 1)
    private void hk3gtl$markCommittedCycle(ChildCraftingSimulationState state,
                                         CraftingSimulationState parent, Operation<Void> original) {
        ((Hk3CraftingCycleFlag) state).hk3gtl$setHasCycles(true);
        original.call(state, parent);
    }

    @WrapOperation(method = "runNodeEnter", at = @At(value = "INVOKE", target =
            "Lorg/gtlcore/gtlcore/integration/ae2/crafting/ICraftingTreeNode;gtlcore$reportMaxFastMissing(J)V"),
            require = 1, expect = 1)
    private void hk3gtl$markTerminalSeed(ICraftingTreeNode node, long amount, Operation<Void> original,
                                        ICraftingTreeNode owner, CraftingSimulationState state) {
        original.call(node, amount);
        Hk3AeCycleMarkers.markReturningInput(node, state, node.gtlcore$getMaxFastKey());
    }
}
