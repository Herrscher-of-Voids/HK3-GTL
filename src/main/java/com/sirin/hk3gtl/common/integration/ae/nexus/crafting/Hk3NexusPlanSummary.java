package com.sirin.hk3gtl.common.integration.ae.nexus.crafting;

import appeng.api.crafting.IPatternDetails;
import appeng.api.stacks.AEKey;
import appeng.menu.me.crafting.CraftingPlanSummary;
import appeng.menu.me.crafting.CraftingPlanSummaryEntry;
import com.sirin.hk3gtl.common.integration.ae.Hk3CraftingCycleFlag;
import net.minecraft.network.FriendlyByteBuf;
import net.minecraftforge.fml.ModList;
import org.gtlcore.gtlcore.integration.ae2.crafting.ICraftingPlanSummaryEntry;
import org.gtlcore.gtlcore.integration.ae2.graph.GraphPlanSummaryView;

import java.math.BigInteger;
import java.util.ArrayList;
import java.util.Collections;
import java.util.LinkedHashMap;
import java.util.LinkedHashSet;
import java.util.List;
import java.util.Map;

public final class Hk3NexusPlanSummary extends CraftingPlanSummary {
    public final BigInteger amount, exactBytes;
    public final boolean batched;

    private Hk3NexusPlanSummary(BigInteger amount, BigInteger bytes, boolean simulation, boolean batched,
            List<CraftingPlanSummaryEntry> entries) {
        super(Hk3NexusLedger.project(bytes), simulation, entries);
        this.amount = amount;
        this.exactBytes = bytes;
        this.batched = batched;
    }

    static Hk3NexusPlanSummary of(Hk3NexusJob job) {
        return of(job, job.bytes, job.ordered, job.missing, job.tasks, job.reservation);
    }

    static Hk3NexusPlanSummary of(Hk3NexusJob job, BigInteger bytes, boolean ordered, Map<AEKey, BigInteger> missing,
            Map<Hk3NexusRecipe, BigInteger> tasks, Map<AEKey, BigInteger> stored) {
        Map<AEKey, BigInteger> crafting = new LinkedHashMap<>();
        Map<AEKey, BigInteger> operations = new LinkedHashMap<>();
        Map<IPatternDetails, BigInteger> patterns = new LinkedHashMap<>();
        tasks.forEach((recipe, count) -> recipe.outputs.forEach((key, output) -> {
            crafting.merge(key, output.multiply(count), BigInteger::add);
            operations.merge(key, count, BigInteger::add);
        }));
        tasks.forEach((recipe, count) -> patterns.merge(recipe.pattern, count, BigInteger::add));
        crafting.putIfAbsent(job.target, job.requested);
        var summary = of(job.target, job.requested, bytes, !job.planned, missing, stored, crafting, operations, patterns);
        ((Hk3CraftingCycleFlag) (Object) summary).hk3gtl$setHasCycles(ordered);
        return summary;
    }

    public static Hk3NexusPlanSummary of(AEKey target, BigInteger amount, BigInteger bytes, boolean simulation,
            Map<AEKey, BigInteger> missing, Map<AEKey, BigInteger> stored,
            Map<AEKey, BigInteger> crafting, Map<AEKey, BigInteger> operations,
            Map<IPatternDetails, BigInteger> patterns) {
        var keys = new LinkedHashSet<>(stored.keySet());
        keys.addAll(missing.keySet()); keys.addAll(crafting.keySet());
        List<CraftingPlanSummaryEntry> entries = new ArrayList<>();
        for (AEKey key : keys) entries.add(new Entry(key, missing.getOrDefault(key, BigInteger.ZERO),
                stored.getOrDefault(key, BigInteger.ZERO), crafting.getOrDefault(key, BigInteger.ZERO),
                operations.getOrDefault(key, BigInteger.ZERO)));
        Collections.sort(entries);
        var summary = new Hk3NexusPlanSummary(amount, bytes, simulation, false, entries);
        if (ModList.get().isLoaded("ae2ct"))
            Hk3NexusCraftingTree.initialize(summary, target, amount, patterns);
        return summary;
    }

