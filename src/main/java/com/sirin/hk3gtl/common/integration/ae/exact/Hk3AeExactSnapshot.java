package com.sirin.hk3gtl.common.integration.ae.exact;

import appeng.api.config.Actionable;
import appeng.api.crafting.IPatternDetails;
import appeng.api.networking.IGrid;
import appeng.api.networking.crafting.ICraftingSimulationRequester;
import appeng.api.stacks.AEKey;
import appeng.blockentity.crafting.IMolecularAssemblerSupportedPattern;
import appeng.me.service.CraftingService;
import net.minecraft.world.level.Level;

import java.math.BigInteger;
import java.util.ArrayDeque;
import java.util.ArrayList;
import java.util.Collections;
import java.util.HashMap;
import java.util.HashSet;
import java.util.LinkedHashMap;
import java.util.Iterator;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.function.BooleanSupplier;
import java.util.function.Predicate;

/** 只在服务器线程捕获权限相关库存与固定样板，后台仅计算不可变快照。 */
public final class Hk3AeExactSnapshot {
    private final AEKey target;
    private final Map<AEKey, BigInteger> inventory;
    private final Map<AEKey, List<Hk3ExactPlanner.Recipe<AEKey, IPatternDetails>>> recipes;
    private final Map<IPatternDetails, Hk3ExactPlanner.Recipe<AEKey, IPatternDetails>> byPattern;
    private final Set<IPatternDetails> remainderPatterns;
    private final Set<AEKey> unsupportedKeys;
    private final Hk3ExactPlanner.Limits limits;
    private final BigInteger treeNodes;

    private Hk3AeExactSnapshot(AEKey target, Map<AEKey, BigInteger> inventory,
                               Map<AEKey, List<Hk3ExactPlanner.Recipe<AEKey, IPatternDetails>>> recipes,
                               Set<IPatternDetails> remainderPatterns, Set<AEKey> unsupportedKeys,
                               Hk3ExactPlanner.Limits limits, BigInteger treeNodes) {
        this.target = target;
        this.inventory = Collections.unmodifiableMap(new LinkedHashMap<>(inventory));
        this.recipes = Collections.unmodifiableMap(new LinkedHashMap<>(recipes));
        Map<IPatternDetails, Hk3ExactPlanner.Recipe<AEKey, IPatternDetails>> bindings = new LinkedHashMap<>();
        recipes.values().forEach(values -> values.forEach(recipe -> bindings.put(recipe.id(), recipe)));
        this.byPattern = Collections.unmodifiableMap(bindings);
        this.remainderPatterns = Set.copyOf(remainderPatterns);
        this.unsupportedKeys = Set.copyOf(unsupportedKeys);
        this.limits = limits;
        this.treeNodes = treeNodes;
    }

    static final class Capture {
        private final Level level;
        private final IGrid grid;
        private final ICraftingSimulationRequester requester;
        private final AEKey target;
        private final Hk3ExactPlanner.Limits limits;
        private final Map<AEKey, BigInteger> stock = new LinkedHashMap<>();
        private final Map<IPatternDetails, List<Hk3ExactPlanner.Recipe<AEKey, IPatternDetails>>> parsed = new LinkedHashMap<>();
        private final Set<IPatternDetails> remainderPatterns = new HashSet<>();
        private final Set<AEKey> unsupportedKeys = new HashSet<>();
        private final Map<AEKey, List<Hk3ExactPlanner.Recipe<AEKey, IPatternDetails>>> recipes = new LinkedHashMap<>();
        private final Set<AEKey> discovered = new HashSet<>();
        private final ArrayDeque<AEKey> pending = new ArrayDeque<>();
        private final Set<IPatternDetails> seen = new HashSet<>();
        private Iterator<IPatternDetails> candidates = Collections.emptyIterator();
        private Iterator<IPatternDetails> variants = Collections.emptyIterator();
        private IPatternDetails pattern;
        private List<Hk3ExactPlanner.Recipe<AEKey, IPatternDetails>> expanded;
        private List<Hk3ExactPlanner.Recipe<AEKey, IPatternDetails>> accepted;
        private AEKey key;
        private int edges, inspected, recipeCount;
        private boolean done, rejected;

