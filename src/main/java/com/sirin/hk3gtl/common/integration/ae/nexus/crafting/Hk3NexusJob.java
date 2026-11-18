package com.sirin.hk3gtl.common.integration.ae.nexus.crafting;

import appeng.api.config.Actionable;
import appeng.api.crafting.IPatternDetails;
import appeng.api.networking.crafting.ICraftingRequester;
import appeng.api.networking.security.IActionSource;
import appeng.api.stacks.AEKey;
import appeng.crafting.CraftingLink;
import appeng.crafting.execution.CraftingCpuHelper;
import appeng.me.service.CraftingService;
import com.sirin.hk3gtl.common.integration.ae.exact.Hk3ExactPlanner;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.nbt.ListTag;
import net.minecraft.nbt.Tag;
import net.minecraft.world.level.Level;

import java.math.BigInteger;
import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.UUID;

final class Hk3NexusJob {
    record Phase(List<Hk3NexusRecipe> recipes, BigInteger repetitions) {}

    final Hk3NexusCrafting host;
    final UUID id, owner;
    final AEKey target;
    final BigInteger requested;
    final Hk3NexusCrafting.NexusCpu cpu;
    CraftingLink link;
    final Map<AEKey, BigInteger> held = new LinkedHashMap<>();
    final Map<AEKey, BigInteger> waiting = new LinkedHashMap<>();
    final Map<AEKey, BigInteger> reservation = new LinkedHashMap<>();
    final Map<AEKey, BigInteger> missing = new LinkedHashMap<>();
    final Map<Hk3NexusRecipe, BigInteger> tasks = new LinkedHashMap<>();
    final List<Phase> phases = new ArrayList<>();
    final Set<AEKey> recoverWaiting = new java.util.LinkedHashSet<>();
    BigInteger bytes = BigInteger.ZERO, delivered = BigInteger.ZERO, totalOperations = BigInteger.ZERO;
    BigInteger rounds = BigInteger.ZERO;
    int phase, recipe, priority;
    long ticks;
    boolean ordered, planned, canceled, flexible, confirmed = true, paused;
    String state = "PLANNING";

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
        detailed.result().batches().forEach((pattern, amount) -> tasks.put(recipes.get(pattern), amount));
        for (var step : detailed.execution()) phases.add(new Phase(step.recipes().stream().map(recipes::get).toList(), step.repetitions()));
        totalOperations = tasks.values().stream().reduce(BigInteger.ZERO, BigInteger::add);
        rounds = phases.isEmpty() ? BigInteger.ZERO : phases.get(0).repetitions();
        planned = true;
        state = "RESERVING";
        host.changed();
    }

    void tick(long deadline) {
        ticks++;
        if (link.isCanceled() && !canceled) { canceled = true; host.changed(); }
        if (canceled) {
            tasks.clear();
            reservation.clear();
            waiting.clear();
            recoverWaiting.clear();
            flush(false, deadline);
            state = held.isEmpty() ? "CANCELED" : "CANCELING";
            return;
        }
        for (AEKey key : Set.copyOf(recoverWaiting)) {
            BigInteger expected = waiting.getOrDefault(key, BigInteger.ZERO);
            long requested = Hk3NexusLedger.project(expected);
            BigInteger recovered = host.extract(key, BigInteger.valueOf(requested));
            if (recovered.signum() > 0) {
                Hk3NexusLedger.add(waiting, key, recovered.negate());
                Hk3NexusLedger.add(held, key, recovered);
                host.changed();
            }
            if (waiting.getOrDefault(key, BigInteger.ZERO).signum() == 0 || recovered.longValue() < requested)
                recoverWaiting.remove(key);
            if (System.nanoTime() >= deadline) return;
        }
        if (paused) { state = "PAUSED"; return; }
        if (!planned) {
            if (ticks == 1 || ticks % 20 == 0) host.plan(this);
            return;
        }
        if (!confirmed) { state = "PREVIEW"; return; }
        if (!reservation.isEmpty()) {
            missing.clear();
            for (var entry : List.copyOf(reservation.entrySet())) {
                BigInteger extracted = host.extract(entry.getKey(), entry.getValue());
                if (extracted.signum() > 0) {
                    Hk3NexusLedger.add(held, entry.getKey(), extracted);
                    Hk3NexusLedger.add(reservation, entry.getKey(), extracted.negate());
                    host.changed();
                }
                if (reservation.containsKey(entry.getKey())) missing.put(entry.getKey(), reservation.get(entry.getKey()));
                if (System.nanoTime() >= deadline) return;
            }
            if (!reservation.isEmpty()) { state = "MISSING_INPUT"; return; }
        }
        state = "RUNNING";
        boolean advanced;
        do {
            missing.clear();
            advanced = ordered ? executeOrdered() : executeUnordered();
        } while (advanced && !tasks.isEmpty() && System.nanoTime() < deadline);
        if (tasks.isEmpty() && waiting.isEmpty()) {
            state = "DRAINING";
            flush(true, deadline);
            if (held.isEmpty() && delivered.equals(requested)) {
                state = "DONE";
                if (!link.isDone()) { link.markDone(); host.changed(); }
            }
        } else if (!advanced) state = waiting.isEmpty() ? "WAITING_MACHINE" : "WAITING_OUTPUT";
    }

    private boolean executeUnordered() {
        for (var entry : List.copyOf(tasks.entrySet())) {
            if (entry.getKey().molecular()) {
                BigInteger done = executeMolecular(List.of(entry.getKey()), entry.getValue());
                if (done.signum() > 0) return true;
            } else if (dispatch(entry.getKey())) return true;
        }
        return false;
    }

    private boolean executeOrdered() {
        if (!waiting.isEmpty() || phase == phases.size()) return false;
        Phase step = phases.get(phase);
        if (recipe == 0 && step.recipes().stream().allMatch(Hk3NexusRecipe::molecular)) {
            BigInteger done = executeMolecular(step.recipes(), rounds);
            if (done.signum() == 0) return false;
            rounds = rounds.subtract(done);
            if (rounds.signum() == 0) nextPhase();
            return true;
        }
        Hk3NexusRecipe current = step.recipes().get(recipe);
        boolean pushed = current.molecular()
                ? executeMolecular(List.of(current), BigInteger.ONE).signum() > 0 : dispatch(current);
        if (pushed && ++recipe == step.recipes().size()) {
            recipe = 0;
            rounds = rounds.subtract(BigInteger.ONE);
            if (rounds.signum() == 0) nextPhase();
        }
        return pushed;
    }

    private void nextPhase() {
        phase++;
        recipe = 0;
        rounds = phase < phases.size() ? phases.get(phase).repetitions() : BigInteger.ZERO;
    }

    private BigInteger executeMolecular(List<Hk3NexusRecipe> sequence, BigInteger count) {
        Map<AEKey, BigInteger> net = new LinkedHashMap<>(), seed = new LinkedHashMap<>();
        for (var part : sequence) {
            var effective = flexible ? new Hk3NexusRecipe(part.pattern,
                    key -> held.getOrDefault(key, BigInteger.ZERO)) : part;
            effective.inputs.forEach((key, amount) -> {
                BigInteger required = amount.subtract(net.getOrDefault(key, BigInteger.ZERO));
                seed.merge(key, required.max(BigInteger.ZERO), BigInteger::max);
                Hk3NexusLedger.add(net, key, amount.negate());
            });
            effective.assemble(effective.grouped, host.level()).forEach((key, amount) -> Hk3NexusLedger.add(net, key, amount));
        }
        BigInteger available = count;
        for (var entry : seed.entrySet()) {
            BigInteger stock = held.getOrDefault(entry.getKey(), BigInteger.ZERO);
            if (stock.compareTo(entry.getValue()) < 0) {
                missing.put(entry.getKey(), entry.getValue().subtract(stock));
                return BigInteger.ZERO;
            }
            BigInteger delta = net.getOrDefault(entry.getKey(), BigInteger.ZERO);
            if (delta.signum() < 0) available = available.min(stock.subtract(entry.getValue()).divide(delta.negate()).add(BigInteger.ONE));
        }
        BigInteger completed = available;
        net.forEach((key, amount) -> Hk3NexusLedger.add(held, key, amount.multiply(completed)));
        sequence.forEach(part -> decrement(part, completed));
        host.changed();
        return completed;
    }

    private boolean dispatch(Hk3NexusRecipe part) {
        var effective = flexible ? new Hk3NexusRecipe(part.pattern,
                key -> held.getOrDefault(key, BigInteger.ZERO)) : part;
        for (var entry : effective.inputs.entrySet()) {
            BigInteger available = held.getOrDefault(entry.getKey(), BigInteger.ZERO);
            if (available.compareTo(entry.getValue()) < 0) {
                missing.put(entry.getKey(), entry.getValue().subtract(available));
                return false;
            }
        }
        var service = (CraftingService) host.grid().getCraftingService();
        for (var provider : service.getProviders(part.pattern)) {
            if (provider == host || provider.isBusy()) continue;
            if (!provider.pushPattern(effective.pattern, Hk3NexusRecipe.copy(effective.grouped))) continue;
            effective.inputs.forEach((key, amount) -> Hk3NexusLedger.add(held, key, amount.negate()));
            effective.outputs.forEach((key, amount) -> Hk3NexusLedger.add(waiting, key, amount));
            decrement(part, BigInteger.ONE);
            host.changed();
            return true;
        }
        return false;
    }

    private void decrement(Hk3NexusRecipe part, BigInteger count) {
        BigInteger remaining = tasks.get(part).subtract(count);
        if (remaining.signum() == 0) tasks.remove(part); else tasks.put(part, remaining);
    }

    long insert(AEKey key, long amount, Actionable mode) {
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

    boolean active() { return !state.equals("DONE") && !state.equals("CANCELED"); }

    CompoundTag write() {
        CompoundTag tag = new CompoundTag();
        tag.putUUID("id", id); tag.putUUID("owner", owner); tag.put("target", target.toTagGeneric());
        tag.putByteArray("requested", requested.toByteArray()); tag.putByteArray("delivered", delivered.toByteArray());
        tag.putByteArray("bytes", bytes.toByteArray()); tag.putByteArray("operations", totalOperations.toByteArray());
        tag.putInt("priority", priority); tag.putLong("ticks", ticks); tag.putString("state", state);
        tag.putBoolean("planned", planned); tag.putBoolean("ordered", ordered); tag.putBoolean("canceled", canceled);
        tag.putBoolean("flexible", flexible);
        tag.putBoolean("confirmed", confirmed); tag.putBoolean("paused", paused);
        tag.put("held", Hk3NexusLedger.write(held)); tag.put("waiting", Hk3NexusLedger.write(waiting));
        tag.put("reservation", Hk3NexusLedger.write(reservation)); tag.put("missing", Hk3NexusLedger.write(missing));
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
        tag.put("program", program); tag.putInt("phase", phase); tag.putInt("recipe", recipe);
        tag.putByteArray("rounds", rounds.toByteArray());
        return tag;
    }

    static Hk3NexusJob read(Hk3NexusCrafting host, CompoundTag tag) {
        var job = new Hk3NexusJob(host, tag.getUUID("id"), tag.getUUID("owner"), AEKey.fromTagGeneric(tag.getCompound("target")),
                new BigInteger(tag.getByteArray("requested")), tag.getInt("priority"), tag.getCompound("link").getBoolean("standalone"));
        job.delivered = new BigInteger(tag.getByteArray("delivered")); job.bytes = new BigInteger(tag.getByteArray("bytes"));
        job.totalOperations = new BigInteger(tag.getByteArray("operations")); job.ticks = tag.getLong("ticks");
        job.state = tag.getString("state"); job.planned = tag.getBoolean("planned"); job.ordered = tag.getBoolean("ordered");
        job.canceled = tag.getBoolean("canceled");
        job.flexible = tag.getBoolean("flexible");
        job.confirmed = tag.getBoolean("confirmed"); job.paused = tag.getBoolean("paused");
        job.link = new CraftingLink(tag.getCompound("link"), job.cpu);
        job.held.putAll(Hk3NexusLedger.read(tag.getList("held", Tag.TAG_COMPOUND)));
        job.waiting.putAll(Hk3NexusLedger.read(tag.getList("waiting", Tag.TAG_COMPOUND)));
        job.reservation.putAll(Hk3NexusLedger.read(tag.getList("reservation", Tag.TAG_COMPOUND)));
        job.missing.putAll(Hk3NexusLedger.read(tag.getList("missing", Tag.TAG_COMPOUND)));
        List<Hk3NexusRecipe> recipes = new ArrayList<>();
        for (Tag element : tag.getList("recipes", Tag.TAG_COMPOUND)) {
            CompoundTag row = (CompoundTag) element;
            var part = Hk3NexusRecipe.read(row, host.level()); recipes.add(part);
            BigInteger remaining = new BigInteger(row.getByteArray("remaining"));
            if (remaining.signum() > 0) job.tasks.put(part, remaining);
        }
        for (Tag element : tag.getList("program", Tag.TAG_COMPOUND)) {
            CompoundTag row = (CompoundTag) element;
            List<Hk3NexusRecipe> parts = new ArrayList<>();
            for (int index : row.getIntArray("recipes")) parts.add(recipes.get(index));
            job.phases.add(new Phase(parts, new BigInteger(row.getByteArray("count"))));
        }
        job.phase = tag.getInt("phase"); job.recipe = tag.getInt("recipe");
        job.rounds = new BigInteger(tag.getByteArray("rounds"));
        return job;
    }
}
