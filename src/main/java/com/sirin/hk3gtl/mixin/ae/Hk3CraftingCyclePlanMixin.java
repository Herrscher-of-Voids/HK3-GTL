package com.sirin.hk3gtl.mixin.ae;

import appeng.crafting.CraftingPlan;
import com.sirin.hk3gtl.common.integration.ae.Hk3CraftingCycleFlag;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Unique;

@Mixin(value = CraftingPlan.class, remap = false)
public abstract class Hk3CraftingCyclePlanMixin implements Hk3CraftingCycleFlag {
    @Unique private boolean hk3gtl$hasCycles;

    @Override
    public boolean hk3gtl$hasCycles() { return hk3gtl$hasCycles; }

    @Override
    public void hk3gtl$setHasCycles(boolean value) { hk3gtl$hasCycles = value; }
}
