package com.sirin.hk3gtl.common.integration.ae.exact;

import java.math.BigInteger;
import java.util.ArrayDeque;
import java.util.ArrayList;
import java.util.Collections;
import java.util.HashSet;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.function.BooleanSupplier;
import java.util.function.Function;
import java.util.function.Predicate;

public final class Hk3ExactPlanner {
    private static final BigInteger ZERO = BigInteger.ZERO;

    public enum Status { SUCCESS, MISSING_INPUT, REJECTED, UNSUPPORTED, BUDGET_EXCEEDED, CANCELLED }

    public record Limits(int maxNodes, int maxEdges) {
        public Limits {
            if (maxNodes < 1 || maxEdges < 1) throw new IllegalArgumentException("图预算必须为正数");
        }
    }

    /** 限制候选路线、循环顺序证明尝试与压缩程序中的样板条目数。 */
    public record SearchLimits(int maxRouteAttempts, int maxOrderAttempts, int maxSteps) {
        public SearchLimits {
            if (maxRouteAttempts < 1 || maxOrderAttempts < 1 || maxSteps < 1)
                throw new IllegalArgumentException("搜索与执行证书预算必须为正数");
        }
        public static SearchLimits defaults() { return new SearchLimits(64, 16, 8192); }
    }

    /** 一轮按顺序执行列表中每个样板一批，整轮重复次数不展开。 */
    public record Step<R>(List<R> recipes, BigInteger repetitions) {
        public Step {
            recipes = List.copyOf(recipes);

            if (recipes.isEmpty() || repetitions.signum() <= 0)
                throw new IllegalArgumentException("执行单元及重复次数必须为正");
        }
    }

    /** 循环必须按证书执行；原生无序patternTimes不能替代种子与回流证明。 */
    public record DetailedResult<K, R>(Result<K, R> result, List<Step<R>> execution,
                                       Map<K, BigInteger> seedRequired,
                                       boolean orderedExecutionRequired, int routeAttempts,
                                       List<R> cycleRecipes) {
        public DetailedResult {
            execution = List.copyOf(execution);
            seedRequired = immutable(seedRequired);
            cycleRecipes = List.copyOf(cycleRecipes);
        }
    }

    /** 每批逻辑成本由适配器定义，不代表完整AE字节公式。 */
    public record Recipe<K, R>(R id, Map<K, BigInteger> inputs, Map<K, BigInteger> outputs,
                               BigInteger logicalBytesPerBatch) {
        public Recipe {
            inputs = quantities(inputs);
            outputs = quantities(outputs);

            if (logicalBytesPerBatch.signum() < 0) throw new IllegalArgumentException("逻辑成本不能为负数");
        }

        public boolean produces(K key) {
            return outputs.getOrDefault(key, BigInteger.ZERO).compareTo(inputs.getOrDefault(key, BigInteger.ZERO)) > 0;
        }
    }

    /** 缺料计划仅供诊断；只有SUCCESS允许适配器提交。surplus只含本次生产余量。 */
    public record Result<K, R>(Status status, String reason, Map<R, BigInteger> batches,
                               Map<K, BigInteger> stockUsed, Map<K, BigInteger> leafDemand,
                               Map<K, BigInteger> missing, Map<K, BigInteger> surplus,
                               BigInteger logicalBytes, int visitedNodes, int visitedEdges) {
        public Result {
            batches = immutable(batches);
            stockUsed = immutable(stockUsed);
            leafDemand = immutable(leafDemand);
            missing = immutable(missing);
            surplus = immutable(surplus);
        }

        public boolean successful() { return status == Status.SUCCESS; }
    }

    private record Node<K, R>(Recipe<K, R> recipe, List<K> inputs) {}

    private Hk3ExactPlanner() {}

    /** 多输出与可证明循环的入口；旧plan保留保守DAG域，避免旧适配器误提交循环。 */
    public static <K, R> DetailedResult<K, R> planDetailed(K target, BigInteger amount,
            Map<K, BigInteger> inventory, Function<K, List<Recipe<K, R>>> lookup,
            Limits limits, BooleanSupplier cancelled) {
        return planDetailed(target, amount, inventory, lookup, limits, cancelled, result -> true);
    }

