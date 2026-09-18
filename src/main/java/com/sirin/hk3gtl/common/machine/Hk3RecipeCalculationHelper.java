package com.sirin.hk3gtl.common.machine;
import com.gregtechceu.gtceu.api.capability.recipe.EURecipeCapability;
import com.gregtechceu.gtceu.api.capability.recipe.IRecipeCapabilityHolder;
import com.gregtechceu.gtceu.api.capability.recipe.RecipeCapability;
import com.gregtechceu.gtceu.api.machine.MetaMachine;
import com.gregtechceu.gtceu.api.machine.feature.IRecipeLogicMachine;
import com.gregtechceu.gtceu.api.recipe.GTRecipe;
import com.gregtechceu.gtceu.api.recipe.GTRecipeType;
import com.gregtechceu.gtceu.api.recipe.content.Content;
import com.gregtechceu.gtceu.api.recipe.content.ContentModifier;
import com.gregtechceu.gtceu.api.recipe.modifier.ParallelLogic;
import it.unimi.dsi.fastutil.longs.LongArrayList;
import it.unimi.dsi.fastutil.objects.ObjectArrayList;
import org.slf4j.Logger;
import com.mojang.logging.LogUtils;
import org.gtlcore.gtlcore.api.recipe.RecipeRunnerHelper;

import java.math.BigInteger;
import java.util.*;


public final class Hk3RecipeCalculationHelper {

    private static final Logger LOGGER = LogUtils.getLogger();

    private Hk3RecipeCalculationHelper() {}

    public static boolean commitInputs(IRecipeCapabilityHolder machine, GTRecipe recipe) {
        if (!(machine instanceof IRecipeLogicMachine recipeMachine)) return false;
        if (!recipe.checkConditions(recipeMachine.getRecipeLogic()).isSuccess()) return false;
        return RecipeRunnerHelper.handleRecipeInput(recipeMachine, recipe);
    }

    public static GTRecipe withoutProcessedInputs(GTRecipe recipe) {
        GTRecipe result = recipe.copy();
        result.inputs.clear();
        result.inputChanceLogics.clear();
        return result;
    }

    // ── 配方倍乘 ──────────────────────────────────────────────────────────

    /**
     * 将配方所有内容按 parallel 倍乘，返回新副本。
     */
    public static GTRecipe multipleRecipe(GTRecipe recipe, long parallel) {
        if (parallel <= 1) return recipe.copy();
        int multiplier = (int) Math.min(parallel, Integer.MAX_VALUE);
        ContentModifier mod = ContentModifier.multiplier(multiplier);
        GTRecipe copy = recipe.copy();
        copyContentsInPlace(copy.inputs, mod);
        copyContentsInPlace(copy.outputs, mod);
        copyContentsInPlace(copy.tickInputs, mod);
        copyContentsInPlace(copy.tickOutputs, mod);
        return copy;
    }

    /** 对 map 中每个 Content 应用 modifier 生成倍乘副本（原地替换） */
    private static void copyContentsInPlace(Map<RecipeCapability<?>, List<Content>> map, ContentModifier modifier) {
        for (var entry : map.entrySet()) {
            RecipeCapability<?> cap = entry.getKey();
            List<Content> list = entry.getValue();
            for (int i = 0; i < list.size(); i++) {
                list.set(i, list.get(i).copy(cap, modifier));
            }
        }
    }

    // ── 单配方并行计算 ────────────────────────────────────────────────────

    /**
     * 计算单个配方在当前机器条件下的最大可行并行量。
     *
     * @param machine     机器实例
     * @param recipe      原始配方
     * @param maxParallel 并行量上限
     * @return [0]=实际并行量, [1]=该并行量消耗的 EU（估算）
     */
    public static long[] calculateParallel(IRecipeCapabilityHolder machine, GTRecipe recipe, long maxParallel) {
        if (maxParallel <= 0) return new long[]{0, 0};

        GTRecipe testRecipe = recipe.copy();
        var parallelResult = ParallelLogic.applyParallel((MetaMachine) machine, testRecipe,
                (int) Math.min(maxParallel, Integer.MAX_VALUE), false);
        int limitedParallel = parallelResult.getSecond();

        if (limitedParallel <= 0) return new long[]{0, 0};

        long actualParallel = Math.min((long) limitedParallel, maxParallel);
        long energyPerTick = getRecipeEUt(recipe);
        BigInteger totalEnergy = BigInteger.valueOf(energyPerTick).abs()
                .multiply(BigInteger.valueOf(recipe.duration).abs())
                .multiply(BigInteger.valueOf(actualParallel));
        long saturatedEnergy = totalEnergy.compareTo(BigInteger.valueOf(Long.MAX_VALUE)) > 0
                ? Long.MAX_VALUE : totalEnergy.longValue();

        return new long[]{actualParallel, saturatedEnergy};
    }

