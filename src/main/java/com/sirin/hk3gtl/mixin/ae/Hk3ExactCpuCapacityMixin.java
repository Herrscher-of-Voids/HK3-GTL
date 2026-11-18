package com.sirin.hk3gtl.mixin.ae;

import appeng.blockentity.crafting.CraftingBlockEntity;
import appeng.crafting.execution.CraftingCpuLogic;
import appeng.me.cluster.implementations.CraftingCPUCluster;
import com.sirin.hk3gtl.common.integration.ae.exact.Hk3ExactCpuCapacity;
import org.spongepowered.asm.mixin.Final;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Shadow;
import org.spongepowered.asm.mixin.Unique;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

import java.math.BigInteger;
import java.util.List;

/** 不改装配流程，兼容 EAEP 的 HEAD 取消与 MAE2 的协处理器重定向。 */
@Mixin(value = CraftingCPUCluster.class, remap = false)
public abstract class Hk3ExactCpuCapacityMixin implements Hk3ExactCpuCapacity.Access {
    @Shadow @Final private List<CraftingBlockEntity> blockEntities;
    @Shadow @Final public CraftingCpuLogic craftingLogic;
    @Unique private int hk3gtl$countedStorageBlocks = -1;
    @Unique private BigInteger hk3gtl$exactStorage = BigInteger.ZERO;

    @Override
    public BigInteger hk3gtl$storageBytes() {
        // 原生 cluster 只追加方块，拆除时销毁整个 cluster；重组会重新计算容量。
        if (hk3gtl$countedStorageBlocks != blockEntities.size()) {
            hk3gtl$exactStorage = Hk3ExactCpuCapacity.sumStorage(blockEntities, CraftingBlockEntity::getStorageBytes);
            hk3gtl$countedStorageBlocks = blockEntities.size();
        }
        return hk3gtl$exactStorage;
    }

    @Override
    public BigInteger hk3gtl$activeBytes() {
        return ((Hk3ExactCpuCapacity.JobAccess) craftingLogic).hk3gtl$activeBytes();
    }

    @Inject(method = "getAvailableStorage", at = @At("RETURN"), cancellable = true)
    private void hk3gtl$projectExactCapacity(CallbackInfoReturnable<Long> ci) {
        ci.setReturnValue(Hk3ExactCpuCapacity.project(hk3gtl$storageBytes()));
    }
}