    public Hk3NexusPlanSummary batched() {
        return new Hk3NexusPlanSummary(amount, exactBytes, isSimulation(), true, getEntries()).copyMetadata(this);
    }

    public static Hk3NexusPlanSummary fromGraph(CraftingPlanSummary source, BigInteger amount, BigInteger bytes) {
        return new Hk3NexusPlanSummary(amount, bytes, source.isSimulation(), false, source.getEntries())
                .copyMetadata(source);
    }

    private Hk3NexusPlanSummary copyMetadata(CraftingPlanSummary source) {
        ((Hk3CraftingCycleFlag) (Object) this).hk3gtl$setHasCycles(((Hk3CraftingCycleFlag) source).hk3gtl$hasCycles());
        var sourceGraph = (GraphPlanSummaryView) source;
        var targetGraph = (GraphPlanSummaryView) (Object) this;
        targetGraph.gtlcore$graphPlanId(sourceGraph.gtlcore$graphPlanId());
        targetGraph.gtlcore$seedOptimality(sourceGraph.gtlcore$seedOptimality());
        targetGraph.gtlcore$fallback(sourceGraph.gtlcore$fallback());
        targetGraph.gtlcore$conditionalPreview(sourceGraph.gtlcore$conditionalPreview());
        if (ModList.get().isLoaded("ae2ct")) Hk3NexusCraftingTree.copy(source, this);
        return this;
    }

    public static Entry exactEntry(CraftingPlanSummaryEntry source, BigInteger missing, BigInteger stored,
            BigInteger crafting, BigInteger operations) {
        var entry = new Entry(source.getWhat(), missing, stored, crafting, operations);
        var sourceDetails = (ICraftingPlanSummaryEntry) source;
        var targetDetails = (ICraftingPlanSummaryEntry) (Object) entry;
        targetDetails.gtlcore$setCraftTimes(sourceDetails.gtlcore$getCraftTimes());
        targetDetails.gtlcore$setGraphSeed(sourceDetails.gtlcore$getGraphSeed());
        targetDetails.gtlcore$setMissingGraphSeed(sourceDetails.gtlcore$isMissingGraphSeed());
        targetDetails.gtlcore$setGroupedToolStates(sourceDetails.gtlcore$getGroupedToolStates());
        targetDetails.gtlcore$setMissingKeys(sourceDetails.gtlcore$getMissingKeys());
        targetDetails.gtlcore$setMissingSourceMask(sourceDetails.gtlcore$getMissingSourceMask());
        return entry;
    }

    public void writeExact(FriendlyByteBuf buffer) {
        buffer.writeUtf(amount.toString()); buffer.writeUtf(exactBytes.toString()); buffer.writeBoolean(batched);
        for (var value : getEntries()) {
            Entry entry = (Entry) value;
            buffer.writeUtf(entry.missing.toString()); buffer.writeUtf(entry.stored.toString());
            buffer.writeUtf(entry.crafting.toString()); buffer.writeUtf(entry.operations.toString());
        }
    }

    public static Hk3NexusPlanSummary readExact(CraftingPlanSummary projected, FriendlyByteBuf buffer) {
        BigInteger amount = new BigInteger(buffer.readUtf()), bytes = new BigInteger(buffer.readUtf());
        boolean batched = buffer.readBoolean();
        List<CraftingPlanSummaryEntry> entries = new ArrayList<>();
        for (var entry : projected.getEntries()) entries.add(exactEntry(entry,
                new BigInteger(buffer.readUtf()), new BigInteger(buffer.readUtf()),
                new BigInteger(buffer.readUtf()), new BigInteger(buffer.readUtf())));
        return new Hk3NexusPlanSummary(amount, bytes, projected.isSimulation(), batched, entries).copyMetadata(projected);
    }

    public static final class Entry extends CraftingPlanSummaryEntry {
        public final BigInteger missing, stored, crafting, operations;

        Entry(AEKey key, BigInteger missing, BigInteger stored, BigInteger crafting, BigInteger operations) {
            super(key, Hk3NexusLedger.project(missing), Hk3NexusLedger.project(stored), Hk3NexusLedger.project(crafting));
            this.missing = missing; this.stored = stored; this.crafting = crafting; this.operations = operations;
        }
    }
}
