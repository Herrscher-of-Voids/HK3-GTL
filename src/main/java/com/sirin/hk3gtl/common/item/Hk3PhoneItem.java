package com.sirin.hk3gtl.common.item;

/** 【变更记录 #1】2026-09-29 19:19:27（内测5修订96）：新增一次性个人通讯终端；服务器写入安装资格后才消耗物品，重复使用不消耗。 */
import com.sirin.hk3gtl.common.phone.Hk3PhoneData;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResultHolder;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.Level;

/**
 * 【变更记录 #2】2026-09-30 18:44:46（内测5修订113）
 * 删除：安装消耗物品与重复使用失败；新增：GT电池能力、右键安装并打开、物品电量条。
 * 修改：手机保留在背包，实际EU电量随物品保存；用途：与快捷键共用入口且支持GT充电。
 */
/** 【变更记录 #3】2026-10-01 01:25:10（修订125）：删除电量变化引发的重复持物抬手；新增忽略Charge字段的装备动画判断；修改仅充放电不重播，换槽、换物品及其他NBT改变仍重播；用途：保留真实电量同步且避免每秒抖动。 */
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
