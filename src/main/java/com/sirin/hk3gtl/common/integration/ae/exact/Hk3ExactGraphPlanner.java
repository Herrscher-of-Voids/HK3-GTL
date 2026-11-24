package com.sirin.hk3gtl.common.integration.ae.exact;

import java.math.BigInteger;
import java.util.ArrayDeque;
import java.util.ArrayList;
import java.util.Collections;
import java.util.HashSet;
import java.util.Iterator;
import java.util.LinkedHashMap;
import java.util.LinkedHashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.function.BooleanSupplier;
import java.util.function.Function;
import java.util.function.Predicate;

import static com.sirin.hk3gtl.common.integration.ae.exact.Hk3ExactPlanner.*;

/** 独立的守恒图规划：共享多产物、有限路线与可制种、可按库存承担周转损耗的循环。 */
final class Hk3ExactGraphPlanner<K, R> {
    private static final BigInteger ZERO = BigInteger.ZERO;
    private final Map<K, BigInteger> targets;
    private final Map<K, BigInteger> inventory;
    private final Set<K> infinite;
    private final Function<K, List<Recipe<K, R>>> lookup;
    private final Limits limits;
    private final SearchLimits search;
    private final BooleanSupplier cancelled;
    private final Predicate<DetailedResult<K, R>> acceptance;
    private Map<K, List<Recipe<K, R>>> choices;
    private Set<K> keys;
    private int edges;
    private int attempts;
    private boolean routeNeedsCycle;
    private boolean allowSeedCraft;
    private Set<K> probabilitySources = Set.of();
    private Map<K, BigInteger> quotedStock = Map.of();
    private OrderBudget seedRouteBudget;

    static final class Prepared<K, R> {
        private Graph<K, R> graph;
        private Layout<K, R> fixedRoute;
    }

    private record Graph<K, R>(Map<K, List<Recipe<K, R>>> choices, Set<K> keys, int edges) {}

    private static final class Halt extends RuntimeException {
        final Status status;
        Halt(Status status, String reason) { super(reason, null, false, false); this.status = status; }
    }
    private record Walk<K, R>(R recipe, Iterator<K> inputs, Iterator<R> shared) {
        R next(Map<K, R> producer) {
            while (inputs.hasNext()) {
                R next = producer.get(inputs.next());
                if (next != null) return next;
            }
            return shared.hasNext() ? shared.next() : null;
        }
    }
    private record Route<K, R>(Map<R, Recipe<K, R>> recipes, Map<K, R> producer, Map<R, List<R>> shared) {
        Walk<K, R> walk(R id) {
            var extra = shared.get(id);
            return new Walk<>(id, recipes.get(id).inputs().keySet().iterator(), extra == null ? Collections.emptyIterator() : extra.iterator());
        }
    }
    private record Groups<R>(List<R> order, Map<R, List<R>> cycles) {}
    private record Layout<K, R>(Route<K, R> route, Groups<R> groups) {}
    private record Loss(BigInteger tail, BigInteger floor) {}
    private record Proof<K, R>(List<R> order, Map<K, BigInteger> seed, DetailedResult<K, R> startup) {}
    private static final class OrderBudget {
        int left;
        OrderBudget(int left) { this.left = left; }
        void take() { if (left == 0) throw budget("循环启动顺序与制种样板的搜索次数已用完"); left--; }
    }

    Hk3ExactGraphPlanner(Map<K, BigInteger> targets, Map<K, BigInteger> inventory,
            Function<K, List<Recipe<K, R>>> lookup, Limits limits, SearchLimits search, BooleanSupplier cancelled,
            Predicate<DetailedResult<K, R>> acceptance) {
        this(targets, inventory, Set.of(), lookup, limits, search, cancelled, acceptance);
    }

    Hk3ExactGraphPlanner(Map<K, BigInteger> targets, Map<K, BigInteger> inventory, Set<K> infinite,
            Function<K, List<Recipe<K, R>>> lookup, Limits limits, SearchLimits search, BooleanSupplier cancelled,
            Predicate<DetailedResult<K, R>> acceptance) {
        this.targets = new LinkedHashMap<>(targets);
        this.inventory = inventory;
        this.infinite = infinite;
        this.lookup = lookup;
        this.limits = limits;
        this.search = search;
        this.cancelled = cancelled;
        this.acceptance = acceptance;
        if (targets.isEmpty()) throw new IllegalArgumentException("至少需要一个新增目标");
        targets.forEach((key, value) -> {
            if (key == null || value == null || value.signum() <= 0) throw new IllegalArgumentException("目标数量必须为正整数");
        });
    }

    DetailedResult<K, R> plan() {
        return plan(null);
    }

    DetailedResult<K, R> plan(Prepared<K, R> prepared) {
        return plan(prepared, true, false, Set.of());
    }

    DetailedResult<K, R> plan(Prepared<K, R> prepared, boolean keepAcyclicSteps, boolean allowSeedCraft, Set<K> probabilitySources) {
        this.probabilitySources = probabilitySources;
        this.allowSeedCraft = allowSeedCraft;
        return search(keepAcyclicSteps, prepared, () -> {
            if (prepared == null) {
                capture();
            } else if (prepared.graph == null) {
                capture();
                choices = Collections.unmodifiableMap(choices);
                keys = Collections.unmodifiableSet(keys);
                prepared.graph = new Graph<>(choices, keys, edges);
            } else {
                choices = prepared.graph.choices();
                keys = prepared.graph.keys();
                edges = prepared.graph.edges();
            }
        });
    }

