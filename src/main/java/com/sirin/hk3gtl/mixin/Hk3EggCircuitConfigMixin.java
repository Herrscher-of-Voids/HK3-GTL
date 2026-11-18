package com.sirin.hk3gtl.mixin;
import com.gregtechceu.gtceu.common.item.IntCircuitBehaviour;
import com.lowdragmc.lowdraglib.gui.factory.HeldItemUIFactory;
import org.spongepowered.asm.mixin.*;
import org.spongepowered.asm.mixin.injection.*;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;
@Mixin(value=IntCircuitBehaviour.class,remap=false)

public abstract class Hk3EggCircuitConfigMixin {
    @Redirect(method="setCircuitConfiguration(Lcom/lowdragmc/lowdraglib/gui/factory/HeldItemUIFactory$HeldItemHolder;I)V",at=@At(value="INVOKE",target="Lcom/gregtechceu/gtceu/common/item/IntCircuitBehaviour;setCircuitConfiguration(Lnet/minecraft/world/item/ItemStack;I)V"))
    private static void hk3gtl$set(net.minecraft.world.item.ItemStack stack,int value,HeldItemUIFactory.HeldItemHolder holder,int requested){int before=IntCircuitBehaviour.getCircuitConfiguration(stack);IntCircuitBehaviour.setCircuitConfiguration(stack,value);com.sirin.hk3gtl.common.easter.Hk3EggTools.circuitChanged(holder,before,IntCircuitBehaviour.getCircuitConfiguration(stack));}
}
