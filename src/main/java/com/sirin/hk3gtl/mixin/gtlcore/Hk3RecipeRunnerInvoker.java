package com.sirin.hk3gtl.mixin.gtlcore;

import com.gregtechceu.gtceu.api.capability.recipe.IRecipeCapabilityHolder;
import com.gregtechceu.gtceu.api.capability.recipe.RecipeCapability;
import com.gregtechceu.gtceu.api.recipe.GTRecipe;
import com.gregtechceu.gtceu.api.recipe.content.Content;
import it.unimi.dsi.fastutil.objects.Object2IntMap;
import it.unimi.dsi.fastutil.objects.Reference2ObjectOpenHashMap;
import org.gtlcore.gtlcore.api.recipe.RecipeRunner;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.gen.Invoker;

import java.util.List;
import java.util.Map;

@Mixin(value = RecipeRunner.class, remap = false)
public interface Hk3RecipeRunnerInvoker {
    @Invoker("fillContent")
    static Reference2ObjectOpenHashMap<RecipeCapability<?>, List<Object>> hk3gtl$fillContent(
            Map<RecipeCapability<?>, List<Content>> contents, GTRecipe recipe, IRecipeCapabilityHolder holder,
            Map<RecipeCapability<?>, Object2IntMap<?>> chanceCaches, boolean simulated) {
        throw new AssertionError();
    }
}
