package com.sirin.hk3gtl.mixin.gtlcore;

import appeng.api.crafting.IPatternDetails;
import com.google.common.collect.BiMap;
import org.gtlcore.gtlcore.common.machine.multiblock.part.ae.MEPatternBufferPartMachine;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.gen.Invoker;
import org.spongepowered.asm.mixin.gen.Accessor;

@Mixin(value = MEPatternBufferPartMachine.class, remap = false)
public interface Hk3ProbabilityPatternSlot {
    @Accessor("patternSlotMap") BiMap<IPatternDetails, Integer> hk3gtl$patterns();
    @Invoker("getSlotIndexForPattern") Integer hk3gtl$slot(IPatternDetails pattern);
}
