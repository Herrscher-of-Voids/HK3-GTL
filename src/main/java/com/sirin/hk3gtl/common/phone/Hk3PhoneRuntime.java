package com.sirin.hk3gtl.common.phone;

import com.sirin.hk3gtl.common.item.Hk3PhoneItem;
import com.sirin.hk3gtl.common.item.Hk3Items;
import com.gregtechceu.gtceu.api.capability.GTCapabilityHelper;
import com.sirin.hk3gtl.common.network.Hk3Network;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.network.chat.Component;
import net.minecraft.world.item.ItemStack;
import net.minecraftforge.network.PacketDistributor;









public final class Hk3PhoneRuntime {
    private Hk3PhoneRuntime(){}
    public static void prefer(ServerPlayer p,ItemStack stack){
        for(int i=0;i<p.getInventory().getContainerSize();i++)if(p.getInventory().getItem(i)==stack)p.getPersistentData().putInt("Hk3PhoneSlot",i);
    }
    public static ItemStack phone(ServerPlayer p){
        int preferred=p.getPersistentData().getInt("Hk3PhoneSlot");
        if(preferred>=0&&preferred<p.getInventory().getContainerSize()){
            var s=p.getInventory().getItem(preferred);if(s.getItem() instanceof Hk3PhoneItem)return s;
        }
        for(int i=0;i<p.getInventory().getContainerSize();i++){
            var s=p.getInventory().getItem(i);if(s.getItem() instanceof Hk3PhoneItem){prefer(p,s);return s;}
        }
        return ItemStack.EMPTY;
    }
    public static void migrate(ServerPlayer p){
        var data=Hk3PhoneData.get(p);if(!data.needsPhysical(p.getUUID()))return;
        if(!phone(p).isEmpty()){data.physicalDelivered(p.getUUID());return;}
        if(p.getInventory().getFreeSlot()<0)return;
        var stack=new ItemStack(Hk3Items.PERSONAL_PHONE.get());
        if(p.getInventory().add(stack)){
            data.physicalDelivered(p.getUUID());
            p.sendSystemMessage(Component.literal("旧版安装已补发一部实体手机；安装不再消耗，请先充电。"));
        }
    }
    public static boolean powered(ServerPlayer p){migrate(p);return Hk3PhoneItem.charge(phone(p))>=8;}
    public static boolean requirePower(ServerPlayer p){
        if(powered(p))return true;
        p.sendSystemMessage(Component.literal("请随身携带已充电的通讯终端（GT电力充电槽，LV或以上）。"));return false;
    }
    public static CompoundTag status(ServerPlayer p){
        migrate(p);var n=new CompoundTag();var stack=phone(p);
        n.putBoolean("Present",!stack.isEmpty());n.putLong("Charge",Hk3PhoneItem.charge(stack));n.putLong("Capacity",Hk3PhoneItem.CAPACITY);
        n.putLong("DayTime",p.serverLevel().getDayTime());
        n.putLong("SaveDayTime",p.server.overworld().getDayTime());
        var biome=p.level().getBiome(p.blockPosition());String id=biome.unwrapKey().map(k->k.location().toString()).orElse("unknown");
        n.putString("Biome",id);n.putString("Dimension",p.level().dimension().location().toString());
        n.putInt("X",p.getBlockX());n.putInt("Z",p.getBlockZ());
        n.putInt("Temperature",Math.round(biome.value().getBaseTemperature()*20));
        n.putString("Weather",p.level().isRainingAt(p.blockPosition())?"降水":p.level().isThundering()?"雷暴":"晴");
        n.putBoolean("AE",net.minecraftforge.fml.ModList.get().isLoaded("ae2")&&Hk3PhoneAeLink.connected(p));
        return n;
    }
    public static int poll(ServerPlayer p){
        if(!Hk3PhoneData.get(p).installed(p.getUUID()))return 0;
        // 用服务器游戏刻限制频率；连接重开也不会让客户端自行申报电量。
        long tick=p.server.overworld().getGameTime();var data=p.getPersistentData();
        if(data.contains("Hk3PhonePoll")&&tick>=data.getLong("Hk3PhonePoll")&&tick-data.getLong("Hk3PhonePoll")<20)return 0;
        data.putLong("Hk3PhonePoll",tick);
        var battery=GTCapabilityHelper.getElectricItem(phone(p));
        if(battery!=null)battery.discharge(8,Integer.MAX_VALUE,true,false,false);
        var view=new CompoundTag();view.putString("Mode","status");view.put("Runtime",status(p));
        Hk3Network.CHANNEL.send(PacketDistributor.PLAYER.with(()->p),new Hk3PhonePacket(view));return 1;
    }
    public static int openAe(ServerPlayer p){
        if(!Hk3PhoneData.get(p).installed(p.getUUID())||!requirePower(p))return 0;
        if(net.minecraftforge.fml.ModList.get().isLoaded("ae2"))return Hk3PhoneAeLink.choose(p);
        return 0;
    }
    public static int openAe(ServerPlayer p,int slot){
        if(!Hk3PhoneData.get(p).installed(p.getUUID())||!requirePower(p))return 0;
        return net.minecraftforge.fml.ModList.get().isLoaded("ae2")?Hk3PhoneAeLink.open(p,slot):0;
    }
}