    DetailedResult<K, R> planCaptured(Map<K, List<Recipe<K, R>>> captured, Iterable<Recipe<K, R>> multiOutput,
            int edgeCount, Set<K> probabilitySources, Prepared<K, R> prepared, boolean quoteProbability) {
        this.probabilitySources = probabilitySources;
        allowSeedCraft = true;
        choices = captured;
        keys = captured.keySet();
        edges = edgeCount;
        var plan = search(false, prepared, () -> {
            if (prepared.graph != null) return;
            indexByproducts(multiOutput, new LinkedHashMap<>());
            prepared.graph = new Graph<>(choices, keys, edges);
        });
        if (!quoteProbability || !incompleteProbabilityPlan(plan)) return plan;
        var first = plan;
        quotedStock = new LinkedHashMap<>();
        do {
            if (attempts >= search.maxRouteAttempts()) return failed(Status.BUDGET_EXCEEDED, "概率前置规划超过路线预算");
            plan.result().missing().forEach((key, amount) -> quotedStock.put(key, stock(key).add(amount)));
            plan = search(false, prepared, () -> {});
        } while (incompleteProbabilityPlan(plan));
        var result = plan.result();
        if (!result.successful() && result.status() != Status.MISSING_INPUT) return plan;
        Map<K, BigInteger> needs = new LinkedHashMap<>();
        boolean completeRoute = result.successful() || !result.batches().isEmpty();
        for (var entry : quotedStock.entrySet()) {
            K key = entry.getKey();
            BigInteger required = completeRoute ? result.stockUsed().getOrDefault(key, ZERO) : entry.getValue();
            add(needs, key, required.subtract(inventory.getOrDefault(key, ZERO)).max(ZERO));
        }
        result.missing().forEach((key, amount) -> add(needs, key, amount));
        if (needs.isEmpty()) return first;
        // 报价只交出缺口。机器实物入网后，主单用真实库存重新规划。
        return new DetailedResult<>(result(Status.MISSING_INPUT, "等待制种与生产原料", Map.of(), Map.of(), Map.of(),
                needs, Map.of(), result.logicalBytes()), List.of(), first.seedRequired(), true, attempts);
    }

    private DetailedResult<K, R> search(boolean keepAcyclicSteps, Prepared<K, R> prepared, Runnable prepare) {
        try {
            prepare.run();
            Map<K, Integer> decision = prepared != null && prepared.fixedRoute != null ? Map.of() : new LinkedHashMap<>();
            DetailedResult<K, R> firstMissing = null, firstUnsupported = null, firstBudget = null, firstRejected = null;
            while (true) {
                check();
                attempts++;
                routeNeedsCycle = false;
                var fixed = prepared == null ? null : prepared.fixedRoute;
                List<K> branching = fixed == null ? new ArrayList<>() : List.of();
                DetailedResult<K, R> result;
                try {
                    if (fixed == null) {
                        var route = select(decision, branching);
                        var groups = groups(route);
                        if (prepared != null && branching.isEmpty()) prepared.fixedRoute = new Layout<>(route, groups);
                        result = solve(route, groups, keepAcyclicSteps);
                    } else result = solve(fixed.route(), fixed.groups(), keepAcyclicSteps);
                } catch (Halt failure) {
                    if (failure.status == Status.CANCELLED) throw failure;
                    result = failed(failure.status, failure.getMessage());
                }
                if (result.result().successful()) {
                    boolean accepted = acceptance.test(result);
                    check();
                    if (accepted) return result;
                    result = failed(Status.REJECTED, "库存可行路线均未通过调用方接纳条件");
                }
                if (result.result().status() == Status.MISSING_INPUT && (firstMissing == null
                        || probabilityCanSupply(result) && !probabilityCanSupply(firstMissing))) firstMissing = result;
                if (result.result().status() == Status.BUDGET_EXCEEDED && firstBudget == null) firstBudget = result;
                if (result.result().status() == Status.UNSUPPORTED && firstUnsupported == null) firstUnsupported = result;
                if (result.result().status() == Status.REJECTED && firstRejected == null) firstRejected = result;
                if (!advance(decision, branching)) {
                    DetailedResult<K, R> chosen;
                    if (firstBudget != null) chosen = firstBudget;
                    else if (firstRejected != null) chosen = firstUnsupported == null ? firstRejected : firstUnsupported;
                    else chosen = firstMissing == null ? firstUnsupported : firstMissing;
                    return new DetailedResult<>(chosen.result(), chosen.execution(), chosen.seedRequired(),
                            chosen.orderedExecutionRequired(), attempts);
                }
                if (seedRouteBudget != null) seedRouteBudget.take();
                if (attempts >= search.maxRouteAttempts())
                    return failed(Status.BUDGET_EXCEEDED, "候选路线预算耗尽，未将未经证明的路线当作可执行计划");
            }
        } catch (Halt failure) { return failed(failure.status, failure.getMessage()); }
    }

    private boolean incompleteProbabilityPlan(DetailedResult<K, R> plan) {
        return plan.result().status() == Status.MISSING_INPUT && plan.orderedExecutionRequired()
                && plan.result().batches().isEmpty() && probabilityCanSupply(plan);
    }

