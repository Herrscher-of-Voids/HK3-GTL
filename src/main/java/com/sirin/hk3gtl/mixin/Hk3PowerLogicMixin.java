package com.sirin.hk3gtl.mixin;

import com.gregtechceu.gtceu.api.capability.recipe.IO;
import com.gregtechceu.gtceu.api.machine.trait.RecipeLogic;
import com.gregtechceu.gtceu.api.recipe.GTRecipe;
import com.sirin.hk3gtl.common.capability.Hk3EnergyTick;
import com.sirin.hk3gtl.common.capability.Hk3MaterialTick;
import com.sirin.hk3gtl.common.capability.Hk3RefundJournal;
import com.sirin.hk3gtl.common.machine.Hk3RecipeLogic;
import com.sirin.hk3gtl.common.recipe.power.Hk3PowerWork;
import com.sirin.hk3gtl.common.recipe.power.Hk3RecipePower;
import com.sirin.hk3gtl.common.research.Hk3RecipeAccess;
import com.sirin.hk3gtl.common.research.Hk3RecipeEnvironment;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerLevel;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Shadow;
import org.spongepowered.asm.mixin.Unique;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

/**
 * 标准GT循环的显式HK工况足额能源事务，原第三方工况不进入本分支。
 */
@Mixin(value = RecipeLogic.class, remap = false)
public abstract class Hk3PowerLogicMixin implements Hk3PowerWork {
    @Shadow protected GTRecipe lastRecipe;
    @Shadow protected int progress;
    @Shadow protected long totalContinuousRunningTime;
    @Unique private Hk3EnergyTick hk3gtl$powerTick;
    @Unique private boolean hk3gtl$powerWorking;
    @Unique private long hk3gtl$lastRefundLog;
    @Unique private static final org.slf4j.Logger HK3GTL$POWER_LOG = com.mojang.logging.LogUtils.getLogger();

    @Inject(method = "serverTick", at = @At("HEAD"), cancellable = true, require = 1)
    private void hk3gtl$retryPowerRefund(CallbackInfo callback) {
        RecipeLogic logic = (RecipeLogic) (Object) this;
        if (logic instanceof Hk3RecipeLogic hk) {
            if (!hk.retryPendingRefund()) callback.cancel();
            return;
        }
        if (hk3gtl$powerWorking) return;
        if (!(logic.getMachine().getLevel() instanceof ServerLevel level) || !level.getServer().isSameThread()) {
            callback.cancel();
            return;
        }
        try {
            if (hk3gtl$powerTick == null) hk3gtl$powerTick = Hk3RefundJournal.resume(logic.getMachine());
            if (hk3gtl$powerTick == null) return;
            if (hk3gtl$powerTick.finish(false)) { hk3gtl$powerTick = null; return; }
        } catch (RuntimeException problem) {
            long now = System.nanoTime();
            if (hk3gtl$lastRefundLog == 0 || now - hk3gtl$lastRefundLog >= 10_000_000_000L) {
                hk3gtl$lastRefundLog = now;
                HK3GTL$POWER_LOG.warn("[HK3GTL] 固定工况退款恢复失败，位置={}", logic.getMachine().getPos(), problem);
            }
        }
        logic.setWaiting(Component.translatable("hk3gtl.machine.energy_refund_pending"));
        callback.cancel();
    }

