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
    public final Cycle cycle;

    private Hk3NexusPlanSummary(BigInteger amount, BigInteger bytes, boolean simulation, boolean batched,
            List<CraftingPlanSummaryEntry> entries, Cycle cycle) {
        super(Hk3NexusLedger.project(bytes), simulation, entries);
        this.amount = amount;
        this.exactBytes = bytes;
        this.batched = batched;
        this.cycle = cycle;
    }

    static Hk3NexusPlanSummary of(Hk3NexusJob job) {
        return of(job, job.bytes, job.missing, job.tasks, job.reservation);
    }

    static Hk3NexusPlanSummary of(Hk3NexusJob job, BigInteger bytes, Map<AEKey, BigInteger> missing,
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
        return of(job.target, job.requested, bytes, !job.planned, missing, stored, crafting, operations,
                patterns, job.cycle);
    }

    public static Hk3NexusPlanSummary of(AEKey target, BigInteger amount, BigInteger bytes, boolean simulation,
            Map<AEKey, BigInteger> missing, Map<AEKey, BigInteger> stored,
            Map<AEKey, BigInteger> crafting, Map<AEKey, BigInteger> operations,
            Map<IPatternDetails, BigInteger> patterns) {
        return of(target, amount, bytes, simulation, missing, stored, crafting, operations, patterns, null);
    }

    public static Hk3NexusPlanSummary of(AEKey target, BigInteger amount, BigInteger bytes, boolean simulation,
            Map<AEKey, BigInteger> missing, Map<AEKey, BigInteger> stored,
            Map<AEKey, BigInteger> crafting, Map<AEKey, BigInteger> operations,
            Map<IPatternDetails, BigInteger> patterns, Cycle cycle) {
        var marked = new LinkedHashSet<AEKey>();
        if (cycle != null) {
            var consumed = new LinkedHashSet<AEKey>();
            for (var step : cycle.steps()) {
                consumed.addAll(step.inputs().keySet());
                step.outputs().forEach((key, count) -> {
                    if (count.compareTo(step.inputs().getOrDefault(key, BigInteger.ZERO)) > 0) marked.add(key);
                });
            }
            marked.retainAll(consumed);
        }
        var keys = new LinkedHashSet<>(stored.keySet());
        keys.addAll(missing.keySet()); keys.addAll(crafting.keySet()); keys.addAll(marked);
        List<CraftingPlanSummaryEntry> entries = new ArrayList<>();
        for (AEKey key : keys) entries.add(new Entry(key, missing.getOrDefault(key, BigInteger.ZERO),
                stored.getOrDefault(key, BigInteger.ZERO), crafting.getOrDefault(key, BigInteger.ZERO),
                operations.getOrDefault(key, BigInteger.ZERO), marked.contains(key)));
        Collections.sort(entries);
        var summary = new Hk3NexusPlanSummary(amount, bytes, simulation, false, entries, cycle);
        ((Hk3CraftingCycleFlag) (Object) summary).hk3gtl$setHasCycles(!marked.isEmpty());
        if (ModList.get().isLoaded("ae2ct"))
            Hk3NexusCraftingTree.initialize(summary, target, amount, patterns);
        return summary;
    }

    public Hk3NexusPlanSummary batched() {
        return new Hk3NexusPlanSummary(amount, exactBytes, isSimulation(), true, getEntries(), cycle).copyMetadata(this);
    }

    public static Hk3NexusPlanSummary fromGraph(CraftingPlanSummary source, BigInteger amount, BigInteger bytes) {
        return new Hk3NexusPlanSummary(amount, bytes, source.isSimulation(), false, source.getEntries(), null)
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

    private static Entry exactEntry(CraftingPlanSummaryEntry source, BigInteger missing, BigInteger stored,
            BigInteger crafting, BigInteger operations, boolean cycle) {
        var entry = new Entry(source.getWhat(), missing, stored, crafting, operations, cycle);
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

    public static Entry exactEntry(CraftingPlanSummaryEntry source, BigInteger missing, BigInteger stored,
            BigInteger crafting, BigInteger operations) {
        return exactEntry(source, missing, stored, crafting, operations, false);
    }

    public void writeExact(FriendlyByteBuf buffer) {
        buffer.writeUtf(amount.toString()); buffer.writeUtf(exactBytes.toString()); buffer.writeBoolean(batched);
        for (var value : getEntries()) {
            Entry entry = (Entry) value;
            buffer.writeUtf(entry.missing.toString()); buffer.writeUtf(entry.stored.toString());
            buffer.writeUtf(entry.crafting.toString()); buffer.writeUtf(entry.operations.toString());
            buffer.writeBoolean(entry.cycle);
        }
        buffer.writeBoolean(cycle != null);
        if (cycle != null) cycle.write(buffer);
    }

    public static Hk3NexusPlanSummary readExact(CraftingPlanSummary projected, FriendlyByteBuf buffer) {
        BigInteger amount = new BigInteger(buffer.readUtf()), bytes = new BigInteger(buffer.readUtf());
        boolean batched = buffer.readBoolean();
        List<CraftingPlanSummaryEntry> entries = new ArrayList<>();
        for (var entry : projected.getEntries()) entries.add(exactEntry(entry,
                new BigInteger(buffer.readUtf()), new BigInteger(buffer.readUtf()),
                new BigInteger(buffer.readUtf()), new BigInteger(buffer.readUtf()), buffer.readBoolean()));
        var cycle = buffer.readBoolean() ? Cycle.read(buffer) : null;
        return new Hk3NexusPlanSummary(amount, bytes, projected.isSimulation(), batched, entries, cycle)
                .copyMetadata(projected);
    }

    private static void writeAmounts(FriendlyByteBuf buffer, Map<AEKey, BigInteger> amounts) {
        buffer.writeVarInt(amounts.size());
        amounts.forEach((key, amount) -> {
            AEKey.writeKey(buffer, key);
            buffer.writeUtf(amount.toString());
        });
    }

    private static Map<AEKey, BigInteger> readAmounts(FriendlyByteBuf buffer) {
        Map<AEKey, BigInteger> amounts = new LinkedHashMap<>();
        for (int i = buffer.readVarInt(); i > 0; i--) amounts.put(AEKey.readKey(buffer), new BigInteger(buffer.readUtf()));
        return amounts;
    }

    public record CycleStep(Map<AEKey, BigInteger> inputs, Map<AEKey, BigInteger> outputs, BigInteger batches) {}

    public record Cycle(List<CycleStep> steps, String reason, Map<AEKey, BigInteger> missing) {
        private void write(FriendlyByteBuf buffer) {
            buffer.writeUtf(reason);
            buffer.writeVarInt(steps.size());
            for (var step : steps) {
                buffer.writeUtf(step.batches().toString());
                writeAmounts(buffer, step.inputs());
                writeAmounts(buffer, step.outputs());
            }
            writeAmounts(buffer, missing);
        }

        private static Cycle read(FriendlyByteBuf buffer) {
            String reason = buffer.readUtf();
            List<CycleStep> steps = new ArrayList<>();
            for (int i = buffer.readVarInt(); i > 0; i--) {
                BigInteger batches = new BigInteger(buffer.readUtf());
                steps.add(new CycleStep(readAmounts(buffer), readAmounts(buffer), batches));
            }
            return new Cycle(steps, reason, readAmounts(buffer));
        }
    }

    public static final class Entry extends CraftingPlanSummaryEntry {
        public final BigInteger missing, stored, crafting, operations;
        public final boolean cycle;

        Entry(AEKey key, BigInteger missing, BigInteger stored, BigInteger crafting, BigInteger operations,
                boolean cycle) {
            super(key, Hk3NexusLedger.project(missing), Hk3NexusLedger.project(stored), Hk3NexusLedger.project(crafting));
            this.missing = missing; this.stored = stored; this.crafting = crafting; this.operations = operations;
            this.cycle = cycle;
        }
    }
}