    private boolean probabilityCanSupply(DetailedResult<K, R> plan) {
        return !probabilitySources.isEmpty() && !plan.result().missing().isEmpty()
                && probabilitySources.containsAll(plan.result().missing().keySet());
    }

    private void capture() {
        choices = new LinkedHashMap<>();
        keys = new HashSet<>();
        Map<R, Recipe<K, R>> definitions = new LinkedHashMap<>();
        Map<K, Set<R>> indexedIds = new LinkedHashMap<>();
        ArrayDeque<K> pending = new ArrayDeque<>(targets.keySet());
        Set<K> queued = new HashSet<>(targets.keySet());
        while (!pending.isEmpty()) {
            check();
            K key = pending.removeFirst();
            keys.add(key);
            var found = lookup.apply(key);
            if (found == null) throw unsupported("配方来源无效");
            if (found.size() > limits.maxNodes()) throw budget("单资源候选数量超过图预算");
            if (keys.size() > limits.maxNodes()) throw budget("目标闭包资源数超过图预算");
            if (found.isEmpty()) continue;
            List<Recipe<K, R>> candidates = new ArrayList<>(found.size());
            Set<R> candidateIds = found.size() == 1 ? null : new HashSet<>();
            choices.put(key, candidates);
            if (candidateIds != null) indexedIds.put(key, candidateIds);
            for (var recipe : found) {
                check();
                if (!recipe.outputs().containsKey(key)) throw unsupported("配方未产出对应需求");
                var old = definitions.putIfAbsent(recipe.id(), recipe);
                if (old != null && !old.equals(recipe)) throw unsupported("同一配方身份对应了不同定义");
                if (candidateIds == null || candidateIds.add(recipe.id())) candidates.add(recipe);
                if (old != null) continue;
                if (definitions.size() > limits.maxNodes()) throw budget("候选样板数量超过图预算");
                int added = recipe.inputs().size() + recipe.outputs().size();
                if (added > limits.maxEdges() - edges) throw budget("候选输入输出边超过图预算");
                edges += added;
                keys.addAll(recipe.inputs().keySet());
                keys.addAll(recipe.outputs().keySet());
                if (keys.size() > limits.maxNodes()) throw budget("目标闭包资源数超过图预算");
                for (K input : recipe.inputs().keySet()) if (queued.add(input)) pending.addLast(input);
            }
        }
        indexByproducts(definitions.values(), indexedIds);
    }

    // 部分 AE 索引只登记主产物；保留原候选顺序，再补副产物。
    private void indexByproducts(Iterable<Recipe<K, R>> recipes, Map<K, Set<R>> indexedIds) {
        for (var recipe : recipes) {
            check();
            if (recipe.outputs().size() == 1) continue;
            for (K output : recipe.outputs().keySet()) {
                var candidates = choices.get(output);
                if (candidates == null || candidates.isEmpty()) {
                    List<Recipe<K, R>> first = new ArrayList<>(1);
                    first.add(recipe);
                    choices.put(output, first);
                    if (keys.size() > limits.maxNodes()) throw budget("目标闭包资源数超过图预算");
                    continue;
                }
                if (candidates.get(0).id().equals(recipe.id())) continue;
                var ids = indexedIds.computeIfAbsent(output, key -> {
                    Set<R> known = new HashSet<>();
                    for (var candidate : candidates) known.add(candidate.id());
                    return known;
                });
                if (ids.add(recipe.id())) candidates.add(recipe);
            }
        }
    }

    private List<Recipe<K, R>> candidates(K key) {
        return seedRouteBudget == null ? choices.getOrDefault(key, List.of()) : choices.computeIfAbsent(key, lookup);
    }

    private Route<K, R> select(Map<K, Integer> decision, List<K> branching) {
        Map<R, Recipe<K, R>> selected = new LinkedHashMap<>();
        Map<K, R> producer = new LinkedHashMap<>();
        Map<R, List<R>> shared = new java.util.HashMap<>();
        Set<K> queued = new HashSet<>(targets.keySet());
        ArrayDeque<K> pending = new ArrayDeque<>(targets.keySet());
        while (!pending.isEmpty()) {
            check();
            K key = pending.removeFirst();
            if (producer.containsKey(key)) continue;
            var candidates = candidates(key);
            if (candidates.isEmpty()) continue;
            int paths = pathCount(key, candidates.size());
            if (paths > 1) branching.add(key);
            int index = decision.getOrDefault(key, 0);
            if (index == candidates.size()) continue;
            var recipe = candidates.get(index);
            if (selected.putIfAbsent(recipe.id(), recipe) != null) continue;
            for (K output : recipe.outputs().keySet()) {
                R previous = producer.putIfAbsent(output, recipe.id());
                if (previous != null) {
                    shared.computeIfAbsent(recipe.id(), k -> new ArrayList<>()).add(previous);
                    shared.computeIfAbsent(previous, k -> new ArrayList<>()).add(recipe.id());
                }
            }
            for (K input : recipe.inputs().keySet()) if (queued.add(input)) pending.addLast(input);
        }
        for (K target : targets.keySet()) if (!producer.containsKey(target)) throw unsupported("新增目标没有生产路线");
        return new Route<>(selected, producer, shared);
    }

