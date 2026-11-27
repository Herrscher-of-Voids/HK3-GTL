package com.sirin.hk3gtl.common.integration.ae.nexus.crafting;

import appeng.api.config.Actionable;
import appeng.api.crafting.IPatternDetails;
import appeng.api.networking.crafting.ICraftingProvider;
import appeng.api.networking.crafting.ICraftingRequester;
import appeng.api.networking.security.IActionSource;
import appeng.api.stacks.AEItemKey;
import appeng.api.stacks.AEKey;
import appeng.crafting.CraftingLink;
import appeng.crafting.execution.CraftingCpuHelper;
import appeng.crafting.pattern.AEProcessingPattern;
import com.sirin.hk3gtl.common.integration.ae.exact.Hk3ExactPlanner;
import com.sirin.hk3gtl.common.integration.ae.exact.Hk3ExactScaledPattern;
import com.sirin.hk3gtl.common.integration.ae.exact.Hk3ProbabilityOrderService;
import com.sirin.hk3gtl.common.integration.ae.exact.Hk3ProbabilitySupport;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.nbt.ListTag;
import net.minecraft.nbt.Tag;
import net.minecraft.world.level.Level;
import org.gtlcore.gtlcore.common.item.VirtualIngredientBehavior;
import org.gtlcore.gtlcore.common.machine.multiblock.part.ae.MEPatternBufferPartMachineBase;
import org.gtlcore.gtlcore.integration.ae2.AEUtils;
import org.gtlcore.gtlcore.integration.ae2.crafting.CraftingPatternAutoExpand;
import org.gtlcore.gtlcore.integration.ae2.crafting.IPatternProviderAutoExpand;
import org.gtlcore.gtlcore.integration.ae2.graph.GraphDispatchContext;
import org.gtlcore.gtlcore.integration.ae2.graph.GraphDispatchPreflight;

import java.math.BigInteger;
import java.util.ArrayDeque;
import java.util.ArrayList;
import java.util.Collections;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.UUID;
import net.minecraft.server.level.ServerLevel;
import com.sirin.hk3gtl.common.integration.ae.exact.Hk3ExactCpuTracker;

final class Hk3NexusJob {
    record Phase(List<Hk3NexusRecipe> recipes, BigInteger repetitions) {}

    final Hk3NexusCrafting host;
    final UUID id, owner;
    final AEKey target;
    BigInteger requested;
    final Hk3NexusCrafting.NexusCpu cpu;
    CraftingLink link;
    final Map<AEKey, BigInteger> held = new LinkedHashMap<>();
    final Map<AEKey, BigInteger> waiting = new LinkedHashMap<>();
    final Map<AEKey, BigInteger> reservation = new LinkedHashMap<>();
    final Map<AEKey, BigInteger> missing = new LinkedHashMap<>();
    final Map<AEKey, BigInteger> probabilityNeeds = new LinkedHashMap<>();
    boolean probabilityTarget, probabilityReceipt;
    final Map<Hk3NexusRecipe, BigInteger> tasks = new LinkedHashMap<>();
    final ArrayDeque<Phase> phases = new ArrayDeque<>();
    BigInteger bytes = BigInteger.ZERO, delivered = BigInteger.ZERO, totalOperations = BigInteger.ZERO;
    BigInteger rounds = BigInteger.ZERO;
    int recipe;
    boolean processingPhase;
    long ticks, retryAt;
    Map<AEKey, BigInteger> previousMissingStock = Map.of();
    Hk3NexusCrafting.Calculation calculation;
    Hk3NexusCrafting.PlanningCapture capture;
    Hk3NexusProbabilityRun probability;
    UUID batchToken;
    boolean cancelUnsettled;
    java.util.concurrent.Future<Hk3NexusCrafting.Solved> planning;
    Hk3NexusPlanSummary missingPreview;
    Hk3NexusPlanSummary.Cycle cycle;
    boolean ordered, planned, canceled, flexible, confirmed = true, paused;
    String state = "PLANNING", dispatchNote = "";

    Hk3NexusJob(Hk3NexusCrafting host, UUID id, UUID owner, AEKey target, BigInteger requested,
            boolean standalone) {
        this.host = host;
        this.id = id;
        this.owner = owner;
        this.target = target;
        this.requested = requested;
        cpu = new Hk3NexusCrafting.NexusCpu(host, this);
        link = new CraftingLink(CraftingCpuHelper.generateLinkData(id, standalone, false), cpu);
    }

