package com.sirin.hk3gtl.mixin;
import net.minecraft.world.entity.decoration.ArmorStand;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.entity.EquipmentSlot;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.InteractionHand;
import net.minecraft.server.level.ServerPlayer;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.*;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;
@Mixin(ArmorStand.class)
 
 
 
public abstract class Hk3EggArmorStandMixin {
    @Inject(method="setItemSlot",at=@At("TAIL"))private void hk3gtl$clearOwner(EquipmentSlot slot,ItemStack stack,org.spongepowered.asm.mixin.injection.callback.CallbackInfo ci){
        var stand=(ArmorStand)(Object)this;
        if(!stand.level().isClientSide&&slot.getType()==EquipmentSlot.Type.ARMOR)stand.getPersistentData().remove("hk3_egg_armorer_"+slot.getName());
    }
    @Inject(method="swapItem",at=@At("RETURN"))private void hk3gtl$equipped(Player player,EquipmentSlot slot,ItemStack item,InteractionHand hand,CallbackInfoReturnable<Boolean> ci){if(Boolean.TRUE.equals(ci.getReturnValue())&&player instanceof ServerPlayer p&&slot.getType()==EquipmentSlot.Type.ARMOR)com.sirin.hk3gtl.common.easter.Hk3EggPersonalScenes.armored(p,(ArmorStand)(Object)this,slot);}
}
