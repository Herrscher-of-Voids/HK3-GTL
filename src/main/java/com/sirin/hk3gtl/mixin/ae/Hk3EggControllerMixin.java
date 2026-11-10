package com.sirin.hk3gtl.mixin.ae;
import appeng.blockentity.networking.ControllerBlockEntity;
import appeng.api.networking.IGridNodeListener;
import net.minecraft.server.level.ServerLevel;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.*;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;
@Mixin(value=ControllerBlockEntity.class,remap=false)
/** 【变更记录 #1】2026-10-01 06:03:54（修订128）：删除无；新增当前AE成功回调旁注；修改无；用途：已审核原条件，不干预AE权限和生产。 */
public abstract class Hk3EggControllerMixin {
    @Inject(method="onMainNodeStateChanged",at=@At("RETURN"))
    private void hk3gtl$online(IGridNodeListener.State reason,CallbackInfo ci){
        var be=(ControllerBlockEntity)(Object)this;
        if(be.getLevel() instanceof ServerLevel level&&be.getMainNode().isActive()&&be.getPersistentData().hasUUID(com.sirin.hk3gtl.common.easter.Hk3EggProduction.OWNER)){
            com.sirin.hk3gtl.common.easter.Hk3EggProductionData.get(level.getServer()).produced(be.getPersistentData().getUUID(com.sirin.hk3gtl.common.easter.Hk3EggProduction.OWNER),"receipt:195",1);
        }
    }
}
