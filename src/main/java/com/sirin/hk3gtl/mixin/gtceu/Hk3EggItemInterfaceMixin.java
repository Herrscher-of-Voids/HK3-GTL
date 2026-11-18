package com.sirin.hk3gtl.mixin.gtceu;

import com.gregtechceu.gtceu.api.capability.recipe.IO;
import com.gregtechceu.gtceu.api.machine.trait.NotifiableItemStackHandler;
import com.gregtechceu.gtceu.api.recipe.GTRecipe;
import com.sirin.hk3gtl.common.easter.Hk3EggInterfaces;
import net.minecraft.world.item.crafting.Ingredient;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Unique;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

import java.util.List;

@Mixin(value=NotifiableItemStackHandler.class,remap=false)
public abstract class Hk3EggItemInterfaceMixin {
    @Unique private long hk3gtl$itemsBefore;
    @Unique private boolean hk3gtl$watch;
    @Unique private long hk3gtl$itemCount(){
        var handler=(NotifiableItemStackHandler)(Object)this;
        long total=0;
        for(int slot=0;slot<handler.getSlots();slot++)total+=handler.getStackInSlot(slot).getCount();
        return total;
    }
    @Inject(method="handleRecipeInner",at=@At("HEAD"))
    private void hk3gtl$before(IO io,GTRecipe recipe,List<Ingredient> left,String slotName,boolean simulate,CallbackInfoReturnable<List<Ingredient>> callback){
        hk3gtl$watch=!simulate&&Hk3EggInterfaces.watches(((NotifiableItemStackHandler)(Object)this).getMachine(),io==IO.IN?"item_in":"item_out");
        if(hk3gtl$watch)hk3gtl$itemsBefore=hk3gtl$itemCount();
    }
    @Inject(method="handleRecipeInner",at=@At("RETURN"))
    private void hk3gtl$after(IO io,GTRecipe recipe,List<Ingredient> left,String slotName,boolean simulate,CallbackInfoReturnable<List<Ingredient>> callback){
        if(!hk3gtl$watch)return;
        long after=hk3gtl$itemCount();
        if(io==IO.IN&&after<hk3gtl$itemsBefore||io==IO.OUT&&after>hk3gtl$itemsBefore)
            Hk3EggInterfaces.transferred(((NotifiableItemStackHandler)(Object)this).getMachine(),recipe,io==IO.IN?"item_in":"item_out");
    }
}
