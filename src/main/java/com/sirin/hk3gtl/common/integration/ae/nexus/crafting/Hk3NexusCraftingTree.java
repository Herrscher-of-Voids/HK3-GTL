package com.sirin.hk3gtl.common.integration.ae.nexus.crafting;

import appeng.api.crafting.IPatternDetails;
import appeng.api.stacks.AEKey;
import appeng.api.stacks.GenericStack;
import appeng.menu.me.crafting.CraftingPlanSummary;
import com.neuvillette.ae2ct.api.ICraftingPlanSummary;
import com.neuvillette.ae2ct.api.RecipeHelper;

import java.math.BigInteger;
import java.util.Arrays;
import java.util.Map;

final class Hk3NexusCraftingTree {
    private Hk3NexusCraftingTree() {}

    static void initialize(CraftingPlanSummary summary, AEKey target, BigInteger amount,
            Map<IPatternDetails, BigInteger> patterns) {
        var recipes = patterns.entrySet().stream().map(entry -> {
            var pattern = entry.getKey();
            var inputs = Arrays.stream(pattern.getInputs()).map(input -> {
                var stack = input.getPossibleInputs()[0];
                return new GenericStack(stack.what(), Hk3NexusLedger.project(
                        BigInteger.valueOf(stack.amount()).multiply(BigInteger.valueOf(input.getMultiplier()))));
            }).toList();
            return new RecipeHelper.Recipe(inputs, Arrays.asList(pattern.getOutputs()),
                    Hk3NexusLedger.project(entry.getValue()));
        }).toList();
        ((ICraftingPlanSummary) summary).setJob(new RecipeHelper(
                new GenericStack(target, Hk3NexusLedger.project(amount)), recipes));
    }

    static void copy(CraftingPlanSummary source, CraftingPlanSummary target) {
        ((ICraftingPlanSummary) target).setJob(((ICraftingPlanSummary) source).getJob());
    }
}
