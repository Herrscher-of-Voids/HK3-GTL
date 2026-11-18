package com.sirin.hk3gtl.mixin.gtlcore;

import appeng.api.stacks.AEFluidKey;
import appeng.api.stacks.AEItemKey;
import it.unimi.dsi.fastutil.objects.Object2LongOpenHashMap;
import it.unimi.dsi.fastutil.objects.ObjectSet;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.gen.Accessor;

@Mixin(targets = "org.gtlcore.gtlcore.common.machine.multiblock.part.ae.MEPatternBufferPartMachineBase$InternalSlot", remap = false)
public interface Hk3ProbabilitySlotAccess {
    @Accessor("itemInventory") Object2LongOpenHashMap<AEItemKey> hk3gtl$items();
    @Accessor("fluidInventory") Object2LongOpenHashMap<AEFluidKey> hk3gtl$fluids();
    @Accessor("configuredVirtualItems") ObjectSet<AEItemKey> hk3gtl$virtualItems();
    @Accessor("configuredVirtualFluids") ObjectSet<AEFluidKey> hk3gtl$virtualFluids();
    @Accessor("slotIndex") int hk3gtl$index();
    @Accessor("onContentsChanged") Runnable hk3gtl$changed();
}
