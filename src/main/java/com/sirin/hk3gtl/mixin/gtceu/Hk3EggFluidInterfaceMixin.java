package com.sirin.hk3gtl.mixin.gtceu;

import com.gregtechceu.gtceu.api.capability.recipe.IO;
import com.gregtechceu.gtceu.api.machine.trait.NotifiableFluidTank;
import com.gregtechceu.gtceu.api.recipe.GTRecipe;
import com.gregtechceu.gtceu.api.recipe.ingredient.FluidIngredient;
import com.sirin.hk3gtl.common.easter.Hk3EggInterfaces;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Unique;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

import java.util.List;

@Mixin(value=NotifiableFluidTank.class,remap=false)
public abstract class Hk3EggFluidInterfaceMixin {
    @Unique private long hk3gtl$fluidBefore;
    @Unique private boolean hk3gtl$watch;
    @Unique private long hk3gtl$fluidCount(){
        long total=0;
        for(var storage:((NotifiableFluidTank)(Object)this).getStorages())total+=storage.getFluid().getAmount();
        return total;
    }
    @Inject(method="handleRecipeInner",at=@At("HEAD"))
    private void hk3gtl$before(IO io,GTRecipe recipe,List<FluidIngredient> left,String slotName,boolean simulate,CallbackInfoReturnable<List<FluidIngredient>> callback){
        hk3gtl$watch=!simulate&&Hk3EggInterfaces.watches(((NotifiableFluidTank)(Object)this).getMachine(),io==IO.IN?"fluid_in":"fluid_out");
        if(hk3gtl$watch)hk3gtl$fluidBefore=hk3gtl$fluidCount();
    }
    @Inject(method="handleRecipeInner",at=@At("RETURN"))
    private void hk3gtl$after(IO io,GTRecipe recipe,List<FluidIngredient> left,String slotName,boolean simulate,CallbackInfoReturnable<List<FluidIngredient>> callback){
        if(!hk3gtl$watch)return;
        long after=hk3gtl$fluidCount();
        if(io==IO.IN&&after<hk3gtl$fluidBefore||io==IO.OUT&&after>hk3gtl$fluidBefore)
            Hk3EggInterfaces.transferred(((NotifiableFluidTank)(Object)this).getMachine(),recipe,io==IO.IN?"fluid_in":"fluid_out");
    }
}