    void initialize(Map<IPatternDetails, Hk3NexusRecipe> recipes,
            Hk3ExactPlanner.DetailedResult<AEKey, IPatternDetails> detailed) {
        bytes = detailed.result().logicalBytes();
        reservation.putAll(detailed.result().stockUsed());
        ordered = detailed.orderedExecutionRequired();
        var batches = detailed.result().batches();
        if (ordered) batches.forEach((pattern, amount) -> tasks.put(recipes.get(pattern), amount));
        else {
            var patterns = new ArrayList<>(batches.keySet());
            for (int i = patterns.size() - 1; i >= 0; i--) {
                var pattern = patterns.get(i);
                tasks.put(recipes.get(pattern), batches.get(pattern));
            }
        }
        if (ordered) for (var step : detailed.execution()) phases.add(new Phase(step.recipes().stream().map(recipes::get).toList(), step.repetitions()));
        totalOperations = tasks.values().stream().reduce(BigInteger.ZERO, BigInteger::add);
        rounds = phases.isEmpty() ? BigInteger.ZERO : phases.getFirst().repetitions();
        planned = true;
        state = "RESERVING";
        if (calculation == null) host.changed();
    }

    void cancelPlanning() {
        if (planning != null) planning.cancel(true);
        planning = null;
        capture = null;
    }

    void clearWork() {
        tasks.clear();
        phases.clear();
        reservation.clear();
        for (var key : waiting.keySet()) host.unindexOutput(key, this);
        waiting.clear();
    }

    boolean tick(long deadline) {
        ticks++;
        if (batchToken != null) {
            var level = (ServerLevel) host.level();
            if (Hk3ExactCpuTracker.freezeRequested(level, batchToken)) return false;
            if (!canceled && Hk3ExactCpuTracker.cancelRequested(level, batchToken)) host.cancel(id);
        }
        if (link.isCanceled() && !canceled) host.cancel(id);
        if (canceled) {
            clearWork();
            if (probability != null && probability.child != null) probability.tick(this);
            return false;
        }
        if (paused) { state = "PAUSED"; return false; }
        if (state.equals("DRAINING")) return false;
        if (probability != null && probability.index < probability.routes.size()) { probability.tick(this); return false; }
        if (!planned) {
            host.plan(this, deadline);
            return false;
        }
        if (!confirmed) return false;
        if (!reservation.isEmpty()) {
            missing.clear();
            var entries = reservation.entrySet().iterator();
            while (entries.hasNext()) {
                var entry = entries.next();
                var key = entry.getKey();
                BigInteger extracted = host.extract(key, entry.getValue(), deadline);
                var left = entry.getValue().subtract(extracted);
                if (extracted.signum() > 0) {
                    Hk3NexusLedger.add(held, key, extracted);
                    if (left.signum() == 0) entries.remove();
                    else entry.setValue(left);
                    host.changed();
                }
                if (left.signum() > 0) missing.put(key, left);
                if (System.nanoTime() >= deadline) return false;
            }
            if (!reservation.isEmpty()) { state = "MISSING_INPUT"; return false; }
        }
        return advance(deadline);
    }

    boolean advance(long deadline) {
        state = "RUNNING";
        missing.clear();
        boolean advanced = ordered ? executeOrdered(deadline) : executeUnordered(deadline);
        if (tasks.isEmpty() && waiting.isEmpty()) {
            state = "DRAINING";
        } else if (!advanced) {
            state = waiting.isEmpty() ? "WAITING_MACHINE" : "WAITING_OUTPUT";
        }
        return advanced && !tasks.isEmpty();
    }

    private void finishBatch(boolean success) {
        if (batchToken == null) return;
        Hk3ExactCpuTracker.finished((ServerLevel) host.level(), batchToken, success,
                cancelUnsettled ? -1L : delivered.longValueExact());
        batchToken = null;
        host.changed();
    }

    private boolean executeUnordered(long deadline) {
        for (int remaining = tasks.size(); remaining > 0 && System.nanoTime() < deadline; remaining--) {
            var entry = tasks.entrySet().iterator().next();
            var part = entry.getKey();
            var count = entry.getValue();
            var done = part.molecular() ? executeMolecular(List.of(part), count) : dispatch(part, count, deadline);
            if (done.signum() > 0) return true;
            tasks.remove(part);
            tasks.put(part, count);
        }
        return false;
    }

