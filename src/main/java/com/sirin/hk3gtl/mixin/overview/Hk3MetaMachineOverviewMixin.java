package com.sirin.hk3gtl.mixin.overview;

import com.gregtechceu.gtceu.api.machine.MetaMachine;
import com.sirin.hk3gtl.common.overview.Hk3MachineOverviewHooks;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

/**
 * 【文件职责】观察GT机器加载/卸载；卸载不会删除已登记位置或重新推断归属。
 * 【变更记录 #1】2026-10-19 02:07:23（第1次备注 · 修订171）
 * 删除：无。新增：GTCEu 1.4.4已核验的onLoad/onUnload返回旁注。
 * 修改：无；不增加tick订阅，不改变原生命周期；用途：第三方继承机器也能更新已有总览快照。
 */
@Mixin(value = MetaMachine.class, remap = false)
public abstract class Hk3MetaMachineOverviewMixin {
    @Inject(method = "onLoad", at = @At("RETURN"))
    private void hk3gtl$overviewLoaded(CallbackInfo ci) { Hk3MachineOverviewHooks.loaded((MetaMachine) (Object) this); }

    @Inject(method = "onUnload", at = @At("RETURN"))
    private void hk3gtl$overviewUnloaded(CallbackInfo ci) { Hk3MachineOverviewHooks.unloaded((MetaMachine) (Object) this); }
}
