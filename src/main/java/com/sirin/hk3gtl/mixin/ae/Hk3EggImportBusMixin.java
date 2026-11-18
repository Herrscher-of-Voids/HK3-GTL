package com.sirin.hk3gtl.mixin.ae;
import appeng.parts.automation.ImportBusPart;
import appeng.api.networking.IGrid;
import appeng.core.definitions.AEItems;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.*;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;
@Mixin(value=ImportBusPart.class,remap=false)

public abstract class Hk3EggImportBusMixin {
    @Inject(method="doBusWork",at=@At("RETURN"))private void hk3gtl$moved(IGrid grid,CallbackInfoReturnable<Boolean> ci){
        if(!Boolean.TRUE.equals(ci.getReturnValue()))return;var part=(ImportBusPart)(Object)this;
        if(part.getUpgrades().isInstalled(AEItems.SPEED_CARD))com.sirin.hk3gtl.common.easter.Hk3EggAeUpgrades.receipt(part,0,204,true);
        if(part.getUpgrades().isInstalled(AEItems.INVERTER_CARD)&&!part.getConfig().keySet().isEmpty())com.sirin.hk3gtl.common.easter.Hk3EggAeUpgrades.receipt(part,2,206,false);
    }
}
