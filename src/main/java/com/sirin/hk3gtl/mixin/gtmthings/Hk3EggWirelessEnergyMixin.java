package com.sirin.hk3gtl.mixin.gtmthings;
import com.hepdd.gtmthings.common.cover.WirelessEnergyReceiveCover;
import com.gregtechceu.gtceu.api.cover.CoverBehavior;
import com.gregtechceu.gtceu.api.capability.IEnergyContainer;
import net.minecraft.core.Direction;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.item.ItemStack;
import org.spongepowered.asm.mixin.*;
import org.spongepowered.asm.mixin.injection.*;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;
import com.sirin.hk3gtl.common.easter.Hk3EggCovers;
@Mixin(value=WirelessEnergyReceiveCover.class,priority=1100,remap=false)


public abstract class Hk3EggWirelessEnergyMixin {
    @Shadow @Final private int tier;
    @Inject(method="onAttached",at=@At("RETURN"))private void hk3gtl$attached(ItemStack stack,ServerPlayer p,CallbackInfo ci){Hk3EggCovers.attached((CoverBehavior)(Object)this,p);}
    @Redirect(method="updateEnergy",at=@At(value="INVOKE",target="Lcom/gregtechceu/gtceu/api/capability/IEnergyContainer;addEnergy(J)J"))
    private long hk3gtl$added(IEnergyContainer energy,long requested){long actual=energy.addEnergy(requested);if(tier==1&&actual>0)Hk3EggCovers.delivered((CoverBehavior)(Object)this,276);return actual;}
    @Redirect(method="updateEnergy",at=@At(value="INVOKE",target="Lcom/gregtechceu/gtceu/api/capability/IEnergyContainer;acceptEnergyFromNetwork(Lnet/minecraft/core/Direction;JJ)J"))
    private long hk3gtl$accepted(IEnergyContainer energy,Direction side,long voltage,long amps){long actual=energy.acceptEnergyFromNetwork(side,voltage,amps);if(tier==1&&voltage>0&&actual>0)Hk3EggCovers.delivered((CoverBehavior)(Object)this,276);return actual;}
}
