package com.sirin.hk3gtl.mixin.ae;

import appeng.crafting.execution.ExecutingCraftingJob;
import appeng.api.crafting.IPatternDetails;
import appeng.crafting.inv.ListCraftingInventory;
import java.util.Map;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.gen.Accessor;

/** 原生任务尚未清空时读取目标余量，不使用总工序进度估算产量。 */
@Mixin(value = ExecutingCraftingJob.class, remap = false)
public interface Hk3ExactExecutingJobAccess {
    @Accessor("remainingAmount")
    long hk3gtl$remainingAmount();

    @Accessor("remainingAmount")
    void hk3gtl$remainingAmount(long amount);

    @Accessor("tasks")
    Map<IPatternDetails, Object> hk3gtl$tasks();

    @Accessor("waitingFor")
    ListCraftingInventory hk3gtl$waitingFor();
}
