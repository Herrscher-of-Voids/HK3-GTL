package com.sirin.hk3gtl.common.integration.ae.exact;

import appeng.api.crafting.IPatternDetails;
import appeng.api.networking.crafting.ICraftingPlan;
import appeng.api.stacks.AEKey;

import java.math.BigInteger;
import java.util.function.BooleanSupplier;

/** 按库存、字节容量及原生计数限制二分批量，次数与订单数量的位数相关。 */
final class Hk3ExactBatchPlanner {
    record Batch(Hk3AeExactSnapshot snapshot, long amount, ICraftingPlan plan) {}

    static Batch select(Hk3AeExactSnapshot snapshot, BigInteger remaining, long capacity,
                        BooleanSupplier cancelled) {
        return select(snapshot, remaining, BigInteger.valueOf(capacity), cancelled);
    }

    static Batch select(Hk3AeExactSnapshot snapshot, BigInteger remaining, BigInteger capacity,
                        BooleanSupplier cancelled) {
        if (remaining.signum() <= 0 || capacity.signum() < 0) return null;
        long low = 1, high = remaining.min(BigInteger.valueOf(Long.MAX_VALUE)).longValueExact();
        Batch best = null;
        var prepared = new Hk3ExactGraphPlanner.Prepared<AEKey, IPatternDetails>();
        while (low <= high && !cancelled.getAsBoolean() && !Thread.currentThread().isInterrupted()) {
            long amount = low + ((high - low) >>> 1);
            ICraftingPlan[] accepted = new ICraftingPlan[1];
            var detailed = snapshot.planDetailed(BigInteger.valueOf(amount), cancelled, candidate -> {
                var plan = Hk3AeExactPlanAdapter.toNative(snapshot, amount, candidate);
                if (plan.isEmpty() || Hk3ExactCpuCapacity.requiredBytes(plan.get()).compareTo(capacity) > 0) return false;
                accepted[0] = plan.get();
                return true;
            }, prepared);
            var result = detailed.result();
            if (result.status() == Hk3ExactPlanner.Status.CANCELLED) return null;
            if (result.status() != Hk3ExactPlanner.Status.SUCCESS
                    && result.status() != Hk3ExactPlanner.Status.MISSING_INPUT
                    && result.status() != Hk3ExactPlanner.Status.REJECTED) return null;
            if (result.successful() && accepted[0] != null) {
                best = new Batch(snapshot, amount, accepted[0]);
                if (amount == Long.MAX_VALUE) break;
                low = amount + 1;
            } else {
                high = amount - 1;
            }
        }
        return cancelled.getAsBoolean() || Thread.currentThread().isInterrupted() ? null : best;
    }
}
