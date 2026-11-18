package com.sirin.hk3gtl.mixin.ae;

import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.gen.Accessor;

/** 原生任务次数仍为受溢出保护的 long，程序只控制真实投料顺序。 */
@Mixin(targets = "appeng.crafting.execution.ExecutingCraftingJob$TaskProgress", remap = false)
public interface Hk3ExactTaskProgressAccess {
    @Accessor("value") long hk3gtl$value();
    @Accessor("value") void hk3gtl$value(long amount);
}
