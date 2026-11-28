package com.sirin.hk3gtl.mixin.enhanced.iv;

import com.gregtechceu.gtceu.api.capability.IEnergyContainer;
import com.gregtechceu.gtceu.api.machine.multiblock.WorkableMultiblockMachine;
import com.gregtechceu.gtceu.api.machine.trait.RecipeLogic;
import com.gregtechceu.gtceu.api.recipe.GTRecipe;
import com.gtl.enhancedcore.common.recipe.GridEnergyRecipeInput;
import com.llamalad7.mixinextras.injector.wrapoperation.Operation;
import com.llamalad7.mixinextras.injector.wrapoperation.WrapOperation;
import com.llamalad7.mixinextras.sugar.Share;
import com.llamalad7.mixinextras.sugar.ref.LocalRef;
import com.sirin.hk3gtl.common.capability.Hk3DualEnergyCosts;
import com.sirin.hk3gtl.common.capability.Hk3EnergyTick;
import com.sirin.hk3gtl.common.capability.Hk3RefundJournal;
import com.sirin.hk3gtl.common.recipe.power.Hk3PortPayment;
import com.sirin.hk3gtl.common.recipe.power.Hk3IsolatedPower;
import com.sirin.hk3gtl.common.recipe.power.Hk3RecipePower;
import com.sirin.hk3gtl.common.recipe.power.Hk3PowerWork;
import org.spongepowered.asm.mixin.Final;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Pseudo;
import org.spongepowered.asm.mixin.Shadow;
import org.spongepowered.asm.mixin.Unique;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Coerce;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

import java.math.BigInteger;
import java.util.List;
import java.util.Map;

@Pseudo
@Mixin(targets = "com.gtl.enhancedcore.common.recipe.iv.IvNativeEngine", remap = false)
public abstract class Hk3IvNativePowerMixin implements Hk3PowerWork.Isolated {
    @Unique private boolean hk3gtl$prepareFixed;
    @Shadow @Final private WorkableMultiblockMachine machine;
    @Shadow @Final private RecipeLogic logic;

    @WrapOperation(method = "start", at = @At(value = "INVOKE", target =
            "Lcom/gtl/enhancedcore/common/recipe/iv/IvMachineScope;unmeteredBatch(Lcom/gregtechceu/gtceu/api/machine/multiblock/WorkableMultiblockMachine;Lcom/gregtechceu/gtceu/api/recipe/GTRecipe;)Z"))
    private boolean hk3gtl$shareParallelBudget(WorkableMultiblockMachine host, GTRecipe recipe, Operation<Boolean> original) {
        return !Hk3RecipePower.marked(recipe) && original.call(host, recipe);
    }

    @WrapOperation(method = "prepare", at = @At(value = "INVOKE", target =
            "Lcom/gtl/enhancedcore/common/recipe/iv/IvBuffers;availableVirtual(Lorg/gtlcore/gtlcore/common/machine/multiblock/part/ae/MEPatternBufferPartMachine;Lcom/gtl/enhancedcore/common/recipe/iv/IvJob;)Ljava/util/Map;"))
    private Map<?, ?> hk3gtl$captureOrder(@Coerce Object buffer, @Coerce Object job, Operation<Map<?, ?>> original,
                                         @Share("fixed") LocalRef<GTRecipe> fixed) {
        GTRecipe recipe = ((Hk3IvJobAccess) job).hk3gtl$recipe();
        Map<?, ?> available = original.call(buffer, job);
        hk3gtl$prepareFixed = Hk3RecipePower.marked(recipe);
        if (hk3gtl$prepareFixed) fixed.set(recipe);
        return available;
    }

    @WrapOperation(method = "prepare", at = @At(value = "INVOKE", target =
            "Lcom/gtl/enhancedcore/common/recipe/iv/IvMachineScope;batching(Lcom/gregtechceu/gtceu/api/machine/multiblock/WorkableMultiblockMachine;)Z"))
    private boolean hk3gtl$useExactRecipe(WorkableMultiblockMachine host, Operation<Boolean> original,
                                          @Share("fixed") LocalRef<GTRecipe> fixed) {
        return fixed.get() == null && original.call(host);
    }

