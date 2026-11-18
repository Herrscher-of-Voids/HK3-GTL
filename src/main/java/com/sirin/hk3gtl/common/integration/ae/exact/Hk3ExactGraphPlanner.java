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
import java.util.Objects;
import java.util.Set;
import java.util.function.BooleanSupplier;
import java.util.function.Function;
import java.util.function.Predicate;

import static com.sirin.hk3gtl.common.integration.ae.exact.Hk3ExactPlanner.*;

/** 独立的守恒图规划：共享多产物、有限路线与真实库存启动的非负净增益循环。 */
final class Hk3ExactGraphPlanner<K, R> {
    private static final BigInteger ZERO = BigInteger.ZERO;
    private final Map<K, BigInteger> targets;
    private final Map<K, BigInteger> inventory;
    private final Function<K, List<Recipe<K, R>>> lookup;
    private final Limits limits;
    private final SearchLimits search;
    private final BooleanSupplier cancelled;
    private final Predicate<DetailedResult<K, R>> acceptance;
    private Map<K, List<Recipe<K, R>>> choices = new LinkedHashMap<>();
    private Set<K> keys = new HashSet<>();
    private int edges;
    private int attempts;

    static final class Prepared<K, R> {
        private Graph<K, R> graph;
    }

    private record Graph<K, R>(Map<K, List<Recipe<K, R>>> choices, Set<K> keys, int edges) {}

    private static final class Halt extends RuntimeException {
        final Status status;
        Halt(Status status, String reason) { super(reason, null, false, false); this.status = status; }
    }
    private record Walk<R>(R recipe, Iterator<R> next) {}
    private record Route<K, R>(Map<R, Recipe<K, R>> recipes, Map<K, R> producer) {}
    private record Group<R>(List<R> recipes, boolean cyclic) {}
    private record Proof<K, R>(List<R> order, Map<K, BigInteger> seed) {}

    Hk3ExactGraphPlanner(Map<K, BigInteger> targets, Map<K, BigInteger> inventory,
            Function<K, List<Recipe<K, R>>> lookup, Limits limits, SearchLimits search, BooleanSupplier cancelled,
            Predicate<DetailedResult<K, R>> acceptance) {
        this.targets = new LinkedHashMap<>(targets);
        this.inventory = new LinkedHashMap<>(inventory);
        this.lookup = lookup;
        this.limits = limits;
        this.search = search;
        this.cancelled = cancelled;
        this.acceptance = acceptance;
        if (targets.isEmpty()) throw new IllegalArgumentException("至少需要一个新增目标");
        targets.forEach((key, value) -> {
            if (key == null || value == null || value.signum() <= 0) throw new IllegalArgumentException("目标数量必须为正整数");
        });
        inventory.forEach((key, value) -> {
            if (key == null || value == null || value.signum() < 0) throw new IllegalArgumentException("库存必须为非负整数");
        });
    }

    DetailedResult<K, R> plan() {
        return plan(null);
    }

    DetailedResult<K, R> plan(Prepared<K, R> prepared) {
        try {
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
            Map<K, Integer> decision = new LinkedHashMap<>();
            DetailedResult<K, R> firstMissing = null, firstUnsupported = null, firstBudget = null, firstRejected = null;
            while (true) {
                check();
                attempts++;
                List<K> branching = new ArrayList<>();
                DetailedResult<K, R> result;
                try { result = solve(select(decision, branching)); }
                catch (Halt failure) {
                    if (failure.status == Status.CANCELLED) throw failure;
                    result = failed(failure.status, failure.getMessage());
                }
                if (result.result().successful()) {
                    boolean accepted = acceptance.test(result);
                    check();
                    if (accepted) return result;
                    result = failed(Status.REJECTED, "库存可行路线均未通过调用方接纳条件");
                }
                if (result.result().status() == Status.MISSING_INPUT && firstMissing == null) firstMissing = result;
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
                if (attempts >= search.maxRouteAttempts())
                    return failed(Status.BUDGET_EXCEEDED, "候选路线预算耗尽，未将未经证明的路线当作可执行计划");
            }
        } catch (Halt failure) { return failed(failure.status, failure.getMessage()); }
    }

