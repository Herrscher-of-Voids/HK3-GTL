package com.sirin.hk3gtl.common.integration.ae.exact;

import com.gregtechceu.gtceu.api.recipe.GTRecipe;
import it.unimi.dsi.fastutil.ints.Int2ObjectMap;

public interface Hk3ProbabilityAssemblyAccess {
    boolean hk3gtl$hasUnitScale();
    Int2ObjectMap<GTRecipe> getSlotBoundRecipes();
    boolean commitSlotBoundRecipes(Int2ObjectMap<GTRecipe> recipes);
}
