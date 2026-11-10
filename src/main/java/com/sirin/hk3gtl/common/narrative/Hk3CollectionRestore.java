package com.sirin.hk3gtl.common.narrative;

import net.minecraft.server.level.ServerPlayer;
import net.minecraft.network.chat.Component;
import net.minecraftforge.event.entity.player.PlayerEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;

/** 【变更记录 #1】2026-10-01 01:54:14（修订127）：删除无；新增旧收藏静默补入本人收件箱；修改无；用途：登录只读取已有解锁，不从团队或通知反向解锁，不重放弹窗或奖励。 */
@Mod.EventBusSubscriber(modid="hk3gtl")
public final class Hk3CollectionRestore {
    private Hk3CollectionRestore(){}
    @SubscribeEvent public static void login(PlayerEvent.PlayerLoggedInEvent event){
        if(!(event.getEntity() instanceof ServerPlayer player))return;
        var state=player.getPersistentData();var inbox=com.sirin.hk3gtl.common.phone.Hk3PhoneData.get(player);
        for(var node:Hk3CollectionRecords.unlocked(state,"all"))
            if(inbox.entry(player.getUUID(),"narrative_"+node.id())==null)
                Hk3CollectionRecords.record(state,inbox,player.getUUID(),node,System.currentTimeMillis(),k->Component.translatable(k).getString());
    }
}
