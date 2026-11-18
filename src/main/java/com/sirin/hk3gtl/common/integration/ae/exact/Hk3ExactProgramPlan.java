package com.sirin.hk3gtl.common.integration.ae.exact;

import appeng.api.crafting.IPatternDetails;
import appeng.api.networking.crafting.ICraftingPlan;
import appeng.api.stacks.GenericStack;
import appeng.api.stacks.KeyCounter;
import com.sirin.hk3gtl.common.integration.ae.Hk3CraftingCycleFlag;

import java.math.BigInteger;
import java.util.List;
import java.util.Map;

/** 只有附带可执行见证的计划，才交给严格顺序 CPU 路径。 */
public record Hk3ExactProgramPlan(ICraftingPlan delegate,
        List<Hk3ExactPlanner.Step<IPatternDetails>> execution, long targetSeed)
        implements ICraftingPlan, Hk3ExactBytePlan, Hk3CraftingCycleFlag {
    public Hk3ExactProgramPlan {
        execution = List.copyOf(execution);
        Hk3ExactCpuProgram.validate(execution);
        if (targetSeed < 0 || execution.isEmpty()) throw new IllegalArgumentException("程序或目标种子无效");
        Map<IPatternDetails, BigInteger> counts = Hk3ExactBoundPattern.nativeCounts(
                new Hk3ExactProgramCursor<>(execution).remainingCounts());
        if (counts.size() != delegate.patternTimes().size() || counts.entrySet().stream().anyMatch(entry ->
                !entry.getValue().equals(BigInteger.valueOf(delegate.patternTimes().getOrDefault(entry.getKey(), 0L)))))
            throw new IllegalArgumentException("执行见证与真实样板次数不一致");
        Math.addExact(targetSeed, delegate.finalOutput().amount());
    }

    public BigInteger exactBytes() { return Hk3ExactCpuCapacity.requiredBytes(delegate); }
    public GenericStack finalOutput() { return delegate.finalOutput(); }
    public long bytes() { return delegate.bytes(); }
    public boolean simulation() { return delegate.simulation(); }
    public boolean multiplePaths() { return delegate.multiplePaths(); }
    public KeyCounter usedItems() { return delegate.usedItems(); }
    public KeyCounter emittedItems() { return delegate.emittedItems(); }
    public KeyCounter missingItems() { return delegate.missingItems(); }
    public Map<IPatternDetails, Long> patternTimes() { return delegate.patternTimes(); }
    public boolean hk3gtl$hasCycles() { return ((Hk3CraftingCycleFlag) delegate).hk3gtl$hasCycles(); }
    public void hk3gtl$setHasCycles(boolean value) { ((Hk3CraftingCycleFlag) delegate).hk3gtl$setHasCycles(value); }
}
