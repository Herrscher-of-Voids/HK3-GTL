package com.sirin.hk3gtl.mixin.ae;

import appeng.api.networking.IGrid;
import appeng.menu.me.crafting.CraftConfirmMenu;
import com.llamalad7.mixinextras.injector.ModifyExpressionValue;
import com.llamalad7.mixinextras.sugar.Local;
import com.sirin.hk3gtl.common.integration.ae.nexus.crafting.Hk3NexusCrafting;
import org.spongepowered.asm.mixin.Dynamic;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;

@Mixin(value = CraftConfirmMenu.class, remap = false, priority = 1300)
public abstract class Hk3NexusCoreGraphMixin {
    @Dynamic("GTLCore 合并到确认页的长整数规划入口")
    @ModifyExpressionValue(method = "gtlcore$planLongAmountJob(Lappeng/api/stacks/AEKey;JLappeng/api/networking/crafting/CalculationStrategy;Z)Z",
            at = @At(value = "INVOKE", target = "Lorg/gtlcore/gtlcore/integration/ae2/graph/CraftingEngineRouter;useGraph()Z"), require = 1)
    private boolean hk3gtl$reserveForCoreGraph(boolean useGraph, @Local IGrid grid) {
        return useGraph && Hk3NexusCrafting.plannerOn(grid) == null;
    }
}
