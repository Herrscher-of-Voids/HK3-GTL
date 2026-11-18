package com.sirin.hk3gtl.mixin.ae;

import appeng.api.networking.IGrid;
import appeng.api.config.Actionable;
import appeng.api.networking.crafting.ICraftingLink;
import appeng.api.networking.crafting.ICraftingPlan;
import appeng.api.networking.crafting.ICraftingRequester;
import appeng.api.networking.crafting.ICraftingSubmitResult;
import appeng.api.networking.energy.IEnergyService;
import appeng.api.networking.security.IActionSource;
import appeng.api.stacks.AEKey;
import appeng.api.stacks.GenericStack;
import appeng.crafting.execution.CraftingCpuLogic;
import appeng.crafting.execution.CraftingSubmitResult;
import appeng.crafting.execution.ExecutingCraftingJob;
import appeng.me.cluster.implementations.CraftingCPUCluster;
import appeng.me.service.CraftingService;
import com.sirin.hk3gtl.common.integration.ae.exact.Hk3ExactCpuTracker;
import com.sirin.hk3gtl.common.integration.ae.exact.Hk3ExactProgramHost;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.nbt.Tag;
import net.minecraft.server.level.ServerLevel;
import org.spongepowered.asm.mixin.Final;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Shadow;
import org.spongepowered.asm.mixin.Unique;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

import java.util.UUID;

/** 只记录所属批次的真实生产回执，不接管原生库存或彩蛋研究回执。 */
@Mixin(value = CraftingCpuLogic.class, remap = false)
public abstract class Hk3ExactCraftingCpuMixin implements Hk3ExactCpuTracker.BatchAccess {
    @Shadow @Final private CraftingCPUCluster cluster;
    @Shadow private ExecutingCraftingJob job;
    @Shadow public abstract ICraftingLink getLastLink();
    @Shadow public abstract GenericStack getFinalJobOutput();
    @Shadow public abstract long getWaitingFor(AEKey key);
    @Shadow public abstract void cancel();

    @Unique private UUID hk3gtl$exactToken;
    @Unique private UUID hk3gtl$finishingExactToken;
    @Unique private long hk3gtl$batchOriginalAmount = -1;
    @Unique private long hk3gtl$finishingProduced = -1;

    @Override public boolean hk3gtl$matchesBatch(UUID token, AEKey target, long amount) {
        GenericStack output = getFinalJobOutput();
        return token.equals(hk3gtl$exactToken) && amount == hk3gtl$batchOriginalAmount
                && job != null && getLastLink() != null && !getLastLink().isCanceled()
                && output != null && amount == output.amount() && target.equals(output.what())
                && (!(this instanceof Hk3ExactCpuTracker.ProgramAccess program) || program.hk3gtl$recoverableProgram());
    }

    @Inject(method = "trySubmitJob", at = @At("HEAD"), cancellable = true)
    private void hk3gtl$protectOrphanedBatch(IGrid grid, ICraftingPlan plan, IActionSource source,
                                            ICraftingRequester requester,
                                            CallbackInfoReturnable<ICraftingSubmitResult> ci) {
        if (hk3gtl$exactToken != null && cluster.getLevel() instanceof ServerLevel level
                && Hk3ExactCpuTracker.freezeRequested(level, hk3gtl$exactToken)) {
            ci.setReturnValue(CraftingSubmitResult.CPU_BUSY);
        }
    }

    @Inject(method = "trySubmitJob", at = @At("RETURN"))
    private void hk3gtl$trackSubmission(IGrid grid, ICraftingPlan plan, IActionSource source,
                                       ICraftingRequester requester,
                                       CallbackInfoReturnable<ICraftingSubmitResult> ci) {
        if (!ci.getReturnValue().successful()) return;
        hk3gtl$exactToken = Hk3ExactCpuTracker.currentSubmission();
        hk3gtl$batchOriginalAmount = hk3gtl$exactToken == null ? -1 : plan.finalOutput().amount();
        cluster.markDirty();
    }