    @Inject(method = "wireless", at = @At("HEAD"), cancellable = true)
    private void hk3gtl$usePortPayment(CallbackInfoReturnable<Object> callback) {
        if (hk3gtl$prepareFixed) {
            hk3gtl$prepareFixed = false;
            callback.setReturnValue(null);
        }
    }

    @WrapOperation(method = {"prepare", "advance"}, at = @At(value = "INVOKE", target =
            "Lcom/gtl/enhancedcore/common/recipe/iv/IvNativeRecipeContext;tickRecipe(Lcom/gregtechceu/gtceu/api/recipe/GTRecipe;)Lcom/gregtechceu/gtceu/api/recipe/GTRecipe;"))
    private GTRecipe hk3gtl$isolatedTick(GTRecipe recipe, Operation<GTRecipe> original,
                                        @Share("committed") LocalRef<GTRecipe> committed) {
        GTRecipe tick = original.call(recipe);
        boolean fixed = Hk3RecipePower.marked(recipe);
        committed.set(fixed ? recipe : null);
        return fixed ? Hk3RecipePower.isolatedTick(tick) : tick;
    }

    @WrapOperation(method = "advance", at = @At(value = "INVOKE", target =
            "Lcom/gtl/enhancedcore/common/recipe/GridEnergyInputs;remove(Lcom/gregtechceu/gtceu/api/capability/IEnergyContainer;Lcom/gtl/enhancedcore/common/recipe/GridEnergyRecipeInput;J)J"))
    private long hk3gtl$withdrawExact(IEnergyContainer energy, GridEnergyRecipeInput grid, long amount, Operation<Long> original,
                                       @Share("committed") LocalRef<GTRecipe> committed, @Share("payment") LocalRef<Hk3EnergyTick> payment,
                                       @Share("portBudget") LocalRef<List<Hk3PortPayment.Port>> ports) {
        GTRecipe recipe = committed.get();
        if (recipe == null) return original.call(energy, grid, amount);
        if (!machine.getLevel().getServer().isSameThread()) return 0;
        var pending = Hk3RefundJournal.resume(machine);
        if (pending != null && !pending.finish(false)) return 0;
        if (ports.get() == null) ports.set(Hk3IsolatedPower.tickBudget(logic));
        Hk3EnergyTick tick = Hk3RefundJournal.open(machine);
        boolean paid = false;
        try {
            paid = Hk3PortPayment.pay(ports.get(), BigInteger.valueOf(amount), tick)
                    && Hk3RecipePower.reserveHonkai(logic, Hk3DualEnergyCosts.getMergedCost(recipe), tick);
            if (!paid) return 0;
            payment.set(tick);
            return amount;
        } finally {
            if (!paid) tick.finish(false);
        }
    }

    @WrapOperation(method = "advance", at = @At(value = "INVOKE", target =
            "Lorg/gtlcore/gtlcore/api/machine/computation/ComputationRecipes;undoOnFailure(Ljava/lang/Runnable;)V"))
    private void hk3gtl$registerExactRefund(Runnable refund, Operation<Void> original, @Share("payment") LocalRef<Hk3EnergyTick> payment) {
        Hk3EnergyTick tick = payment.get();
        original.call(tick == null ? refund : (Runnable) () -> { tick.finish(false); payment.set(null); });
    }

    @Inject(method = "advance", at = @At(value = "INVOKE", target =
            "Lorg/gtlcore/gtlcore/api/machine/computation/ComputationRecipes$Scope;commit(Z)V", shift = At.Shift.AFTER))
    private void hk3gtl$commitPayment(List<?> orders, CallbackInfo callback, @Share("payment") LocalRef<Hk3EnergyTick> payment) {
        if (payment.get() != null) {
            payment.get().finish(true);
            payment.set(null);
        }
    }

}