    private boolean executeOrdered(long deadline) {
        if (phases.isEmpty()) return false;
        var step = phases.getFirst();
        if (rounds.signum() == 0) {
            if (!waiting.isEmpty()) return false;
            nextPhase();
            return true;
        }
        var current = step.recipes().get(recipe);
        boolean parallel = step.recipes().size() == 1 && !current.molecular()
                && Collections.disjoint(current.inputs.keySet(), current.outputs.keySet());
        if (!waiting.isEmpty() && !(parallel && processingPhase)) return false;
        if (recipe == 0 && step.recipes().stream().allMatch(Hk3NexusRecipe::molecular)) {
            BigInteger done = executeMolecular(step.recipes(), rounds);
            if (done.signum() == 0) return false;
            rounds = rounds.subtract(done);
            if (rounds.signum() == 0) nextPhase();
            return true;
        }
        BigInteger limit = step.recipes().size() == 1 ? rounds : BigInteger.ONE;
        BigInteger pushed = current.molecular()
                ? executeMolecular(List.of(current), BigInteger.ONE) : dispatch(current, limit, deadline);
        if (pushed.signum() == 0) return false;
        processingPhase = parallel;
        if (++recipe == step.recipes().size()) {
            recipe = 0;
            rounds = rounds.subtract(pushed);
            if (rounds.signum() == 0 && waiting.isEmpty()) nextPhase();
        }
        return true;
    }

    private void nextPhase() {
        phases.removeFirst();
        recipe = 0;
        processingPhase = false;
        rounds = phases.isEmpty() ? BigInteger.ZERO : phases.getFirst().repetitions();
    }

    private BigInteger executeMolecular(List<Hk3NexusRecipe> sequence, BigInteger count) {
        Map<AEKey, BigInteger> net = new LinkedHashMap<>(), seed = new LinkedHashMap<>();
        for (var part : sequence) {
            var effective = flexible ? new Hk3NexusRecipe(part.pattern,
                    key -> held.getOrDefault(key, BigInteger.ZERO)) : part;
            for (var input : effective.inputs.entrySet()) {
                var key = input.getKey();
                var amount = input.getValue();
                var required = amount.subtract(net.getOrDefault(key, BigInteger.ZERO));
                var stock = held.getOrDefault(key, BigInteger.ZERO);
                if (required.compareTo(stock) > 0) {
                    missing.put(key, required.subtract(stock));
                    return BigInteger.ZERO;
                }
                seed.merge(key, required.max(BigInteger.ZERO), BigInteger::max);
                Hk3NexusLedger.add(net, key, amount.negate());
            }
            effective.assemble(effective.grouped, host.level()).forEach((key, amount) -> Hk3NexusLedger.add(net, key, amount));
        }
        BigInteger available = count;
        for (var entry : seed.entrySet()) {
            BigInteger stock = held.getOrDefault(entry.getKey(), BigInteger.ZERO);
            BigInteger delta = net.getOrDefault(entry.getKey(), BigInteger.ZERO);
            if (delta.signum() < 0) available = available.min(stock.subtract(entry.getValue()).divide(delta.negate()).add(BigInteger.ONE));
        }
        BigInteger completed = available;
        net.forEach((key, amount) -> Hk3NexusLedger.add(held, key, amount.multiply(completed)));
        sequence.forEach(part -> decrement(part, completed));
        host.changed();
        return completed;
    }