    public static <K, R> DetailedResult<K, R> planNexus(K target, BigInteger amount,
            Map<K, BigInteger> inventory, Set<K> infinite, Function<K, List<Recipe<K, R>>> lookup,
            Limits limits, BooleanSupplier cancelled) {
        return new Hk3ExactGraphPlanner<>(Map.of(target, amount), inventoryCopy(inventory), infinite, lookup, limits,
                SearchLimits.defaults(), cancelled, result -> true).plan(null, false, true, Set.of());
    }

    /** 接收本单独占的候选表；后台仅补副产物，库存快照只读。 */
    public static <K, R> DetailedResult<K, R> planCapturedNexus(K target, BigInteger amount,
            Map<K, BigInteger> inventory, Set<K> infinite, Map<K, List<Recipe<K, R>>> graph,
            Iterable<Recipe<K, R>> multiOutput, int edges, Limits limits, Set<K> probabilitySources, BooleanSupplier cancelled) {
        return planCapturedNexus(target, amount, inventory, infinite, graph, multiOutput, edges, limits,
                SearchLimits.defaults(), probabilitySources, cancelled);
    }

    public static <K, R> DetailedResult<K, R> planCapturedNexus(K target, BigInteger amount,
            Map<K, BigInteger> inventory, Set<K> infinite, Map<K, List<Recipe<K, R>>> graph,
            Iterable<Recipe<K, R>> multiOutput, int edges, Limits limits, SearchLimits search,
            Set<K> probabilitySources, BooleanSupplier cancelled) {
        return capturedNexus(target, inventory, infinite, graph, multiOutput, edges, limits, search, probabilitySources, cancelled)
                .solve(amount, true);
    }

    public interface CapturedNexus<K, R> {
        DetailedResult<K, R> solve(BigInteger amount, boolean quoteProbability);
    }

    public static <K, R> CapturedNexus<K, R> capturedNexus(K target, Map<K, BigInteger> inventory, Set<K> infinite,
            Map<K, List<Recipe<K, R>>> graph, Iterable<Recipe<K, R>> multiOutput, int edges, Limits limits,
            SearchLimits search, Set<K> probabilitySources, BooleanSupplier cancelled) {
        var prepared = new Hk3ExactGraphPlanner.Prepared<K, R>();
        return (amount, quote) -> new Hk3ExactGraphPlanner<>(Map.of(target, amount), inventory, infinite, graph::get,
                limits, search, cancelled, result -> true).planCaptured(graph, multiOutput, edges, probabilitySources, prepared, quote);
    }

    public static <K, R> DetailedResult<K, R> planDetailed(K target, BigInteger amount,
            Map<K, BigInteger> inventory, Function<K, List<Recipe<K, R>>> lookup,
            Limits limits, BooleanSupplier cancelled, Predicate<DetailedResult<K, R>> acceptance) {
        return planDetailed(target, amount, inventory, lookup, limits, SearchLimits.defaults(), cancelled, acceptance);
    }

    public static <K, R> DetailedResult<K, R> planDetailed(K target, BigInteger amount,
            Map<K, BigInteger> inventory, Function<K, List<Recipe<K, R>>> lookup,
            Limits limits, SearchLimits searchLimits, BooleanSupplier cancelled) {
        return planDetailed(target, amount, inventory, lookup, limits, searchLimits, cancelled, result -> true);
    }

    public static <K, R> DetailedResult<K, R> planDetailed(K target, BigInteger amount,
            Map<K, BigInteger> inventory, Function<K, List<Recipe<K, R>>> lookup,
            Limits limits, SearchLimits searchLimits, BooleanSupplier cancelled,
            Predicate<DetailedResult<K, R>> acceptance) {
        return planDetailed(Map.of(target, amount), inventory, lookup, limits, searchLimits, cancelled, acceptance);
    }

    /** 所有目标均为新增量；目标库存可做循环种子，但不能抵扣新增需求。 */
    public static <K, R> DetailedResult<K, R> planDetailed(Map<K, BigInteger> targets,
            Map<K, BigInteger> inventory, Function<K, List<Recipe<K, R>>> lookup,
            Limits limits, SearchLimits searchLimits, BooleanSupplier cancelled) {
        return planDetailed(targets, inventory, lookup, limits, searchLimits, cancelled, result -> true);
    }

