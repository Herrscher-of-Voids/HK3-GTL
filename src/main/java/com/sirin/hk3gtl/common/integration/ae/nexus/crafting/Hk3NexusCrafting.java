package com.sirin.hk3gtl.common.integration.ae.nexus.crafting;

import appeng.api.config.Actionable;
import appeng.api.config.CpuSelectionMode;
import appeng.api.crafting.IPatternDetails;
import appeng.api.networking.IGrid;
import appeng.api.networking.IGridNode;
import appeng.api.networking.crafting.CraftingJobStatus;
import appeng.api.networking.crafting.ICraftingCPU;
import appeng.api.networking.crafting.ICraftingPlan;
import appeng.api.networking.crafting.ICraftingProvider;
import appeng.api.networking.crafting.ICraftingRequester;
import appeng.api.networking.crafting.ICraftingSubmitResult;
import appeng.api.networking.events.GridCraftingCpuChange;
import appeng.api.networking.security.IActionSource;
import appeng.api.stacks.AEKey;
import appeng.api.stacks.GenericStack;
import appeng.api.stacks.KeyCounter;
import appeng.blockentity.crafting.IMolecularAssemblerSupportedPattern;
import appeng.crafting.CraftingLink;
import appeng.crafting.execution.CraftingCpuHelper;
import appeng.crafting.execution.CraftingSubmitResult;
import appeng.me.service.CraftingService;
import appeng.menu.me.crafting.CraftingStatus;
import appeng.menu.me.crafting.CraftingStatusEntry;
import com.sirin.hk3gtl.common.integration.ae.exact.Hk3ExactBoundPattern;
import com.sirin.hk3gtl.common.integration.ae.exact.Hk3ExactCpuCapacity;
import com.sirin.hk3gtl.common.integration.ae.exact.Hk3ExactPlanner;
import com.sirin.hk3gtl.common.integration.ae.exact.Hk3ExactProgramPlan;
import com.sirin.hk3gtl.common.integration.ae.exact.Hk3ExactScaledPattern;
import com.sirin.hk3gtl.common.integration.ae.nexus.network.Hk3NexusBulkInsert;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.nbt.ListTag;
import net.minecraft.nbt.Tag;
import net.minecraft.network.chat.Component;
import net.minecraft.world.level.Level;

import java.math.BigInteger;
import java.util.ArrayDeque;
import java.util.ArrayList;
import java.util.Collection;
import java.util.Comparator;
import java.util.LinkedHashMap;
import java.util.LinkedHashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.TreeMap;
import java.util.UUID;
import java.util.function.Predicate;
import java.util.function.Supplier;

public final class Hk3NexusCrafting implements ICraftingProvider {
    public record OrderView(UUID id, UUID owner, AEKey target, BigInteger requested, BigInteger remaining,
            BigInteger bytes, int priority, String state, Map<AEKey, BigInteger> missing) {}

    private final Supplier<IGridNode> node;
    private final Supplier<Level> level;
    private final Runnable changed;
    private final Map<UUID, Hk3NexusJob> jobs = new LinkedHashMap<>();
    private final Map<AEKey, BigInteger> bufferedOutputs = new LinkedHashMap<>();
    private final NexusCpu availableCpu = new NexusCpu(this, null);
    private Supplier<List<IPatternDetails>> patterns = List::of;
    private Predicate<AEKey> infinite = key -> false;
    private IGrid boundGrid;
    private CompoundTag pending;
    private int roundRobin;

    public Hk3NexusCrafting(Supplier<IGridNode> node, Supplier<Level> level, Runnable changed) {
        this.node = node; this.level = level; this.changed = changed;
    }

    public void setPatterns(Supplier<List<IPatternDetails>> patterns) { this.patterns = patterns; }
    public void setInfiniteSource(Predicate<AEKey> infinite) { this.infinite = infinite; }
    public Level level() { return level.get(); }
    public IGrid grid() { return node.get().getGrid(); }
    void changed() { changed.run(); }
    public void patternsChanged() {
        IGridNode current = node.get();
        if (current != null) current.getGrid().getCraftingService().refreshNodeCraftingProvider(current);
    }

    public UUID submit(AEKey target, BigInteger amount, UUID owner, int priority) {
        var job = new Hk3NexusJob(this, UUID.randomUUID(), owner, target, amount, priority, true);
        jobs.put(job.id, job);
        publish(job);
        changed();
        return job.id;
    }

