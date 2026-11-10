package com.sirin.hk3gtl.common.machine;

import com.gregtechceu.gtceu.api.recipe.GTRecipe;

import java.util.Arrays;
import java.util.List;
import java.util.Objects;

/** 中文维护备注：历史变更说明已整理；当前实现以代码为准。 */
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