    private void capture() {
        Map<R, Recipe<K, R>> definitions = new LinkedHashMap<>();
        ArrayDeque<K> pending = new ArrayDeque<>(targets.keySet());
        Set<K> queued = new HashSet<>(targets.keySet());
        while (!pending.isEmpty()) {
            check();
            K key = pending.removeFirst();
            keys.add(key);
            var found = lookup.apply(key);
            if (found == null) throw unsupported("配方来源无效");
            if (found.size() > limits.maxNodes()) throw budget("单资源候选数量超过图预算");
            List<Recipe<K, R>> candidates = List.copyOf(found);
            choices.put(key, candidates);
            for (var recipe : candidates) {
                check();
                if (!recipe.outputs().containsKey(key)) throw unsupported("配方未产出对应需求");
                var old = definitions.putIfAbsent(recipe.id(), recipe);
                if (old != null && !old.equals(recipe)) throw unsupported("同一配方身份对应了不同定义");
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
            if (keys.size() > limits.maxNodes()) throw budget("目标闭包资源数超过图预算");
        }
        // 部分AE索引只登记主产物；已发现的副产物仍必须共享同一样板。
        Map<K, Map<R, Recipe<K, R>>> indexed = new LinkedHashMap<>();
        choices.forEach((key, recipes) -> {
            Map<R, Recipe<K, R>> candidates = new LinkedHashMap<>();
            recipes.forEach(recipe -> candidates.putIfAbsent(recipe.id(), recipe));
            indexed.put(key, candidates);
        });
        for (var recipe : definitions.values()) {
            check();
            for (K output : recipe.outputs().keySet())
                indexed.computeIfAbsent(output, key -> new LinkedHashMap<>()).putIfAbsent(recipe.id(), recipe);
        }
        indexed.forEach((key, candidates) -> choices.put(key, List.copyOf(candidates.values())));
    }

    private Route<K, R> select(Map<K, Integer> decision, List<K> branching) {
        Map<R, Recipe<K, R>> selected = new LinkedHashMap<>();
        Map<K, R> producer = new LinkedHashMap<>();
        Set<K> visited = new HashSet<>();
        ArrayDeque<K> pending = new ArrayDeque<>(targets.keySet());
        while (!pending.isEmpty()) {
            check();
            K key = pending.removeFirst();
            if (!visited.add(key) || producer.containsKey(key)) continue;
            var candidates = choices.getOrDefault(key, List.of());
            if (candidates.isEmpty()) continue;
            if (candidates.size() > 1) branching.add(key);
            int index = decision.getOrDefault(key, 0);
            if (index >= candidates.size()) throw unsupported("路线选择无效");
            var recipe = candidates.get(index);
            if (selected.putIfAbsent(recipe.id(), recipe) != null) continue;
            for (K output : recipe.outputs().keySet()) producer.putIfAbsent(output, recipe.id());
            pending.addAll(recipe.inputs().keySet());
        }
        for (K target : targets.keySet()) if (!producer.containsKey(target)) throw unsupported("新增目标没有生产路线");
        return new Route<>(selected, producer);
    }

    private boolean advance(Map<K, Integer> decision, List<K> branching) {
        for (int index = branching.size() - 1; index >= 0; index--) {
            K key = branching.get(index);
            int next = decision.getOrDefault(key, 0) + 1;
            if (next < choices.get(key).size()) {
                decision.put(key, next);
                Set<K> prefix = new HashSet<>(branching.subList(0, index + 1));
                decision.keySet().removeIf(previous -> !prefix.contains(previous));
                return true;
            }
            decision.remove(key);
        }
        return false;
    }

    private DetailedResult<K, R> solve(Route<K, R> route) {
        var groups = groups(route);
        Map<R, Integer> membership = new LinkedHashMap<>();
        for (int group = 0; group < groups.size(); group++)
            for (R recipe : groups.get(group).recipes()) membership.put(recipe, group);
        Map<K, BigInteger> demand = new LinkedHashMap<>(targets), stock = new LinkedHashMap<>();
        Map<K, BigInteger> seeds = new LinkedHashMap<>(), surplus = new LinkedHashMap<>();
        Map<R, BigInteger> batches = new LinkedHashMap<>();
        List<Step<R>> execution = new ArrayList<>();
        BigInteger bytes = ZERO;
        int certificateSize = 0;
        boolean ordered = false;
        for (int groupIndex = 0; groupIndex < groups.size(); groupIndex++) {
            check();
            Group<R> group = groups.get(groupIndex);
            Set<K> outputs = new LinkedHashSet<>();
            Map<K, BigInteger> net = new LinkedHashMap<>(), take = new LinkedHashMap<>(), minimum = new LinkedHashMap<>();
            for (R id : group.recipes()) {
                var recipe = route.recipes().get(id);
                outputs.addAll(recipe.outputs().keySet());
                recipe.outputs().forEach((key, count) -> net.merge(key, count, BigInteger::add));
                for (var input : recipe.inputs().entrySet()) {
                    if (Objects.equals(membership.get(route.producer().get(input.getKey())), groupIndex))
                        net.merge(input.getKey(), input.getValue().negate(), BigInteger::add);
                }
            }
            boolean productionNeeded = false;
            for (K key : outputs) {
                BigInteger needed = demand.getOrDefault(key, ZERO);
                BigInteger used = targets.containsKey(key) ? ZERO : inventory.getOrDefault(key, ZERO).min(needed);
                take.put(key, used);
                minimum.put(key, needed.compareTo(used) > 0 ? BigInteger.ONE : ZERO);
                productionNeeded |= needed.compareTo(used) > 0;
            }
            if (!productionNeeded) { take.forEach((key, count) -> add(stock, key, count)); continue; }
            Proof<K, R> proof = new Proof<>(group.recipes(), Map.of());
            if (group.cyclic()) {
                if (outputs.stream().anyMatch(key -> net.getOrDefault(key, ZERO).compareTo(minimum.get(key)) < 0))
                    group = balance(group, route, net, outputs, minimum, search.maxSteps() - certificateSize);
                proof = prove(group, route.recipes(), outputs);
                if (proof == null) {
                    boolean anyStart = group.recipes().stream().anyMatch(id -> route.recipes().get(id).inputs().entrySet()
                            .stream().filter(input -> outputs.contains(input.getKey())).allMatch(input ->
                                    inventory.getOrDefault(input.getKey(), ZERO).compareTo(input.getValue()) >= 0));
                    if (anyStart) {
                        if (new HashSet<>(group.recipes()).size() > search.maxOrderAttempts()) throw budget("循环顺序搜索预算耗尽");
                        throw unsupported("当前有界顺序搜索未能证明此循环可执行，不宣称种子不可能存在");
                    }
                    Map<K, BigInteger> required = prefix(group.recipes(), route.recipes(), outputs);
                    Map<K, BigInteger> missingSeed = new LinkedHashMap<>();
                    required.forEach((key, count) -> add(missingSeed, key, count.subtract(inventory.getOrDefault(key, ZERO)).max(ZERO)));
                    return new DetailedResult<>(result(Status.MISSING_INPUT, "循环缺少可核验的真实启动种子；没有生成可提交程序",
                            Map.of(), Map.of(), Map.of(), missingSeed, Map.of(), ZERO), List.of(), required, true, attempts);
                }
                proof.seed().forEach((key, count) -> {
                    take.merge(key, count, BigInteger::max);
                    seeds.merge(key, count, BigInteger::add);
                });
                ordered = true;
            }
            BigInteger rounds = ZERO;
            for (K key : outputs) {
                BigInteger deficit = demand.getOrDefault(key, ZERO);
                if (!targets.containsKey(key)) deficit = deficit.subtract(take.getOrDefault(key, ZERO));
                if (deficit.signum() <= 0) continue;
                BigInteger gain = net.getOrDefault(key, ZERO);
                if (gain.signum() <= 0) throw unsupported("循环对此需求没有正净产出，不能用回流抵扣新增量");
                rounds = rounds.max(ceil(deficit, gain));
            }
            if (rounds.signum() <= 0) throw unsupported("执行单元没有可证明的新增需求");
            certificateSize += group.recipes().size();
            if (certificateSize > search.maxSteps()) throw budget("压缩执行程序超过样板条目预算");
            execution.add(new Step<>(proof.order(), rounds));
            for (R id : group.recipes()) {
                var recipe = route.recipes().get(id);
                batches.merge(id, rounds, BigInteger::add);
                bytes = bytes.add(recipe.logicalBytesPerBatch().multiply(rounds));
                for (var input : recipe.inputs().entrySet())
                    if (!Objects.equals(membership.get(route.producer().get(input.getKey())), groupIndex))
                        demand.merge(input.getKey(), input.getValue().multiply(rounds), BigInteger::add);
            }
            for (K key : outputs) {
                add(stock, key, take.getOrDefault(key, ZERO));
                add(surplus, key, take.getOrDefault(key, ZERO).add(net.getOrDefault(key, ZERO).multiply(rounds))
                        .subtract(demand.getOrDefault(key, ZERO)));
            }
        }
        Map<K, BigInteger> leafDemand = new LinkedHashMap<>(), missing = new LinkedHashMap<>();
        for (var entry : demand.entrySet()) {
            check();
            if (route.producer().containsKey(entry.getKey())) continue;
            BigInteger used = inventory.getOrDefault(entry.getKey(), ZERO).min(entry.getValue());
            add(leafDemand, entry.getKey(), entry.getValue());
            add(stock, entry.getKey(), used);
            add(missing, entry.getKey(), entry.getValue().subtract(used));
        }
        Collections.reverse(execution);
        return new DetailedResult<>(result(missing.isEmpty() ? Status.SUCCESS : Status.MISSING_INPUT,
                missing.isEmpty() ? "守恒规划与压缩执行顺序已证明" : "外部原料不足；执行证书仅供诊断",
                batches, stock, leafDemand, missing, surplus, bytes), execution, seeds, ordered, attempts);
    }

    /** 按短缺资源选择正净产出样板增配，展开规模服从现有程序预算。 */
    private Group<R> balance(Group<R> group, Route<K, R> route, Map<K, BigInteger> net,
            Set<K> internal, Map<K, BigInteger> minimum, int budget) {
        Map<R, Integer> weights = new LinkedHashMap<>();
        group.recipes().forEach(id -> weights.put(id, 1));
        int size = group.recipes().size();
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
            R id = null;
            BigInteger gain = ZERO;
            for (R candidate : weights.keySet()) {
                var definition = route.recipes().get(candidate);
                BigInteger available = definition.outputs().getOrDefault(key, ZERO)
                        .subtract(definition.inputs().getOrDefault(key, ZERO));
                if (available.compareTo(gain) > 0) { id = candidate; gain = available; }
            }
            if (id == null) throw unsupported("所选执行组没有能补足短缺资源的正净产出样板");
            var recipe = route.recipes().get(id);
            BigInteger added = ceil(deficit, gain);
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
        return new Group<>(expanded, true);
    }

    /** 所有内部资源的整轮净量非负，首轮前缀种子足够即可归纳证明任意大数轮数。 */
    private Proof<K, R> prove(Group<R> group, Map<R, Recipe<K, R>> recipes, Set<K> internal) {
        Map<R, Integer> counts = new LinkedHashMap<>();
        group.recipes().forEach(id -> counts.merge(id, 1, Integer::sum));
        int attempts = Math.min(search.maxOrderAttempts(), counts.size());
        for (int start = 0; start < attempts; start++) {
            check();
            List<R> candidates = new ArrayList<>(counts.keySet());
            Collections.rotate(candidates, -start);
            Map<R, Integer> left = new LinkedHashMap<>(counts);
            Map<K, BigInteger> balance = new LinkedHashMap<>();
            internal.forEach(key -> balance.put(key, inventory.getOrDefault(key, ZERO)));
            List<R> order = new ArrayList<>();
            while (!left.isEmpty()) {
                check();
                R chosen = null;
                for (R id : candidates) {
                    if (!left.containsKey(id)) continue;
                    boolean ready = true;
                    for (var input : recipes.get(id).inputs().entrySet())
                        if (internal.contains(input.getKey()) && balance.getOrDefault(input.getKey(), ZERO).compareTo(input.getValue()) < 0)
                            ready = false;
                    if (ready) { chosen = id; break; }
                }
                if (chosen == null) break;
                var recipe = recipes.get(chosen);
                recipe.inputs().forEach((key, count) -> { if (internal.contains(key)) balance.merge(key, count.negate(), BigInteger::add); });
                recipe.outputs().forEach((key, count) -> balance.merge(key, count, BigInteger::add));
                order.add(chosen);
                if (left.merge(chosen, -1, Integer::sum) == 0) left.remove(chosen);
            }
            if (left.isEmpty()) return new Proof<>(order, prefix(order, recipes, internal));
        }
        return null;
    }

    private Map<K, BigInteger> prefix(List<R> order, Map<R, Recipe<K, R>> recipes, Set<K> internal) {
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
        return seed;
    }

    /** 迭代Kosaraju，再对分量图按需求向原料方向排序；没有Java递归。 */
    private List<Group<R>> groups(Route<K, R> route) {
        Map<R, Set<R>> graph = new LinkedHashMap<>(), reverse = new LinkedHashMap<>();
        route.recipes().keySet().forEach(id -> { graph.put(id, new LinkedHashSet<>()); reverse.put(id, new LinkedHashSet<>()); });
        route.recipes().forEach((id, recipe) -> recipe.inputs().keySet().forEach(key -> {
            R producer = route.producer().get(key);
            if (producer != null) { graph.get(id).add(producer); reverse.get(producer).add(id); }
        }));
        // 共享副产物的样板同组核算；整组执行可能多产，但不会重复抵扣同一份产物。
        route.recipes().forEach((id, recipe) -> recipe.outputs().keySet().forEach(key -> {
            R producer = route.producer().get(key);
            if (!id.equals(producer)) {
                graph.get(id).add(producer); reverse.get(producer).add(id);
                graph.get(producer).add(id); reverse.get(id).add(producer);
            }
        }));
        Set<R> visited = new HashSet<>();
        List<R> finish = new ArrayList<>();
        for (R id : graph.keySet()) {
            if (!visited.add(id)) continue;
            ArrayDeque<Walk<R>> stack = new ArrayDeque<>();
            stack.push(new Walk<>(id, graph.get(id).iterator()));
            while (!stack.isEmpty()) {
                check();
                var frame = stack.peek();
                if (!frame.next().hasNext()) { finish.add(frame.recipe()); stack.pop(); continue; }
                R next = frame.next().next();
                if (visited.add(next)) stack.push(new Walk<>(next, graph.get(next).iterator()));
            }
        }
        Collections.reverse(finish);
        visited.clear();
        Map<R, Integer> position = new LinkedHashMap<>();
        for (R id : route.recipes().keySet()) position.put(id, position.size());
        List<Group<R>> result = new ArrayList<>();
        for (R id : finish) {
            if (!visited.add(id)) continue;
            List<R> members = new ArrayList<>();
            ArrayDeque<R> stack = new ArrayDeque<>();
            stack.push(id);
            while (!stack.isEmpty()) {
                check();
                R current = stack.pop(); members.add(current);
                for (R next : reverse.get(current)) if (visited.add(next)) stack.push(next);
            }
            members.sort(java.util.Comparator.comparingInt(position::get));
            result.add(new Group<>(members, members.size() > 1 || graph.get(members.get(0)).contains(members.get(0))));
        }
        return result;
    }

    private Result<K, R> result(Status status, String reason, Map<R, BigInteger> batches,
            Map<K, BigInteger> stock, Map<K, BigInteger> leaf, Map<K, BigInteger> missing,
            Map<K, BigInteger> surplus, BigInteger bytes) {
        return new Result<>(status, reason, batches, stock, leaf, missing, surplus, bytes, keys.size(), edges);
    }
    private DetailedResult<K, R> failed(Status status, String reason) {
        return new DetailedResult<>(result(status, reason, Map.of(), Map.of(), Map.of(), Map.of(), Map.of(), ZERO),
                List.of(), Map.of(), false, attempts);
    }
    private void check() {
        if (Thread.currentThread().isInterrupted() || cancelled.getAsBoolean()) throw new Halt(Status.CANCELLED, "规划已取消");
    }
    private static Halt unsupported(String message) { return new Halt(Status.UNSUPPORTED, message); }
    private static Halt budget(String message) { return new Halt(Status.BUDGET_EXCEEDED, message); }
    private static BigInteger ceil(BigInteger amount, BigInteger perBatch) { return amount.subtract(BigInteger.ONE).divide(perBatch).add(BigInteger.ONE); }
    private static <K> void add(Map<K, BigInteger> map, K key, BigInteger amount) {
        if (amount.signum() < 0) throw new IllegalStateException("守恒规划产生了负余量");
        if (amount.signum() > 0) map.merge(key, amount, BigInteger::add);
    }
}
