package com.sirin.hk3gtl.common.machine;

import com.gregtechceu.gtceu.api.recipe.GTRecipe;

import java.util.Arrays;
import java.util.List;
import java.util.Objects;

/**
 * 多配方并行计算的结果数据容器。
 *
 * <p>由 {@link Hk3RecipeCalculationHelper} 在并行分配阶段产出，
 * 供 {@link Hk3MultiRecipeLogic} 在配方构建阶段消费。</p>
 *
 * @param originRecipeList   原始匹配配方列表（未经并行倍乘）
 * @param parallels          每个配方的并行量（与 originRecipeList 一一对应）
 * @param shouldProcess      是否已完成一次性输入提交；两阶段事务规划结果固定为 false，
 *                           由 Hk3MultiRecipeLogic 在最终统一模拟成功后提交
 * @param processedRecipeList 已完成并行倍乘、仍保留完整 inputs 的规划配方列表
 *
 * 【变更记录 #1】2026-07-19 15:35:56（第 1 次备注 · 内测四第 30 次更新）
 * - 删除：
 *   1) 删除 processedRecipeList 仅在 shouldProcess=true 时有效的旧契约。
 *   2) 删除“分配阶段已扣输入”的默认语义，避免结果对象掩盖提前落账风险。
 * - 新增：
 *   1) 明确规划配方必须保留完整 inputs，供最终聚合模拟与统一提交。
 * - 修改：
 *   1) shouldProcess 在当前两阶段流程中固定为 false，仅保留字段和访问器以兼容现有测试结构。
 * - 用途：
 *   1) 在并行分配与最终 RecipeLogic 提交之间传递无副作用的规划结果。
 */
public class ParallelData {
    private final List<GTRecipe> originRecipeList;
    private final long[] parallels;
    private final boolean shouldProcess;
    private final List<GTRecipe> processedRecipeList;

    public ParallelData(List<GTRecipe> originRecipeList, long[] parallels,
                        boolean shouldProcess, List<GTRecipe> processedRecipeList) {
        this.originRecipeList = originRecipeList;
        this.parallels = parallels;
        this.shouldProcess = shouldProcess;
        this.processedRecipeList = processedRecipeList;
    }

    public List<GTRecipe> getOriginRecipeList() { return originRecipeList; }
    public long[] getParallels() { return parallels; }
    public boolean getShouldProcess() { return shouldProcess; }
    public List<GTRecipe> getProcessedRecipeList() { return processedRecipeList; }

    /** 是否包含有效结果。 */
    public boolean isValid() {
        return originRecipeList != null && !originRecipeList.isEmpty()
                && parallels != null && parallels.length == originRecipeList.size();
    }

    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (!(o instanceof ParallelData that)) return false;
        return shouldProcess == that.shouldProcess
                && Objects.equals(originRecipeList, that.originRecipeList)
                && Arrays.equals(parallels, that.parallels)
                && Objects.equals(processedRecipeList, that.processedRecipeList);
    }

    @Override
    public int hashCode() {
        int result = Objects.hash(originRecipeList, shouldProcess, processedRecipeList);
        result = 31 * result + Arrays.hashCode(parallels);
        return result;
    }

    @Override
    public String toString() {
        return "ParallelData{recipes=" + (originRecipeList != null ? originRecipeList.size() : 0)
                + ", parallels=" + Arrays.toString(parallels)
                + ", shouldProcess=" + shouldProcess + "}";
    }
}