    private int pathCount(K key, int recipes) {
        // 另一路从库存取料，缺口只能由已确认的概率机器实际补齐。
        return probabilitySources.contains(key) && !targets.containsKey(key) ? recipes + 1 : recipes;
    }

    private boolean advance(Map<K, Integer> decision, List<K> branching) {
        for (int index = branching.size() - 1; index >= 0; index--) {
            K key = branching.get(index);
            int next = decision.getOrDefault(key, 0) + 1;
            if (next < pathCount(key, choices.get(key).size())) {
                decision.put(key, next);
                Set<K> prefix = new HashSet<>(branching.subList(0, index + 1));
                decision.keySet().removeIf(previous -> !prefix.contains(previous));
                return true;
            }
            decision.remove(key);
        }
        return false;
    }

    private DetailedResult<K, R> solve(Route<K, R> route, Groups<R> groups, boolean keepAcyclicSteps) {
        boolean hasCycles = !groups.cycles().isEmpty();
        if (seedRouteBudget != null && hasCycles) throw unsupported("制种路线包含循环");
        boolean keepSteps = keepAcyclicSteps || hasCycles;
        Map<K, BigInteger> demand = new LinkedHashMap<>(targets), stock = new LinkedHashMap<>();
        Map<K, BigInteger> seeds = new LinkedHashMap<>(), surplus = new LinkedHashMap<>();
        Map<R, BigInteger> batches = new LinkedHashMap<>();
        List<Step<R>> execution = keepSteps ? new ArrayList<>() : List.of();
        BigInteger bytes = ZERO;
        int certificateSize = 0;
        boolean ordered = false;
        for (R id : groups.order()) {
            check();
            List<R> group = hasCycles ? groups.cycles().get(id) : null;
            boolean cyclic = group != null;
            Map<K, BigInteger> net = cyclic ? new LinkedHashMap<>() : route.recipes().get(id).outputs();
            Set<K> outputs = cyclic ? new LinkedHashSet<>() : net.keySet();
            if (cyclic) {
                for (R member : group) outputs.addAll(route.recipes().get(member).outputs().keySet());
                for (R member : group) {
                    var recipe = route.recipes().get(member);
                    recipe.outputs().forEach((key, count) -> net.merge(key, count, BigInteger::add));
                    for (var input : recipe.inputs().entrySet()) {
                        if (outputs.contains(input.getKey()))
                            net.merge(input.getKey(), input.getValue().negate(), BigInteger::add);
                    }
                }
            }
            boolean productionNeeded = false;
            for (K key : outputs) {
                BigInteger needed = demand.getOrDefault(key, ZERO);
                BigInteger used = targets.containsKey(key) ? ZERO : available(key, needed);
                if (used.signum() > 0) stock.put(key, used);
                productionNeeded |= needed.compareTo(used) > 0;
            }
            if (!productionNeeded) {
                outputs.forEach(demand::remove);
                continue;
            }
            List<R> order = group;
            List<Step<R>> starts = List.of();
            Map<K, BigInteger> made = Map.of();
            Map<K, Loss> losses = Map.of();
            BigInteger rounds = ZERO;
            if (cyclic) {
                Map<K, BigInteger> minimum = new LinkedHashMap<>();
                routeNeedsCycle = true;
                for (K key : outputs) minimum.put(key, demand.getOrDefault(key, ZERO)
                        .compareTo(stock.getOrDefault(key, ZERO)) > 0 ? BigInteger.ONE : ZERO);
                boolean rebalance = outputs.stream().anyMatch(key -> net.get(key).compareTo(minimum.get(key)) < 0)
                        && !canFundLosses(group, net, minimum, demand, stock);
                var orderBudget = new OrderBudget(search.maxOrderAttempts() - 1);
                Proof<K, R> proof;
                Map<K, BigInteger> required;
                while (true) {
                    if (rebalance) group = balance(group, route, net, outputs, minimum, search.maxSteps() - certificateSize);
                    if (net.values().stream().anyMatch(amount -> amount.signum() < 0)) {
                        rounds = requiredRounds(net, demand, stock, made);
                        if (rounds.signum() == 0) {
                            Map<K, BigInteger> shortfall = new LinkedHashMap<>();
                            for (K key : outputs) add(shortfall, key, demand.getOrDefault(key, ZERO).subtract(stock.getOrDefault(key, ZERO)));
                            return new DetailedResult<>(result(Status.MISSING_INPUT, "循环不能补充自身净消耗的周转料",
                                    Map.of(), Map.of(), Map.of(), shortfall, Map.of(), ZERO), List.of(), Map.of(), true, attempts);
                        }
                        losses = losses(net, demand, rounds);
                    } else losses = Map.of();
                    required = requiredStock(group, route.recipes(), outputs, losses);
                    boolean stockOnly = !rebalance && group.size() > 1 && !coversLosses(losses.keySet(), required);
                    proof = prove(group, route, outputs, losses, required, orderBudget, stockOnly);
                    if (proof != null || !stockOnly) break;
                    rebalance = true;
                }
                if (proof == null) {
                    return new DetailedResult<>(result(Status.MISSING_INPUT, losses.isEmpty() ? "循环缺少启动种子" : "循环周转料不足",
                            Map.of(), Map.of(), Map.of(), missingSeed(required), Map.of(), ZERO), List.of(), required, true, attempts);
                }
                if (proof.startup() != null) {
                    var startup = proof.startup().result();
                    if (!startup.successful()) return new DetailedResult<>(result(Status.MISSING_INPUT, "制种样板缺少概率原料",
                            Map.of(), Map.of(), Map.of(), startup.missing(), Map.of(), ZERO), List.of(), proof.seed(), true, attempts);
                    starts = proof.startup().execution();
                    made = missingSeed(proof.seed());
                    for (var extra : startup.surplus().entrySet()) {
                        if (outputs.contains(extra.getKey())) add(made, extra.getKey(), extra.getValue());
                        else add(surplus, extra.getKey(), extra.getValue());
                    }
                    startup.batches().forEach((part, count) -> add(batches, part, count));
                    startup.stockUsed().forEach((key, count) -> add(demand, key, count));
                    bytes = bytes.add(startup.logicalBytes());
                }
                for (var seed : proof.seed().entrySet()) {
                    K key = seed.getKey();
                    BigInteger fromStock = seed.getValue().subtract(made.getOrDefault(key, ZERO)).max(ZERO);
                    if (fromStock.signum() > 0) {
                        stock.merge(key, fromStock, BigInteger::max);
                        seeds.merge(key, fromStock, BigInteger::add);
                    }
                }
                order = proof.order();
                ordered = true;
            }
            if (losses.isEmpty()) rounds = requiredRounds(net, demand, stock, made);
            if (rounds.signum() <= 0 && starts.isEmpty()) throw unsupported("执行单元没有可证明的新增需求");
            int parts = cyclic ? group.size() : 1;
            certificateSize += (rounds.signum() > 0 ? parts : 0) + starts.size();
            if (certificateSize > search.maxSteps()) throw budget("压缩执行程序超过样板条目预算");
            if (keepSteps) {
                if (rounds.signum() > 0) execution.add(new Step<>(cyclic ? order : List.of(id), rounds));
                for (int i = starts.size() - 1; i >= 0; i--) execution.add(starts.get(i));
            }
            if (rounds.signum() > 0) for (int part = 0; part < parts; part++) {
                R member = cyclic ? group.get(part) : id;
                var recipe = route.recipes().get(member);
                batches.merge(member, rounds, BigInteger::add);
                bytes = bytes.add(recipe.logicalBytesPerBatch().multiply(rounds));
                for (var input : recipe.inputs().entrySet())
                    if (!cyclic || !outputs.contains(input.getKey()))
                        demand.merge(input.getKey(), input.getValue().multiply(rounds), BigInteger::add);
            }
            for (K key : outputs) {
                var needed = demand.remove(key);
                add(surplus, key, stock.getOrDefault(key, ZERO).add(made.getOrDefault(key, ZERO)).add(net.get(key).multiply(rounds))
                        .subtract(needed == null ? ZERO : needed));
            }
        }
        Map<K, BigInteger> missing = new LinkedHashMap<>();
        for (var entry : demand.entrySet()) {
            check();
            BigInteger used = available(entry.getKey(), entry.getValue());
            add(stock, entry.getKey(), used);
            add(missing, entry.getKey(), entry.getValue().subtract(used));
        }
        if (keepSteps) Collections.reverse(execution);
        return new DetailedResult<>(result(missing.isEmpty() ? Status.SUCCESS : Status.MISSING_INPUT,
                missing.isEmpty() ? "守恒规划与压缩执行顺序已证明" : "外部原料不足；执行证书仅供诊断",
                batches, stock, demand, missing, surplus, bytes), execution, seeds, ordered, attempts);
    }