    @Inject(method = "handleRecipeWorking", at = @At("HEAD"), cancellable = true, require = 1)
    private void hk3gtl$workPower(CallbackInfo callback) {
        RecipeLogic logic = (RecipeLogic) (Object) this;
        if (logic instanceof Hk3RecipeLogic || !Hk3RecipePower.marked(lastRecipe)) return;
        callback.cancel();
        if (hk3gtl$powerWorking) throw new IllegalStateException("能源工作循环不允许重入");
        if (!(logic.getMachine().getLevel() instanceof ServerLevel level) || !level.getServer().isSameThread()) return;
        try {
            if (hk3gtl$powerTick == null) hk3gtl$powerTick = Hk3RefundJournal.resume(logic.getMachine());
            if (hk3gtl$powerTick != null && !hk3gtl$powerTick.finish(false)) {
                logic.setWaiting(Component.translatable("hk3gtl.machine.energy_refund_pending"));
                return;
            }
            hk3gtl$powerTick = Hk3RefundJournal.open(logic.getMachine());
        } catch (RuntimeException problem) {
            logic.setWaiting(Component.translatable("hk3gtl.machine.energy_refund_pending"));
            return;
        }
        hk3gtl$powerWorking = true;
        GTRecipe recipe = lastRecipe;
        int before = progress;
        boolean[] advanced = {false};
        try {
            hk3gtl$powerTick.runWork(() -> {
                var result = recipe.checkConditions(logic);
                if (result.isSuccess()) result = recipe.matchTickRecipe(logic.machine);
                if (!result.isSuccess()) {
                    logic.setWaiting(result.reason() == null ? null : result.reason().get());
                    return;
                }
                if (Hk3RecipeAccess.blocks(recipe, logic.getMachine()) || Hk3RecipeEnvironment.throttlesByGaze(logic.getMachine())) {
                    logic.setWaiting(Component.translatable("hk3gtl.compat.environment_paused"));
                    return;
                }
                if (!Hk3RecipePower.pay(recipe, logic, hk3gtl$powerTick)) {
                    logic.setWaiting(Component.translatable("hk3gtl.machine.recipe_commit_failed"));
                    return;
                }
                GTRecipe tick = Hk3RecipePower.withoutEU(recipe);
                if (!Hk3MaterialTick.run(hk3gtl$powerTick, tick, logic,
                        () -> tick.handleTickRecipeIO(IO.IN, logic.machine, logic.getChanceCaches())
                                && tick.handleTickRecipeIO(IO.OUT, logic.machine, logic.getChanceCaches()))) {
                    logic.setWaiting(Component.translatable("hk3gtl.machine.recipe_commit_failed"));
                    return;
                }
                logic.setStatus(RecipeLogic.Status.WORKING);
                if (!logic.machine.onWorking()) { logic.interruptRecipe(); return; }
                progress++;
                totalContinuousRunningTime++;
                advanced[0] = true;
            }, () -> advanced[0] && progress == before + 1);
        } catch (RuntimeException problem) {
            HK3GTL$POWER_LOG.warn("[HK3GTL] 固定工况能源工作失败，位置={}", logic.getMachine().getPos(), problem);
            logic.setWaiting(Component.translatable("hk3gtl.machine.recipe_commit_failed"));
        } finally {
            hk3gtl$powerWorking = false;
            if (hk3gtl$powerTick.settled()) hk3gtl$powerTick = null;
            else logic.setWaiting(Component.translatable("hk3gtl.machine.energy_refund_pending"));
        }
    }

    @Inject(method = "handleRecipeIO", at = @At("HEAD"), cancellable = true, require = 1)
    private void hk3gtl$fixedInput(GTRecipe recipe, IO io, CallbackInfoReturnable<Boolean> callback) {
        if (!Hk3RecipePower.marked(recipe)) return;
        RecipeLogic logic = (RecipeLogic) (Object) this;
        callback.setReturnValue(recipe.handleRecipeIO(io, logic.machine, logic.getChanceCaches()));
    }

    @Inject(method = "handleTickRecipe", at = @At("HEAD"), cancellable = true, require = 1)
    private void hk3gtl$rejectUnticketedTick(GTRecipe recipe, CallbackInfoReturnable<GTRecipe.ActionResult> callback) {
        if (!((Object) this instanceof Hk3RecipeLogic) && Hk3RecipePower.marked(recipe))
            callback.setReturnValue(GTRecipe.ActionResult.fail(() -> Component.translatable("hk3gtl.recipe.power.executor")));
    }
}
