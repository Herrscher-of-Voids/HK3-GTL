package com.sirin.hk3gtl.common.integration.ae.exact;

import java.math.BigInteger;
import java.util.Map;
import java.util.UUID;

public final class Hk3ExactProbabilityLedgerTest {
    public static void main(String[] args) {
        probabilityBoundaries();
        actualOutputAndRetry();
        cancellationAndRecovery();
        corruptedSnapshotsAndReceipts();
        System.out.println("概率预算断言通过：零/满概率、离散产量、罕见产出、投料封顶、真实回执补差、取消与重启对账");
    }

    private static void probabilityBoundaries() {
        var zero = new Hk3ExactProbabilityLedger<>(plan(1, 0, 100, 1, 10, 10));
        equal(Hk3ExactProbabilityLedger.Status.NO_CHANCE, zero.status());
        require(zero.begin().isEmpty() && zero.snapshot().allocatedAttempts().signum() == 0);
        var certain = new Hk3ExactProbabilityLedger<>(plan(3, 100, 100, 2, 10, 10));
        var batch = certain.begin().orElseThrow();
        require(batch.attempts() == 2);
        rejects(() -> certain.complete(receipt(batch, 2)));
        certain.complete(receipt(batch, 4));
        equal(Hk3ExactProbabilityLedger.Status.SATISFIED, certain.status());
        require(certain.snapshot().actualOutput().equals(BigInteger.valueOf(4)));
        require(plan(3, 1, 2, 2, 10, 10).expectedAttempts().orElseThrow().equals(BigInteger.valueOf(4)));
        var rarePlan = new Hk3ExactProbabilityPlan<>("可信配方:罕见", BigInteger.TEN, BigInteger.ONE,
                BigInteger.TEN.pow(100), BigInteger.ONE, Map.of("原料", BigInteger.TWO),
                Map.of("原料", BigInteger.valueOf(6)), BigInteger.valueOf(Long.MAX_VALUE), Integer.MAX_VALUE);
        require(rarePlan.expectedAttempts().orElseThrow().equals(BigInteger.TEN.pow(101)));
        require(rarePlan.attemptCapacity().equals(BigInteger.valueOf(3)));
        equal(Map.of("原料", BigInteger.valueOf(6)), rarePlan.allocatedInputs(BigInteger.valueOf(3)));
        var rare = new Hk3ExactProbabilityLedger<>(rarePlan);
        var three = rare.begin().orElseThrow();
        require(three.attempts() == 3 && rare.begin().isEmpty());
        rare.complete(receipt(three, 0));
        equal(Hk3ExactProbabilityLedger.Status.BUDGET_EXHAUSTED, rare.status());
        require(rare.begin().isEmpty() && rare.snapshot().actualOutput().signum() == 0);
        rejects(() -> rarePlan.allocatedInputs(BigInteger.valueOf(4)));
        rejects(() -> plan(1, 101, 100, 1, 10, 10));
        var exhausted = new Hk3ExactProbabilityLedger<>(plan(1, 1, 2, 1, 0, 10));
        equal(Hk3ExactProbabilityLedger.Status.BUDGET_EXHAUSTED, exhausted.status());
    }

    private static void actualOutputAndRetry() {
        var ledger = new Hk3ExactProbabilityLedger<>(plan(3, 1, 2, 1, 10, 10));
        var first = ledger.begin().orElseThrow();
        require(first.attempts() == 6);
        var firstReceipt = receipt(first, 1);
        require(ledger.complete(firstReceipt));
        require(!ledger.complete(firstReceipt));
        require(ledger.snapshot().actualOutput().equals(BigInteger.ONE));
        var second = ledger.begin().orElseThrow();
        require(second.attempts() == 4 && !second.token().equals(first.token()));
        ledger.complete(receipt(second, 0));
        equal(Hk3ExactProbabilityLedger.Status.BUDGET_EXHAUSTED, ledger.status());
        require(ledger.snapshot().allocatedAttempts().equals(BigInteger.TEN) && ledger.snapshot().actualOutput().intValueExact() == 1);
        rejects(() -> ledger.complete(firstReceipt));
        var cap = new Hk3ExactProbabilityLedger<>(plan(2, 1, 2, 1, 10, 1));
        require(cap.begin().orElseThrow().attempts() == 1);
    }

