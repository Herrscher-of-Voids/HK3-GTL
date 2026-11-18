package com.sirin.hk3gtl.common.item;


import com.sirin.hk3gtl.common.phone.Hk3PhoneData;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResultHolder;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.Level;







public final class Hk3PhoneItem extends Item {
    public static final long CAPACITY=com.sirin.hk3gtl.common.phone.Hk3PhoneBattery.CAPACITY;
    public Hk3PhoneItem(Properties properties){super(properties);}
    @Override public boolean shouldCauseReequipAnimation(ItemStack oldStack,ItemStack newStack,boolean slotChanged){
        return slotChanged || oldStack.getItem()!=newStack.getItem()
                || com.sirin.hk3gtl.common.phone.Hk3PhoneVisualState.changed(oldStack.getTag(),newStack.getTag());
    }
    @Override public net.minecraftforge.common.capabilities.ICapabilityProvider initCapabilities(ItemStack stack,net.minecraft.nbt.CompoundTag nbt){
        var electric=new com.sirin.hk3gtl.common.phone.Hk3PhoneBattery(stack::getOrCreateTag,stack::getCount);
        var optional=net.minecraftforge.common.util.LazyOptional.of(()->electric);
        return new net.minecraftforge.common.capabilities.ICapabilityProvider(){
            @Override public <T> net.minecraftforge.common.util.LazyOptional<T> getCapability(net.minecraftforge.common.capabilities.Capability<T> cap,net.minecraft.core.Direction side){
                return cap==com.gregtechceu.gtceu.api.capability.forge.GTCapability.CAPABILITY_ELECTRIC_ITEM?optional.cast():net.minecraftforge.common.util.LazyOptional.empty();
            }
        };
    }
    @Override public InteractionResultHolder<ItemStack> use(Level level,Player player,InteractionHand hand){
        ItemStack stack=player.getItemInHand(hand);
        if(!level.isClientSide()&&player instanceof ServerPlayer owner){
            Hk3PhoneData.get(owner).install(owner.getUUID());
            com.sirin.hk3gtl.common.phone.Hk3PhoneRuntime.prefer(owner,stack);
            com.sirin.hk3gtl.common.phone.Hk3PhoneService.open(owner,"home",0);
        }
        return InteractionResultHolder.sidedSuccess(stack,level.isClientSide());
    }
    @Override public boolean isBarVisible(ItemStack stack){return true;}
    @Override public int getBarWidth(ItemStack stack){return (int)Math.round(13.0*charge(stack)/CAPACITY);}
    @Override public int getBarColor(ItemStack stack){return charge(stack)<CAPACITY/5?0xEF7777:0xA687E8;}
    public static long charge(ItemStack stack){
        var e=com.gregtechceu.gtceu.api.capability.GTCapabilityHelper.getElectricItem(stack);
        return e==null?0:e.getCharge();
    }
    @Override public void appendHoverText(ItemStack stack,Level level,java.util.List<Component> lines,net.minecraft.world.item.TooltipFlag flag){
        lines.add(Component.translatable("hk3gtl.phone.charge",charge(stack),CAPACITY));
        lines.add(Component.translatable("hk3gtl.phone.charger"));
        lines.add(Component.translatable("hk3gtl.phone.install_hint"));
        lines.add(Component.translatable("hk3gtl.phone.power_hint"));
    }
}