    private BigInteger requiredRounds(Map<K, BigInteger> net, Map<K, BigInteger> demand,
            Map<K, BigInteger> stock, Map<K, BigInteger> made) {
        BigInteger rounds = ZERO;
        for (var output : net.entrySet()) {
            K key = output.getKey();
            BigInteger gain = output.getValue();
            if (gain.signum() < 0 && !targets.containsKey(key)) continue;
            BigInteger deficit = demand.getOrDefault(key, ZERO).subtract(made.getOrDefault(key, ZERO));
            if (!targets.containsKey(key)) deficit = deficit.subtract(stock.getOrDefault(key, ZERO));
            if (deficit.signum() <= 0) continue;
            if (gain.signum() <= 0) throw unsupported("循环对此需求没有正净产出，不能用回流抵扣新增量");
            rounds = rounds.max(ceil(deficit, gain));
        }
        return rounds;
    }

    private Map<K, Loss> losses(Map<K, BigInteger> net, Map<K, BigInteger> demand, BigInteger rounds) {
        Map<K, Loss> losses = new LinkedHashMap<>();
        net.forEach((key, gain) -> {
            if (gain.signum() < 0) {
                BigInteger consumed = gain.negate().multiply(rounds);
                losses.put(key, new Loss(consumed.add(gain), demand.getOrDefault(key, ZERO).add(consumed)));
            }
        });
        return losses;
    }

    private Map<K, BigInteger> missingSeed(Map<K, BigInteger> required) {
        Map<K, BigInteger> missing = new LinkedHashMap<>();
        required.forEach((key, count) -> add(missing, key, count.subtract(available(key, count))));
        return missing;
    }

