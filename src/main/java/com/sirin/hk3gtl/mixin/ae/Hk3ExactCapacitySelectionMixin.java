package com.sirin.hk3gtl.mixin.ae;

import appeng.api.networking.crafting.ICraftingPlan;
import appeng.api.networking.crafting.UnsuitableCpus;
import appeng.api.networking.security.IActionSource;
import appeng.me.cluster.implementations.CraftingCPUCluster;
import appeng.me.service.CraftingService;
import com.llamalad7.mixinextras.injector.wrapoperation.Operation;
import com.llamalad7.mixinextras.injector.wrapoperation.WrapOperation;
import com.sirin.hk3gtl.common.integration.ae.exact.Hk3ExactCpuCapacity;
import org.apache.commons.lang3.mutable.MutableObject;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;

/** 只扩展自动选 CPU 的容量比较，原生排序和选择策略保持生效。 */
@Mixin(value = CraftingService.class, remap = false)
public abstract class Hk3ExactCapacitySelectionMixin {
    @WrapOperation(method = "findSuitableCraftingCPU",
            at = @At(value = "INVOKE", target = "Lappeng/me/cluster/implementations/CraftingCPUCluster;getAvailableStorage()J"))
    private long hk3gtl$compareExactCapacity(CraftingCPUCluster cpu, Operation<Long> original,
                                            ICraftingPlan plan, boolean prioritizePower, IActionSource source,
                                            MutableObject<UnsuitableCpus> unsuitable) {
        return Hk3ExactCpuCapacity.admissionStorage(cpu, plan, original.call(cpu));
    }
}
