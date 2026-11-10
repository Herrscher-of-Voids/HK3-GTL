package com.sirin.hk3gtl.mixin.overview;

import com.gregtechceu.gtceu.api.machine.multiblock.MultiblockControllerMachine;
import com.sirin.hk3gtl.common.overview.Hk3MachineOverviewHooks;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

/**
 * 【文件职责】观察GT多方块实际成型/失效完成后的状态，不执行匹配或读写结构。
 * 【变更记录 #1】2026-10-19 02:07:23（第1次备注 · 修订171）
 * 删除：无。新增：GTCEu 1.4.4控制器两个既存回调的RETURN旁注。
 * 修改：无；异步线程回调不写账本，由低频补查刷新。用途：成型/失效事件同步已绑定机器。
 */
@Mixin(value = MultiblockControllerMachine.class, remap = false)
public abstract class Hk3MultiblockOverviewMixin {
    @Inject(method = {"onStructureFormed", "onStructureInvalid"}, at = @At("RETURN"))
    private void hk3gtl$overviewStructureChanged(CallbackInfo ci) {
        Hk3MachineOverviewHooks.changed((MultiblockControllerMachine) (Object) this);
    }
}