    public UUID prepare(AEKey target, BigInteger amount, UUID owner) {
        var job = new Hk3NexusJob(this, UUID.randomUUID(), owner, target, amount, 0, true);
        job.confirmed = false;
        jobs.put(job.id, job);
        plan(job);
        if (job.planned) job.state = "PREVIEW";
        changed();
        return job.id;
    }

    public void confirm(UUID id) {
        var job = jobs.get(id);
        job.confirmed = true; job.paused = false;
        job.state = job.planned ? "READY" : "PLANNING";
        publish(job);
        changed();
    }

    public void pause(UUID id) { var job = jobs.get(id); job.paused = true; job.state = "PAUSED"; changed(); }
    public void resume(UUID id) { confirm(id); }
    public boolean confirmed(UUID id) { return jobs.get(id).confirmed; }

    public void discardPreview(UUID id) {
        var job = jobs.get(id);
        if (job != null && !job.confirmed) { jobs.remove(id); changed(); }
    }

    public boolean cancel(UUID id) {
        var job = jobs.get(id);
        if (job == null || !job.active()) return false;
        job.canceled = true;
        job.state = "CANCELING";
        job.link.cancel();
        changed();
        return true;
    }

    public void setPriority(UUID id, int priority) { jobs.get(id).priority = priority; changed(); }

    public List<OrderView> orders() {
        return jobs.values().stream().map(job -> new OrderView(job.id, job.owner, job.target, job.requested,
                job.requested.subtract(job.delivered), job.bytes, job.priority, job.state, Map.copyOf(job.missing))).toList();
    }

    public BigInteger inFlight(AEKey key) {
        return jobs.values().stream().filter(job -> job.active() && !job.canceled && job.target.equals(key))
                .map(job -> job.requested.subtract(job.delivered)).reduce(BigInteger.ZERO, BigInteger::add);
    }

    public void tick() {
        IGridNode current = node.get();
        if (current == null || !current.isActive()) return;
        if (pending != null) {
            for (Tag element : pending.getList("orders", Tag.TAG_COMPOUND)) {
                var job = Hk3NexusJob.read(this, (CompoundTag) element);
                jobs.put(job.id, job);
            }
            bufferedOutputs.putAll(Hk3NexusLedger.read(pending.getList("outputs", Tag.TAG_COMPOUND)));
            pending = null;
        }
        if (boundGrid != grid()) {
            boundGrid = grid();
            for (var job : jobs.values()) if (job.active() && job.confirmed) {
                job.recoverWaiting.addAll(job.waiting.keySet());
                publish(job);
            }
            patternsChanged();
        }
        // 时间片约束服务器工作量，逻辑并行数与订单数不设玩法上限。
        long deadline = System.nanoTime() + 2_000_000L;
        for (var entry : List.copyOf(bufferedOutputs.entrySet())) {
            BigInteger accepted = insert(entry.getKey(), entry.getValue());
            if (accepted.signum() > 0) { Hk3NexusLedger.add(bufferedOutputs, entry.getKey(), accepted.negate()); changed(); }
            if (System.nanoTime() >= deadline) return;
        }
        Map<Integer, List<Hk3NexusJob>> priorities = new TreeMap<>(Comparator.reverseOrder());
        jobs.values().stream().filter(Hk3NexusJob::active)
                .forEach(job -> priorities.computeIfAbsent(job.priority, ignored -> new ArrayList<>()).add(job));
        int cursor = roundRobin++;
        for (var running : priorities.values()) {
            int start = Math.floorMod(cursor, running.size());
            for (int offset = 0; offset < running.size(); offset++) {
                running.get((start + offset) % running.size()).tick(deadline);
                if (System.nanoTime() >= deadline) return;
            }
        }
    }

    public void close() { boundGrid = null; }

    private void publish(Hk3NexusJob job) {
        IGridNode current = node.get();
        if (current == null || !current.isActive()) return;
        if (!job.link.isStandalone()) ((CraftingService) grid().getCraftingService()).addLink(job.link);
        grid().postEvent(new GridCraftingCpuChange(current));
    }

    BigInteger extract(AEKey key, BigInteger amount) {
        if (infinite.test(key)) return amount;
        long extracted = grid().getStorageService().getInventory().extract(key, Hk3NexusLedger.project(amount),
                Actionable.MODULATE, source());
        return BigInteger.valueOf(extracted);
    }

    BigInteger insert(AEKey key, BigInteger amount) {
        return Hk3NexusBulkInsert.insert(grid().getStorageService().getInventory(), key, amount, source());
    }

    private IActionSource source() { return IActionSource.ofMachine(node::get); }