    private BigInteger dispatch(Hk3NexusRecipe part, BigInteger limit, long deadline) {
        var effective = flexible ? new Hk3NexusRecipe(part.pattern,
                key -> held.getOrDefault(key, BigInteger.ZERO)) : part;
        dispatchNote = "";
        boolean recirculating = effective.inputs.keySet().stream().anyMatch(effective.outputs::containsKey);
        boolean externalBatch = effective.pattern instanceof AEProcessingPattern
                && effective.pattern.supportsPushInputsToExternalInventory()
                && effective.inputs.keySet().stream().noneMatch(key -> AEUtils.isIntegratedCircuit(key)
                        || key instanceof AEItemKey item && VirtualIngredientBehavior.isMarked(item.getReadOnlyStack()));
        if (recirculating) dispatchNote = "样板有同键回流，逐批保留周转物资";
        BigInteger ready = recirculating ? BigInteger.ONE : limit;
        BigInteger perPush = BigInteger.valueOf(Long.MAX_VALUE);
        for (var entry : effective.inputs.entrySet()) {
            BigInteger available = held.getOrDefault(entry.getKey(), BigInteger.ZERO);
            if (available.compareTo(entry.getValue()) < 0) {
                missing.put(entry.getKey(), entry.getValue().subtract(available));
                return BigInteger.ZERO;
            }
            ready = ready.min(available.divide(entry.getValue()));
            perPush = perPush.min(BigInteger.valueOf(Long.MAX_VALUE).divide(entry.getValue()));
        }
        for (BigInteger amount : effective.outputs.values())
            perPush = perPush.min(BigInteger.valueOf(Long.MAX_VALUE).divide(amount));
        BigInteger dispatched = BigInteger.ZERO;
        Map<AEKey, Long> inputs = new LinkedHashMap<>();
        if (!recirculating) effective.inputs.forEach((key, amount) -> inputs.put(key, amount.longValueExact()));
        var turn = host.providers(part.pattern);
        for (int remaining = turn.providers.size(); remaining > 0 && dispatched.compareTo(ready) < 0
                && System.nanoTime() < deadline; remaining--) {
            var provider = turn.next();
            if (provider == host || provider.isBusy()) continue;
            if (Hk3ProbabilitySupport.AVAILABLE && !Collections.disjoint(effective.outputs.keySet(),
                    Hk3ProbabilityOrderService.rolledOutputs(provider, part.pattern))) continue;
            long operations = 1;
            boolean patternBuffer = provider instanceof MEPatternBufferPartMachineBase;
            if (!recirculating && (patternBuffer || externalBatch)) {
                BigInteger divisor = BigInteger.valueOf(remaining);
                BigInteger share = ready.subtract(dispatched).add(divisor).subtract(BigInteger.ONE).divide(divisor);
                operations = push(provider, effective, inputs, share.min(perPush).longValueExact(), patternBuffer);
            } else if (!provider.pushPattern(effective.pattern, Hk3NexusRecipe.copy(effective.grouped))) continue;
            if (operations == 0) continue;
            BigInteger count = BigInteger.valueOf(operations);
            effective.inputs.forEach((key, amount) -> Hk3NexusLedger.add(held, key, amount.multiply(count).negate()));
            effective.outputs.forEach((key, amount) -> {
                boolean first = !waiting.containsKey(key);
                Hk3NexusLedger.add(waiting, key, amount.multiply(count));
                if (first) host.indexOutput(key, this);
            });
            dispatched = dispatched.add(count);
        }
        if (dispatched.signum() > 0) {
            decrement(part, dispatched);
            host.changed();
        }
        return dispatched;
    }

    private long push(ICraftingProvider provider, Hk3NexusRecipe recipe, Map<AEKey, Long> inputs, long limit,
            boolean patternBuffer) {
        var pattern = recipe.pattern;
        boolean nativeBatch = limit > 1 && (patternBuffer || CraftingPatternAutoExpand.canAutoExpand(true, provider));
        long operations = limit;
        if (provider instanceof GraphDispatchPreflight preflight) {
            if (!preflight.gtlcore$canProduceGraphPattern(pattern)) return 0;
            operations = Math.min(operations, preflight.gtlcore$graphCapacity(pattern, inputs, operations));
        }
        if (operations <= 0) return 0;
        if (operations > 1 && nativeBatch && provider instanceof IPatternProviderAutoExpand expand) {
            long cap = operations;
            operations = GraphDispatchContext.call(inputs, cap, () -> expand.gtlcore$getMaxPatternOperations(recipe.pattern, cap));
            if (operations <= 0) return 0;
            operations = Math.min(cap, operations);
        }
        if (!(nativeBatch && (provider instanceof IPatternProviderAutoExpand || provider instanceof GraphDispatchPreflight))) {
            var scaled = Hk3ExactScaledPattern.forDispatch(pattern, operations);
            operations = Hk3ExactScaledPattern.operations(scaled);
            pattern = Hk3ExactScaledPattern.providerPattern(scaled);
        }
        if (pushBatch(provider, recipe, inputs, pattern, operations)) return operations;
        if (operations == 1 || !pushBatch(provider, recipe, inputs, recipe.pattern, 1)) return 0;
        dispatchNote = "供给器拒绝批量，已改为单次派单";
        return 1;
    }

