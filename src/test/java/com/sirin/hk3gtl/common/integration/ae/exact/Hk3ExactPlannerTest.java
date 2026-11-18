package com.sirin.hk3gtl.common.integration.ae.exact;

import java.math.BigInteger;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.concurrent.atomic.AtomicInteger;

/** 纯Java大数与共享前置回归，不替代AE原生CPU或游戏验收。 */
public final class Hk3ExactPlannerTest {
    private static final Hk3ExactPlanner.Limits LIMITS = new Hk3ExactPlanner.Limits(100, 100);
    private static int checks;

    public static void main(String[] args) {
        hugeAmount();
        sharedInputsAndStock();
        surplusAndShortage();
        unsupportedRoutes();
        budgetsAndCancellation();
        deepGraphAndImmutability();
        System.out.println("精确DAG离线核验通过：" + checks + "项；未进行AE或游戏实测。");
    }

    private static void hugeAmount() {
        BigInteger amount = BigInteger.ONE.shiftLeft(100).add(BigInteger.ONE);
        Map<String, List<Hk3ExactPlanner.Recipe<String, String>>> recipes = Map.of(
                "target", List.of(recipe("make", Map.of("ore", n(3)), "target", n(2), n(7))));
        AtomicInteger lookedUp = new AtomicInteger();
        var result = Hk3ExactPlanner.plan("target", amount, Map.of("ore", amount.multiply(n(3)), "target", amount),
                key -> { lookedUp.incrementAndGet(); return recipes.getOrDefault(key, List.of()); }, LIMITS, () -> false);
        BigInteger batches = amount.add(BigInteger.ONE).divide(n(2));
        check(result.successful(), "超过long的目标可完成规划");
        check(result.batches().get("make").equals(batches), "批次不截断为long");
        check(result.stockUsed().get("ore").equals(batches.multiply(n(3))), "大数投料精确");
        check(!result.stockUsed().containsKey("target"), "新增目标不抵扣现有成品");
        check(result.logicalBytes().equals(batches.multiply(n(7))), "逻辑成本大数乘加");
        check(result.surplus().equals(Map.of("target", BigInteger.ONE)), "奇数需求余量精确");
        check(lookedUp.get() == 2 && result.visitedNodes() == 2, "计算规模不按订单数量增长");
    }

    private static void sharedInputsAndStock() {
        Map<String, List<Hk3ExactPlanner.Recipe<String, String>>> recipes = Map.of(
                "target", List.of(recipe("assemble", ordered("left", 1, "right", 1), "target", n(1), n(1))),
                "left", List.of(recipe("left", Map.of("middle", n(2)), "left", n(1), n(1))),
                "right", List.of(recipe("right", Map.of("middle", n(3)), "right", n(1), n(1))),
                "middle", List.of(recipe("middle", Map.of("ore", n(2)), "middle", n(4), n(1))));
        Map<String, BigInteger> stock = Map.of("middle", n(3), "ore", n(100));
        var result = plan(recipes, stock, n(2));
        check(result.successful(), "共享前置有库存时可完成");
        check(result.stockUsed().get("middle").equals(n(3)), "共享库存只消费一次");
        check(result.batches().get("middle").equals(n(2)), "先合并十个中间件需求再扣三库存再取整");
        check(result.stockUsed().get("ore").equals(n(4)), "共用前置不重复展开");
        check(result.surplus().equals(Map.of("middle", n(1))), "共享批次余量统一结算");
        check(stock.equals(Map.of("middle", n(3), "ore", n(100))), "库存输入未修改");

        var stocked = plan(recipes, Map.of("left", n(2), "right", n(2)), n(2));
        check(stocked.successful() && stocked.batches().equals(Map.of("assemble", n(2))), "前置成品足够时不生产其原料");
        check(stocked.leafDemand().isEmpty(), "零需求原料不产生缺口");
        var uneven = plan(Map.of(
                "target", List.of(recipe("target", ordered("middle", 1, "left", 1), "target", n(1), n(1))),
                "left", List.of(recipe("left", Map.of("middle", n(1)), "left", n(1), n(1))),
                "middle", List.of(recipe("middle", Map.of("ore", n(1)), "middle", n(2), n(1)))),
                Map.of("ore", n(1)), n(1));
        check(uneven.successful() && uneven.batches().get("middle").equals(n(1)), "不同深度同键需求也先合并再取整");
    }

    private static void surplusAndShortage() {
        Map<String, List<Hk3ExactPlanner.Recipe<String, String>>> recipes = Map.of(
                "target", List.of(recipe("make", Map.of("ore", n(3)), "target", n(2), n(8))));
        var result = plan(recipes, Map.of("ore", n(4)), n(3));
        check(result.status() == Hk3ExactPlanner.Status.MISSING_INPUT, "不足不能报告成功");
        check(result.leafDemand().equals(Map.of("ore", n(6))), "叶子报告总需求");
        check(result.stockUsed().equals(Map.of("ore", n(4))) && result.missing().equals(Map.of("ore", n(2))), "保留库存与净缺口区分");
        check(result.surplus().equals(Map.of("target", n(1))), "缺料诊断仍给出批量余量");
    }

