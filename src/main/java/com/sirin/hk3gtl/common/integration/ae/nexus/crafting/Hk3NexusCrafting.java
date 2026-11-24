package com.sirin.hk3gtl.common.integration.ae.nexus.crafting;

import appeng.api.config.Actionable;
import appeng.api.config.CpuSelectionMode;
import appeng.api.crafting.IPatternDetails;
import appeng.api.networking.IGrid;
import appeng.api.networking.IGridNode;
import appeng.api.networking.crafting.CalculationStrategy;
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
import com.sirin.hk3gtl.common.integration.ae.exact.Hk3ExactCpuTracker;
import com.sirin.hk3gtl.common.integration.ae.exact.Hk3ExactPlanner;
import com.sirin.hk3gtl.common.integration.ae.exact.Hk3ExactProgramPlan;
import com.sirin.hk3gtl.common.integration.ae.exact.Hk3ExactScaledPattern;
import com.sirin.hk3gtl.common.integration.ae.exact.Hk3ProbabilityOrderService;
import com.sirin.hk3gtl.common.integration.ae.exact.Hk3ProbabilitySupport;
import com.sirin.hk3gtl.common.integration.ae.nexus.network.Hk3NexusBulkInsert;
import com.sirin.hk3gtl.common.integration.ae.nexus.network.Hk3NexusStock;
import com.sirin.hk3gtl.common.integration.ae.nexus.network.Hk3NexusGrid;
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
import java.util.concurrent.CompletableFuture;
import java.util.function.Predicate;
import java.util.function.Supplier;

public final class Hk3NexusCrafting implements ICraftingProvider {
    public record OrderView(UUID id, UUID owner, AEKey target, BigInteger requested, BigInteger remaining,
            BigInteger bytes, int priority, String state, String dispatchNote, Map<AEKey, BigInteger> missing) {}

    private final Supplier<IGridNode> node;
    private final Supplier<Level> level;
    private final Supplier<UUID> identity;
    private final Runnable changed;
    private final Map<UUID, Hk3NexusJob> jobs = new LinkedHashMap<>();
    private final Set<Hk3NexusJob> previews = new LinkedHashSet<>();
    private final Map<AEKey, BigInteger> bufferedOutputs = new LinkedHashMap<>();
    private final NexusCpu availableCpu = new NexusCpu(this, null);
    private Supplier<List<IPatternDetails>> patterns = List::of;
    private Predicate<AEKey> infinite = key -> false;
    private IGrid boundGrid;
    private CompoundTag pending;
    private int roundRobin;

    public Hk3NexusCrafting(Supplier<IGridNode> node, Supplier<Level> level, Supplier<UUID> identity, Runnable changed) {
        this.node = node; this.level = level; this.identity = identity; this.changed = changed;
    }

    UUID identity() { return identity.get(); }