    private static long getRecipeEUt(GTRecipe recipe) {
        if (recipe == null) return 0L;

        long inputEU = getFirstEUContent(recipe.getTickInputContents(EURecipeCapability.CAP));
        if (inputEU != 0L) return inputEU;

        long outputEU = getFirstEUContent(recipe.getTickOutputContents(EURecipeCapability.CAP));
        return outputEU == 0L ? 0L : -outputEU;
    }

    private static long getFirstEUContent(List<Content> contents) {
        if (contents == null || contents.isEmpty()) return 0L;
        Object value = contents.get(0).getContent();
        return value instanceof Number number ? number.longValue() : 0L;
    }

    // ── 跨配方分配算法 ────────────────────────────────────────────────────

    /**
     * 贪心分配：按配方遍历顺序，每个配方尽可能多地分配并行量。
     */
    public static ParallelData calculateParallelsWithGreedyAllocation(
            Collection<GTRecipe> recipes,
            long maxParallel,
            IRecipeCapabilityHolder machine,
            FullRecipeModifier fullModifier,
            ParallelCalculator parallelCalculator) {

        if (recipes.isEmpty() || maxParallel <= 0) return null;

        ObjectArrayList<GTRecipe> originList = new ObjectArrayList<>();
        ObjectArrayList<GTRecipe> processedList = new ObjectArrayList<>();
        LongArrayList parallelList = new LongArrayList();
        long remainingParallel = maxParallel;
        int skippedModify = 0, skippedParallel = 0, skippedMatch = 0;

        for (GTRecipe raw : recipes) {
            if (remainingParallel <= 0) break;

            GTRecipe modified;
            try {
                modified = fullModifier.modify(raw);
            } catch (Exception e) {
                LOGGER.warn("[HK3GTL-diag] fullModify 异常: recipe={} error={}", raw.id, e.toString());
                skippedModify++;
                continue;
            }
            if (modified == null) {
                skippedModify++;
                continue;
            }

            long[] result = parallelCalculator.calculate(machine, modified, remainingParallel);
            long actualParallel = result[0];
            if (actualParallel <= 0) {
                skippedParallel++;
                continue;
            }

            actualParallel = findFittingParallel(machine, processedList, modified, actualParallel);
            if (actualParallel <= 0) { skippedMatch++; continue; }
            GTRecipe multiplied = multipleRecipe(modified, actualParallel);

            remainingParallel -= actualParallel;
            originList.add(raw);
            processedList.add(multiplied);
            parallelList.add(actualParallel);
        }

        if (originList.isEmpty()) {
            LOGGER.warn("[HK3GTL-diag] 贪心分配全部被拒: 配方数={} fullModify失败={} parallel=0={} match失败={}",
                    recipes.size(), skippedModify, skippedParallel, skippedMatch);
            return null;
        }

        return new ParallelData(
                originList,
                parallelList.toLongArray(),
                false,
                processedList
        );
    }