    private BigInteger available(AEKey key) {
        return BigInteger.valueOf(grid().getStorageService().getInventory().extract(key, Long.MAX_VALUE,
                Actionable.SIMULATE, source()));
    }

    void plan(Hk3NexusJob job) {
        Map<AEKey, BigInteger> stock = new LinkedHashMap<>(
                com.sirin.hk3gtl.common.integration.ae.nexus.network.Hk3NexusStock.snapshot(grid()));
        Map<AEKey, List<Hk3ExactPlanner.Recipe<AEKey, IPatternDetails>>> graph = new LinkedHashMap<>();
        Map<IPatternDetails, Hk3NexusRecipe> bindings = new LinkedHashMap<>();
        ArrayDeque<AEKey> pending = new ArrayDeque<>();
        Set<AEKey> seen = new LinkedHashSet<>();
        pending.add(job.target); seen.add(job.target);
        BigInteger infiniteBudget = job.requested.add(BigInteger.ONE);
        while (!pending.isEmpty()) {
            AEKey key = pending.removeFirst();
            stock.putIfAbsent(key, BigInteger.ZERO);
            List<Hk3ExactPlanner.Recipe<AEKey, IPatternDetails>> recipes = new ArrayList<>();
            for (var pattern : grid().getCraftingService().getCraftingFor(key)) {
                var bound = bindings.computeIfAbsent(pattern, candidate -> new Hk3NexusRecipe(candidate,
                        resource -> stock.computeIfAbsent(resource, ignored -> BigInteger.ZERO)));
                recipes.add(new Hk3ExactPlanner.Recipe<>(pattern, bound.inputs, bound.outputs, BigInteger.ONE));
                infiniteBudget = infiniteBudget.multiply(bound.inputs.values().stream()
                        .reduce(BigInteger.ONE, BigInteger::add));
                for (AEKey input : bound.inputs.keySet()) if (seen.add(input)) pending.addLast(input);
            }
            graph.put(key, recipes);
        }
        BigInteger supply = infiniteBudget;
        stock.replaceAll((key, count) -> infinite.test(key) ? supply : count);
        var detailed = Hk3ExactPlanner.planDetailed(job.target, job.requested, stock,
                key -> graph.getOrDefault(key, List.of()), new Hk3ExactPlanner.Limits(Integer.MAX_VALUE, Integer.MAX_VALUE), () -> false);
        job.missing.clear();
        job.missing.putAll(detailed.result().missing());
        job.bytes = detailed.result().logicalBytes();
        if (!detailed.result().successful()) {
            job.state = detailed.result().status() == Hk3ExactPlanner.Status.MISSING_INPUT ? "MISSING_INPUT" : "UNSUPPORTED_PLAN";
            changed();
            return;
        }
        job.initialize(bindings, detailed);
    }

    public ICraftingSubmitResult submitNative(ICraftingPlan plan, ICraftingRequester requester, IActionSource source) {
        if (plan.simulation()) return CraftingSubmitResult.INCOMPLETE_PLAN;
        if (plan instanceof Hk3NexusNativePlan exact) return submitExact(exact, requester, source);
        UUID owner = source.player().map(player -> player.getUUID()).orElse(node.get().getOwningPlayerProfileId());
        if (owner == null) owner = new UUID(0, 0);
        if (!(plan instanceof Hk3ExactProgramPlan program)) {
            // 外部计划的原料与次数已受long限制，按最终目标重新精确规划。
            var output = plan.finalOutput();
            return submitNative(preview(output.what(), BigInteger.valueOf(output.amount()), owner), requester, source);
        }
        for (var entry : plan.usedItems()) {
            if (available(entry.getKey()).compareTo(BigInteger.valueOf(entry.getLongValue())) < 0)
                return CraftingSubmitResult.missingIngredient(new GenericStack(entry.getKey(), entry.getLongValue()));
        }
        var job = new Hk3NexusJob(this, UUID.randomUUID(), owner, plan.finalOutput().what(),
                BigInteger.valueOf(plan.finalOutput().amount()), 0, requester == null);
        job.bytes = Hk3ExactCpuCapacity.requiredBytes(plan);
        for (var entry : plan.usedItems()) job.reservation.put(entry.getKey(), BigInteger.valueOf(entry.getLongValue()));
        for (var entry : plan.emittedItems()) job.waiting.put(entry.getKey(), BigInteger.valueOf(entry.getLongValue()));
        Map<IPatternDetails, Hk3NexusRecipe> bindings = new LinkedHashMap<>();
        job.ordered = true;
        for (var step : program.execution()) {
            List<Hk3NexusRecipe> recipes = new ArrayList<>();
            BigInteger repetitions = step.repetitions();
            for (var selected : step.recipes()) {
                IPatternDetails normalized = selected instanceof Hk3ExactScaledPattern
                        ? Hk3ExactBoundPattern.original(selected) : selected;
                var recipe = bindings.computeIfAbsent(normalized, pattern -> new Hk3NexusRecipe(pattern, this::available));
                recipes.add(recipe);
                if (selected instanceof Hk3ExactScaledPattern) repetitions = repetitions.multiply(BigInteger.valueOf(Hk3ExactScaledPattern.operations(selected)));
            }
            job.phases.add(new Hk3NexusJob.Phase(recipes, repetitions));
            BigInteger count = repetitions;
            recipes.forEach(recipe -> job.tasks.merge(recipe, count, BigInteger::add));
        }
        job.rounds = job.phases.get(0).repetitions();
        job.totalOperations = job.tasks.values().stream().reduce(BigInteger.ZERO, BigInteger::add);
        job.planned = true;
        job.state = "RESERVING";
        jobs.put(job.id, job);
        publish(job);
        CraftingLink requesterLink = null;
        if (requester != null) {
            requesterLink = new CraftingLink(CraftingCpuHelper.generateLinkData(job.id, false, true), requester);
            ((CraftingService) grid().getCraftingService()).addLink(requesterLink);
        }
        changed();
        return CraftingSubmitResult.successful(requesterLink);
    }