    @Inject(method = "finishJob", at = @At("HEAD"))
    private void hk3gtl$captureCompletion(boolean success, CallbackInfo ci) {
        // 原生收尾异常时保留活动身份，恢复后暂停核对，不能误当成功重发。
        hk3gtl$finishingExactToken = hk3gtl$exactToken;
        hk3gtl$finishingProduced = -1;
        GenericStack output = getFinalJobOutput();
        if (hk3gtl$exactToken != null && job != null && output != null
                && output.amount() == hk3gtl$batchOriginalAmount) {
            long remaining = ((Hk3ExactExecutingJobAccess) (Object) job).hk3gtl$remainingAmount();
            // 外部机器已接收的任务无法撤回；迟到目标产物未对清时禁止自动恢复余量。
            hk3gtl$finishingProduced = Hk3ExactCpuTracker.produced(hk3gtl$batchOriginalAmount,
                    remaining, success, getWaitingFor(output.what()));
            if ((Object) this instanceof Hk3ExactProgramHost program && program.hk3gtl$hasProgram()) {
                hk3gtl$finishingProduced = program.hk3gtl$programProduced(success, hk3gtl$batchOriginalAmount, output.what());
            }
        }
    }

    @Inject(method = "finishJob", at = @At("RETURN"))
    private void hk3gtl$finishCompletion(boolean success, CallbackInfo ci) {
        UUID token = hk3gtl$finishingExactToken;
        long produced = hk3gtl$finishingProduced;
        hk3gtl$finishingExactToken = null;
        hk3gtl$finishingProduced = -1;
        if (token == null) return;
        if (token.equals(hk3gtl$exactToken)) {
            hk3gtl$exactToken = null;
            hk3gtl$batchOriginalAmount = -1;
        }
        cluster.markDirty();
        if (cluster.getLevel() instanceof ServerLevel level) {
            Hk3ExactCpuTracker.finished(level, token, success, produced);
        }
    }

    @Inject(method = "tickCraftingLogic", at = @At("HEAD"), cancellable = true)
    private void hk3gtl$cancelOwnedBatch(IEnergyService energy, CraftingService crafting, CallbackInfo ci) {
        if (hk3gtl$exactToken == null || !(cluster.getLevel() instanceof ServerLevel level)) return;
        // 账本与区块不是同一事务；孤立令牌仅冻结，不运行或自动取消退库。
        if (Hk3ExactCpuTracker.freezeRequested(level, hk3gtl$exactToken)) {
            ci.cancel();
            return;
        }
        if (getLastLink() != null && Hk3ExactCpuTracker.cancelRequested(level, hk3gtl$exactToken)) {
            cancel();
            ci.cancel();
        }
    }

    @Inject(method = "insert", at = @At("HEAD"), cancellable = true)
    private void hk3gtl$freezeOrphanedReturn(AEKey key, long amount, Actionable mode,
                                           CallbackInfoReturnable<Long> ci) {
        // 回流入口不经过 tick；孤立 CPU 不能借迟到物品推进旧任务。
        if (hk3gtl$exactToken != null && cluster.getLevel() instanceof ServerLevel level
                && Hk3ExactCpuTracker.freezeRequested(level, hk3gtl$exactToken)) {
            ci.setReturnValue(0L);
        }
    }

    @Inject(method = "writeToNBT", at = @At("RETURN"))
    private void hk3gtl$saveExactToken(CompoundTag tag, CallbackInfo ci) {
        tag.remove("hk3ExactBatch");
        tag.remove("hk3ExactBatchAmount");
        if (hk3gtl$exactToken != null) {
            tag.putUUID("hk3ExactBatch", hk3gtl$exactToken);
            if (hk3gtl$batchOriginalAmount > 0) tag.putLong("hk3ExactBatchAmount", hk3gtl$batchOriginalAmount);
        }
    }

    @Inject(method = "readFromNBT", at = @At("RETURN"))
    private void hk3gtl$loadExactToken(CompoundTag tag, CallbackInfo ci) {
        hk3gtl$exactToken = tag.hasUUID("hk3ExactBatch") ? tag.getUUID("hk3ExactBatch") : null;
        hk3gtl$batchOriginalAmount = hk3gtl$exactToken != null && tag.contains("hk3ExactBatchAmount", Tag.TAG_LONG)
                ? tag.getLong("hk3ExactBatchAmount") : -1;
        hk3gtl$finishingExactToken = null;
        hk3gtl$finishingProduced = -1;
    }
}
