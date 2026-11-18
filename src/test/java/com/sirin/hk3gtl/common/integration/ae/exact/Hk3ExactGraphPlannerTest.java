package com.sirin.hk3gtl.common.integration.ae.exact;

import java.math.BigInteger;
import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.LinkedHashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.concurrent.atomic.AtomicInteger;

import static com.sirin.hk3gtl.common.integration.ae.exact.Hk3ExactPlanner.*;

/** 独立校验证书前缀、巨大轮次及逐资源守恒，不冒充AE执行验收。 */
public final class Hk3ExactGraphPlannerTest {
    private static final Limits LIMITS = new Limits(1000, 4000);
    private static final SearchLimits SEARCH = SearchLimits.defaults();
    private static int checks;

    public static void main(String[] args) {
        coproducts();
        alternatives();
        seededCycles();
        rejectedCycles();
        budgets();
        deterministicSweep();
        deepGraph();
        System.out.println("多输出与种子循环离线核验通过：" + checks + "项；未进行AE或游戏实测。");
    }

    private static void deepGraph() {
        int depth = 10_000;
        AtomicInteger lookups = new AtomicInteger();
        var result = Hk3ExactPlanner.<Integer, Integer>planDetailed(0, n(1), Map.of(depth, n(1)), key -> {
            lookups.incrementAndGet();
            return key == depth ? List.of() : List.of(new Recipe<>(key, Map.of(key + 1, n(1)), Map.of(key, n(1)), n(1)));
        }, new Limits(depth + 1, depth * 2), new SearchLimits(1, 1, depth), () -> false);
        check(result.result().successful() && result.execution().size() == depth, "万层详细图迭代构建证书，无栈溢出");
        check(lookups.get() == depth + 1 && result.execution().get(0).recipes().equals(List.of(depth - 1)), "每键查询一次且深层生产者最先执行");
    }

    private static void coproducts() {
        var joint = recipe("joint", Map.of("ore", n(2)), ordered("a", 3, "b", 2));
        var goals = ordered("a", 7, "b", 5);
        var result = run(goals, Map.of("ore", n(6)), List.of(joint));
        check(result.result().batches().equals(Map.of("joint", n(3))), "多目标共享一次批数，不为两个输出重复生产");
        check(result.result().surplus().equals(ordered("a", 2, "b", 1)), "多产物余量统一结算");
        verify(result, goals, Map.of("ore", n(6)), List.of(joint));

        var assemble = recipe("assemble", ordered("a", 1, "b", 1), Map.of("target", n(1)));
        var shared = recipe("shared", Map.of("ore", n(1)), ordered("a", 1, "b", 1));
        var hiddenSide = Hk3ExactPlanner.<String, String>planDetailed("target", n(9), Map.of("ore", n(9)), key -> switch (key) {
            case "target" -> List.of(assemble);
            case "b" -> List.of(shared);
            default -> List.of();
        }, LIMITS, SEARCH, () -> false);
        check(hiddenSide.result().batches().equals(Map.of("assemble", n(9), "shared", n(9))), "AE未索引副产物时自动复用已发现样板");
        check(!hiddenSide.orderedExecutionRequired() && hiddenSide.execution().get(0).recipes().equals(List.of("shared")), "DAG证书按生产者到消费者执行");
        verify(hiddenSide, Map.of("target", n(9)), Map.of("ore", n(9)), List.of(assemble, shared));

        var stocked = run(Map.of("target", n(7)), ordered("a", 5, "ore", 7), List.of(assemble, shared));
        check(stocked.result().batches().get("shared").equals(n(7)) && stocked.result().surplus().get("a").equals(n(5)), "一个产物有库存时另一个需求仍决定共享批量");
        verify(stocked, Map.of("target", n(7)), ordered("a", 5, "ore", 7), List.of(assemble, shared));
    }

