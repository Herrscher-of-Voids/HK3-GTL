package com.sirin.hk3gtl.mixin.enhanced.iv;

import com.gregtechceu.gtceu.api.machine.trait.RecipeLogic;
import com.gregtechceu.gtceu.api.recipe.GTRecipe;
import com.llamalad7.mixinextras.injector.ModifyExpressionValue;
import com.llamalad7.mixinextras.injector.wrapoperation.Operation;
import com.llamalad7.mixinextras.injector.wrapoperation.WrapOperation;
import com.llamalad7.mixinextras.sugar.Local;
import com.llamalad7.mixinextras.sugar.Share;
import com.llamalad7.mixinextras.sugar.ref.LocalBooleanRef;
import com.llamalad7.mixinextras.sugar.ref.LocalRef;
import com.sirin.hk3gtl.common.capability.Hk3DualEnergyCosts;
import com.sirin.hk3gtl.common.recipe.power.Hk3IsolatedPower;
import com.sirin.hk3gtl.common.recipe.power.Hk3PowerWork;
import com.sirin.hk3gtl.common.recipe.power.Hk3PortPayment;
import com.sirin.hk3gtl.common.research.Hk3RecipeEnvironment;
import com.sirin.hk3gtl.common.recipe.power.Hk3RecipePower;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Pseudo;
import org.spongepowered.asm.mixin.Shadow;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Coerce;

import java.math.BigInteger;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

@Pseudo
@Mixin(targets = "com.gtl.enhancedcore.common.recipe.iv.IvRecipeLogic", remap = false)
public abstract class Hk3IvPowerMixin implements Hk3PowerWork.Isolated {
    @Shadow private long currentEUt;
    @Shadow private BigInteger currentGridEUt;

    @WrapOperation(method = "start", at = @At(value = "INVOKE", target =
            "Lcom/gtl/enhancedcore/common/recipe/iv/IvRecipeInputs;maxParallel(Lcom/gregtechceu/gtceu/api/recipe/GTRecipe;Ljava/util/Map;Ljava/util/Map;J)J"))
    private long hk3gtl$capExactBatch(GTRecipe recipe, Map<?, ?> stock, Map<?, ?> catalysts, long limit, Operation<Long> original) {
        if (Hk3RecipePower.marked(recipe)) limit = Hk3IsolatedPower.parallel((RecipeLogic) (Object) this, recipe, limit);
        return limit == 0 ? 0 : original.call(recipe, stock, catalysts, limit);
    }

    @WrapOperation(method = "prepare", at = @At(value = "FIELD", ordinal = 0, target =
            "Lcom/gtl/enhancedcore/common/recipe/iv/IvJob;recipe:Lcom/gregtechceu/gtceu/api/recipe/GTRecipe;"))
    private GTRecipe hk3gtl$preserveFixedRate(@Coerce Object job, Operation<GTRecipe> original, @Local(index = 7) LocalBooleanRef stellar) {
        GTRecipe recipe = original.call(job);
        if (Hk3RecipePower.marked(recipe)) stellar.set(false);
        return recipe;
    }

    @WrapOperation(method = "prepare", at = @At(value = "INVOKE", target =
            "Lcom/gtladd/gtladditions/utils/recipe/RecipeCalculationHelper;multipleRecipe(Lcom/gregtechceu/gtceu/api/recipe/GTRecipe;J)Lcom/gregtechceu/gtceu/api/recipe/GTRecipe;"))
    private GTRecipe hk3gtl$scaleExact(@Coerce Object helper, GTRecipe recipe, long parallel, Operation<GTRecipe> original) {
        return Hk3RecipePower.marked(recipe) ? Hk3IsolatedPower.scale(recipe, parallel) : original.call(helper, recipe, parallel);
    }

    @ModifyExpressionValue(method = "prepare", at = @At(value = "FIELD", ordinal = 0, target =
            "Lcom/gtl/enhancedcore/common/recipe/iv/IvRecipeLogic;inputPower:J"))
    private long hk3gtl$skipApproximateTimingLimit(long power, @Local(index = 9) GTRecipe scaled) {
        return Hk3RecipePower.marked(scaled) ? Long.MAX_VALUE : power;
    }

    @WrapOperation(method = "prepare", at = @At(value = "INVOKE", target =
            "Lcom/gtladd/gtladditions/utils/recipe/RecipeCalculationHelper;buildNormalRecipe(Ljava/util/List;Ljava/util/List;DJI)Lcom/gregtechceu/gtceu/api/recipe/GTRecipe;"))
    private GTRecipe hk3gtl$exactTiming(@Coerce Object helper, List<?> items, List<?> fluids, double cost,
                                      long power, int ticks, Operation<GTRecipe> original, @Local(index = 9) GTRecipe scaled) {
        return Hk3RecipePower.marked(scaled) ? scaled : original.call(helper, items, fluids, cost, power, ticks);
    }

    @WrapOperation(method = "advance", at = @At(value = "FIELD", ordinal = 0, target =
            "Lcom/gtl/enhancedcore/common/recipe/iv/IvJob;eut:J"))
    private long hk3gtl$withdrawExact(@Coerce Object job, Operation<Long> original, @Local(index = 8) int index,
                                      @Share("paid") LocalRef<Map<Integer, BigInteger>> paid,
                                      @Share("portBudget") LocalRef<List<Hk3PortPayment.Port>> ports) {
        var order = (Hk3IvJobAccess) job;
        GTRecipe recipe = order.hk3gtl$recipe();
        long requested = original.call(job);
        if (!Hk3RecipePower.marked(recipe)) return requested;
        var logic = (RecipeLogic) (Object) this;
        if (Hk3RecipeEnvironment.throttlesByGaze(logic.getMachine())) return 0;
        if (paid.get() == null) paid.set(new HashMap<>());
        if (ports.get() == null) ports.set(Hk3IsolatedPower.tickBudget(logic));
        var parallel = BigInteger.valueOf(order.hk3gtl$parallel());
        var eu = Hk3RecipePower.cost(recipe).multiply(parallel);
        var hw = Hk3DualEnergyCosts.getMergedCost(recipe);
        if (Hk3IsolatedPower.pay(logic, ports.get(), eu, hw == null ? null : hw.multiply(parallel))) paid.get().put(index, eu);
        return 0;
    }

    @ModifyExpressionValue(method = "advance", at = @At(value = "FIELD", target =
            "Lcom/gtl/enhancedcore/common/recipe/iv/IvRecipeLogic;inputPower:J"))
    private long hk3gtl$remainingInputPower(long power, @Share("paid") LocalRef<Map<Integer, BigInteger>> paid) {
        if (paid.get() == null) return power;
        var used = paid.get().values().stream().reduce(BigInteger.ZERO, BigInteger::add);
        return BigInteger.valueOf(power).subtract(used).max(BigInteger.ZERO).longValueExact();
    }

    @ModifyExpressionValue(method = "advance", at = @At(value = "INVOKE", ordinal = 3, target =
            "Ljava/math/BigInteger;valueOf(J)Ljava/math/BigInteger;"))
    private BigInteger hk3gtl$registerExactGrant(BigInteger original, @Local(index = 11) int index,
                                                @Share("paid") LocalRef<Map<Integer, BigInteger>> paid) {
        if (paid.get() == null) return original;
        BigInteger amount = paid.get().get(index);
        if (amount == null) return original;
        currentGridEUt = currentGridEUt.add(amount);
        currentEUt = currentGridEUt.min(BigInteger.valueOf(Long.MAX_VALUE)).longValueExact();
        return amount;
    }
}