    public Hk3NexusNativePlan preview(AEKey target, BigInteger amount, UUID owner) {
        var job = new Hk3NexusJob(this, UUID.randomUUID(), owner, target, amount, 0, true);
        job.confirmed = false;
        plan(job);
        return new Hk3NexusNativePlan(job);
    }

    public BigInteger missingAmount(AEKey target, BigInteger amount) {
        if (infinite.test(target)) return BigInteger.ZERO;
        return amount.subtract(com.sirin.hk3gtl.common.integration.ae.nexus.network.Hk3NexusStock.snapshot(grid())
                .getOrDefault(target, BigInteger.ZERO)).max(BigInteger.ZERO);
    }

    private ICraftingSubmitResult submitExact(Hk3NexusNativePlan plan, ICraftingRequester requester, IActionSource source) {
        var stock = com.sirin.hk3gtl.common.integration.ae.nexus.network.Hk3NexusStock.snapshot(grid());
        for (var entry : plan.preview.reservation.entrySet()) {
            if (!infinite.test(entry.getKey()) && stock.getOrDefault(entry.getKey(), BigInteger.ZERO).compareTo(entry.getValue()) < 0)
                return CraftingSubmitResult.missingIngredient(new GenericStack(entry.getKey(), Hk3NexusLedger.project(entry.getValue())));
        }
        UUID owner = source.player().map(player -> player.getUUID()).orElse(plan.preview.owner);
        var job = new Hk3NexusJob(this, UUID.randomUUID(), owner, plan.target(), plan.amount(), 0, requester == null);
        job.bytes = plan.exactBytes();
        job.reservation.putAll(plan.preview.reservation);
        job.tasks.putAll(plan.preview.tasks);
        job.phases.addAll(plan.preview.phases);
        job.ordered = plan.preview.ordered;
        job.rounds = plan.preview.rounds;
        job.totalOperations = plan.preview.totalOperations;
        job.planned = true;
        job.state = "RESERVING";
        jobs.put(job.id, job);
        publish(job);
        CraftingLink requesterLink = null;
        if (requester != null) {
            requesterLink = new CraftingLink(CraftingCpuHelper.generateLinkData(job.id, false, true), requester);
            ((CraftingService) grid().getCraftingService()).addLink(requesterLink);
        }
        changed();
        return CraftingSubmitResult.successful(requesterLink);
    }

    @Override public List<IPatternDetails> getAvailablePatterns() {
        return patterns.get().stream().filter(pattern -> pattern instanceof IMolecularAssemblerSupportedPattern).toList();
    }
    @Override public boolean isBusy() { return node.get() == null || !node.get().isActive(); }

    @Override public boolean pushPattern(IPatternDetails pattern, KeyCounter[] inputs) {
        if (!(pattern instanceof IMolecularAssemblerSupportedPattern) || isBusy()) return false;
        var recipe = new Hk3NexusRecipe(pattern, this::available);
        recipe.assemble(inputs, level()).forEach((key, amount) -> Hk3NexusLedger.add(bufferedOutputs, key, amount));
        changed();
        return true;
    }

