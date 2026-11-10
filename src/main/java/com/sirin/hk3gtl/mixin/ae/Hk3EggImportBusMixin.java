package com.sirin.hk3gtl.mixin.ae;
import appeng.parts.automation.ImportBusPart;
import appeng.api.networking.IGrid;
import appeng.core.definitions.AEItems;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.*;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;
@Mixin(value=ImportBusPart.class,remap=false)
/** 【变更记录 #1】2026-10-01 06:31:11（修订128）：删除无；新增联动真实安装/传输观察；修改无；用途：模拟、仅持有与空过滤不冒充成功，按本人安装归属。 */
public abstract class Hk3EggImportBusMixin {
    @Inject(method="doBusWork",at=@At("RETURN"))private void hk3gtl$moved(IGrid grid,CallbackInfoReturnable<Boolean> ci){
        if(!Boolean.TRUE.equals(ci.getReturnValue()))return;var part=(ImportBusPart)(Object)this;
        if(part.getUpgrades().isInstalled(AEItems.SPEED_CARD))com.sirin.hk3gtl.common.easter.Hk3EggAeUpgrades.receipt(part,0,204,true);
        if(part.getUpgrades().isInstalled(AEItems.INVERTER_CARD)&&!part.getConfig().keySet().isEmpty())com.sirin.hk3gtl.common.easter.Hk3EggAeUpgrades.receipt(part,2,206,false);
    }
}
