package com.sirin.hk3gtl.common.integration.ae.nexus.crafting;

import appeng.api.crafting.IPatternDetails;
import appeng.api.networking.crafting.ICraftingPlan;
import appeng.api.stacks.AEKey;
import appeng.api.stacks.GenericStack;
import appeng.api.stacks.KeyCounter;
import com.sirin.hk3gtl.common.integration.ae.exact.Hk3ExactBytePlan;

import java.math.BigInteger;
import java.util.LinkedHashMap;
import java.util.Map;

public final class Hk3NexusNativePlan implements ICraftingPlan, Hk3ExactBytePlan {
    final Hk3NexusJob preview;

    Hk3NexusNativePlan(Hk3NexusJob preview) { this.preview = preview; }

    public Hk3NexusCrafting host() { return preview.host; }
    public AEKey target() { return preview.target; }
    public BigInteger amount() { return preview.requested; }
    @Override public BigInteger exactBytes() { return preview.bytes; }
    @Override public GenericStack finalOutput() { return new GenericStack(target(), Hk3NexusLedger.project(amount())); }
    @Override public long bytes() { return Hk3NexusLedger.project(exactBytes()); }
    @Override public boolean simulation() { return !preview.planned; }
    @Override public boolean multiplePaths() { return false; }
    @Override public KeyCounter usedItems() { return project(preview.reservation); }
    @Override public KeyCounter emittedItems() { return new KeyCounter(); }
    @Override public KeyCounter missingItems() { return project(preview.missing); }

    @Override public Map<IPatternDetails, Long> patternTimes() {
        Map<IPatternDetails, BigInteger> exact = new LinkedHashMap<>();
        preview.tasks.forEach((recipe, count) -> exact.merge(recipe.pattern, count, BigInteger::add));
        Map<IPatternDetails, Long> projected = new LinkedHashMap<>();
        exact.forEach((pattern, count) -> projected.put(pattern, Hk3NexusLedger.project(count)));
        return projected;
    }

    private static KeyCounter project(Map<AEKey, BigInteger> amounts) {
        KeyCounter result = new KeyCounter();
        amounts.forEach((key, amount) -> result.add(key, Hk3NexusLedger.project(amount)));
        return result;
    }

    public Hk3NexusPlanSummary summary() { return Hk3NexusPlanSummary.of(preview); }
}
