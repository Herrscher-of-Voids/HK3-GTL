package com.sirin.hk3gtl.common.integration.ae.exact;

import appeng.api.crafting.IPatternDetails;
import appeng.api.networking.crafting.ICraftingPlan;
import appeng.api.stacks.GenericStack;
import appeng.api.stacks.KeyCounter;
import com.sirin.hk3gtl.common.integration.ae.Hk3CraftingCycleFlag;

import java.math.BigInteger;
import java.util.Map;

/** 扩展单任务的字节需求，原生物料、样板次数和执行进度仍保留 long 边界。 */
public record Hk3ExactCapacityPlan(ICraftingPlan delegate, BigInteger exactBytes)
        implements ICraftingPlan, Hk3ExactBytePlan, Hk3CraftingCycleFlag {
    public Hk3ExactCapacityPlan {
        if (exactBytes.signum() < 0) throw new IllegalArgumentException("计划字节数不能为负数");
    }

    @Override public GenericStack finalOutput() { return delegate.finalOutput(); }
    @Override public long bytes() { return Hk3ExactCpuCapacity.project(exactBytes); }
    @Override public boolean simulation() { return delegate.simulation(); }
    @Override public boolean multiplePaths() { return delegate.multiplePaths(); }
    @Override public KeyCounter usedItems() { return delegate.usedItems(); }
    @Override public KeyCounter emittedItems() { return delegate.emittedItems(); }
    @Override public KeyCounter missingItems() { return delegate.missingItems(); }
    @Override public Map<IPatternDetails, Long> patternTimes() { return delegate.patternTimes(); }
    @Override public boolean hk3gtl$hasCycles() { return ((Hk3CraftingCycleFlag) delegate).hk3gtl$hasCycles(); }
    @Override public void hk3gtl$setHasCycles(boolean value) { ((Hk3CraftingCycleFlag) delegate).hk3gtl$setHasCycles(value); }
}
