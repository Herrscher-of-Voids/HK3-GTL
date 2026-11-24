package com.sirin.hk3gtl.common.integration.ae.nexus.crafting;

import appeng.api.config.Actionable;
import appeng.api.crafting.IPatternDetails;
import appeng.api.networking.crafting.ICraftingRequester;
import appeng.api.networking.security.IActionSource;
import appeng.api.stacks.AEItemKey;
import appeng.api.stacks.AEKey;
import appeng.crafting.CraftingLink;
import appeng.crafting.execution.CraftingCpuHelper;
import appeng.crafting.pattern.AEProcessingPattern;
import appeng.me.service.CraftingService;
import com.sirin.hk3gtl.common.integration.ae.exact.Hk3ExactPlanner;
import com.sirin.hk3gtl.common.integration.ae.exact.Hk3ExactScaledPattern;
import com.sirin.hk3gtl.common.integration.ae.exact.Hk3ProbabilityOrderService;
import com.sirin.hk3gtl.common.integration.ae.exact.Hk3ProbabilitySupport;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.nbt.ListTag;
import net.minecraft.nbt.Tag;
import net.minecraft.world.level.Level;
import org.gtlcore.gtlcore.common.item.VirtualIngredientBehavior;
import org.gtlcore.gtlcore.integration.ae2.AEUtils;
import org.gtlcore.gtlcore.integration.ae2.crafting.CraftingPatternAutoExpand;

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
    int recipe, priority;
    long ticks, retryAt;
    Map<AEKey, BigInteger> previousMissingStock = Map.of();
    Hk3NexusCrafting.Calculation calculation;
    Hk3NexusCrafting.PlanningCapture capture;
    Hk3NexusProbabilityRun probability;
    UUID batchToken;
    boolean cancelUnsettled;
    java.util.concurrent.Future<Hk3NexusCrafting.Solved> planning;
    Hk3NexusPlanSummary missingPreview;
    boolean ordered, planned, canceled, flexible, confirmed = true, paused;
    String state = "PLANNING", dispatchNote = "";

    Hk3NexusJob(Hk3NexusCrafting host, UUID id, UUID owner, AEKey target, BigInteger requested,
            int priority, boolean standalone) {
        this.host = host;
        this.id = id;
        this.owner = owner;
        this.target = target;
        this.requested = requested;
        this.priority = priority;
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

    void tick(long deadline) {
        ticks++;
        if (batchToken != null) {
            var level = (ServerLevel) host.level();
            if (Hk3ExactCpuTracker.freezeRequested(level, batchToken)) return;
            if (!canceled && Hk3ExactCpuTracker.cancelRequested(level, batchToken)) host.cancel(id);
        }
        if (link.isCanceled() && !canceled) host.cancel(id);
        if (canceled) {
            if (probability != null && probability.child != null) { probability.tick(this); return; }
            cancelPlanning();
            tasks.clear();
            phases.clear();
            reservation.clear();
            waiting.clear();
            flush(false, deadline);
            state = held.isEmpty() ? "CANCELED" : "CANCELING";
            if (held.isEmpty()) finishBatch(false);
            return;
        }
        if (paused) { state = "PAUSED"; return; }
        if (probability != null && probability.index < probability.routes.size()) { probability.tick(this); return; }
        if (!planned) {
            host.plan(this, deadline);
            return;
        }
        if (!confirmed) return;
        if (!reservation.isEmpty()) {
            missing.clear();
            var entries = reservation.entrySet().iterator();
            while (entries.hasNext()) {
                var entry = entries.next();
                var key = entry.getKey();
                BigInteger extracted = host.extract(key, entry.getValue());
                var left = entry.getValue().subtract(extracted);
                if (extracted.signum() > 0) {
                    Hk3NexusLedger.add(held, key, extracted);
                    if (left.signum() == 0) entries.remove();
                    else entry.setValue(left);
                    host.changed();
                }
                if (left.signum() > 0) missing.put(key, left);
                if (System.nanoTime() >= deadline) return;
            }
            if (!reservation.isEmpty()) { state = "MISSING_INPUT"; return; }
        }
        state = "RUNNING";
        boolean advanced;
        do {
            missing.clear();
            advanced = ordered ? executeOrdered(deadline) : executeUnordered(deadline);
        } while (advanced && !tasks.isEmpty() && System.nanoTime() < deadline);
        if (tasks.isEmpty() && waiting.isEmpty()) {
            state = "DRAINING";
            flush(true, deadline);
            if (held.isEmpty() && delivered.equals(requested)) {
                state = "DONE";
                if (!link.isDone()) { link.markDone(); host.changed(); }
                finishBatch(true);
            }
        } else if (!advanced) state = waiting.isEmpty() ? "WAITING_MACHINE" : "WAITING_OUTPUT";
    }

    private void finishBatch(boolean success) {
        if (batchToken == null) return;
        Hk3ExactCpuTracker.finished((ServerLevel) host.level(), batchToken, success,
                cancelUnsettled ? -1L : delivered.longValueExact());
        batchToken = null;
        host.changed();
    }

    private boolean executeUnordered(long deadline) {
        for (var entry : tasks.entrySet()) {
            if (entry.getKey().molecular()) {
                BigInteger done = executeMolecular(List.of(entry.getKey()), entry.getValue());
                if (done.signum() > 0) return true;
            } else if (dispatch(entry.getKey(), entry.getValue(), deadline).signum() > 0) return true;
        }
        return false;
    }

    private boolean executeOrdered(long deadline) {
        if (!waiting.isEmpty() || phases.isEmpty()) return false;
        Phase step = phases.getFirst();
        if (recipe == 0 && step.recipes().stream().allMatch(Hk3NexusRecipe::molecular)) {
            BigInteger done = executeMolecular(step.recipes(), rounds);
            if (done.signum() == 0) return false;
            rounds = rounds.subtract(done);
            if (rounds.signum() == 0) nextPhase();
            return true;
        }
        Hk3NexusRecipe current = step.recipes().get(recipe);
        BigInteger limit = step.recipes().size() == 1 ? rounds : BigInteger.ONE;
        BigInteger pushed = current.molecular()
                ? executeMolecular(List.of(current), BigInteger.ONE) : dispatch(current, limit, deadline);
        if (pushed.signum() == 0) return false;
        if (++recipe == step.recipes().size()) {
            recipe = 0;
            rounds = rounds.subtract(pushed);
            if (rounds.signum() == 0) nextPhase();
        }
        return true;
    }

    private void nextPhase() {
        phases.removeFirst();
        recipe = 0;
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
        if (!(effective.pattern instanceof AEProcessingPattern) || !effective.pattern.supportsPushInputsToExternalInventory()) {
            dispatchNote = "供给器接口不支持批量加工";
        } else if (recirculating) {
            dispatchNote = "样板有同键回流，逐批保留周转物资";
        } else if (effective.inputs.keySet().stream().anyMatch(key -> AEUtils.isIntegratedCircuit(key)
                || key instanceof AEItemKey item && VirtualIngredientBehavior.isMarked(item.getReadOnlyStack()))) {
            dispatchNote = "含配置电路或虚拟原料，按供给器原生路径发料";
        }
        boolean batchable = dispatchNote.isEmpty();
        BigInteger maxTransfer = BigInteger.valueOf(Long.MAX_VALUE);
        BigInteger total = BigInteger.ZERO;
        var service = (CraftingService) host.grid().getCraftingService();
        for (var provider : service.getProviders(part.pattern)) {
            if (System.nanoTime() >= deadline || total.equals(limit)) break;
            if (provider == host || provider.isBusy()) continue;
            if (Hk3ProbabilitySupport.AVAILABLE && !Collections.disjoint(effective.outputs.keySet(),
                    Hk3ProbabilityOrderService.rolledOutputs(provider, part.pattern))) continue;
            BigInteger max = batchable ? limit.subtract(total).min(maxTransfer) : BigInteger.ONE;
            for (var entry : effective.inputs.entrySet()) {
                BigInteger available = held.getOrDefault(entry.getKey(), BigInteger.ZERO);
                if (available.compareTo(entry.getValue()) < 0) {
                    if (total.signum() == 0) missing.put(entry.getKey(), entry.getValue().subtract(available));
                    return total;
                }
                max = max.min(available.min(maxTransfer).divide(entry.getValue()));
            }
            for (BigInteger amount : effective.outputs.values()) max = max.min(maxTransfer.divide(amount));
            long cap = Math.max(1, max.longValueExact());
            long operations = cap > 1 ? CraftingPatternAutoExpand.getOperations(true, provider, effective.pattern, cap) : 1;
            IPatternDetails pattern = effective.pattern;
            if (operations == 1 && cap > 1) {
                var scaled = Hk3ExactScaledPattern.forDispatch(pattern, cap);
                operations = Hk3ExactScaledPattern.operations(scaled);
                pattern = Hk3ExactScaledPattern.providerPattern(scaled);
            }
            if (!provider.pushPattern(pattern, Hk3NexusRecipe.scaledInputs(effective.grouped, operations))) {
                if (operations == 1 || !provider.pushPattern(effective.pattern, Hk3NexusRecipe.copy(effective.grouped))) continue;
                dispatchNote = "供给器拒绝批量，已改为单次派单";
                operations = 1;
            }
            BigInteger count = BigInteger.valueOf(operations);
            effective.inputs.forEach((key, amount) -> Hk3NexusLedger.add(held, key, amount.multiply(count).negate()));
            effective.outputs.forEach((key, amount) -> Hk3NexusLedger.add(waiting, key, amount.multiply(count)));
            decrement(part, count);
            host.changed();
            total = total.add(count);
        }
        return total;
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
            Hk3NexusLedger.add(waiting, key, BigInteger.valueOf(accepted).negate());
            Hk3NexusLedger.add(held, key, BigInteger.valueOf(accepted));
            host.changed();
        }
        return accepted;
    }

    private void flush(boolean deliverTarget, long deadline) {
        if (deliverTarget && delivered.compareTo(requested) < 0) {
            BigInteger amount = held.getOrDefault(target, BigInteger.ZERO).min(requested.subtract(delivered));
            BigInteger accepted = link.isStandalone() ? host.insert(target, amount)
                    : BigInteger.valueOf(link.insert(target, Hk3NexusLedger.project(amount), Actionable.MODULATE));
            if (accepted.signum() > 0) {
                Hk3NexusLedger.add(held, target, accepted.negate());
                delivered = delivered.add(accepted);
                host.changed();
            }
            if (!delivered.equals(requested)) return;
        }
        for (var entry : List.copyOf(held.entrySet())) {
            BigInteger accepted = host.insert(entry.getKey(), entry.getValue());
            if (accepted.signum() > 0) {
                Hk3NexusLedger.add(held, entry.getKey(), accepted.negate());
                host.changed();
            }
            if (System.nanoTime() >= deadline) return;
        }
    }

    boolean active() { return !state.equals("DONE") && !state.equals("CANCELED") && !state.equals("PROBABILITY_STOPPED"); }

    CompoundTag write() {
        CompoundTag tag = new CompoundTag();
        tag.putUUID("id", id); tag.putUUID("owner", owner); tag.put("target", target.toTagGeneric());
        tag.putByteArray("requested", requested.toByteArray()); tag.putByteArray("delivered", delivered.toByteArray());
        tag.putByteArray("bytes", bytes.toByteArray()); tag.putByteArray("operations", totalOperations.toByteArray());
        tag.putInt("priority", priority); tag.putLong("ticks", ticks); tag.putString("state", state);
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
        return tag;
    }

    static Hk3NexusJob read(Hk3NexusCrafting host, CompoundTag tag) {
        var job = new Hk3NexusJob(host, tag.getUUID("id"), tag.getUUID("owner"), AEKey.fromTagGeneric(tag.getCompound("target")),
                new BigInteger(tag.getByteArray("requested")), tag.getInt("priority"), tag.getCompound("link").getBoolean("standalone"));
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
        job.probabilityReceipt = tag.getBoolean("probabilityReceipt");
        if ((job.probability != null || job.probabilityReceipt) && com.sirin.hk3gtl.common.integration.ae.exact.Hk3ProbabilitySupport.AVAILABLE)
            Hk3NexusProbabilityRun.restore(job);
        return job;
    }
}