    private DetailedResult<K, R> seedPlan(Map<K, BigInteger> missing, Route<K, R> route, Set<K> internal, OrderBudget budget) {
        var startup = new Hk3ExactGraphPlanner<>(missing, inventory, infinite, key ->
                choices.getOrDefault(key, List.of()).stream().filter(recipe -> !route.recipes().containsKey(recipe.id())
                        && (recipe.outputs().size() == 1 || recipe.outputs().keySet().stream()
                                .noneMatch(output -> route.producer().containsKey(output) && !internal.contains(output)))
                        && Collections.disjoint(recipe.inputs().keySet(), route.producer().keySet())).toList(),
                limits, search, cancelled, result -> true);
        startup.probabilitySources = probabilitySources;
        startup.quotedStock = quotedStock;
        startup.seedRouteBudget = budget;
        startup.choices = new java.util.HashMap<>();
        startup.keys = keys;
        startup.edges = edges;
        var plan = startup.search(true, null, () -> {});
        var status = plan.result().status();
        if (status == Status.CANCELLED || status == Status.BUDGET_EXCEEDED) throw new Halt(status, plan.result().reason());
        return plan.result().successful() || status == Status.MISSING_INPUT && probabilityCanSupply(plan) ? plan : null;
    }

    private boolean canFundLosses(List<R> group, Map<K, BigInteger> net, Map<K, BigInteger> minimum,
            Map<K, BigInteger> demand, Map<K, BigInteger> stock) {
        if (!allowSeedCraft) return false;
        for (var output : net.entrySet()) {
            var gain = output.getValue();
            if (gain.compareTo(minimum.get(output.getKey())) < 0
                    && (gain.signum() >= 0 || targets.containsKey(output.getKey()))) return false;
        }
        if (group.size() == 1) return true;
        BigInteger rounds = requiredRounds(net, demand, stock, Map.of());
        if (rounds.signum() == 0) return false;
        // 净消耗与样板顺序无关；每轮先投哪一份周转料由 prove 选择。
        for (var output : net.entrySet()) if (output.getValue().signum() < 0) {
            K key = output.getKey();
            var floor = demand.getOrDefault(key, ZERO).subtract(output.getValue().multiply(rounds));
            if (available(key, floor).compareTo(floor) < 0) return false;
        }
        return true;
    }

    private boolean coversLosses(Set<K> keys, Map<K, BigInteger> required) {
        for (K key : keys) if (available(key, required.get(key)).compareTo(required.get(key)) < 0) return false;
        return true;
    }

    /** 按短缺资源选择正净产出样板增配，展开规模服从现有程序预算。 */
    private List<R> balance(List<R> group, Route<K, R> route, Map<K, BigInteger> net,
            Set<K> internal, Map<K, BigInteger> minimum, int budget) {
        Map<R, Integer> weights = new LinkedHashMap<>();
        record Producer<R>(R id, BigInteger gain) {}
        Map<K, Producer<R>> producers = new java.util.HashMap<>();
        for (R id : group) {
            weights.put(id, 1);
            var recipe = route.recipes().get(id);
            for (var output : recipe.outputs().entrySet()) {
                K key = output.getKey();
                BigInteger gain = output.getValue().subtract(recipe.inputs().getOrDefault(key, ZERO));
                var best = producers.get(key);
                if (gain.signum() > 0 && (best == null || gain.compareTo(best.gain()) > 0))
                    producers.put(key, new Producer<>(id, gain));
            }
        }
        int size = group.size();
        ArrayDeque<K> deficits = new ArrayDeque<>();
        Set<K> queued = new HashSet<>();
        net.forEach((key, amount) -> {
            if (amount.compareTo(minimum.getOrDefault(key, ZERO)) < 0) { deficits.add(key); queued.add(key); }
        });
        while (!deficits.isEmpty()) {
            check();
            K key = deficits.removeFirst();
            queued.remove(key);
            BigInteger deficit = minimum.getOrDefault(key, ZERO).subtract(net.get(key));
            if (deficit.signum() <= 0) continue;
            var best = producers.get(key);
            if (best == null && allowSeedCraft && net.get(key).signum() < 0 && !targets.containsKey(key)) continue;
            if (best == null) throw unsupported("所选执行组没有能补足短缺资源的正净产出样板");
            R id = best.id();
            var recipe = route.recipes().get(id);
            BigInteger added = ceil(deficit, best.gain());
            if (added.compareTo(BigInteger.valueOf(budget - size)) > 0)
                throw budget("循环整数配比搜索达到程序预算，未断言不存在可行配比");
            int count = added.intValueExact();
            size += count;
            weights.merge(id, count, Integer::sum);
            recipe.outputs().forEach((resource, amount) -> net.merge(resource, amount.multiply(added), BigInteger::add));
            for (var input : recipe.inputs().entrySet()) if (internal.contains(input.getKey())) {
                BigInteger amount = net.merge(input.getKey(), input.getValue().multiply(added).negate(), BigInteger::add);
                if (amount.compareTo(minimum.getOrDefault(input.getKey(), ZERO)) < 0 && queued.add(input.getKey()))
                    deficits.addLast(input.getKey());
            }
        }
        List<R> expanded = new ArrayList<>(size);
        weights.forEach((id, count) -> { for (int i = 0; i < count; i++) expanded.add(id); });
        return expanded;
    }