    private static boolean pushBatch(ICraftingProvider provider, Hk3NexusRecipe recipe, Map<AEKey, Long> inputs,
            IPatternDetails pattern, long operations) {
        var grouped = Hk3NexusRecipe.scaledInputs(recipe.grouped, operations);
        return provider instanceof GraphDispatchPreflight
                ? GraphDispatchContext.call(inputs, operations, () -> provider.pushPattern(pattern, grouped))
                : provider.pushPattern(pattern, grouped);
    }

    private void decrement(Hk3NexusRecipe part, BigInteger count) {
        BigInteger remaining = tasks.get(part).subtract(count);
        if (remaining.signum() == 0) tasks.remove(part); else tasks.put(part, remaining);
    }

    boolean awaitsOutput() { return !waiting.isEmpty() && !canceled && !link.isCanceled(); }

    long insert(AEKey key, long amount, Actionable mode) {
        if (!awaitsOutput()) return 0;
        long accepted = Hk3NexusLedger.project(waiting.getOrDefault(key, BigInteger.ZERO).min(BigInteger.valueOf(amount)));
        if (mode == Actionable.MODULATE && accepted > 0) {
            BigInteger received = BigInteger.valueOf(accepted);
            Hk3NexusLedger.add(waiting, key, received.negate());
            if (!waiting.containsKey(key)) host.unindexOutput(key, this);
            Hk3NexusLedger.add(held, key, received);
            host.changed();
        }
        return accepted;
    }

    boolean returning() {
        return (canceled || !paused && state.equals("DRAINING")) && active()
                && (batchToken == null || !Hk3ExactCpuTracker.freezeRequested((ServerLevel) host.level(), batchToken));
    }

    boolean delivering(AEKey key) {
        return !canceled && target.equals(key) && delivered.compareTo(requested) < 0;
    }

    void finishReturns() {
        if (canceled) {
            if (probability != null && probability.child != null) return;
            state = "CANCELED";
        } else {
            if (!delivered.equals(requested)) return;
            state = "DONE";
            if (!link.isDone()) link.markDone();
        }
        finishBatch(!canceled);
        host.changed();
    }

    boolean active() { return !state.equals("DONE") && !state.equals("CANCELED") && !state.equals("PROBABILITY_STOPPED"); }

    CompoundTag write() {
        CompoundTag tag = new CompoundTag();
        tag.putUUID("id", id); tag.putUUID("owner", owner); tag.put("target", target.toTagGeneric());
        tag.putByteArray("requested", requested.toByteArray()); tag.putByteArray("delivered", delivered.toByteArray());
        tag.putByteArray("bytes", bytes.toByteArray()); tag.putByteArray("operations", totalOperations.toByteArray());
        tag.putLong("ticks", ticks); tag.putString("state", state);
        if (state.equals("PROBABILITY_STOPPED")) tag.putString("dispatchNote", dispatchNote);
        tag.putBoolean("planned", planned); tag.putBoolean("ordered", ordered); tag.putBoolean("canceled", canceled);
        tag.putBoolean("flexible", flexible);
        tag.putBoolean("confirmed", confirmed); tag.putBoolean("paused", paused);
        tag.put("held", Hk3NexusLedger.write(held)); tag.put("waiting", Hk3NexusLedger.write(waiting));
        tag.put("reservation", Hk3NexusLedger.write(reservation)); tag.put("missing", Hk3NexusLedger.write(missing));
        if (probability != null) tag.put("probability", probability.save());
        if (probabilityReceipt) tag.putBoolean("probabilityReceipt", true);
        if (batchToken != null) { tag.putUUID("batchToken", batchToken); tag.putBoolean("cancelUnsettled", cancelUnsettled); }
        CompoundTag linkTag = new CompoundTag(); link.writeToNBT(linkTag); tag.put("link", linkTag);
        Map<Hk3NexusRecipe, Integer> indices = new LinkedHashMap<>();
        tasks.keySet().forEach(part -> indices.computeIfAbsent(part, ignored -> indices.size()));
        phases.forEach(step -> step.recipes().forEach(part -> indices.computeIfAbsent(part, ignored -> indices.size())));
        ListTag recipes = new ListTag();
        indices.keySet().forEach(part -> {
            CompoundTag row = part.write();
            row.putByteArray("remaining", tasks.getOrDefault(part, BigInteger.ZERO).toByteArray());
            recipes.add(row);
        });
        tag.put("recipes", recipes);
        ListTag program = new ListTag();
        for (Phase step : phases) {
            CompoundTag row = new CompoundTag();
            row.putIntArray("recipes", step.recipes().stream().mapToInt(indices::get).toArray());
            row.putByteArray("count", step.repetitions().toByteArray());
            program.add(row);
        }
        tag.put("program", program); tag.putInt("recipe", recipe);
        tag.putByteArray("rounds", rounds.toByteArray());
        tag.putBoolean("processingPhase", processingPhase);
        return tag;
    }