    private static void alternatives() {
        var expensive = recipe("expensive", Map.of("ore", n(2)), Map.of("target", n(1)));
        var cheap = recipe("cheap", Map.of("ore", n(1)), Map.of("target", n(1)));
        var result = run(Map.of("target", n(3)), Map.of("ore", n(3)), List.of(expensive, cheap));
        check(result.result().successful() && result.routeAttempts() == 2
                && result.result().batches().equals(Map.of("cheap", n(3))), "第一条缺料时有界搜索后续可行路线");
        verify(result, Map.of("target", n(3)), Map.of("ore", n(3)), List.of(expensive, cheap));
        var capped = detailed(Map.of("target", n(3)), Map.of("ore", n(3)), List.of(expensive, cheap), new SearchLimits(1, 16, 100));
        check(capped.result().status() == Status.BUDGET_EXCEEDED && capped.execution().isEmpty(), "未穷尽候选时不把首份缺料计划当作搜索结论");
        var conflicting = recipe("expensive", Map.of("ore", n(9)), Map.of("target", n(1)));
        check(run(Map.of("target", n(1)), Map.of(), List.of(expensive, conflicting)).result().status() == Status.UNSUPPORTED, "同一身份冲突定义不能混用");

        AtomicInteger offers = new AtomicInteger();
        java.util.function.Function<String, List<Recipe<String, String>>> lookup = key ->
                key.equals("target") ? List.of(expensive, cheap) : List.of();
        var accepted = Hk3ExactPlanner.planDetailed("target", n(3), Map.of("ore", n(6)), lookup,
                LIMITS, () -> false, candidate -> {
                    offers.incrementAndGet();
                    return candidate.result().batches().containsKey("cheap");
                });
        check(accepted.result().successful() && accepted.routeAttempts() == 2 && offers.get() == 2
                && accepted.result().batches().equals(Map.of("cheap", n(3))), "首条库存可行但接纳拒绝后继续搜索第二条");
        verify(accepted, Map.of("target", n(3)), Map.of("ore", n(6)), List.of(expensive, cheap));
        var rejected = Hk3ExactPlanner.planDetailed(Map.of("target", n(3)), Map.of("ore", n(6)), lookup,
                LIMITS, SEARCH, () -> false, candidate -> false);
        check(rejected.result().status() == Status.REJECTED && rejected.routeAttempts() == 2
                && rejected.execution().isEmpty() && rejected.result().batches().isEmpty()
                && rejected.result().reason().equals("库存可行路线均未通过调用方接纳条件"), "所有接纳拒绝不泄露可提交成功计划");
        var stalled = recipe("stalled", Map.of("target", n(1)), Map.of("target", n(1)));
        var mixed = Hk3ExactPlanner.<String, String>planDetailed("target", n(3), ordered("ore", 6, "target", 1),
                key -> key.equals("target") ? List.of(expensive, stalled) : List.of(), LIMITS,
                () -> false, candidate -> false);
        check(mixed.result().status() == Status.UNSUPPORTED && mixed.execution().isEmpty(),
                "真正不支持的候选不能被接纳拒绝状态掩盖");
        var cappedAcceptance = Hk3ExactPlanner.planDetailed("target", n(3), Map.of("ore", n(6)), lookup,
                LIMITS, new SearchLimits(1, 16, 100), () -> false, candidate -> false);
        check(cappedAcceptance.result().status() == Status.BUDGET_EXCEEDED
                && cappedAcceptance.execution().isEmpty(), "接纳拒绝仍服从候选预算，不假称已穷尽");
        java.util.concurrent.atomic.AtomicBoolean cancelled = new java.util.concurrent.atomic.AtomicBoolean();
        var cancelledAcceptance = Hk3ExactPlanner.planDetailed("target", n(3), Map.of("ore", n(6)), lookup,
                LIMITS, cancelled::get, candidate -> { cancelled.set(true); return true; });
        check(cancelledAcceptance.result().status() == Status.CANCELLED
                && cancelledAcceptance.execution().isEmpty(), "接纳期间取消不得返回成功证书");
    }

