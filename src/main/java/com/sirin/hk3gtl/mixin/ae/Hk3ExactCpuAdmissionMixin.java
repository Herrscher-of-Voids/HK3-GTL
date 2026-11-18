package com.sirin.hk3gtl.mixin.ae;

import appeng.api.networking.IGrid;
import appeng.api.networking.crafting.ICraftingPlan;
import appeng.api.networking.crafting.ICraftingRequester;
import appeng.api.networking.crafting.ICraftingSubmitResult;
import appeng.api.networking.security.IActionSource;
import appeng.crafting.execution.CraftingCpuLogic;
import appeng.crafting.execution.CraftingSubmitResult;
import appeng.crafting.execution.ExecutingCraftingJob;
import appeng.me.cluster.implementations.CraftingCPUCluster;
import com.sirin.hk3gtl.common.integration.ae.exact.Hk3ExactBytePlan;
import com.sirin.hk3gtl.common.integration.ae.exact.Hk3ExactCpuCapacity;
import net.minecraft.nbt.CompoundTag;
import org.spongepowered.asm.mixin.Final;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Shadow;
import org.spongepowered.asm.mixin.Unique;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

import java.math.BigInteger;

/** 精确容量在原生投料前判定，绝不跳过忙碌、离线或库存扣除检查。 */
@Mixin(value = CraftingCpuLogic.class, remap = false, priority = 1200)
public abstract class Hk3ExactCpuAdmissionMixin implements Hk3ExactCpuCapacity.JobAccess {
    @Shadow @Final private CraftingCPUCluster cluster;
    @Shadow private ExecutingCraftingJob job;
    @Unique private BigInteger hk3gtl$activeRequiredBytes;

    @Override
    public BigInteger hk3gtl$activeBytes() {
        return job != null && hk3gtl$activeRequiredBytes != null
                ? hk3gtl$activeRequiredBytes : BigInteger.ZERO;
    }

    @Inject(method = "trySubmitJob", at = @At("HEAD"), cancellable = true)
    private void hk3gtl$checkExactCapacity(IGrid grid, ICraftingPlan plan, IActionSource source,
                                         ICraftingRequester requester,
                                         CallbackInfoReturnable<ICraftingSubmitResult> ci) {
        // 优先于 GTL 的 1100 级 Graph 分支；本计划不冒充 AeGraphPlan。
        if (plan instanceof Hk3ExactBytePlan && !Hk3ExactCpuCapacity.accepts(cluster, plan)) {
            ci.setReturnValue(CraftingSubmitResult.CPU_TOO_SMALL);
        }
    }

    @Inject(method = "trySubmitJob", at = @At("RETURN"))
    private void hk3gtl$recordExactCharge(IGrid grid, ICraftingPlan plan, IActionSource source,
                                        ICraftingRequester requester,
                                        CallbackInfoReturnable<ICraftingSubmitResult> ci) {
        if (ci.getReturnValue().successful() && job != null) {
            hk3gtl$activeRequiredBytes = Hk3ExactCpuCapacity.requiredBytes(plan);
            cluster.markDirty();
        }
    }

    @Inject(method = "finishJob", at = @At("RETURN"))
    private void hk3gtl$clearExactCharge(boolean success, CallbackInfo ci) {
        hk3gtl$activeRequiredBytes = null;
    }

    @Inject(method = "writeToNBT", at = @At("RETURN"))
    private void hk3gtl$saveExactCharge(CompoundTag tag, CallbackInfo ci) {
        Hk3ExactCpuCapacity.writeJobBytes(tag, job == null ? null : hk3gtl$activeRequiredBytes);
    }

    @Inject(method = "readFromNBT", at = @At("RETURN"))
    private void hk3gtl$loadExactCharge(CompoundTag tag, CallbackInfo ci) {
        hk3gtl$activeRequiredBytes = job == null ? null : Hk3ExactCpuCapacity.readJobBytes(tag);
    }
}