        Capture(Level level, IGrid grid, ICraftingSimulationRequester requester, AEKey target,
                Hk3ExactPlanner.Limits limits) {
            this.level = level;
            this.grid = grid;
            this.requester = requester;
            this.target = target;
            this.limits = limits;
            pending.add(target);
            discovered.add(target);
        }

        boolean step(long deadline) {
            var source = requester.getActionSource();
            var node = requester.getGridNode();
            if (source == null || node == null || node.getGrid() != grid || !node.isActive()) {
                rejected = true;
                return true;
            }
            var service = grid.getCraftingService();
            var storage = grid.getStorageService().getInventory();
            for (int steps = 0; steps < 64 && System.nanoTime() < deadline && !done && !rejected; steps++) {
                if (key == null) {
                    if (pending.isEmpty()) { done = true; break; }
                    key = pending.removeFirst();
                    long available = storage.extract(key, Long.MAX_VALUE, Actionable.SIMULATE, source);
                    if (available < 0) { rejected = true; break; }
                    if (available > 0) stock.put(key, BigInteger.valueOf(available));
                    candidates = List.copyOf(service.getCraftingFor(key)).iterator();
                    accepted = new ArrayList<>();
                    seen.clear();
                } else if (pattern != null) {
                    if (variants.hasNext()) inspectVariant(variants.next());
                    else {
                        parsed.put(pattern, List.copyOf(expanded));
                        pattern = null;
                        variants = Collections.emptyIterator();
                        expanded = null;
                    }
                } else if (candidates.hasNext()) {
                    inspect(candidates.next());
                } else {
                    if (accepted.isEmpty() && key.equals(target)) { rejected = true; break; }
                    if (accepted.isEmpty() && (service.canEmitFor(key) || !seen.isEmpty())) unsupportedKeys.add(key);
                    recipes.put(key, List.copyOf(accepted));
                    key = null;
                }
            }
            return done || rejected;
        }

        private void inspect(IPatternDetails pattern) {
            var source = requester.getActionSource();
            var storage = grid.getStorageService().getInventory();
            if (++inspected > limits.maxEdges()) { rejected = true; return; }
            if (!seen.add(pattern)) return;
            boolean available = false;
            for (var provider : ((CraftingService) grid.getCraftingService()).getProviders(pattern)) {
                if (!Hk3ProbabilitySupport.AVAILABLE || !Hk3ProbabilityOrderService.blocksPush(provider)) {
                    available = true;
                    break;
                }
            }
            if (!available) return;
            var cached = parsed.get(pattern);
            if (cached != null) {
                cached.stream().filter(recipe -> recipe.outputs().containsKey(key)).forEach(accepted::add);
                return;
            }
            if (Hk3ExactScaledPattern.processing(pattern)) {
                if (!Hk3ExactScaledPattern.supports(pattern)) return;
                variants = List.of(pattern).iterator();
            } else if (Hk3ExactBoundPattern.supports(pattern)) {
                variants = Hk3ExactBoundPattern.requiresBinding(pattern)
                        ? Hk3ExactBoundPattern.alternativeCandidates((IMolecularAssemblerSupportedPattern) pattern, level,
                            Math.min(Hk3ExactPlanner.SearchLimits.defaults().maxRouteAttempts(), limits.maxNodes() - recipeCount),
                            resource -> storage.extract(resource, Long.MAX_VALUE, Actionable.SIMULATE, source))
                        : List.of(pattern).iterator();
            } else return;
            this.pattern = pattern;
            expanded = new ArrayList<>();
        }