    /**
     * 公平分配：在所有匹配配方间等比例分配可用并行量。
     */
    public static ParallelData calculateParallelsWithFairAllocation(
            Collection<GTRecipe> recipes,
            long maxParallel,
            IRecipeCapabilityHolder machine,
            FullRecipeModifier fullModifier,
            ParallelCalculator parallelCalculator) {

        if (recipes.isEmpty() || maxParallel <= 0) return null;

        ObjectArrayList<GTRecipe> rawList = new ObjectArrayList<>();
        ObjectArrayList<GTRecipe> modifiedList = new ObjectArrayList<>();
        LongArrayList euCostList = new LongArrayList();
        int skippedModifyF = 0, skippedParallelF = 0;

        for (GTRecipe raw : recipes) {
            GTRecipe modified;
            try {
                modified = fullModifier.modify(raw);
            } catch (Exception e) {
                LOGGER.warn("[HK3GTL-diag] fullModify 异常(fair): recipe={} error={}", raw.id, e.toString());
                skippedModifyF++;
                continue;
            }
            if (modified == null) {
                skippedModifyF++;
                continue;
            }

            long[] check = parallelCalculator.calculate(machine, modified, 1);
            if (check[0] <= 0) { skippedParallelF++; continue; }

            rawList.add(raw);
            modifiedList.add(modified);
            euCostList.add(check[1]);
        }

        if (rawList.isEmpty()) return null;

        int n = rawList.size();
        int activeCount = (int) Math.min((long) n, maxParallel);
        double totalWeight = 0;
        double[] weights = new double[activeCount];
        for (int i = 0; i < activeCount; i++) {
            weights[i] = 1.0 / Math.max(euCostList.getLong(i), 1);
            totalWeight += weights[i];
        }

        ObjectArrayList<GTRecipe> originList = new ObjectArrayList<>();
        ObjectArrayList<GTRecipe> processedList = new ObjectArrayList<>();
        LongArrayList parallelList = new LongArrayList();

        long[] fairParallels = new long[n];
        BigInteger allocatedTotal = BigInteger.ZERO;
        for (int i = 0; i < activeCount; i++) {
            double weightedShare = maxParallel * weights[i] / totalWeight;
            fairParallels[i] = Math.max(1L, (long) weightedShare);
            allocatedTotal = allocatedTotal.add(BigInteger.valueOf(fairParallels[i]));
        }

        BigInteger maxParallelValue = BigInteger.valueOf(maxParallel);
        BigInteger excess = allocatedTotal.subtract(maxParallelValue);
        if (excess.signum() > 0) {
            BigInteger remainingCapacity = allocatedTotal.subtract(BigInteger.valueOf(activeCount));
            for (int i = 0; i < activeCount && excess.signum() > 0; i++) {
                long capacity = fairParallels[i] - 1L;
                if (capacity <= 0) continue;
                BigInteger capacityValue = BigInteger.valueOf(capacity);
                BigInteger reduction = capacityValue.multiply(excess)
                        .add(remainingCapacity).subtract(BigInteger.ONE)
                        .divide(remainingCapacity)
                        .min(capacityValue);
                fairParallels[i] -= reduction.longValueExact();
                excess = excess.subtract(reduction);
                remainingCapacity = remainingCapacity.subtract(capacityValue);
            }
        }

        for (int i = 0; i < n; i++) {
            if (fairParallels[i] <= 0) continue;
            long[] available = parallelCalculator.calculate(machine, modifiedList.get(i), fairParallels[i]);
            long actualParallel = Math.min(fairParallels[i], available[0]);
            if (actualParallel <= 0) continue;

            actualParallel = findFittingParallel(machine, processedList, modifiedList.get(i), actualParallel);
            if (actualParallel <= 0) continue;
            GTRecipe multiplied = multipleRecipe(modifiedList.get(i), actualParallel);

            originList.add(rawList.get(i));
            processedList.add(multiplied);
            parallelList.add(actualParallel);
        }

        if (originList.isEmpty()) {
            LOGGER.warn("[HK3GTL-diag] 公平分配全部被拒: 配方数={} fullModify失败={} parallel=0={}",
                    recipes.size(), skippedModifyF, skippedParallelF);
            return null;
        }

        return new ParallelData(
                originList,
                parallelList.toLongArray(),
                false,
                processedList
        );
    }

    private static long findFittingParallel(IRecipeCapabilityHolder machine,
                                            List<GTRecipe> plannedRecipes,
                                            GTRecipe recipe,
                                            long upperBound) {
        long low = 1;
        long high = upperBound;
        long best = 0;
        while (low <= high) {
            long middle = low + ((high - low) >>> 1);
            GTRecipe candidate = multipleRecipe(recipe, middle);
            if (matchesPlannedRecipes(machine, plannedRecipes, candidate)) {
                best = middle;
                low = middle + 1;
            } else {
                high = middle - 1;
            }
        }
        return best;
    }