    /** 净损耗资源按最后一轮的前缀验证，其余资源按首轮验证。 */
    private Proof<K, R> prove(List<R> group, Route<K, R> route, Set<K> internal, Map<K, Loss> losses,
            Map<K, BigInteger> required, OrderBudget budget, boolean stockOnly) {
        if (required.entrySet().stream().allMatch(seed -> available(seed.getKey(), seed.getValue()).equals(seed.getValue())))
            return new Proof<>(group, required, null);
        if (group.size() == 1) {
            if (!allowSeedCraft) return null;
            var startup = seedPlan(missingSeed(required), route, internal, budget);
            return startup == null ? null : new Proof<>(group, required, startup);
        }
        Map<R, Integer> counts = new LinkedHashMap<>();
        group.forEach(id -> counts.merge(id, 1, Integer::sum));
        var candidates = counts.keySet().stream().map(route.recipes()::get).toList();
        int[] left = counts.values().stream().mapToInt(Integer::intValue).toArray();
        int length = group.size(), size = candidates.size();
        int[] next = new int[length], path = new int[length];
        boolean[] tried = new boolean[length];
        Map<K, BigInteger> balance = new java.util.HashMap<>();
        internal.forEach(key -> balance.put(key, stock(key)));
        record Raised<K>(K key, BigInteger before) {}
        record SeedChange<K>(int depth, List<Raised<K>> keys) {}
        Map<K, BigInteger> extra = new LinkedHashMap<>();
        losses.forEach((key, loss) -> {
            if (infinite.contains(key)) return;
            BigInteger have = balance.get(key);
            balance.put(key, have.subtract(loss.tail()));
            add(extra, key, loss.floor().subtract(have).max(ZERO));
        });
        var changes = new ArrayDeque<SeedChange<K>>();
        var order = new ArrayList<R>(length);
        Proof<K, R> awaitingSupply = null;
        while (true) {
            check();
            int depth = order.size();
            if (depth == length) {
                var startup = extra.isEmpty() ? null : seedPlan(extra, route, internal, budget);
                if (extra.isEmpty() || startup != null && startup.result().successful())
                    return new Proof<>(order, requiredStock(order, route.recipes(), internal, losses), startup);
                if (startup != null && awaitingSupply == null)
                    awaitingSupply = new Proof<>(List.of(), requiredStock(order, route.recipes(), internal, losses), startup);
            }
            int end = allowSeedCraft && !stockOnly ? size * 2 : size;
            while (depth < length && next[depth] < end) {
                int slot = next[depth]++;
                boolean craft = slot >= size;
                int index = craft ? slot - size : slot;
                if (left[index] == 0) continue;
                var recipe = candidates.get(index);
                boolean needsSeed = !ready(recipe, internal, balance, extra);
                if (needsSeed != craft) continue;
                if (tried[depth]) {
                    if (stockOnly && budget.left == 0) return null;
                    budget.take();
                }
                tried[depth] = true;
                if (craft) {
                    var raised = new ArrayList<Raised<K>>();
                    for (var input : recipe.inputs().entrySet()) {
                        K key = input.getKey();
                        if (!internal.contains(key) || infinite.contains(key)) continue;
                        BigInteger shortage = input.getValue().subtract(balance.getOrDefault(key, ZERO));
                        var before = extra.getOrDefault(key, ZERO);
                        if (shortage.compareTo(before) > 0) {
                            raised.add(new Raised<>(key, before));
                            extra.put(key, shortage);
                        }
                    }
                    changes.push(new SeedChange<>(depth, raised));
                }
                path[depth] = index;
                left[index]--;
                applyRoundStep(recipe, internal, balance, true);
                order.add(recipe.id());
                break;
            }
            if (order.size() > depth) continue;
            if (depth == 0) return awaitingSupply;
            if (depth < length) {
                next[depth] = 0;
                tried[depth] = false;
            }
            int parent = depth - 1, index = path[parent];
            order.remove(parent);
            left[index]++;
            applyRoundStep(candidates.get(index), internal, balance, false);
            if (!changes.isEmpty() && changes.peek().depth() == parent) for (var change : changes.pop().keys()) {
                if (change.before().signum() == 0) extra.remove(change.key());
                else extra.put(change.key(), change.before());
            }
        }
    }

    private boolean ready(Recipe<K, R> recipe, Set<K> internal, Map<K, BigInteger> balance, Map<K, BigInteger> extra) {
        for (var input : recipe.inputs().entrySet()) {
            K key = input.getKey();
            if (!internal.contains(key) || infinite.contains(key)) continue;
            BigInteger have = balance.getOrDefault(key, ZERO);
            if (have.compareTo(input.getValue()) < 0 && have.add(extra.getOrDefault(key, ZERO)).compareTo(input.getValue()) < 0)
                return false;
        }
        return true;
    }

    private void applyRoundStep(Recipe<K, R> recipe, Set<K> internal, Map<K, BigInteger> balance, boolean forward) {
        recipe.inputs().forEach((key, count) -> { if (internal.contains(key)) balance.merge(key, forward ? count.negate() : count, BigInteger::add); });
        recipe.outputs().forEach((key, count) -> balance.merge(key, forward ? count : count.negate(), BigInteger::add));
    }

