package com.sirin.hk3gtl.common.integration.ae.exact;

import appeng.api.stacks.AEFluidKey;
import appeng.api.stacks.AEItemKey;
import appeng.api.stacks.AEKey;
import com.gregtechceu.gtceu.api.capability.recipe.FluidRecipeCapability;
import com.gregtechceu.gtceu.api.capability.recipe.ItemRecipeCapability;
import com.gregtechceu.gtceu.api.machine.feature.IRecipeLogicMachine;
import com.gregtechceu.gtceu.api.recipe.GTRecipe;
import com.gregtechceu.gtceu.api.recipe.content.Content;
import com.sirin.hk3gtl.mixin.gtlcore.Hk3RecipeRunnerInvoker;

import java.math.BigInteger;
import java.util.ArrayList;
import java.util.Map;

final class Hk3ProbabilityOutput {
    private Hk3ProbabilityOutput() {}

    static GTRecipe capture(IRecipeLogicMachine machine, GTRecipe recipe, Map<AEKey, BigInteger> captured) {
        var actual = Hk3RecipeRunnerInvoker.hk3gtl$fillContent(recipe.outputs, recipe, machine,
                machine.getRecipeLogic().getChanceCaches(), false);
        var settled = recipe.copy();
        settled.data = recipe.data;
        settled.outputs.clear();
        actual.forEach((capability, contents) -> {
            var outputs = new ArrayList<Content>();
            contents.forEach(content -> outputs.add(new Content(content, 1, 1, 0, null, null)));
            settled.outputs.put(capability, outputs);
        });
        for (var entry : actual.entrySet()) for (var content : entry.getValue()) {
            if (entry.getKey() == ItemRecipeCapability.CAP) {
                var stack = ItemRecipeCapability.CAP.of(content).getItems()[0];
                captured.merge(AEItemKey.of(stack), BigInteger.valueOf(stack.getCount()), BigInteger::add);
            } else {
                var ingredient = FluidRecipeCapability.CAP.of(content);
                var stack = ingredient.getStacks()[0];
                captured.merge(AEFluidKey.of(stack.getFluid(), stack.getTag()),
                        BigInteger.valueOf(ingredient.getAmount()), BigInteger::add);
            }
        }
        return settled;
    }
}
