package com.sirin.hk3gtl.mixin;

import com.gregtechceu.gtceu.api.capability.recipe.IO;
import com.gregtechceu.gtceu.api.machine.trait.RecipeLogic;
import com.gregtechceu.gtceu.api.recipe.GTRecipe;
import com.sirin.hk3gtl.common.capability.Hk3EnergyTick;
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
 * 【文件职责】标准GT循环的显式HK工况足额能源事务，原第三方工况不进入本分支。
 * 【变更记录 #1】2026-10-17 16:45:15（第1次备注 · 修订165）
 * 删除：标记工况的double批处理入口及忽略实际tick IO返回值的推进。
 * 新增：服务器工作票据、精确多仓分摊、失败退款重试及未接入外部推进器拒绝。
 * 修改：HK自有双能源逻辑仍由Hk3RecipeLogic处理；用途：只在输入输出和onWorking成功后封账。
 * 边界：能源可撤销，物品流体仍沿GT原执行语义；本类不宣称完整物料事务。
 */
/**
 * 【变更记录 #2】2026-10-17 16:55:08（第2次备注 · 修订165）
 * 删除：配方清空后只靠工作方法重试退款的遗漏。
 * 新增：serverTick在服务器线程先处理未完成退款，失败暂停后续调度；修改：只退未还的实际余额差。
 * 用途：中断/onWorking拒绝/实际IO异常不会因配方已重置而跳过能源撤销。
 */
@Mixin(value = RecipeLogic.class, remap = false)
public abstract class Hk3PowerLogicMixin implements Hk3PowerWork {
    @Shadow protected GTRecipe lastRecipe;
    @Shadow protected int progress;
    @Shadow protected long totalContinuousRunningTime;
    @Unique private Hk3EnergyTick hk3gtl$powerTick;
    @Unique private boolean hk3gtl$powerWorking;
    @Unique private static final org.slf4j.Logger HK3GTL$POWER_LOG = com.mojang.logging.LogUtils.getLogger();

    @Inject(method = "serverTick", at = @At("HEAD"), cancellable = true, require = 1)
    private void hk3gtl$retryPowerRefund(CallbackInfo callback) {
        if (hk3gtl$powerTick == null || hk3gtl$powerWorking) return;
        RecipeLogic logic = (RecipeLogic) (Object) this;
        if (!(logic.getMachine().getLevel() instanceof ServerLevel level) || !level.getServer().isSameThread()) {
            callback.cancel();
            return;
        }
        if (hk3gtl$powerTick.finish(false)) hk3gtl$powerTick = null;
        else {
            logic.setWaiting(Component.translatable("hk3gtl.machine.energy_refund_pending"));
            callback.cancel();
        }
    }

    @Inject(method = "handleRecipeWorking", at = @At("HEAD"), cancellable = true, require = 1)
    private void hk3gtl$workPower(CallbackInfo callback) {
        RecipeLogic logic = (RecipeLogic) (Object) this;
        if (logic instanceof Hk3RecipeLogic || !Hk3RecipePower.marked(lastRecipe)) return;
        callback.cancel();
        if (hk3gtl$powerWorking) throw new IllegalStateException("能源工作循环不允许重入");
        if (!(logic.getMachine().getLevel() instanceof ServerLevel level) || !level.getServer().isSameThread()) return;
        if (hk3gtl$powerTick != null && !hk3gtl$powerTick.finish(false)) {
            logic.setWaiting(Component.translatable("hk3gtl.machine.energy_refund_pending"));
            return;
        }
        hk3gtl$powerTick = new Hk3EnergyTick();
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
                if (!tick.handleTickRecipeIO(IO.IN, logic.machine, logic.getChanceCaches())
                        || !tick.handleTickRecipeIO(IO.OUT, logic.machine, logic.getChanceCaches())) {
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
