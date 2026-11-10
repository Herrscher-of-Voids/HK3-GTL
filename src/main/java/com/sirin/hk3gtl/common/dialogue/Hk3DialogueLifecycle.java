package com.sirin.hk3gtl.common.dialogue;

import com.sirin.hk3gtl.common.network.ResearchStateSyncRequestC2SPacket;
import com.sirin.hk3gtl.common.review.Hk3ReviewData;
import net.minecraft.server.level.ServerPlayer;
import net.minecraftforge.event.entity.player.PlayerEvent;
import net.minecraftforge.event.server.ServerStoppedEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;

/**
 * 【变更记录 #1】2026-10-01 17:04:49（修订136）
 * 删除：无；新增：死亡/末地返回实体重建、维度变化及服务器停止的临时会话清理。
 * 修改：仅暂停审查与对话，不清研究、信件、本人经历或终审资格快照；用途：重生后可重新交互，不遗留跨存档会话。
 */
@Mod.EventBusSubscriber(modid="hk3gtl")
public final class Hk3DialogueLifecycle {
    private Hk3DialogueLifecycle(){}
    private static void transition(ServerPlayer player,boolean leaveReview){
        DialogueSessionManager.pauseForTransition(player);
        if(leaveReview)Hk3ReviewData.get(player.server).change(ledger->{ledger.depart(player.getUUID());return null;});
        ResearchStateSyncRequestC2SPacket.clearRateLimit(player.getUUID());
    }
    @SubscribeEvent public static void clonePlayer(PlayerEvent.Clone event){
        if(event.getEntity() instanceof ServerPlayer p)transition(p,true);
    }
    @SubscribeEvent public static void changedDimension(PlayerEvent.PlayerChangedDimensionEvent event){
        // 剧情召入自身也会换维度，不能在这里一律退出团队审查；由正式场景管理参与者。
        if(event.getEntity() instanceof ServerPlayer p)transition(p,false);
    }
    @SubscribeEvent public static void stopped(ServerStoppedEvent event){
        DialogueSessionManager.clearForServerStop();ResearchStateSyncRequestC2SPacket.clearForServerStop();
    }
}