    public void write(CompoundTag tag) {
        if (pending != null) { tag.merge(pending.copy()); return; }
        ListTag list = new ListTag();
        jobs.values().forEach(job -> list.add(job.write()));
        tag.put("orders", list);
        tag.put("outputs", Hk3NexusLedger.write(bufferedOutputs));
    }

    public void read(CompoundTag tag) { pending = tag.copy(); }

    public static List<Hk3NexusCrafting> forGrid(IGrid grid) {
        return grid.getActiveMachines(com.sirin.hk3gtl.common.integration.ae.nexus.network.Hk3NexusGrid.class).stream()
                .map(network -> network.getActionableNode().getService(ICraftingProvider.class))
                .filter(Hk3NexusCrafting.class::isInstance).map(Hk3NexusCrafting.class::cast).toList();
    }

    public Collection<ICraftingCPU> cpus() {
        List<ICraftingCPU> cpus = new ArrayList<>();
        cpus.add(availableCpu);
        jobs.values().stream().filter(job -> job.active() && job.confirmed).forEach(job -> cpus.add(job.cpu));
        return cpus;
    }

    public long accept(AEKey key, long amount, Actionable mode) {
        long inserted = 0;
        for (var job : jobs.values()) {
            inserted += job.insert(key, amount - inserted, mode);
            if (inserted == amount) break;
        }
        return inserted;
    }

    public BigInteger waiting(AEKey key) {
        return jobs.values().stream().map(job -> job.waiting.getOrDefault(key, BigInteger.ZERO)).reduce(BigInteger.ZERO, BigInteger::add);
    }

    public boolean requestingAny() { return jobs.values().stream().anyMatch(job -> !job.waiting.isEmpty()); }

    public Set<AEKey> waitingKeys() {
        Set<AEKey> keys = new LinkedHashSet<>();
        jobs.values().forEach(job -> keys.addAll(job.waiting.keySet()));
        return keys;
    }

    public static final class NexusCpu implements ICraftingCPU {
        private final Hk3NexusCrafting host;
        private final Hk3NexusJob job;
        NexusCpu(Hk3NexusCrafting host, Hk3NexusJob job) { this.host = host; this.job = job; }
        public Hk3NexusCrafting host() { return host; }
        @Override public boolean isBusy() { return job != null && job.active(); }
        @Override public void cancelJob() { if (job != null) host.cancel(job.id); }
        @Override public long getAvailableStorage() { return Long.MAX_VALUE; }
        @Override public int getCoProcessors() { return Integer.MAX_VALUE; }
        @Override public CpuSelectionMode getSelectionMode() { return CpuSelectionMode.ANY; }
        @Override public Component getName() {
            var name = Component.translatableWithFallback(Hk3NexusNativeMenus.CPU_NAME, "万象天枢");
            return job == null ? name : name.append(" · " + job.id.toString().substring(0, 8));
        }
        @Override public CraftingJobStatus getJobStatus() {
            if (job == null) return null;
            BigInteger remaining = job.tasks.values().stream().reduce(BigInteger.ZERO, BigInteger::add);
            return new CraftingJobStatus(new GenericStack(job.target, Hk3NexusLedger.project(job.requested)),
                    Hk3NexusLedger.project(job.totalOperations), Hk3NexusLedger.project(job.totalOperations.subtract(remaining)), job.ticks * 50_000_000L);
        }
        public CraftingStatus nativeStatus() {
            if (job == null) return CraftingStatus.EMPTY;
            Set<AEKey> keys = new LinkedHashSet<>(job.held.keySet()); keys.addAll(job.waiting.keySet());
            Map<AEKey, BigInteger> pending = new LinkedHashMap<>();
            job.tasks.forEach((recipe, count) -> recipe.outputs.forEach((key, amount) -> Hk3NexusLedger.add(pending, key, amount.multiply(count))));
            keys.addAll(pending.keySet());
            List<CraftingStatusEntry> entries = new ArrayList<>();
            for (var key : keys) entries.add(new CraftingStatusEntry(entries.size(), key,
                    Hk3NexusLedger.project(job.held.getOrDefault(key, BigInteger.ZERO)), Hk3NexusLedger.project(job.waiting.getOrDefault(key, BigInteger.ZERO)),
                    Hk3NexusLedger.project(pending.getOrDefault(key, BigInteger.ZERO))));
            BigInteger remaining = job.tasks.values().stream().reduce(BigInteger.ZERO, BigInteger::add);
            return new CraftingStatus(true, job.ticks * 50_000_000L, Hk3NexusLedger.project(remaining),
                    Hk3NexusLedger.project(job.totalOperations), entries);
        }
    }
}
