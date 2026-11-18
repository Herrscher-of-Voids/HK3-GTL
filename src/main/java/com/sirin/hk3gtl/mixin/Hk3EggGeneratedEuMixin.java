package com.sirin.hk3gtl.mixin;
import com.gregtechceu.gtceu.api.machine.trait.NotifiableEnergyContainer;
import com.gregtechceu.gtceu.api.capability.IEnergyContainer;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.*;
@Mixin(value=NotifiableEnergyContainer.class,remap=false)
 
public abstract class Hk3EggGeneratedEuMixin {
    @Redirect(method="handleRecipeInner",at=@At(value="INVOKE",target="Lcom/gregtechceu/gtceu/api/capability/IEnergyContainer;addEnergy(J)J"))
    private long hk3gtl$actual(IEnergyContainer container,long amount){long actual=container.addEnergy(amount);if(amount>0&&actual>0)com.sirin.hk3gtl.common.easter.Hk3EggGeneration.accepted(actual);return actual;}
}