    private static void seededCycles() {
        BigInteger huge = BigInteger.ONE.shiftLeft(120).add(n(7));
        var grow = recipe("grow", ordered("target", 3, "ore", 2), Map.of("target", n(4)));
        var stock = Map.of("target", n(3), "ore", huge.multiply(n(2)));
        var growing = run(Map.of("target", huge), stock, List.of(grow));
        check(growing.result().batches().get("grow").equals(huge), "单样板按净增量计算而非毛产量");
        check(growing.seedRequired().equals(Map.of("target", n(3))) && growing.result().stockUsed().get("target").equals(n(3)), "真实目标库存只做种子不抵扣新增量");
        check(growing.result().surplus().equals(Map.of("target", n(3))) && growing.execution().size() == 1
                && growing.execution().get(0).repetitions().equals(huge), "巨大轮次压缩且种子完整归还");
        verify(growing, Map.of("target", huge), stock, List.of(grow));

        var catalyst = recipe("catalyst", ordered("cat", 1, "ore", 2), ordered("cat", 1, "target", 1));
        var catalysed = run(Map.of("target", huge), Map.of("cat", n(1), "ore", huge.multiply(n(2))), List.of(catalyst));
        check(catalysed.result().stockUsed().get("cat").equals(n(1))
                && catalysed.result().surplus().equals(Map.of("cat", n(1))), "催化剂抽取一次并完整返还");
        verify(catalysed, Map.of("target", huge), Map.of("cat", n(1), "ore", huge.multiply(n(2))), List.of(catalyst));

        var ab = recipe("ab", Map.of("a", n(1)), Map.of("b", n(1)));
        var bc = recipe("bc", Map.of("b", n(1)), Map.of("c", n(1)));
        var ca = recipe("ca", Map.of("c", n(1)), ordered("a", 1, "target", 1));
        var ring = run(Map.of("target", huge), Map.of("a", n(1)), List.of(ab, bc, ca));
        check(ring.orderedExecutionRequired() && ring.execution().size() == 1
                && ring.execution().get(0).recipes().equals(List.of("ab", "bc", "ca")), "三样板环从真实种子推出可执行顺序");
        check(ring.seedRequired().equals(Map.of("a", n(1))) && ring.result().batches().values().stream().allMatch(huge::equals), "单环聚合次数与启动证明精确");
        verify(ring, Map.of("target", huge), Map.of("a", n(1)), List.of(ab, bc, ca));

        var ba = recipe("ba", Map.of("b", n(1)), Map.of("a", n(2)));
        var two = run(Map.of("a", huge), Map.of("a", n(1)), List.of(ab, ba));
        check(two.result().batches().get("ab").equals(huge) && two.result().surplus().equals(Map.of("a", n(1))), "双样板增殖保留目标种子");
        verify(two, Map.of("a", huge), Map.of("a", n(1)), List.of(ab, ba));
    }

    private static void rejectedCycles() {
        var grow = recipe("grow", Map.of("target", n(1)), Map.of("target", n(2)));
        var noSeed = run(Map.of("target", n(99)), Map.of(), List.of(grow));
        check(noSeed.result().status() == Status.MISSING_INPUT && noSeed.execution().isEmpty()
                && noSeed.result().missing().equals(Map.of("target", n(1))), "净收益不能在零种子下自举");
        var ab = recipe("ab", Map.of("a", n(1)), Map.of("b", n(1)));
        var ba = recipe("ba", Map.of("b", n(1)), Map.of("a", n(1)));
        check(run(Map.of("a", n(1)), Map.of("a", n(1)), List.of(ab, ba)).result().status() == Status.UNSUPPORTED, "零净循环不能把目标库存冒充新增量");
        var lossy = recipe("ab", Map.of("a", n(2)), Map.of("b", n(1)));
        check(run(Map.of("b", n(1)), Map.of("a", n(99)), List.of(lossy, ba)).result().status() == Status.UNSUPPORTED, "减少内部资源的复杂配比不进入当前支持域");
        var seedAndRaw = recipe("make", ordered("cat", 1, "ore", 2), ordered("cat", 1, "target", 1));
        var missing = run(Map.of("target", n(3)), ordered("cat", 1, "ore", 4), List.of(seedAndRaw));
        check(missing.result().status() == Status.MISSING_INPUT && missing.result().missing().equals(Map.of("ore", n(2))), "有种子仍必须满足真实外部原料");
    }

    private static void budgets() {
        var a = recipe("a", Map.of("ore", n(1)), Map.of("a", n(1)));
        var target = recipe("target", Map.of("a", n(1)), Map.of("target", n(1)));
        check(detailed(Map.of("target", n(1)), Map.of("ore", n(1)), List.of(a, target), new SearchLimits(4, 4, 1))
                .result().status() == Status.BUDGET_EXCEEDED, "压缩程序条目预算有效");
        var direct = recipe("direct", Map.of("ore", n(1)), Map.of("target", n(1)));
        var shorter = detailed(Map.of("target", n(1)), Map.of("ore", n(1)), List.of(a, target, direct), new SearchLimits(4, 4, 1));
        check(shorter.result().successful() && shorter.result().batches().equals(Map.of("direct", n(1))), "首条路线超程序预算后仍可选择更短的合法路线");
        AtomicInteger lookups = new AtomicInteger();
        var cancel = Hk3ExactPlanner.<String, String>planDetailed("target", n(1), Map.of(), key -> {
            lookups.incrementAndGet(); return List.of(target);
        }, LIMITS, SEARCH, () -> true);
        check(cancel.result().status() == Status.CANCELLED && lookups.get() == 0 && cancel.execution().isEmpty(), "取消不查图也不交付部分证书");
        AtomicInteger work = new AtomicInteger();
        var midCancel = Hk3ExactPlanner.<String, String>planDetailed("target", n(1), Map.of("ore", n(1)),
                key -> key.equals("target") ? List.of(target) : key.equals("a") ? List.of(a) : List.of(),
                LIMITS, SEARCH, () -> work.incrementAndGet() >= 18);
        check(midCancel.result().status() == Status.CANCELLED && midCancel.result().batches().isEmpty(), "中途取消清除所有部分计划");
    }

