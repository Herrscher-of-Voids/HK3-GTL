package com.sirin.hk3gtl.mixin.ae;

import appeng.api.stacks.AEKeyType;
import appeng.crafting.execution.ElapsedTimeTracker;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.gen.Invoker;

/** 严格程序沿用原生进度统计。 */
@Mixin(value = ElapsedTimeTracker.class, remap = false)
public interface Hk3ExactTimeTrackerAccess {
    @Invoker("decrementItems") void hk3gtl$decrement(long amount, AEKeyType type);
    @Invoker("addMaxItems") void hk3gtl$add(long amount, AEKeyType type);
}