    private static boolean matchesPlannedRecipes(IRecipeCapabilityHolder machine,
                                                  List<GTRecipe> plannedRecipes,
                                                  GTRecipe candidate) {
        GTRecipe planned = candidate.copy();
        for (GTRecipe recipe : plannedRecipes) {
            mergeRecipeInto(planned, recipe);
        }
        if (!(machine instanceof IRecipeLogicMachine recipeMachine)
                || !planned.checkConditions(recipeMachine.getRecipeLogic()).isSuccess()) {
            return false;
        }
        return RecipeRunnerHelper.matchRecipe(machine, planned)
                && planned.matchTickRecipe(machine).isSuccess();
    }

    // ── 最终配方构建 ──────────────────────────────────────────────────────

    /**
     * 将 ParallelData 中所有已处理的配方合并为一个完整的合成配方。
     */
    public static GTRecipe buildNormalRecipe(ParallelData parallelData, GTRecipeType recipeType) {
        if (parallelData == null || !parallelData.isValid()) return null;

        List<GTRecipe> processed = parallelData.getProcessedRecipeList();
        if (processed == null || processed.isEmpty()) return null;

        if (processed.size() == 1) return processed.get(0);

        GTRecipe merged = processed.get(0).copy();
        for (int i = 1; i < processed.size(); i++) {
            mergeRecipeInto(merged, processed.get(i));
        }

        return merged;
    }

    /** 将 other 配方的所有 Content 合并到 base 配方 */
    private static void mergeRecipeInto(GTRecipe base, GTRecipe other) {
        mergeContentMap(base.inputs, other.inputs);
        mergeContentMap(base.outputs, other.outputs);
        mergeContentMap(base.tickInputs, other.tickInputs);
        mergeContentMap(base.tickOutputs, other.tickOutputs);

        other.inputChanceLogics.forEach(base.inputChanceLogics::putIfAbsent);
        other.outputChanceLogics.forEach(base.outputChanceLogics::putIfAbsent);
        other.tickInputChanceLogics.forEach(base.tickInputChanceLogics::putIfAbsent);
        other.tickOutputChanceLogics.forEach(base.tickOutputChanceLogics::putIfAbsent);

        for (var cond : other.conditions) {
            if (!base.conditions.contains(cond)) {
                base.conditions.add(cond);
            }
        }

        base.duration = Math.max(base.duration, other.duration);
    }

    /** 将 add 的所有 Content（深拷贝）追加到 base 对应容量的列表中 */
    private static void mergeContentMap(Map<RecipeCapability<?>, List<Content>> base,
                                        Map<RecipeCapability<?>, List<Content>> add) {
        for (var entry : add.entrySet()) {
            RecipeCapability<?> cap = entry.getKey();
            List<Content> target = base.computeIfAbsent(cap, k -> new ArrayList<>());
            for (Content content : entry.getValue()) {
                target.add(content.copy(cap, null));
            }
        }
    }

    // ── 产出收集（用于 JEI / 调试）────────────────────────────────────────

    /**
     * 从配方中收集所有输出内容到给定列表。
     */
    public static void collectOutputs(GTRecipe recipe, List<Content> outOutputs, List<Content> outTickOutputs) {
        for (var entry : recipe.outputs.entrySet()) {
            outOutputs.addAll(entry.getValue());
        }
        for (var entry : recipe.tickOutputs.entrySet()) {
            outTickOutputs.addAll(entry.getValue());
        }
    }

    // ── 函数式接口 ────────────────────────────────────────────────────────

    /** 单配方并行计算器。输入(机器, 已修改配方, 可用并行上限) → [实际并行, EU消耗] */
    @FunctionalInterface
    public interface ParallelCalculator {
        long[] calculate(IRecipeCapabilityHolder machine, GTRecipe modifiedRecipe, long maxParallel);
    }

    /** 配方修改器（超频 + 自定义修改）。输入原始配方 → 修改后配方。 */
    @FunctionalInterface
    public interface FullRecipeModifier {
        GTRecipe modify(GTRecipe raw) throws Exception;
    }
}