        private void inspectVariant(IPatternDetails variant) {
            if (variant instanceof Hk3ExactBoundPattern bound && !bound.sameResult(level)) return;
            var outputs = variant.getOutputs();
            Map<AEKey, BigInteger> outputCounts = new LinkedHashMap<>();
            boolean valid = outputs.length > 0;
            for (var output : outputs) {
                if (output == null || output.amount() <= 0) { valid = false; break; }
                outputCounts.merge(output.what(), BigInteger.valueOf(output.amount()), BigInteger::add);
                if (outputCounts.size() > limits.maxEdges() - edges) { rejected = true; return; }
            }
            if (!valid || !outputCounts.containsKey(key)) return;
            Map<AEKey, BigInteger> inputs = new LinkedHashMap<>();
            boolean hasRemainder = false;
            for (var input : variant.getInputs()) {
                var possible = input.getPossibleInputs();
                if (possible.length != 1 || possible[0] == null || possible[0].amount() <= 0
                        || input.getMultiplier() <= 0) {
                    valid = false; break;
                }
                BigInteger amount = BigInteger.valueOf(possible[0].amount())
                        .multiply(BigInteger.valueOf(input.getMultiplier()));
                inputs.merge(possible[0].what(), amount, BigInteger::add);
                AEKey remainder = input.getRemainingKey(possible[0].what());
                if (remainder != null) {
                    hasRemainder = true;
                    outputCounts.merge(remainder, BigInteger.valueOf(input.getMultiplier()), BigInteger::add);
                }
                if (inputs.size() + outputCounts.size() > limits.maxEdges() - edges) { rejected = true; return; }
            }
            if (!valid) return;
            if (++recipeCount > limits.maxNodes()) { rejected = true; return; }
            edges += inputs.size() + outputCounts.size();
            for (var resources : List.of(inputs.keySet(), outputCounts.keySet())) {
                for (AEKey resource : resources) {
                    if (discovered.add(resource)) {
                        if (discovered.size() > limits.maxNodes()) { rejected = true; return; }
                        pending.addLast(resource);
                    }
                }
            }
            var recipe = new Hk3ExactPlanner.Recipe<>(variant, inputs, outputCounts, BigInteger.ONE);
            expanded.add(recipe);
            if (hasRemainder) remainderPatterns.add(variant);
            accepted.add(recipe);
        }

        Hk3AeExactSnapshot finish() {
            if (rejected) throw new IllegalArgumentException(
                    "此路线超出图预算或不支持当前加工／工作台输入；未知动态样板与概率样板仍用原入口");
            BigInteger nodes = countTreeNodes(target, recipes);
            if (nodes == null) nodes = BigInteger.valueOf((long) discovered.size() + edges);
            return new Hk3AeExactSnapshot(target, stock, recipes, remainderPatterns, unsupportedKeys, limits, nodes);
        }
    }

    public Hk3ExactPlanner.Result<AEKey, IPatternDetails> plan(BigInteger amount, BooleanSupplier cancelled) {
        return supportedMissing(Hk3ExactPlanner.plan(target, amount, inventory,
                key -> recipes.getOrDefault(key, List.of()), limits, cancelled));
    }

    public Hk3ExactPlanner.DetailedResult<AEKey, IPatternDetails> planDetailed(
            BigInteger amount, BooleanSupplier cancelled) {
        return supportedMissing(Hk3ExactPlanner.planDetailed(target, amount, inventory,
                key -> recipes.getOrDefault(key, List.of()), limits, cancelled));
    }

    public Hk3ExactPlanner.DetailedResult<AEKey, IPatternDetails> planDetailed(BigInteger amount,
            BooleanSupplier cancelled, Predicate<Hk3ExactPlanner.DetailedResult<AEKey, IPatternDetails>> acceptance) {
        return supportedMissing(Hk3ExactPlanner.planDetailed(target, amount, inventory,
                key -> recipes.getOrDefault(key, List.of()), limits, cancelled, acceptance));
    }

