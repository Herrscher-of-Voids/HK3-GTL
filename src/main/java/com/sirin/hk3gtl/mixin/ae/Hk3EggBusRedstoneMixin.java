package com.sirin.hk3gtl.mixin.ae;
import appeng.parts.automation.IOBusPart;
import appeng.core.definitions.AEItems;
import net.minecraft.world.level.BlockGetter;
import net.minecraft.core.BlockPos;
import org.spongepowered.asm.mixin.*;
import org.spongepowered.asm.mixin.injection.*;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;
@Mixin(value=IOBusPart.class,remap=false)
public abstract class Hk3EggBusRedstoneMixin {
    @Shadow protected abstract boolean isSleeping();
    @Unique private boolean hk3gtl$known,hk3gtl$power,hk3gtl$changed;
    @Inject(method="addToWorld",at=@At("RETURN"))private void hk3gtl$baseline(CallbackInfo ci){var part=(IOBusPart)(Object)this;hk3gtl$power=part.getHost().hasRedstone();hk3gtl$known=true;}

    @Inject(method="onNeighborChanged",at=@At("HEAD"))private void hk3gtl$before(BlockGetter level,BlockPos pos,BlockPos neighbor,CallbackInfo ci){var part=(IOBusPart)(Object)this;boolean power=part.getHost().hasRedstone();hk3gtl$changed=hk3gtl$known&&power!=hk3gtl$power;hk3gtl$power=power;hk3gtl$known=true;}
    @Inject(method="onNeighborChanged",at=@At("RETURN"))private void hk3gtl$after(BlockGetter level,BlockPos pos,BlockPos neighbor,CallbackInfo ci){var part=(IOBusPart)(Object)this;if(hk3gtl$changed&&part.getMainNode().isActive()&&part.getUpgrades().isInstalled(AEItems.REDSTONE_CARD)&&!part.getRSMode().name().equals("IGNORE")&&(!part.getRSMode().name().equals("SIGNAL_PULSE")||hk3gtl$power))com.sirin.hk3gtl.common.easter.Hk3EggAeUpgrades.receipt(part,1,205,false);}
}
