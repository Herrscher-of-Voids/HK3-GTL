package com.sirin.hk3gtl.mixin.gtceu;

import com.gregtechceu.gtceu.api.machine.trait.NotifiableEnergyContainer;
import com.sirin.hk3gtl.common.easter.Hk3EggInterfaces;
import net.minecraft.core.Direction;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

@Mixin(value=NotifiableEnergyContainer.class,remap=false)
public abstract class Hk3EggEnergyInterfaceMixin {
    @Inject(method="acceptEnergyFromNetwork",at=@At("RETURN"))
    private void hk3gtl$received(Direction side,long voltage,long amperage,CallbackInfoReturnable<Long> callback){
        if(callback.getReturnValue()>0)Hk3EggInterfaces.transferred(((NotifiableEnergyContainer)(Object)this).getMachine(),"eu");
    }
}