    public static <K, R> DetailedResult<K, R> planDetailed(Map<K, BigInteger> targets,
            Map<K, BigInteger> inventory, Function<K, List<Recipe<K, R>>> lookup,
            Limits limits, BooleanSupplier cancelled, Predicate<DetailedResult<K, R>> acceptance) {
        return planDetailed(targets, inventory, lookup, limits, SearchLimits.defaults(), cancelled, acceptance);
    }

    /** 接纳条件参与候选搜索，CPU容量或原生计数不安全时仍可尝试后续路线。 */
    public static <K, R> DetailedResult<K, R> planDetailed(Map<K, BigInteger> targets,
            Map<K, BigInteger> inventory, Function<K, List<Recipe<K, R>>> lookup,
            Limits limits, SearchLimits searchLimits, BooleanSupplier cancelled,
            Predicate<DetailedResult<K, R>> acceptance) {
        return new Hk3ExactGraphPlanner<K, R>(targets, inventoryCopy(inventory), lookup, limits, searchLimits, cancelled, acceptance).plan();
    }

    /** amount为新增产量，目标库存不抵扣；inventory与lookup必须来自同一稳定快照。 */
    public static <K, R> Result<K, R> plan(K target, BigInteger amount, Map<K, BigInteger> inventory,
                                          Function<K, List<Recipe<K, R>>> lookup, Limits limits,
                                          BooleanSupplier cancelled) {
        if (amount.signum() <= 0) throw new IllegalArgumentException("目标数量必须为正数");

        Map<K, Node<K, R>> nodes = new LinkedHashMap<>();
        Map<K, Integer> incoming = new LinkedHashMap<>();
        Set<R> recipeIds = new HashSet<>();
        Set<K> discovered = new HashSet<>();
        ArrayDeque<K> pending = new ArrayDeque<>();
        pending.add(target);
        discovered.add(target);
        incoming.put(target, 0);
        int edges = 0;
        while (!pending.isEmpty()) {
            if (stopped(cancelled)) return stopped(Status.CANCELLED, "规划已取消", nodes.size(), edges);
            K key = pending.removeFirst();
            if (nodes.containsKey(key)) continue;
            if (nodes.size() >= limits.maxNodes()) {
                return stopped(Status.BUDGET_EXCEEDED, "目标可达节点超过预算", nodes.size(), edges);
            }
            List<Recipe<K, R>> candidates = lookup.apply(key);
            if (candidates == null || candidates.size() > 1) {
                return stopped(Status.UNSUPPORTED, "配方来源无效或存在多条生产路线", nodes.size(), edges);
            }
            if (candidates.isEmpty()) {
                if (key.equals(target)) {
                    return stopped(Status.UNSUPPORTED, "目标没有可用生产配方", nodes.size(), edges);
                }
                nodes.put(key, new Node<>(null, List.of()));
                continue;
            }
            Recipe<K, R> recipe = candidates.get(0);
            if (recipe.outputs().size() != 1 || !recipe.outputs().containsKey(key)) {
                return stopped(Status.UNSUPPORTED, "首版仅支持匹配需求的唯一单输出配方", nodes.size(), edges);
            }
            if (!recipeIds.add(recipe.id())) {
                return stopped(Status.UNSUPPORTED, "不同产物复用了同一配方身份", nodes.size(), edges);
            }
            if (recipe.inputs().size() > limits.maxEdges() - edges) {
                return stopped(Status.BUDGET_EXCEEDED, "目标可达依赖边超过预算", nodes.size(), edges);
            }
            List<K> inputs = new ArrayList<>(recipe.inputs().size());
            for (K input : recipe.inputs().keySet()) {
                if (stopped(cancelled)) return stopped(Status.CANCELLED, "规划已取消", nodes.size(), edges);
                inputs.add(input);
                edges++;
                incoming.merge(input, 1, Math::addExact);
                // 每个键只入队一次；图规模与产量无关。
                if (discovered.add(input)) {
                    if (discovered.size() > limits.maxNodes()) {
                        return stopped(Status.BUDGET_EXCEEDED, "目标可达节点超过预算", nodes.size(), edges);
                    }
                    pending.addLast(input);
                }
            }
            nodes.put(key, new Node<>(recipe, List.copyOf(inputs)));
        }

        ArrayDeque<K> ready = new ArrayDeque<>();
        incoming.forEach((key, count) -> { if (count == 0) ready.addLast(key); });
        Map<K, BigInteger> demand = new LinkedHashMap<>();
        Map<R, BigInteger> batches = new LinkedHashMap<>();
        Map<K, BigInteger> stockUsed = new LinkedHashMap<>();
        Map<K, BigInteger> leafDemand = new LinkedHashMap<>();
        Map<K, BigInteger> missing = new LinkedHashMap<>();
        Map<K, BigInteger> surplus = new LinkedHashMap<>();
        demand.put(target, amount);
        BigInteger logicalBytes = ZERO;
        int processed = 0;
        while (!ready.isEmpty()) {
            if (stopped(cancelled)) return stopped(Status.CANCELLED, "规划已取消", nodes.size(), edges);
            K key = ready.removeFirst();
            Node<K, R> node = nodes.get(key);
            BigInteger required = demand.getOrDefault(key, ZERO);
            BigInteger remaining = required;
            if (!key.equals(target) && required.signum() > 0) {
                BigInteger available = inventory.getOrDefault(key, ZERO);
                if (available == null || available.signum() < 0) {
                    throw new IllegalArgumentException("库存快照必须为非负整数");
                }
                BigInteger used = available.min(required);
                if (used.signum() > 0) stockUsed.put(key, used);
                remaining = required.subtract(used);
            }
            Recipe<K, R> recipe = node.recipe();
            if (recipe == null) {
                if (required.signum() > 0) leafDemand.put(key, required);
                if (remaining.signum() > 0) missing.put(key, remaining);
            } else if (remaining.signum() > 0) {
                BigInteger output = recipe.outputs().get(key);
                BigInteger count = remaining.subtract(BigInteger.ONE).divide(output).add(BigInteger.ONE);
                batches.put(recipe.id(), count);
                logicalBytes = logicalBytes.add(recipe.logicalBytesPerBatch().multiply(count));
                BigInteger extra = output.multiply(count).subtract(remaining);
                if (extra.signum() > 0) surplus.put(key, extra);
                for (Map.Entry<K, BigInteger> input : recipe.inputs().entrySet()) {
                    if (stopped(cancelled)) return stopped(Status.CANCELLED, "规划已取消", nodes.size(), edges);
                    demand.merge(input.getKey(), input.getValue().multiply(count), BigInteger::add);
                }
            }
            processed++;
            for (K input : node.inputs()) {
                int count = incoming.compute(input, (ignored, old) -> old - 1);
                if (count == 0) ready.addLast(input);
            }
        }
        if (processed != nodes.size()) {
            return stopped(Status.UNSUPPORTED, "目标可达生产路线包含循环", nodes.size(), edges);
        }
        return new Result<>(missing.isEmpty() ? Status.SUCCESS : Status.MISSING_INPUT,
                missing.isEmpty() ? "精确批量规划成功" : "叶子材料库存不足", batches, stockUsed,
                leafDemand, missing, surplus, logicalBytes, nodes.size(), edges);
    }

    private static boolean stopped(BooleanSupplier cancelled) {
        return Thread.currentThread().isInterrupted() || cancelled.getAsBoolean();
    }

    private static <K, R> Result<K, R> stopped(Status status, String reason, int nodes, int edges) {
        return new Result<>(status, reason, Map.of(), Map.of(), Map.of(), Map.of(), Map.of(), ZERO, nodes, edges);
    }

    private static <K> Map<K, BigInteger> quantities(Map<K, BigInteger> source) {
        source.forEach((key, amount) -> {
            if (amount == null || amount.signum() <= 0) throw new IllegalArgumentException("配方数量必须为正整数");
        });
        return immutable(source);
    }

    private static <K, V> Map<K, V> immutable(Map<K, V> source) {
        return switch (source.size()) {
            case 0 -> Map.of();
            case 1 -> Map.copyOf(source);
            default -> Collections.unmodifiableMap(new LinkedHashMap<>(source));
        };
    }

    private static <K> Map<K, BigInteger> inventoryCopy(Map<K, BigInteger> inventory) {
        inventory.forEach((key, value) -> {
            if (key == null || value == null || value.signum() < 0) throw new IllegalArgumentException("库存必须为非负整数");
        });
        return new LinkedHashMap<>(inventory);
    }
}