    public void setPatterns(Supplier<List<IPatternDetails>> patterns) { this.patterns = patterns; }
    public void setInfiniteSource(Predicate<AEKey> infinite) { this.infinite = infinite; }
    public boolean isInfiniteSource(AEKey key) { return infinite.test(key); }
    public Level level() { return level.get(); }
    public IGrid grid() { return node.get().getGrid(); }
    public boolean isOn(IGrid grid) {
        var current = node.get();
        return current != null && current.isActive() && current.getGrid() == grid;
    }
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
        changed();
        return job.id;
    }

    public static final class Calculation extends CompletableFuture<ICraftingPlan> {
        public final Hk3NexusCrafting host;
        public final IGrid grid;
        public final BigInteger requested;
        public final CalculationStrategy strategy;
        private final IActionSource source;

        private Calculation(Hk3NexusCrafting host, BigInteger requested, IActionSource source, CalculationStrategy strategy) {
            this.host = host;
            this.source = source;
            grid = host.grid();
            this.requested = requested;
            this.strategy = strategy;
        }
    }

    public Calculation calculate(AEKey target, BigInteger amount, IActionSource source, CalculationStrategy strategy) {
        UUID owner = source.player().map(player -> player.getUUID()).orElse(node.get().getOwningPlayerProfileId());
        var preview = new Hk3NexusJob(this, UUID.randomUUID(), owner == null ? new UUID(0, 0) : owner, target, amount, 0, true);
        preview.confirmed = false;
        preview.calculation = new Calculation(this, amount, source, strategy);
        previews.add(preview);
        return preview.calculation;
    }

    public void confirm(UUID id) {
        var job = jobs.get(id);
        if (!job.active() || job.canceled || job.link.isCanceled()) return;
        if (!job.planned) { job.ticks = 0; job.retryAt = 0; job.previousMissingStock = Map.of(); }
        job.confirmed = true; job.paused = false;
        job.state = job.planned ? "READY" : "PLANNING";
        publish(job);
        changed();
    }

    public void pause(UUID id) { var job = jobs.get(id); job.cancelPlanning(); job.paused = true; job.state = "PAUSED"; changed(); }
    public void resume(UUID id) { confirm(id); }
    public boolean confirmed(UUID id) { return jobs.get(id).confirmed; }

    public void discardPreview(UUID id) {
        var job = jobs.get(id);
        if (job != null && !job.confirmed) { job.cancelPlanning(); jobs.remove(id); changed(); }
    }

    public boolean cancel(UUID id) {
        var job = jobs.get(id);
        if (job == null || !job.active()) return false;
        if (job.probability != null && job.probability.child != null)
            Hk3ProbabilityOrderService.cancelNexus(level().getServer(), job.probability.child);
        job.cancelUnsettled |= job.batchToken != null && (!job.waiting.isEmpty() || job.held.containsKey(job.target));
        job.canceled = true;
        job.cancelPlanning();
        job.waiting.clear();
        job.state = "CANCELING";
        job.link.cancel();
        changed();
        return true;
    }

    public void setPriority(UUID id, int priority) { jobs.get(id).priority = priority; changed(); }

    public List<OrderView> orders() {
        return jobs.values().stream().map(job -> new OrderView(job.id, job.owner, job.target, job.requested,
                job.requested.subtract(job.delivered), job.bytes, job.priority, job.state, job.dispatchNote, Map.copyOf(job.missing))).toList();
    }

    public BigInteger inFlight(AEKey key) {
        return jobs.values().stream().filter(job -> job.active() && !job.canceled && job.target.equals(key))
                .map(job -> job.requested.subtract(job.delivered)).reduce(BigInteger.ZERO, BigInteger::add);
    }

    public void tick() {
        IGridNode current = node.get();
        IGrid activeGrid = current != null && current.isActive() ? current.getGrid() : null;
        if (!previews.isEmpty()) discardCalculations(activeGrid);
        if (activeGrid == null) return;
        if (pending != null) {
            var saved = pending.getList("orders", Tag.TAG_COMPOUND);
            for (Tag element : saved) {
                var job = Hk3NexusJob.read(this, (CompoundTag) element);
                jobs.put(job.id, job);
            }
            if (Hk3ProbabilitySupport.AVAILABLE) {
                for (var start : Hk3ProbabilityOrderService.recoverStarts(level().getServer(), identity(), saved)) {
                    var job = Hk3NexusJob.read(this, start);
                    jobs.put(job.id, job);
                    changed();
                }
            }
            bufferedOutputs.putAll(Hk3NexusLedger.read(pending.getList("outputs", Tag.TAG_COMPOUND)));
            pending = null;
        }
        if (boundGrid != grid()) {
            jobs.values().forEach(Hk3NexusJob::cancelPlanning);
            boundGrid = grid();
            for (var job : jobs.values()) if (job.active() && job.confirmed) publish(job);
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
        if (!previews.isEmpty()) priorities.computeIfAbsent(0, ignored -> new ArrayList<>()).addAll(previews);
        int cursor = roundRobin++;
        for (var running : priorities.values()) {
            int start = Math.floorMod(cursor, running.size());
            for (int offset = 0; offset < running.size(); offset++) {
                var job = running.get((start + offset) % running.size());
                job.tick(deadline);
                if (job.calculation != null && (job.planned || job.state.equals("MISSING_INPUT") || job.state.equals("UNSUPPORTED_PLAN"))) {
                    previews.remove(job);
                    var calculation = job.calculation;
                    job.calculation = null;
                    calculation.complete(new Hk3NexusNativePlan(job));
                }
                if (System.nanoTime() >= deadline) return;
            }
        }
    }

    private void discardCalculations(IGrid activeGrid) {
        for (var it = previews.iterator(); it.hasNext();) {
            var job = it.next();
            if (job.calculation.grid == activeGrid && !job.calculation.isDone()) continue;
            it.remove();
            job.cancelPlanning();
            job.calculation.cancel(false);
        }
    }

    public void close() {
        discardCalculations(null);
        jobs.values().forEach(Hk3NexusJob::cancelPlanning);
        boundGrid = null;
    }

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
        return available(key, source());
    }

    private BigInteger available(AEKey key, IActionSource source) {
        return BigInteger.valueOf(grid().getStorageService().getInventory().extract(key, Long.MAX_VALUE, Actionable.SIMULATE, source));
    }

    private static final BigInteger MAX_NATIVE_STOCK = BigInteger.valueOf(Long.MAX_VALUE);
    private static final Hk3ExactPlanner.SearchLimits SEARCH_LIMITS = Hk3ExactPlanner.SearchLimits.defaults();
    private static final Hk3ExactPlanner.Limits PLAN_LIMITS = new Hk3ExactPlanner.Limits(2048, 8192);

    record Solved(BigInteger amount, Hk3ExactPlanner.DetailedResult<AEKey, IPatternDetails> plan) {}

    final class PlanningCapture {
        final Map<AEKey, BigInteger> stock = new LinkedHashMap<>();
        final Map<AEKey, List<Hk3ExactPlanner.Recipe<AEKey, IPatternDetails>>> graph = new LinkedHashMap<>();
        final Map<IPatternDetails, Hk3NexusRecipe> bindings = new LinkedHashMap<>();
        final Map<IPatternDetails, Hk3ExactPlanner.Recipe<AEKey, IPatternDetails>> sharedOutputs = new LinkedHashMap<>();
        final Set<AEKey> infiniteKeys = new LinkedHashSet<>();
        final Set<AEKey> conditionalKeys = new LinkedHashSet<>();
        final Set<IPatternDetails> conditionalPatterns = new java.util.HashSet<>();
        final ArrayDeque<AEKey> pending = new ArrayDeque<>();
        java.util.Iterator<IPatternDetails> candidates = java.util.Collections.emptyIterator();
        java.util.Iterator<Hk3ExactBoundPattern> variants = java.util.Collections.emptyIterator();
        AEKey key;
        Map<AEKey, BigInteger> overflowStock;
        int edges, inspected;
        String rejection;

        final IActionSource stockSource;
        final int routeBudget;
        final boolean expand;
        boolean hasAlternatives;

        PlanningCapture(Hk3NexusJob job, int routeBudget, boolean expand) {
            stockSource = job.calculation != null ? job.calculation.source : source();
            this.routeBudget = routeBudget;
            this.expand = expand;
            enqueue(job.target);
        }

        private void enqueue(AEKey input) {
            if (graph.putIfAbsent(input, List.of()) == null) pending.addLast(input);
        }

        boolean step(long deadline) {
            for (int steps = 0; steps < 64 && System.nanoTime() < deadline; steps++) {
                if (variants.hasNext()) {
                    var variant = variants.next();
                    if (variant.sameResult(level()) && addRecipe(variant)) return true;
                    continue;
                }
                if (!candidates.hasNext()) {
                    if (pending.isEmpty()) return true;
                    key = pending.removeFirst();
                    stock.computeIfAbsent(key, this::readStock);
                    var found = grid().getCraftingService().getCraftingFor(key);
                    if (found.isEmpty()) continue;
                    if (found.size() > PLAN_LIMITS.maxNodes()) return reject();
                    graph.put(key, new ArrayList<>(found.size()));
                    candidates = found.size() <= 1 || found instanceof Set<?> ? List.copyOf(found).iterator()
                            : new LinkedHashSet<>(found).iterator();
                    continue;
                }
                var pattern = candidates.next();
                if (++inspected > PLAN_LIMITS.maxEdges()) return reject();
                if (conditionalPatterns.contains(pattern)) { conditionalKeys.add(key); continue; }
                if (!(pattern instanceof IMolecularAssemblerSupportedPattern) && Hk3ProbabilitySupport.AVAILABLE) {
                    boolean conditional = false, ordinary = false;
                    for (var provider : ((CraftingService) grid().getCraftingService()).getProviders(pattern)) {
                        if (Hk3ProbabilityOrderService.conditional(provider, pattern)) conditional = true;
                        else ordinary = true;
                        if (conditional && ordinary) break;
                    }
                    if (conditional) {
                        conditionalKeys.add(key);
                        if (!ordinary) { conditionalPatterns.add(pattern); continue; }
                    }
                }
                if (Hk3ExactBoundPattern.hasAlternatives(pattern)) {
                    hasAlternatives = true;
                    variants = Hk3ExactBoundPattern.alternativeCandidates((IMolecularAssemblerSupportedPattern) pattern, level(),
                            expand ? routeBudget : 1,
                            resource -> Hk3NexusLedger.project(stock.computeIfAbsent(resource, this::readStock)));
                } else if (addRecipe(pattern)) return true;
            }
            return false;
        }

        private boolean addRecipe(IPatternDetails pattern) {
            var recipe = sharedOutputs.get(pattern);
            if (recipe == null) {
                var bound = new Hk3NexusRecipe(pattern, resource -> stock.computeIfAbsent(resource, this::readStock));
                if (!bound.outputs.containsKey(key)) return !(pattern instanceof Hk3ExactBoundPattern) && rejectOutput();
                edges += bound.inputs.size() + bound.outputs.size();
                if (edges > PLAN_LIMITS.maxEdges() || bindings.size() >= PLAN_LIMITS.maxNodes()) return reject();
                recipe = new Hk3ExactPlanner.Recipe<>(pattern, bound.inputs, bound.outputs, BigInteger.ONE);
                bindings.put(pattern, bound.bindCounts(recipe));
                if (bound.outputs.size() > 1) sharedOutputs.put(pattern, recipe);
                bound.inputs.keySet().forEach(this::enqueue);
                if (graph.size() > PLAN_LIMITS.maxNodes()) return reject();
            }
            if (recipe.outputs().containsKey(key)) graph.get(key).add(recipe);
            else if (!(pattern instanceof Hk3ExactBoundPattern)) return rejectOutput();
            return false;
        }

        private BigInteger readStock(AEKey resource) {
            if (infinite.test(resource)) {
                infiniteKeys.add(resource);
                return MAX_NATIVE_STOCK;
            }
            var simulated = available(resource, stockSource);
            if (!simulated.equals(MAX_NATIVE_STOCK)) return simulated;
            if (overflowStock == null) overflowStock = Hk3NexusStock.snapshot(grid());
            return overflowStock.getOrDefault(resource, simulated).max(simulated);
        }

        private boolean reject() { rejection = "样板图超过规划预算"; return true; }
        private boolean rejectOutput() { rejection = "样板未产出索引对应的材料"; return true; }

        boolean expandAfter(Hk3ExactPlanner.DetailedResult<AEKey, IPatternDetails> plan) {
            var result = plan.result();
            return !expand && hasAlternatives && routeBudget > plan.routeAttempts() && (result.status() == Hk3ExactPlanner.Status.UNSUPPORTED
                    || result.status() == Hk3ExactPlanner.Status.MISSING_INPUT && !conditionalKeys.containsAll(result.missing().keySet()));
        }

        Solved solve(AEKey target, BigInteger amount, boolean craftLess, long deadline) {
            var search = new Hk3ExactPlanner.SearchLimits(routeBudget, SEARCH_LIMITS.maxOrderAttempts(), SEARCH_LIMITS.maxSteps());
            java.util.function.BooleanSupplier stop = () -> Thread.currentThread().isInterrupted() || System.nanoTime() >= deadline;
            var solver = Hk3ExactPlanner.capturedNexus(target, stock, infiniteKeys, graph, sharedOutputs.values(),
                    edges, PLAN_LIMITS, search, conditionalKeys, stop);
            var full = solver.solve(amount, true);
            var best = new Solved(amount, full);
            if (!craftLess || full.result().status() != Hk3ExactPlanner.Status.MISSING_INPUT || expandAfter(full)) return best;
            var low = BigInteger.ONE;
            var high = amount.subtract(BigInteger.ONE);
            while (low.compareTo(high) <= 0 && !stop.getAsBoolean()) {
                var mid = low.add(high).shiftRight(1);
                var trial = solver.solve(mid, false);
                if (trial.result().successful()) {
                    best = new Solved(mid, trial);
                    low = mid.add(BigInteger.ONE);
                } else high = mid.subtract(BigInteger.ONE);
            }
            return best;
        }
    }

    void plan(Hk3NexusJob job, long deadline) {
        if (job.planning != null) {
            if (!job.planning.isDone()) return;
            var planning = job.planning;
            var captured = job.capture;
            job.planning = null;
            job.capture = null;
            try {
                var solved = planning.get();
                var result = solved.plan();
                if (captured.expandAfter(result)) job.capture = new PlanningCapture(job, captured.routeBudget - result.routeAttempts(), true);
                else {
                    job.requested = solved.amount();
                    applyPlan(job, captured, result);
                }
            } catch (java.util.concurrent.CancellationException | java.util.concurrent.ExecutionException failure) {
                if (job.calculation != null) job.calculation.completeExceptionally(failure);
                else {
                    job.retryAt = job.ticks + 100;
                    job.state = "PLANNING";
                }
            } catch (InterruptedException failure) {
                Thread.currentThread().interrupt();
            }
            return;
        }
        if (job.retryAt > job.ticks) return;
        var server = level().getServer();
        if (job.capture == null) {
            if (job.state.equals("UNSUPPORTED_PLAN")) return;
            if (!com.sirin.hk3gtl.common.integration.ae.Hk3AePlanningService.hasCapacity(server,
                    (int) (collecting(jobs.values()) + collecting(previews)))) return;
            if (job.state.equals("MISSING_INPUT") && !job.previousMissingStock.isEmpty()) {
                var stock = missingStock(job);
                if (job.previousMissingStock.equals(stock)) { job.retryAt = job.ticks + 100; return; }
            }
            job.capture = new PlanningCapture(job, SEARCH_LIMITS.maxRouteAttempts(), false);
            job.state = "PLANNING";
        }
        if (!job.capture.step(deadline)) return;
        if (job.capture.rejection != null) {
            job.dispatchNote = job.capture.rejection;
            job.cancelPlanning();
            unsupportedPlan(job);
            if (job.calculation == null) changed();
            return;
        }
        var captured = job.capture;
        captured.overflowStock = null;
        var target = job.target;
        var amount = job.requested;
        boolean craftLess = job.calculation != null && job.calculation.strategy == CalculationStrategy.CRAFT_LESS;
        job.planning = com.sirin.hk3gtl.common.integration.ae.Hk3AePlanningService.submit(server,
                () -> captured.solve(target, amount, craftLess, System.nanoTime() + 2_000_000_000L));
    }

    private static long collecting(Collection<Hk3NexusJob> jobs) {
        return jobs.stream().filter(job -> job.capture != null && job.planning == null).count();
    }

    private Map<AEKey, BigInteger> missingStock(Hk3NexusJob job) {
        Map<AEKey, BigInteger> missing = new LinkedHashMap<>();
        Map<AEKey, BigInteger> overflow = null;
        for (AEKey key : job.missing.keySet()) {
            if (infinite.test(key)) {
                missing.put(key, job.requested);
            } else {
                var count = available(key);
                if (count.equals(MAX_NATIVE_STOCK)) {
                    if (overflow == null) overflow = Hk3NexusStock.snapshot(grid());
                    count = overflow.getOrDefault(key, count).max(count);
                }
                missing.put(key, count);
            }
        }
        return missing;
    }

    private void applyPlan(Hk3NexusJob job, PlanningCapture captured,
            Hk3ExactPlanner.DetailedResult<AEKey, IPatternDetails> detailed) {
        job.missing.clear();
        job.missing.putAll(detailed.result().missing());
        job.probabilityNeeds.clear();
        var status = detailed.result().status();
        job.probabilityTarget = captured.conditionalKeys.contains(job.target) && (status == Hk3ExactPlanner.Status.UNSUPPORTED
                || !job.confirmed && status == Hk3ExactPlanner.Status.MISSING_INPUT
                        && !captured.conditionalKeys.containsAll(job.missing.keySet()));
        if (job.probabilityTarget) {
            if (job.missing.isEmpty()) job.missing.put(job.target, job.requested);
            job.probabilityNeeds.put(job.target, job.requested);
        } else job.missing.forEach((key, count) -> {
            if (captured.conditionalKeys.contains(key)) job.probabilityNeeds.put(key, count);
        });
        job.bytes = detailed.result().logicalBytes();
        if (!detailed.result().successful()) {
            boolean missing = detailed.result().status() == Hk3ExactPlanner.Status.MISSING_INPUT || !job.probabilityNeeds.isEmpty();
            job.ordered = detailed.orderedExecutionRequired();
            job.dispatchNote = detailed.result().reason();
            if (missing) job.state = "MISSING_INPUT";
            else unsupportedPlan(job);
            if (missing && (jobs.containsKey(job.id) || !job.probabilityNeeds.isEmpty())) {
                Map<AEKey, BigInteger> baseline = new LinkedHashMap<>();
                job.missing.keySet().forEach(key -> baseline.put(key,
                        captured.infiniteKeys.contains(key) ? job.requested : captured.stock.getOrDefault(key, BigInteger.ZERO)));
                job.previousMissingStock = baseline;
                job.retryAt = job.ticks + 100;
                if (job.probability != null && !job.missing.isEmpty() && job.probabilityNeeds.keySet().equals(job.missing.keySet()))
                    job.probability.refill(job);
            }
            if (job.calculation == null) changed();
            return;
        }
        job.probability = null;
        job.initialize(captured.bindings, detailed);
        if (!job.confirmed) job.state = "PREVIEW";
    }

    private static void unsupportedPlan(Hk3NexusJob job) {
        job.state = "UNSUPPORTED_PLAN";
        if (job.confirmed && !job.link.isStandalone()) job.link.cancel();
    }

    public ICraftingSubmitResult submitNative(ICraftingPlan plan, ICraftingRequester requester, IActionSource source) {
        if (plan.simulation()) return CraftingSubmitResult.INCOMPLETE_PLAN;
        if (plan instanceof Hk3NexusNativePlan exact) return submitExact(exact, requester, source);
        UUID owner = source.player().map(player -> player.getUUID()).orElse(node.get().getOwningPlayerProfileId());
        if (owner == null) owner = new UUID(0, 0);
        if (!(plan instanceof Hk3ExactProgramPlan program)) {
            // 外部计划的原料与次数已受long限制，按最终目标重新精确规划。
            var output = plan.finalOutput();
            var job = new Hk3NexusJob(this, UUID.randomUUID(), owner, output.what(),
                    BigInteger.valueOf(output.amount()), 0, requester == null);
            return enqueueNative(job, requester);
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
        job.rounds = job.phases.getFirst().repetitions();
        job.totalOperations = job.tasks.values().stream().reduce(BigInteger.ZERO, BigInteger::add);
        job.planned = true;
        job.state = "RESERVING";
        return enqueueNative(job, requester);
    }

    private ICraftingSubmitResult enqueueNative(Hk3NexusJob job, ICraftingRequester requester) {
        job.batchToken = Hk3ExactCpuTracker.currentSubmission();
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

    public void submitProbability(Hk3NexusNativePlan preview, net.minecraft.server.level.ServerPlayer player,
            List<Hk3ProbabilityOrderService.NexusQuote> routes, BigInteger attempts) {
        var job = new Hk3NexusJob(this, UUID.randomUUID(), player.getUUID(), preview.target(), preview.amount(), 0, true);
        var quoted = preview.preview;
        job.probability = new Hk3NexusProbabilityRun(routes, attempts, quoted.probabilityTarget,
                quoted.probabilityTarget ? Map.of() : quoted.previousMissingStock);
        job.probability.start(job, player, true);
        enqueueNative(job, null);
    }

    public boolean awaitingProbability(UUID parent, UUID child) {
        var job = jobs.get(parent);
        return job != null && !job.canceled && !job.paused && job.probability != null && child.equals(job.probability.child);
    }

    public BigInteger missingAmount(AEKey target, BigInteger amount) {
        if (infinite.test(target)) return BigInteger.ZERO;
        long limit = Hk3NexusLedger.project(amount);
        long present = grid().getStorageService().getInventory().extract(target, limit, Actionable.SIMULATE, source());
        if (present != limit || amount.compareTo(MAX_NATIVE_STOCK) <= 0) return amount.subtract(BigInteger.valueOf(present));
        var exact = Hk3NexusStock.snapshot(grid()).getOrDefault(target, MAX_NATIVE_STOCK).max(MAX_NATIVE_STOCK);
        return amount.subtract(exact).max(BigInteger.ZERO);
    }

    public Hk3NexusNativePlan supplyPlan(UUID owner, AEKey target, long amount,
            Hk3ExactPlanner.DetailedResult<AEKey, IPatternDetails> detailed) {
        var preview = new Hk3NexusJob(this, UUID.randomUUID(), owner, target, BigInteger.valueOf(amount), 0, true);
        Map<IPatternDetails, Hk3NexusRecipe> recipes = new LinkedHashMap<>();
        for (var pattern : detailed.result().batches().keySet()) recipes.put(pattern, new Hk3NexusRecipe(pattern, this::available));
        preview.initialize(recipes, detailed);
        return new Hk3NexusNativePlan(preview);
    }

    private ICraftingSubmitResult submitExact(Hk3NexusNativePlan plan, ICraftingRequester requester, IActionSource source) {
        for (var entry : plan.preview.reservation.entrySet()) {
            var missing = missingAmount(entry.getKey(), entry.getValue());
            if (missing.signum() > 0)
                return CraftingSubmitResult.missingIngredient(new GenericStack(entry.getKey(), Hk3NexusLedger.project(missing)));
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
        return enqueueNative(job, requester);
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

    public static Hk3NexusCrafting firstOn(IGrid grid) {
        for (var node : grid.getMachineNodes(Hk3NexusGrid.class)) {
            if (node.isActive()) return (Hk3NexusCrafting) node.getService(ICraftingProvider.class);
        }
        return null;
    }

    public static List<Hk3NexusCrafting> forGrid(IGrid grid) {
        var machines = grid.getActiveMachines(Hk3NexusGrid.class);
        if (machines.isEmpty()) return List.of();
        return machines.stream()
                .map(network -> network.getActionableNode().getService(ICraftingProvider.class))
                .filter(Hk3NexusCrafting.class::isInstance).map(Hk3NexusCrafting.class::cast).toList();
    }

    public ICraftingCPU availableCpu() { return availableCpu; }

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
        return jobs.values().stream().filter(Hk3NexusJob::awaitsOutput)
                .map(job -> job.waiting.getOrDefault(key, BigInteger.ZERO)).reduce(BigInteger.ZERO, BigInteger::add);
    }

    public boolean requestingAny() { return jobs.values().stream().anyMatch(Hk3NexusJob::awaitsOutput); }

    public void collectWaitingKeys(Set<AEKey> keys) {
        jobs.values().stream().filter(Hk3NexusJob::awaitsOutput).forEach(job -> keys.addAll(job.waiting.keySet()));
    }

    public static final class NexusCpu implements ICraftingCPU, Hk3ExactCpuTracker.BatchAccess {
        private final Hk3NexusCrafting host;
        private final Hk3NexusJob job;
        NexusCpu(Hk3NexusCrafting host, Hk3NexusJob job) { this.host = host; this.job = job; }
        public Hk3NexusCrafting host() { return host; }
        @Override public boolean hk3gtl$matchesBatch(UUID token, AEKey target, long amount) {
            return job != null && job.active() && !job.link.isCanceled() && token.equals(job.batchToken)
                    && job.target.equals(target) && job.requested.equals(BigInteger.valueOf(amount));
        }
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
