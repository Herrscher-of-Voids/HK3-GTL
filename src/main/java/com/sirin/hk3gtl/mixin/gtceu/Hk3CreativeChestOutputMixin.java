package com.sirin.hk3gtl.mixin.gtceu;

/**
 * 【文件职责】仅关闭 gtceu:creative_chest 的自动化无限能力与主动供给，保留样本和创造界面。
 * 【变更记录 #1】2026-11-04 04:26:55（第1次备注 · 内测5修订195）
 * - 删除：无，不删除机器、样本、配方或毕业检测。
 * - 新增：能力查询、周期检查与直接推送的服务端供给入口保护。
 * - 修改：指定机器在全部方向、无方向和覆盖板查询下均不暴露传输能力，推送入口直接结束。
 * - 用途：堵住管道、漏斗、AE与Forge桥的无限取出；普通有限存储及其他注册来源沿原行为。
 */

import com.gregtechceu.gtceu.api.machine.MetaMachine;
import com.gregtechceu.gtceu.common.machine.storage.CreativeChestMachine;
import com.lowdragmc.lowdraglib.side.item.IItemTransfer;
import net.minecraft.core.Direction;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Unique;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

@Mixin(value = CreativeChestMachine.class, remap = false)
public abstract class Hk3CreativeChestOutputMixin {

    @Unique
    private boolean hk3gtl$isRestrictedStorage() {
        var id = ((MetaMachine) (Object) this).getDefinition().getId();
        return "gtceu".equals(id.getNamespace()) && "creative_chest".equals(id.getPath());
    }

    @Inject(method = "getItemTransferCap", at = @At("HEAD"), cancellable = true, remap = false)
    private void hk3gtl$blockInfiniteCapability(Direction side, boolean useCoverCapability,
                                               CallbackInfoReturnable<IItemTransfer> cir) {
        // 无操作者的自动化不因在线玩家模式而放行；样本界面直接使用原有限缓存。
        if (hk3gtl$isRestrictedStorage()) cir.setReturnValue(null);
    }

    @Inject(method = {"checkAutoOutput", "updateItemTick"}, at = @At("HEAD"), cancellable = true, require = 2, remap = false)
    private void hk3gtl$blockInfinitePush(CallbackInfo ci) {
        // 同时截断周期入口和外部直接调用，避免绕过能力查询直接向邻居生成资源。
        if (hk3gtl$isRestrictedStorage()) ci.cancel();
    }
}
