package com.sirin.hk3gtl.common.integration.ae.exact;

import appeng.api.crafting.IPatternDetails;
import appeng.api.networking.crafting.ICraftingPlan;
import appeng.api.stacks.AEKey;
import appeng.api.stacks.GenericStack;
import appeng.api.stacks.KeyCounter;
import appeng.crafting.CraftingPlan;
import com.sirin.hk3gtl.common.integration.ae.Hk3CraftingCycleFlag;

import java.math.BigInteger;
import java.util.HashMap;
import java.util.LinkedHashMap;
import java.util.Map;
import java.util.Optional;

/** 精确诊断只有在全部执行计数可容纳于原生long时才生成可提交计划。 */
public final class Hk3AeExactPlanAdapter {
    private static final BigInteger EIGHT = BigInteger.valueOf(8);

    private Hk3AeExactPlanAdapter() {}

    public static BigInteger estimateBytes(Hk3AeExactSnapshot snapshot, BigInteger amount,
            Hk3ExactPlanner.Result<AEKey, IPatternDetails> result) {
        Map<AEKey, BigInteger> transfers = new LinkedHashMap<>();
        transfers.put(snapshot.target(), amount);
        for (var entry : result.batches().entrySet()) {
            var recipe = snapshot.recipe(entry.getKey());
            if (recipe == null) throw new IllegalArgumentException("计划包含快照外样板");
            recipe.inputs().forEach((key, count) -> transfers.merge(key, count.multiply(entry.getValue()), BigInteger::add));
        }
        BigInteger bytes = result.logicalBytes().add(snapshot.treeNodes().multiply(EIGHT));
        for (var entry : transfers.entrySet()) {
            int perByte = entry.getKey().getType().getAmountPerByte();
            if (perByte <= 0) throw new IllegalArgumentException("AE资源字节单位必须为正数");
            BigInteger numerator = entry.getValue().multiply(EIGHT);
            bytes = bytes.add(numerator.add(BigInteger.valueOf(perByte - 1L)).divide(BigInteger.valueOf(perByte)));
        }
        return bytes;
    }

    public static Optional<ICraftingPlan> toNative(Hk3AeExactSnapshot snapshot, long amount,
            Hk3ExactPlanner.Result<AEKey, IPatternDetails> result) {
        if (result.batches().keySet().stream().anyMatch(Hk3ExactBoundPattern.class::isInstance)) return Optional.empty();
        if (result.batches().keySet().stream().anyMatch(Hk3ExactScaledPattern::enabled)) return Optional.empty();
        return nativePlan(snapshot, amount, result);
    }

    private static Optional<ICraftingPlan> nativePlan(Hk3AeExactSnapshot snapshot, long amount,
            Hk3ExactPlanner.Result<AEKey, IPatternDetails> result) {
        if (amount <= 0 || !result.successful()) return Optional.empty();
        try {
            BigInteger exactBytes = estimateBytes(snapshot, BigInteger.valueOf(amount), result);
            long bytes = Hk3ExactCpuCapacity.project(exactBytes);
            Map<IPatternDetails, Long> times = new LinkedHashMap<>();
            Map<Object, Long> trackedByType = new HashMap<>();
            Map<AEKey, BigInteger> maximumStored = new LinkedHashMap<>(result.stockUsed());
            Map<AEKey, BigInteger> totalInputs = new LinkedHashMap<>();
            for (var entry : result.batches().entrySet()) {
                var recipe = snapshot.recipe(entry.getKey());
                if (recipe == null) return Optional.empty();
                long count = entry.getValue().longValueExact();
                if (count <= 0) return Optional.empty();
                times.merge(Hk3ExactBoundPattern.original(entry.getKey()), count, Math::addExact);
                // 原生执行器会按资源单位累加进度；每次乘法和分类总和都必须不溢出。
                for (var output : recipe.outputs().entrySet()) {
                    BigInteger exactProduced = output.getValue().multiply(entry.getValue());
                    long produced = exactProduced.longValueExact();
                    maximumStored.merge(output.getKey(), exactProduced, BigInteger::add);
                    long tracked = Math.multiplyExact(produced, output.getKey().getAmountPerUnit());
                    trackedByType.merge(output.getKey().getType(), tracked, Math::addExact);
                }
                recipe.inputs().forEach((key, input) ->
                        totalInputs.merge(key, input.multiply(entry.getValue()), BigInteger::add));
            }
            // 不依赖原生任务遍历顺序，初始库存与全部产出同时保留也必须能用long表示。
            for (BigInteger stored : maximumStored.values()) stored.longValueExact();
            for (BigInteger input : totalInputs.values()) input.longValueExact();
            KeyCounter used = counter(result.stockUsed());
            ICraftingPlan plan = new CraftingPlan(new GenericStack(snapshot.target(), amount), bytes,
                    false, false, used, new KeyCounter(), new KeyCounter(), Map.copyOf(times));
            return Optional.of(new Hk3ExactCapacityPlan(plan, exactBytes));
        } catch (ArithmeticException unsafeLong) {
            return Optional.empty();
        }
    }

    public static Optional<ICraftingPlan> toNative(Hk3AeExactSnapshot snapshot, long amount,
            Hk3ExactPlanner.DetailedResult<AEKey, IPatternDetails> detailed) {
        var plan = nativePlan(snapshot, amount, detailed.result());
        if (plan.isEmpty()) return plan;
        ((Hk3CraftingCycleFlag) plan.get()).hk3gtl$setHasCycles(detailed.orderedExecutionRequired());
        try {
            var execution = Hk3ExactScaledPattern.compress(detailed.execution(), snapshot);
            if (!detailed.orderedExecutionRequired()
                    && detailed.result().batches().keySet().stream().noneMatch(pattern ->
                        snapshot.hasContainers(pattern) || pattern instanceof Hk3ExactBoundPattern)
                    && execution.stream().flatMap(step -> step.recipes().stream())
                        .noneMatch(Hk3ExactScaledPattern.class::isInstance)) return plan;
            long seed = detailed.result().stockUsed().getOrDefault(snapshot.target(), BigInteger.ZERO).longValueExact();
            return Optional.of(new Hk3ExactProgramPlan(plan.get(), execution, seed));
        } catch (ArithmeticException | IllegalArgumentException invalidProgram) {
            return Optional.empty();
        }
    }

    private static KeyCounter counter(Map<AEKey, BigInteger> amounts) {
        KeyCounter counter = new KeyCounter();
        amounts.forEach((key, value) -> counter.add(key, value.longValueExact()));
        return counter;
    }
}