    private Map<K, BigInteger> requiredStock(List<R> order, Map<R, Recipe<K, R>> recipes, Set<K> internal, Map<K, Loss> losses) {
        Map<K, BigInteger> balance = new LinkedHashMap<>(), seed = new LinkedHashMap<>();
        for (R id : order) {
            check();
            var recipe = recipes.get(id);
            for (var input : recipe.inputs().entrySet()) if (internal.contains(input.getKey())) {
                BigInteger required = input.getValue().subtract(balance.getOrDefault(input.getKey(), ZERO));
                if (required.signum() > 0) seed.merge(input.getKey(), required, BigInteger::max);
                balance.merge(input.getKey(), input.getValue().negate(), BigInteger::add);
            }
            recipe.outputs().forEach((key, count) -> balance.merge(key, count, BigInteger::add));
        }
        losses.forEach((key, loss) -> seed.put(key, seed.getOrDefault(key, ZERO).add(loss.tail()).max(loss.floor())));
        return seed;
    }

    private Groups<R> groups(Route<K, R> route) {
        if (route.recipes().size() == 1) {
            var recipe = route.recipes().values().iterator().next();
            var order = List.of(recipe.id());
            return new Groups<>(order, Collections.disjoint(recipe.inputs().keySet(), recipe.outputs().keySet())
                    ? Map.of() : Map.of(recipe.id(), order));
        }
        // Gabow 双栈遍历：根栈中的下标分隔尚未归组的样板，回边只合并这些分界。
        var position = new it.unimi.dsi.fastutil.objects.Object2IntOpenHashMap<R>(route.recipes().size());
        position.defaultReturnValue(-2);
        var open = new ArrayList<R>();
        int[] roots = new int[route.recipes().size()];
        int depth = 0;
        List<R> finish = new ArrayList<>(route.recipes().size());
        ArrayDeque<Walk<K, R>> stack = new ArrayDeque<>();
        Map<R, List<R>> cycles = new java.util.HashMap<>(), memberGroups = new java.util.HashMap<>();
        for (R id : route.recipes().keySet()) {
            if (position.containsKey(id)) continue;
            position.put(id, open.size()); roots[depth++] = open.size(); open.add(id);
            stack.push(route.walk(id));
            while (!stack.isEmpty()) {
                check();
                var frame = stack.peek();
                R next = frame.next(route.producer());
                if (next != null) {
                    int seen = position.putIfAbsent(next, open.size());
                    if (seen == -2) {
                        roots[depth++] = open.size(); open.add(next); stack.push(route.walk(next));
                    } else if (seen >= 0) while (roots[depth - 1] > seen) depth--;
                    continue;
                }
                stack.pop();
                R root = frame.recipe();
                int first = roots[depth - 1];
                if (position.getInt(root) != first) continue;
                depth--;
                finish.add(root);
                if (open.size() - first > 1) {
                    var ordered = new ArrayList<R>(open.size() - first);
                    cycles.put(root, ordered);
                    while (open.size() > first) {
                        R member = open.remove(open.size() - 1);
                        position.put(member, -1); memberGroups.put(member, ordered);
                    }
                } else {
                    open.remove(open.size() - 1); position.put(root, -1);
                    var recipe = route.recipes().get(root);
                    if (!Collections.disjoint(recipe.inputs().keySet(), recipe.outputs().keySet())) cycles.put(root, List.of(root));
                }
            }
        }
        // 沿选路时的样板顺序填回各组，保留原先的制种顺序。
        if (!memberGroups.isEmpty()) for (R id : route.recipes().keySet()) {
            var group = memberGroups.get(id);
            if (group != null) group.add(id);
        }
        Collections.reverse(finish);
        return new Groups<>(finish, cycles);
    }

    private Result<K, R> result(Status status, String reason, Map<R, BigInteger> batches,
            Map<K, BigInteger> stock, Map<K, BigInteger> leaf, Map<K, BigInteger> missing,
            Map<K, BigInteger> surplus, BigInteger bytes) {
        return new Result<>(status, reason, batches, stock, leaf, missing, surplus, bytes, keys.size(), edges);
    }
    private DetailedResult<K, R> failed(Status status, String reason) {
        return new DetailedResult<>(result(status, reason, Map.of(), Map.of(), Map.of(), Map.of(), Map.of(), ZERO),
                List.of(), Map.of(), routeNeedsCycle, attempts);
    }
    private void check() {
        if (Thread.currentThread().isInterrupted() || cancelled.getAsBoolean()) throw new Halt(Status.CANCELLED, "规划已取消");
    }
    private BigInteger stock(K key) {
        var quoted = quotedStock.get(key);
        return quoted == null ? inventory.getOrDefault(key, ZERO) : quoted;
    }
    private BigInteger available(K key, BigInteger needed) {
        return infinite.contains(key) ? needed : stock(key).min(needed);
    }
    private static Halt unsupported(String message) { return new Halt(Status.UNSUPPORTED, message); }
    private static Halt budget(String message) { return new Halt(Status.BUDGET_EXCEEDED, message); }
    private static BigInteger ceil(BigInteger amount, BigInteger perBatch) {
        return BigInteger.ONE.equals(perBatch) ? amount : amount.subtract(BigInteger.ONE).divide(perBatch).add(BigInteger.ONE);
    }
    private static <K> void add(Map<K, BigInteger> map, K key, BigInteger amount) {
        if (amount.signum() < 0) throw new IllegalStateException("守恒规划产生了负余量");
        if (amount.signum() > 0) map.merge(key, amount, BigInteger::add);
    }
}
