package com.sirin.hk3gtl.common.event;

import com.mojang.logging.LogUtils;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.item.ItemStack;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.event.entity.player.PlayerEvent;
import net.minecraftforge.event.server.ServerStoppedEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import net.minecraftforge.items.ItemHandlerHelper;
import net.minecraftforge.items.wrapper.PlayerMainInvWrapper;
import java.util.*;

/**
 * 【变更记录 #1】2026-10-01 01:36:39（修订126）
 * 删除：无；新增：指定名字登录触发及待领取礼物每100刻重试。
 * 修改：运行时解析sov物品，模拟背包插入后才实际插入，避免创造模式满背包吞物品。
 * 用途：只发本人的三件礼物；背包满不丢地上，缺物品不崩溃、不虚报领取，损坏账本停止本次会话发奖。
 */
@Mod.EventBusSubscriber(modid="hk3gtl")
public final class Hk3VoidGiftHandler {
    private static final org.slf4j.Logger LOGGER=LogUtils.getLogger();
    private static final Set<UUID> PENDING=java.util.concurrent.ConcurrentHashMap.newKeySet();
    private Hk3VoidGiftHandler() {}
    @SubscribeEvent public static void login(PlayerEvent.PlayerLoggedInEvent event){
        if(!(event.getEntity() instanceof ServerPlayer player))return;
        try{
            var data=Hk3VoidGiftData.get(player.server);data.enroll(player.getUUID(),player.getGameProfile().getName());
            if(data.pending(player.getUUID())){PENDING.add(player.getUUID());attempt(player,data,true);}
        }catch(RuntimeException failure){failed(player,failure);}
    }
    private static void attempt(ServerPlayer player,Hk3VoidGiftData data,boolean login){
        int count=data.deliver(player.getUUID(),index->{
            var gift=Hk3VoidGiftData.GIFTS.get(index);var id=ResourceLocation.tryParse(gift.item());
            if(id==null||!BuiltInRegistries.ITEM.containsKey(id)){
                if(login)LOGGER.warn("[HK3GTL] 首次入世礼物物品暂不可用，保留待发放项：{}",gift.item());
                return false;
            }
            var stack=new ItemStack(BuiltInRegistries.ITEM.get(id),1);
            if(stack.isEmpty())return false;
            var tag=gift.tag();if(!tag.isEmpty())stack.setTag(tag);
            var inventory=new PlayerMainInvWrapper(player.getInventory());
            if(!ItemHandlerHelper.insertItemStacked(inventory,stack.copy(),true).isEmpty())return false;
            return ItemHandlerHelper.insertItemStacked(inventory,stack,false).isEmpty();
        });
        boolean pending=data.pending(player.getUUID());
        if(!pending)PENDING.remove(player.getUUID());
        if(count>0){
            player.getInventory().setChanged();player.inventoryMenu.broadcastChanges();
            player.displayClientMessage(Component.translatable(pending?"hk3gtl.gift.herrscher_void.partial":"hk3gtl.gift.herrscher_void.received",count),true);
        }else if(login&&pending)player.displayClientMessage(Component.translatable("hk3gtl.gift.herrscher_void.pending"),true);
    }
    private static void failed(ServerPlayer player,RuntimeException failure){
        PENDING.remove(player.getUUID());LOGGER.error("[HK3GTL] 专属礼物本次发放停止，保留账本且不阻断登录：{}",player.getUUID(),failure);
    }
    @SubscribeEvent public static void tick(TickEvent.PlayerTickEvent event){
        if(event.phase!=TickEvent.Phase.END||!(event.player instanceof ServerPlayer player)||player.tickCount%100!=0||!PENDING.contains(player.getUUID())||!player.isAlive())return;
        try{attempt(player,Hk3VoidGiftData.get(player.server),false);}catch(RuntimeException failure){failed(player,failure);}
    }
    @SubscribeEvent public static void logout(PlayerEvent.PlayerLoggedOutEvent event){PENDING.remove(event.getEntity().getUUID());}
    @SubscribeEvent public static void stop(ServerStoppedEvent event){PENDING.clear();}
}
