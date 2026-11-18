package com.sirin.hk3gtl.common.review;
import com.sirin.hk3gtl.common.research.*;
import net.minecraft.server.level.ServerPlayer;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.event.entity.player.PlayerEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
@Mod.EventBusSubscriber(modid="hk3gtl")
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

