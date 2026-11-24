package com.sirin.hk3gtl.common.integration.ae.exact;

import appeng.api.crafting.IPatternDetails;
import appeng.api.networking.crafting.ICraftingPlan;
import appeng.api.stacks.AEKey;

import java.math.BigInteger;
import java.util.LinkedHashMap;
import java.util.Map;
import java.util.function.BooleanSupplier;

/** 按库存、字节容量及原生计数限制二分批量，次数与订单数量的位数相关。 */
final class Hk3ExactBatchPlanner {
    record Batch(Hk3AeExactSnapshot snapshot, long amount, ICraftingPlan plan,
                 Hk3ExactPlanner.DetailedResult<AEKey, IPatternDetails> nexusPlan) {}
    record Selection(Batch batch, Map<AEKey, BigInteger> missing) {}

    static Batch select(Hk3AeExactSnapshot snapshot, BigInteger remaining, long capacity,
                        BooleanSupplier cancelled) {
        return select(snapshot, remaining, BigInteger.valueOf(capacity), cancelled);
    }

    static Batch select(Hk3AeExactSnapshot snapshot, BigInteger remaining, BigInteger capacity,
                        BooleanSupplier cancelled) {
        return plan(snapshot, remaining, capacity, cancelled, false).batch();
    }

    static Selection plan(Hk3AeExactSnapshot snapshot, BigInteger remaining, BigInteger capacity,
                          BooleanSupplier cancelled, boolean nexusSupply) {
        if (remaining.signum() <= 0 || capacity.signum() < 0) return new Selection(null, Map.of());
        long low = 1, high = remaining.min(BigInteger.valueOf(Long.MAX_VALUE)).longValueExact();
        Batch best = null;
        boolean full = true;
        var prepared = new Hk3ExactGraphPlanner.Prepared<AEKey, IPatternDetails>();
        while (low <= high && !cancelled.getAsBoolean() && !Thread.currentThread().isInterrupted()) {
            long amount = full ? high : low + ((high - low) >>> 1);
            ICraftingPlan[] accepted = new ICraftingPlan[1];
            var detailed = snapshot.planDetailed(BigInteger.valueOf(amount), cancelled, candidate -> {
                if (nexusSupply) return true;
                var plan = Hk3AeExactPlanAdapter.toNative(snapshot, amount, candidate);
                if (plan.isEmpty() || Hk3ExactCpuCapacity.requiredBytes(plan.get()).compareTo(capacity) > 0) return false;
                accepted[0] = plan.get();
                return true;
            }, prepared, nexusSupply);
            var result = detailed.result();
            if (result.status() == Hk3ExactPlanner.Status.CANCELLED) return new Selection(null, Map.of());
            if (nexusSupply && amount == 1 && !result.successful() && result.status() != Hk3ExactPlanner.Status.MISSING_INPUT)
                throw new IllegalArgumentException(result.reason());
            if (amount == 1 && result.status() == Hk3ExactPlanner.Status.MISSING_INPUT && best == null) {
                Map<AEKey, BigInteger> required = new LinkedHashMap<>();
                result.missing().forEach((key, count) -> required.put(key,
                        snapshot.inventory().getOrDefault(key, BigInteger.ZERO).add(count)));
                return new Selection(null, required);
            }
            Batch candidate = result.successful() && (nexusSupply || accepted[0] != null)
                    ? new Batch(snapshot, amount, accepted[0], nexusSupply ? detailed : null) : null;
            if (full) {
                full = false;
                if (candidate != null) return new Selection(candidate, Map.of());
                high = amount - 1;
                continue;
            }
            if (!nexusSupply && result.status() != Hk3ExactPlanner.Status.SUCCESS
                    && result.status() != Hk3ExactPlanner.Status.MISSING_INPUT
                    && result.status() != Hk3ExactPlanner.Status.REJECTED) return new Selection(null, Map.of());
            if (candidate != null) {
                best = candidate;
                if (amount == Long.MAX_VALUE) break;
                low = amount + 1;
            } else {
                high = amount - 1;
            }
        }
        return new Selection(cancelled.getAsBoolean() || Thread.currentThread().isInterrupted() ? null : best, Map.of());
    }
}
