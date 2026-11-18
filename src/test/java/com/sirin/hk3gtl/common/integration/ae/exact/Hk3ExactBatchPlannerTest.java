package com.sirin.hk3gtl.common.integration.ae.exact;

import java.math.BigInteger;
import java.util.concurrent.atomic.AtomicInteger;

/** 二分只改变新增批量，库存、容量和原生数值保护仍共同限制结果。 */
public final class Hk3ExactBatchPlannerTest {
    private static int checks;

    public static void main(String[] args) throws Exception {
        var snapshot = Hk3AeExactPlanAdapterTest.batchSnapshot(1_000, 3);
        var inventoryLimited = Hk3ExactBatchPlanner.select(snapshot, BigInteger.ONE.shiftLeft(100), Long.MAX_VALUE, () -> false);
        check(inventoryLimited != null && inventoryLimited.amount() == 333, "超过long的总订单按可用库存缩批");
        check(inventoryLimited.plan().usedItems().get(snapshot.inventory().keySet().iterator().next()) == 999,
                "二分批次只预留真实所需材料");
        var capacityLimited = Hk3ExactBatchPlanner.select(snapshot, BigInteger.valueOf(1_000), 170, () -> false);
        check(capacityLimited != null && capacityLimited.amount() == 30 && capacityLimited.plan().bytes() == 166,
                "容量阈值找到最大可执行整数批量");
        check(Hk3ExactBatchPlanner.select(snapshot, BigInteger.valueOf(2), Long.MAX_VALUE, () -> false).amount() == 2,
                "尾批不超过剩余订单");
        check(Hk3ExactBatchPlanner.select(snapshot, BigInteger.valueOf(2), 20, () -> false) == null,
                "最小批次放不进CPU时不提交");
        var starved = Hk3AeExactPlanAdapterTest.batchSnapshot(2, 3);
        check(Hk3ExactBatchPlanner.select(starved, BigInteger.TEN, Long.MAX_VALUE, () -> false) == null,
                "库存不足一批不产生空计划");
        check(Hk3ExactBatchPlanner.select(snapshot, BigInteger.TEN, Long.MAX_VALUE, () -> true) == null,
                "取消立即拒绝批次");
        AtomicInteger polls = new AtomicInteger();
        check(Hk3ExactBatchPlanner.select(snapshot, BigInteger.ONE.shiftLeft(100), Long.MAX_VALUE,
                () -> polls.incrementAndGet() > 3) == null, "规划中取消不泄露部分可提交批次");
        var large = Hk3AeExactPlanAdapterTest.batchSnapshot(Long.MAX_VALUE, 1);
        var longLimited = Hk3ExactBatchPlanner.select(large, BigInteger.ONE.shiftLeft(100), Long.MAX_VALUE, () -> false);
        check(longLimited != null && longLimited.amount() == (Long.MAX_VALUE - 16) / 3,
                "long极值二分无上下界回绕且保留完整字节成本");
        System.out.println("AE精确分批二分离线核验通过：" + checks + "项；未执行原生CPU或客户端测试。");
    }

    private static void check(boolean condition, String message) {
        checks++;
        if (!condition) throw new AssertionError(message);
    }
}