    private static void deterministicSweep() {
        for (int seed = 1; seed <= 20; seed++) {
            BigInteger amount = n(seed * 13L + 7);
            var grow = recipe("grow", ordered("target", seed, "ore", 3), Map.of("target", n(seed + 2)));
            var stock = Map.of("target", n(seed), "ore", amount.add(n(1)).divide(n(2)).multiply(n(3)));
            var result = run(Map.of("target", amount), stock, List.of(grow));
            verify(result, Map.of("target", amount), stock, List.of(grow));
        }
    }

    /** 不按轮次迭代：前缀缺口+负净量×(轮次−1)独立证明整段可执行。 */
    private static void verify(DetailedResult<String, String> result, Map<String, BigInteger> goals,
            Map<String, BigInteger> inventory, List<Recipe<String, String>> recipes) {
        check(result.result().successful(), "成功样例必须真正成功：" + result.result().reason());
        Map<String, Recipe<String, String>> byId = new LinkedHashMap<>();
        recipes.forEach(recipe -> byId.put(recipe.id(), recipe));
        Map<String, BigInteger> balance = new LinkedHashMap<>(result.result().stockUsed());
        result.result().stockUsed().forEach((key, count) -> check(count.compareTo(inventory.getOrDefault(key, n(0))) <= 0, "抽取不能超过真实库存"));
        Map<String, BigInteger> executed = new LinkedHashMap<>();
        for (var step : result.execution()) {
            Map<String, BigInteger> delta = new LinkedHashMap<>(), prefix = new LinkedHashMap<>();
            for (String id : step.recipes()) {
                var recipe = byId.get(id);
                check(recipe != null, "程序只引用已知样板");
                recipe.inputs().forEach((key, count) -> {
                    prefix.merge(key, count.subtract(delta.getOrDefault(key, n(0))), BigInteger::max);
                    delta.merge(key, count.negate(), BigInteger::add);
                });
                recipe.outputs().forEach((key, count) -> delta.merge(key, count, BigInteger::add));
                executed.merge(id, step.repetitions(), BigInteger::add);
            }
            Set<String> all = new LinkedHashSet<>(delta.keySet()); all.addAll(prefix.keySet());
            for (String key : all) {
                BigInteger required = prefix.getOrDefault(key, n(0)).max(n(0)).add(delta.getOrDefault(key, n(0))
                        .negate().max(n(0)).multiply(step.repetitions().subtract(n(1))));
                check(balance.getOrDefault(key, n(0)).compareTo(required) >= 0, "每轮前缀均有真实输入：" + key);
                balance.merge(key, delta.getOrDefault(key, n(0)).multiply(step.repetitions()), BigInteger::add);
            }
        }
        check(executed.equals(result.result().batches()), "程序轮次与聚合样板数量一致");
        goals.forEach((key, count) -> balance.merge(key, count.negate(), BigInteger::add));
        balance.entrySet().removeIf(entry -> entry.getValue().signum() == 0);
        check(balance.values().stream().noneMatch(count -> count.signum() < 0), "最终目标确实满足");
        check(balance.equals(result.result().surplus()), "抽取+产出−消耗−目标逐资源等于余量");
    }

    private static DetailedResult<String, String> run(Map<String, BigInteger> goals, Map<String, BigInteger> stock,
            List<Recipe<String, String>> recipes) { return detailed(goals, stock, recipes, SEARCH); }
    private static DetailedResult<String, String> detailed(Map<String, BigInteger> goals, Map<String, BigInteger> stock,
            List<Recipe<String, String>> recipes, SearchLimits limits) {
        return Hk3ExactPlanner.planDetailed(goals, stock,
                key -> recipes.stream().filter(recipe -> recipe.outputs().containsKey(key)).toList(), LIMITS, limits, () -> false);
    }
    private static Recipe<String, String> recipe(String id, Map<String, BigInteger> in, Map<String, BigInteger> out) {
        return new Recipe<>(id, in, out, n(1));
    }
    private static Map<String, BigInteger> ordered(String a, long av, String b, long bv) {
        Map<String, BigInteger> result = new LinkedHashMap<>(); result.put(a, n(av)); result.put(b, n(bv)); return result;
    }
    private static BigInteger n(long value) { return BigInteger.valueOf(value); }
    private static void check(boolean success, String reason) { if (!success) throw new AssertionError(reason); checks++; }
}
