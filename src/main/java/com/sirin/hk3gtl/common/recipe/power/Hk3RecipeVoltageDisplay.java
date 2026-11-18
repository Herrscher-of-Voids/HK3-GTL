package com.sirin.hk3gtl.common.recipe.power;

/** 仅修正配方查看器的工作档位，不按总功率推断升压，也不改机器判定。 */
public final class Hk3RecipeVoltageDisplay {
    private Hk3RecipeVoltageDisplay() {}

    public static int minimumTier(int originalTier, int requiredTier, int tierCount) {
        return requiredTier > 14 && requiredTier < tierCount ? requiredTier : originalTier;
    }
}
