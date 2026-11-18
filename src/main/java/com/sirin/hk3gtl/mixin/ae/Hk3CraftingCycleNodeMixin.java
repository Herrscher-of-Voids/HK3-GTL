package com.sirin.hk3gtl.mixin.ae;

import appeng.api.stacks.AEKey;
import appeng.api.stacks.KeyCounter;
import appeng.crafting.CraftingCalculation;
import appeng.crafting.CraftingTreeNode;
import appeng.crafting.execution.InputTemplate;
import appeng.crafting.inv.CraftingSimulationState;
import appeng.crafting.inv.ICraftingInventory;
import com.llamalad7.mixinextras.injector.wrapoperation.Operation;
import com.llamalad7.mixinextras.injector.wrapoperation.WrapOperation;
import com.sirin.hk3gtl.common.integration.ae.Hk3AeCycleMarkers;
import org.gtlcore.gtlcore.integration.ae2.crafting.ICraftingCalculation;
import org.gtlcore.gtlcore.integration.ae2.crafting.ICraftingTreeNode;
import org.spongepowered.asm.mixin.Dynamic;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

@Mixin(value = CraftingTreeNode.class, remap = false)
public abstract class Hk3CraftingCycleNodeMixin {
    @WrapOperation(method = "request", at = @At(value = "INVOKE", target =
            "Lappeng/crafting/execution/CraftingCpuHelper;extractTemplates(Lappeng/crafting/inv/ICraftingInventory;Lappeng/crafting/execution/InputTemplate;J)J"),
            require = 1, expect = 1)
    private long hk3gtl$markLegacyInput(ICraftingInventory inventory, InputTemplate template, long amount,
                                       Operation<Long> original) {
        long extracted = original.call(inventory, template, amount);
        if (extracted > 0) Hk3AeCycleMarkers.markReturningInput(
                (ICraftingTreeNode) this, (CraftingSimulationState) inventory, template.key());
        return extracted;
    }

    @WrapOperation(method = "request", at = @At(value = "INVOKE", target =
            "Lappeng/crafting/CraftingCalculation;addMissing(Lappeng/api/stacks/AEKey;J)V"),
            require = 1, expect = 1)
    private void hk3gtl$markLegacySeed(CraftingCalculation calculation, AEKey key, long amount,
                                      Operation<Void> original, CraftingSimulationState state) {
        original.call(calculation, key, amount);
        Hk3AeCycleMarkers.markReturningInput((ICraftingTreeNode) this, state, key);
    }

    @Dynamic("GTLCore合并到配方树的实际材料提取方法")
    @Inject(method = "gTLCore$extractTemplate", at = @At("RETURN"))
    private void hk3gtl$markFastInput(CraftingSimulationState state, long requestedAmount, KeyCounter containerItems,
                                     ICraftingCalculation calculation, InputTemplate template,
                                     CallbackInfoReturnable<Long> ci) {
        if (ci.getReturnValue() < requestedAmount) Hk3AeCycleMarkers.markReturningInput(
                (ICraftingTreeNode) this, state, template.key());
    }

    @Dynamic("GTLCore合并到配方树的FAST缺料路径")
    @WrapOperation(method = "fastRequest", at = @At(value = "INVOKE", target =
            "Lappeng/api/stacks/KeyCounter;add(Lappeng/api/stacks/AEKey;J)V"), require = 1, expect = 1)
    private void hk3gtl$markFastSeed(KeyCounter missing, AEKey key, long amount, Operation<Void> original,
                                    CraftingSimulationState state) {
        original.call(missing, key, amount);
        Hk3AeCycleMarkers.markReturningInput((ICraftingTreeNode) this, state, key);
    }

    @Dynamic("GTLCore合并到配方树的ULTRA及MAX边界缺料路径")
    @WrapOperation(method = "gtlcore$runUltraFastTail", at = @At(value = "INVOKE", target =
            "Lappeng/crafting/CraftingTreeNode;gtlcore$reportMaxFastMissing(J)V"), require = 1, expect = 1)
    private void hk3gtl$markBoundarySeed(CraftingTreeNode node, long amount, Operation<Void> original,
                                        CraftingSimulationState state) {
        original.call(node, amount);
        var treeNode = (ICraftingTreeNode) node;
        Hk3AeCycleMarkers.markReturningInput(treeNode, state, treeNode.gtlcore$getMaxFastKey());
    }
}