    Hk3ExactPlanner.DetailedResult<AEKey, IPatternDetails> planDetailed(BigInteger amount,
            BooleanSupplier cancelled, Predicate<Hk3ExactPlanner.DetailedResult<AEKey, IPatternDetails>> acceptance,
            Hk3ExactGraphPlanner.Prepared<AEKey, IPatternDetails> prepared) {
        return supportedMissing(new Hk3ExactGraphPlanner<>(Map.of(target, amount), inventory,
                key -> recipes.getOrDefault(key, List.of()), limits, Hk3ExactPlanner.SearchLimits.defaults(),
                cancelled, acceptance).plan(prepared));
    }

    private Hk3ExactPlanner.Result<AEKey, IPatternDetails> supportedMissing(
            Hk3ExactPlanner.Result<AEKey, IPatternDetails> result) {
        if (result.status() != Hk3ExactPlanner.Status.MISSING_INPUT
                || result.missing().keySet().stream().noneMatch(unsupportedKeys::contains)) return result;
        return new Hk3ExactPlanner.Result<>(Hk3ExactPlanner.Status.REJECTED,
                "需求依赖当前不支持的样板、超预算替代组合或合成发信器；大数订单未提交，请使用原生入口",
                result.batches(), result.stockUsed(), result.leafDemand(), result.missing(), result.surplus(),
                result.logicalBytes(), result.visitedNodes(), result.visitedEdges());
    }

    private Hk3ExactPlanner.DetailedResult<AEKey, IPatternDetails> supportedMissing(
            Hk3ExactPlanner.DetailedResult<AEKey, IPatternDetails> detailed) {
        var result = supportedMissing(detailed.result());
        return result == detailed.result() ? detailed : new Hk3ExactPlanner.DetailedResult<>(result,
                detailed.execution(), detailed.seedRequired(), detailed.orderedExecutionRequired(), detailed.routeAttempts());
    }

    public AEKey target() { return target; }
    public Map<AEKey, BigInteger> inventory() { return inventory; }
    public BigInteger treeNodes() { return treeNodes; }

    public boolean sameRecipes(Hk3AeExactSnapshot other) {
        return other != null && target.equals(other.target) && recipes.equals(other.recipes);
    }

    Hk3ExactPlanner.Recipe<AEKey, IPatternDetails> recipe(IPatternDetails pattern) {
        return byPattern.get(pattern);
    }

    boolean hasContainers(IPatternDetails pattern) { return remainderPatterns.contains(pattern); }

    private static BigInteger countTreeNodes(AEKey target,
            Map<AEKey, List<Hk3ExactPlanner.Recipe<AEKey, IPatternDetails>>> recipes) {
        Map<AEKey, Integer> incoming = new HashMap<>();
        recipes.keySet().forEach(key -> incoming.put(key, 0));
        recipes.values().forEach(values -> values.forEach(recipe ->
                recipe.inputs().keySet().forEach(key -> incoming.merge(key, 1, Math::addExact))));
        ArrayDeque<AEKey> ready = new ArrayDeque<>();
        incoming.forEach((key, degree) -> { if (degree == 0) ready.addLast(key); });
        Map<AEKey, BigInteger> multiplicity = new HashMap<>();
        multiplicity.put(target, BigInteger.ONE);
        BigInteger nodes = BigInteger.ZERO;
        int visited = 0;
        while (!ready.isEmpty()) {
            AEKey key = ready.removeFirst();
            BigInteger paths = multiplicity.getOrDefault(key, BigInteger.ZERO);
            nodes = nodes.add(paths);
            visited++;
            for (var recipe : recipes.get(key)) {
                for (AEKey ingredient : recipe.inputs().keySet()) {
                    multiplicity.merge(ingredient, paths, BigInteger::add);
                    if (incoming.compute(ingredient, (ignored, count) -> count - 1) == 0) {
                        ready.addLast(ingredient);
                    }
                }
            }
        }
        return visited == recipes.size() ? nodes : null;
    }
}
