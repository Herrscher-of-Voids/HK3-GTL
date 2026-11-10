package com.sirin.hk3gtl.mixin.ae;
import appeng.parts.automation.ExportBusPart;
import appeng.api.behaviors.StackExportStrategy;
import appeng.api.behaviors.StackTransferContext;
import appeng.api.stacks.AEKey;
import appeng.core.definitions.AEItems;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.*;
@Mixin(value=ExportBusPart.class,remap=false)
/** 【变更记录 #1】2026-10-01 06:31:11（修订128）：删除无；新增联动真实安装/传输观察；修改无；用途：模拟、仅持有与空过滤不冒充成功，按本人安装归属。 */
public abstract class Hk3EggExportBusMixin {
    @Redirect(method="doBusWork",at=@At(value="INVOKE",target="Lappeng/api/behaviors/StackExportStrategy;transfer(Lappeng/api/behaviors/StackTransferContext;Lappeng/api/stacks/AEKey;J)J"))
    private long hk3gtl$moved(StackExportStrategy strategy,StackTransferContext context,AEKey what,long amount){
        long actual=strategy.transfer(context,what,amount);if(actual>0){var part=(ExportBusPart)(Object)this;
            if(part.getUpgrades().isInstalled(AEItems.SPEED_CARD))com.sirin.hk3gtl.common.easter.Hk3EggAeUpgrades.receipt(part,0,204,true);
            if(part.getUpgrades().isInstalled(AEItems.FUZZY_CARD)&&!part.getConfig().keySet().contains(what))com.sirin.hk3gtl.common.easter.Hk3EggAeUpgrades.receipt(part,3,207,false);
        }return actual;
    }
}
