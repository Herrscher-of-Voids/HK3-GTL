package com.sirin.hk3gtl.mixin;
import com.gregtechceu.gtceu.api.machine.multiblock.MultiblockControllerMachine;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.*;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;
@Mixin(value=MultiblockControllerMachine.class,remap=false)
/** 【变更记录 #1】2026-10-01 06:23:20（修订128）：删除无；新增服务端真实事件旁注；修改无；用途：原条件、原世界结果不变，只授个人可选收藏。 */
public abstract class Hk3EggFormedMixin {
    @Inject(method="onStructureFormed",at=@At("RETURN"))private void hk3gtl$formed(CallbackInfo ci){com.sirin.hk3gtl.common.easter.Hk3EggStructureScenes.formed((MultiblockControllerMachine)(Object)this);}
}
