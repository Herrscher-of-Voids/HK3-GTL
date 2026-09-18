package com.sirin.hk3gtl.common.machine;

import com.gregtechceu.gtceu.api.recipe.GTRecipeType;

import java.util.Collections;
import java.util.List;

/**
 * 支持多配方类型同时运行的多方块机器接口。
 *
 * <p>实现此接口的多方块机器，其 {@link Hk3MultiRecipeLogic} 会跨所有声明的
 * {@link GTRecipeType} 搜索可执行配方，实现真正的"跨配方类型"组合加工。</p>
 *
 * <p>用法：在机器定义类中覆写 {@code Hk3WorkableMultiblockMachine#getExtendRecipeTypes()}，
 * 返回该机器支持的全部额外 RecipeType 列表。主 RecipeType（GTCEu 原生）总是被包含。</p>
 *
 * <p>如需支持跨多个 RecipeType 运行，请覆写此方法自行返回完整列表。</p>
 */
public interface IMultiTypeRecipeMachine {
    /**
     * 返回此机器支持的全部额外配方类型（主配方类型由 GTCEu 原生管理）。
     * 返回 null 或空列表表示仅使用主配方类型。
     */
    default List<GTRecipeType> getExtendRecipeTypes() {
        return Collections.emptyList();
    }
}