    private static void cancellationAndRecovery() {
        var ledger = new Hk3ExactProbabilityLedger<>(plan(2, 1, 2, 1, 10, 10));
        var pending = ledger.begin().orElseThrow();
        ledger.markUnknown(pending.token());
        equal(Hk3ExactProbabilityLedger.Status.RECOVERY_REQUIRED, ledger.status());
        require(ledger.begin().isEmpty());
        ledger.cancel();
        var recovered = Hk3ExactProbabilityLedger.restore(ledger.snapshot());
        equal(Hk3ExactProbabilityLedger.Status.RECOVERY_REQUIRED, recovered.status());
        require(recovered.snapshot().cancelled() && recovered.begin().isEmpty());
        recovered.complete(receipt(pending, 1));
        equal(Hk3ExactProbabilityLedger.Status.CANCELLED, recovered.status());
        require(recovered.snapshot().actualOutput().equals(BigInteger.ONE));
        require(recovered.snapshot().allocatedAttempts().equals(BigInteger.valueOf(pending.attempts())));
        equal(Hk3ExactProbabilityLedger.Status.CANCELLED,
                Hk3ExactProbabilityLedger.restore(recovered.snapshot()).status());
        var active = new Hk3ExactProbabilityLedger<>(plan(1, 1, 2, 1, 10, 10));
        var activePending = active.begin().orElseThrow();
        var restored = Hk3ExactProbabilityLedger.restore(active.snapshot());
        require(restored.begin().isEmpty());
        restored.complete(receipt(activePending, 0));
        require(restored.begin().isPresent());
        var satisfied = new Hk3ExactProbabilityLedger<>(plan(1, 1, 1, 1, 10, 10));
        satisfied.complete(receipt(satisfied.begin().orElseThrow(), 1));
        equal(Hk3ExactProbabilityLedger.Status.SATISFIED,
                Hk3ExactProbabilityLedger.restore(satisfied.snapshot()).status());
    }

    private static void corruptedSnapshotsAndReceipts() {
        var plan = plan(2, 1, 2, 2, 10, 10);
        var ledger = new Hk3ExactProbabilityLedger<>(plan);
        var batch = ledger.begin().orElseThrow();
        rejects(() -> ledger.complete(new Hk3ExactProbabilityLedger.Receipt(UUID.randomUUID(),
                batch.metadataId(), batch.attempts(), BigInteger.ZERO)));
        rejects(() -> ledger.complete(new Hk3ExactProbabilityLedger.Receipt(batch.token(),
                "其他配方", batch.attempts(), BigInteger.ZERO)));
        rejects(() -> ledger.complete(receipt(batch, 1)));
        rejects(() -> ledger.complete(receipt(batch, 6)));
        ledger.complete(receipt(batch, 0));
        rejects(() -> ledger.complete(receipt(batch, 2)));
        var snapshot = ledger.snapshot();
        rejects(() -> Hk3ExactProbabilityLedger.restore(new Hk3ExactProbabilityLedger.Snapshot<>(plan,
                BigInteger.valueOf(11), BigInteger.ZERO, null, snapshot.lastReceipt(), false)));
        rejects(() -> Hk3ExactProbabilityLedger.restore(new Hk3ExactProbabilityLedger.Snapshot<>(plan,
                BigInteger.TWO, BigInteger.ZERO, null, null, false)));
        rejects(() -> Hk3ExactProbabilityLedger.restore(new Hk3ExactProbabilityLedger.Snapshot<>(plan,
                BigInteger.TWO, BigInteger.ONE, null, snapshot.lastReceipt(), false)));
        rejects(() -> new Hk3ExactProbabilityPlan<>("可信配方", BigInteger.ONE, BigInteger.ONE,
                BigInteger.TWO, BigInteger.ONE, Map.of("原料", BigInteger.ONE), Map.of(), BigInteger.ONE, 1));
    }

    private static Hk3ExactProbabilityPlan<String> plan(long target, long chance, long scale,
            long yield, long materialCap, int batch) {
        return new Hk3ExactProbabilityPlan<>("可信配方:版本1:机器修正1", BigInteger.valueOf(target),
                BigInteger.valueOf(chance), BigInteger.valueOf(scale), BigInteger.valueOf(yield),
                Map.of("原料", BigInteger.ONE), Map.of("原料", BigInteger.valueOf(materialCap)), BigInteger.valueOf(100), batch);
    }

    private static Hk3ExactProbabilityLedger.Receipt receipt(Hk3ExactProbabilityLedger.Pending batch, long output) {
        return new Hk3ExactProbabilityLedger.Receipt(batch.token(), batch.metadataId(), batch.attempts(), BigInteger.valueOf(output));
    }

    private static void rejects(Runnable action) {
        try {
            action.run();
        } catch (IllegalArgumentException expected) {
            return;
        }
        throw new AssertionError("应拒绝无效状态");
    }

    private static void equal(Object expected, Object actual) {
        if (!expected.equals(actual)) throw new AssertionError(expected + " != " + actual);
    }

    private static void require(boolean value) {
        if (!value) throw new AssertionError("概率预算断言失败");
    }
}