    private static void unsupportedRoutes() {
        var multi = new Hk3ExactPlanner.Recipe<>("multi", Map.of("ore", n(1)), Map.of("target", n(1), "side", n(1)), n(1));
        check(plan(Map.of("target", List.of(multi)), Map.of(), n(1)).status() == Hk3ExactPlanner.Status.UNSUPPORTED, "多输出明确回退，不误用副产物");
        var a = recipe("a", Map.of("ore", n(1)), "target", n(1), n(1));
        var b = recipe("b", Map.of("ore", n(2)), "target", n(1), n(1));
        check(plan(Map.of("target", List.of(a, b)), Map.of(), n(1)).status() == Hk3ExactPlanner.Status.UNSUPPORTED, "多条路线明确回退");
        check(plan(Map.of(), Map.of("target", n(100)), n(1)).status() == Hk3ExactPlanner.Status.UNSUPPORTED, "无生产路线不能造物");
        Map<String, List<Hk3ExactPlanner.Recipe<String, String>>> cycle = Map.of(
                "target", List.of(recipe("target", Map.of("middle", n(1)), "target", n(1), n(1))),
                "middle", List.of(recipe("middle", Map.of("target", n(1)), "middle", n(1), n(1))));
        var cyclic = plan(cycle, Map.of(), n(1));
        check(cyclic.status() == Hk3ExactPlanner.Status.UNSUPPORTED && cyclic.batches().isEmpty(), "循环不返回可提交部分计划");
        check(plan(Map.of("target", List.of(recipe("self", Map.of("target", n(1)), "target", n(2), n(1)))), Map.of(), n(1)).status() == Hk3ExactPlanner.Status.UNSUPPORTED, "增殖自环也不硬推");
    }

    private static void budgetsAndCancellation() {
        var recipes = Map.of("target", List.of(recipe("make", ordered("one", 1, "two", 1), "target", n(1), n(1))));
        var nodes = Hk3ExactPlanner.plan("target", n(1), Map.<String, BigInteger>of(), key -> recipes.getOrDefault(key, List.of()),
                new Hk3ExactPlanner.Limits(2, 10), () -> false);
        check(nodes.status() == Hk3ExactPlanner.Status.BUDGET_EXCEEDED && nodes.batches().isEmpty(), "节点预算不返回截断计划");
        var edges = Hk3ExactPlanner.plan("target", n(1), Map.<String, BigInteger>of(), key -> recipes.getOrDefault(key, List.of()),
                new Hk3ExactPlanner.Limits(10, 1), () -> false);
        check(edges.status() == Hk3ExactPlanner.Status.BUDGET_EXCEEDED, "边预算生效");
        AtomicInteger lookups = new AtomicInteger();
        var cancelled = Hk3ExactPlanner.<String, String>plan("target", n(1), Map.of(), key -> {
            lookups.incrementAndGet(); return List.of();
        }, LIMITS, () -> true);
        check(cancelled.status() == Hk3ExactPlanner.Status.CANCELLED && lookups.get() == 0, "取消后不读取配方");
        AtomicInteger cancelChecks = new AtomicInteger();
        var duringPropagation = Hk3ExactPlanner.plan("target", n(1), Map.<String, BigInteger>of(),
                key -> recipes.getOrDefault(key, List.of()), LIMITS, () -> cancelChecks.incrementAndGet() >= 7);
        check(duringPropagation.status() == Hk3ExactPlanner.Status.CANCELLED && duringPropagation.batches().isEmpty(), "传播中途取消不交付部分计划");
        Thread.currentThread().interrupt();
        try {
            check(plan(recipes, Map.of(), n(1)).status() == Hk3ExactPlanner.Status.CANCELLED, "线程中断保留取消语义");
            check(Thread.currentThread().isInterrupted(), "核心不吞中断标记");
        } finally { Thread.interrupted(); }
    }

    private static void deepGraphAndImmutability() {
        int depth = 10_000;
        AtomicInteger lookups = new AtomicInteger();
        var result = Hk3ExactPlanner.<Integer, Integer>plan(0, n(1), Map.of(depth, n(1)), key -> {
            lookups.incrementAndGet();
            return key == depth ? List.of() : List.of(new Hk3ExactPlanner.Recipe<>(key,
                    Map.of(key + 1, n(1)), Map.of(key, n(1)), n(1)));
        }, new Hk3ExactPlanner.Limits(depth + 1, depth), () -> false);
        check(result.successful() && result.batches().size() == depth, "万层依赖使用迭代遍历不栈溢出");
        check(lookups.get() == depth + 1 && result.visitedEdges() == depth, "只查询目标可达键一次");
        try { result.batches().put(-1, n(1)); throw new AssertionError("输出必须不可变"); }
        catch (UnsupportedOperationException expected) { checks++; }
        Map<String, BigInteger> inputs = new LinkedHashMap<>(Map.of("ore", n(1)));
        var recipe = recipe("copy", inputs, "target", n(1), n(1));
        inputs.put("ore", n(9));
        check(recipe.inputs().get("ore").equals(n(1)), "配方防御拷贝");
    }

    private static Hk3ExactPlanner.Result<String, String> plan(
            Map<String, List<Hk3ExactPlanner.Recipe<String, String>>> recipes,
            Map<String, BigInteger> inventory, BigInteger amount) {
        return Hk3ExactPlanner.plan("target", amount, inventory, key -> recipes.getOrDefault(key, List.of()), LIMITS, () -> false);
    }

    private static Hk3ExactPlanner.Recipe<String, String> recipe(String id, Map<String, BigInteger> inputs,
                                                                String output, BigInteger amount, BigInteger cost) {
        return new Hk3ExactPlanner.Recipe<>(id, inputs, Map.of(output, amount), cost);
    }

    private static Map<String, BigInteger> ordered(String first, long firstAmount, String second, long secondAmount) {
        Map<String, BigInteger> result = new LinkedHashMap<>();
        result.put(first, n(firstAmount)); result.put(second, n(secondAmount)); return result;
    }

    private static BigInteger n(long value) { return BigInteger.valueOf(value); }
    private static void check(boolean ok, String reason) {
        if (!ok) throw new AssertionError(reason);
        checks++;
    }
}