    static Hk3NexusJob read(Hk3NexusCrafting host, CompoundTag tag) {
        var job = new Hk3NexusJob(host, tag.getUUID("id"), tag.getUUID("owner"), AEKey.fromTagGeneric(tag.getCompound("target")),
                new BigInteger(tag.getByteArray("requested")), tag.getCompound("link").getBoolean("standalone"));
        job.delivered = new BigInteger(tag.getByteArray("delivered")); job.bytes = new BigInteger(tag.getByteArray("bytes"));
        job.totalOperations = new BigInteger(tag.getByteArray("operations")); job.ticks = tag.getLong("ticks");
        job.state = tag.getString("state"); job.planned = tag.getBoolean("planned"); job.ordered = tag.getBoolean("ordered");
        job.dispatchNote = tag.getString("dispatchNote");
        job.canceled = tag.getBoolean("canceled");
        job.flexible = tag.getBoolean("flexible");
        job.confirmed = tag.getBoolean("confirmed"); job.paused = tag.getBoolean("paused");
        job.link = new CraftingLink(tag.getCompound("link"), job.cpu);
        job.held.putAll(Hk3NexusLedger.read(tag.getList("held", Tag.TAG_COMPOUND)));
        job.waiting.putAll(Hk3NexusLedger.read(tag.getList("waiting", Tag.TAG_COMPOUND)));
        job.reservation.putAll(Hk3NexusLedger.read(tag.getList("reservation", Tag.TAG_COMPOUND)));
        job.missing.putAll(Hk3NexusLedger.read(tag.getList("missing", Tag.TAG_COMPOUND)));
        if (tag.contains("probability")) job.probability = Hk3NexusProbabilityRun.read(tag.getCompound("probability"));
        if (tag.hasUUID("batchToken")) { job.batchToken = tag.getUUID("batchToken"); job.cancelUnsettled = tag.getBoolean("cancelUnsettled"); }
        List<Hk3NexusRecipe> recipes = new ArrayList<>();
        for (Tag element : tag.getList("recipes", Tag.TAG_COMPOUND)) {
            CompoundTag row = (CompoundTag) element;
            var part = Hk3NexusRecipe.read(row, host.level()); recipes.add(part);
            BigInteger remaining = new BigInteger(row.getByteArray("remaining"));
            if (remaining.signum() > 0) job.tasks.put(part, remaining);
        }
        var program = tag.getList("program", Tag.TAG_COMPOUND);
        for (int i = tag.getInt("phase"); i < program.size(); i++) {
            CompoundTag row = program.getCompound(i);
            List<Hk3NexusRecipe> parts = new ArrayList<>();
            for (int index : row.getIntArray("recipes")) parts.add(recipes.get(index));
            job.phases.add(new Phase(parts, new BigInteger(row.getByteArray("count"))));
        }
        job.recipe = tag.getInt("recipe");
        job.rounds = new BigInteger(tag.getByteArray("rounds"));
        job.processingPhase = tag.getBoolean("processingPhase");
        job.probabilityReceipt = tag.getBoolean("probabilityReceipt");
        if ((job.probability != null || job.probabilityReceipt) && com.sirin.hk3gtl.common.integration.ae.exact.Hk3ProbabilitySupport.AVAILABLE)
            Hk3NexusProbabilityRun.restore(job);
        return job;
    }
}
