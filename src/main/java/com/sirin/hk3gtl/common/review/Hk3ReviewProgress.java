package com.sirin.hk3gtl.common.review;
import com.sirin.hk3gtl.common.research.*;
import net.minecraft.server.level.ServerPlayer;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.event.entity.player.PlayerEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
/** 【变更记录 #1】2026-09-30 20:31:18（修订117）：删除无；新增已结算审查到研究许可、手机阶段的幂等同步；修改无；用途：只读取实际会面回执，不将预览、旧研究或聊天当作通过，不免费完成课题。 */
@Mod.EventBusSubscriber(modid="hk3gtl")
/** 【变更记录 #2】2026-10-01 01:28:10（修订125）：删除每个玩家重复扫描团队的入口；新增每100tick按在线团队去重采集真实资格；修改已有会面许可继续逐人同步；用途：补齐研究到准入的生产桥，不自动结算会面。 */
public final class Hk3ReviewProgress {
    private Hk3ReviewProgress(){}
    public static void sync(ServerPlayer p){
        var scope=Hk3ResearchTeams.scope(p.server,p.getUUID());var review=Hk3ReviewData.get(p.server);var research=Hk3ResearchData.get(p.server);
        for(var kind:Hk3ReviewLedger.Kind.values()){
            var receipt=review.settlement(scope,kind);if(receipt!=null)research.recordReviewPermission(scope,kind==Hk3ReviewLedger.Kind.FIRST?1:2,receipt);
            if(review.experienced(p.getUUID(),kind))com.sirin.hk3gtl.common.phone.Hk3SocialService.reviewCompleted(p,kind==Hk3ReviewLedger.Kind.FIRST?2:3);
        }
    }
    @SubscribeEvent public static void tick(TickEvent.ServerTickEvent e){
        if(e.phase!=TickEvent.Phase.END)return;
        var server=net.minecraftforge.server.ServerLifecycleHooks.getCurrentServer();
        if(server==null||server.getTickCount()%100!=0)return;
        var teams=new java.util.HashSet<java.util.UUID>();
        for(var p:server.getPlayerList().getPlayers()){
            var scope=Hk3ResearchTeams.scope(server,p.getUUID());
            if(teams.add(scope))Hk3ReviewQualification.refresh(server,scope);
            sync(p);
        }
    }
    @SubscribeEvent public static void logout(PlayerEvent.PlayerLoggedOutEvent e){if(e.getEntity() instanceof ServerPlayer p)Hk3ReviewData.get(p.server).change(ledger->{ledger.depart(p.getUUID());return null;});}
}

// 【变更记录 · 修订161】2026-10-17 14:11:55：本轮仅将活动类名、资源与工业配方引用迁移为长期业务命名；历史备注保留，不代表旧逻辑已全部按现行设计重写。
