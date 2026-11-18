package com.sirin.hk3gtl.mixin.ae;
import appeng.parts.automation.ExportBusPart;
import appeng.api.behaviors.StackExportStrategy;
import appeng.api.behaviors.StackTransferContext;
import appeng.api.stacks.AEKey;
import appeng.core.definitions.AEItems;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.*;
@Mixin(value=ExportBusPart.class,remap=false)
 
public abstract class Hk3EggExportBusMixin {
    @Redirect(method="doBusWork",at=@At(value="INVOKE",target="Lappeng/api/behaviors/StackExportStrategy;transfer(Lappeng/api/behaviors/StackTransferContext;Lappeng/api/stacks/AEKey;J)J"))
    private long hk3gtl$moved(StackExportStrategy strategy,StackTransferContext context,AEKey what,long amount){
        long actual=strategy.transfer(context,what,amount);if(actual>0){var part=(ExportBusPart)(Object)this;
            if(part.getUpgrades().isInstalled(AEItems.SPEED_CARD))com.sirin.hk3gtl.common.easter.Hk3EggAeUpgrades.receipt(part,0,204,true);
            if(part.getUpgrades().isInstalled(AEItems.FUZZY_CARD)&&!part.getConfig().keySet().contains(what))com.sirin.hk3gtl.common.easter.Hk3EggAeUpgrades.receipt(part,3,207,false);
        }return actual;
    }
}
