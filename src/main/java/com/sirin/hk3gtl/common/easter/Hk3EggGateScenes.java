package com.sirin.hk3gtl.common.easter;

import com.sirin.hk3gtl.common.compat.stargate.Hk3StargateApi;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.stats.Stats;
import net.minecraft.world.phys.Vec3;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.event.entity.player.PlayerEvent;
import net.minecraftforge.event.server.ServerStoppedEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import net.povstalec.sgjourney.common.block_entities.stargate.AbstractStargateEntity;
import net.povstalec.sgjourney.common.data.StargateNetwork;
import net.povstalec.sgjourney.common.init.StatisticsInit;
import net.povstalec.sgjourney.common.sgjourney.stargate.Stargate;

import java.util.Map;
import java.util.UUID;
import java.util.concurrent.ConcurrentHashMap;

@Mod.EventBusSubscriber(modid="hk3gtl")
public final class Hk3EggGateScenes {
    private static final class Walk {
        AbstractStargateEntity gate;Stargate registered;UUID connection;Vec3 previous;
        long tick;int travels,end,crossings;
    }
    private static final Map<UUID,Walk> WALKS=new ConcurrentHashMap<>();
    private Hk3EggGateScenes(){}
    private static int travels(ServerPlayer p){return p.getStats().getValue(Stats.CUSTOM.get(StatisticsInit.TIMES_USED_WORMHOLE.get()));}
    private static double depth(ServerPlayer p,Stargate gate){
        var offset=p.position().subtract(Hk3StargateApi.position(p.server, gate));
        if(Math.abs(offset.dot(Hk3StargateApi.right(p.server, gate)))>.75
                ||Math.abs(offset.dot(Hk3StargateApi.up(p.server, gate)))>gate.getInnerRadius())return -1;
        return offset.dot(Hk3StargateApi.forward(p.server, gate));
    }
    private static Walk find(ServerPlayer p){
        var pos=p.blockPosition();var level=p.serverLevel();var network=StargateNetwork.get(level);
        for(int x=(pos.getX()-8)>>4;x<=(pos.getX()+8)>>4;x++)
            for(int z=(pos.getZ()-8)>>4;z<=(pos.getZ()+8)>>4;z++){
                if(!level.hasChunk(x,z))continue;
                for(var be:level.getChunk(x,z).getBlockEntities().values()){
                    if(!(be instanceof AbstractStargateEntity gate)||!gate.getConnectionState().isConnected()
                            ||Hk3StargateApi.openTime(network, gate.getConnectionID())<=0)continue;
                    var registered=network.getStargate(gate.get9ChevronAddress());
                    if(registered==null)continue;
                    double depth=depth(p,registered);if(depth<.75||depth>3.25)continue;
                    var walk=new Walk();walk.gate=gate;walk.registered=registered;walk.connection=gate.getConnectionID();
                    walk.previous=p.position();walk.tick=p.server.overworld().getGameTime();walk.travels=travels(p);
                    return walk;
                }
            }
        return null;
    }
    @SubscribeEvent public static void tick(TickEvent.PlayerTickEvent e){
        if(e.phase!=TickEvent.Phase.END||!(e.player instanceof ServerPlayer p)
                ||com.sirin.hk3gtl.common.narrative.Hk3NarrativeLog.isUnlocked(p,"E-EG-082"))return;
        var walk=WALKS.get(p.getUUID());
        if(walk==null){
            if(p.tickCount%20==0){walk=find(p);if(walk!=null)WALKS.put(p.getUUID(),walk);}
            return;
        }
        long now=p.server.overworld().getGameTime();var gate=walk.gate;var network=StargateNetwork.get(p.serverLevel());
        if(gate.getLevel()!=p.level()||!p.level().hasChunkAt(gate.getBlockPos())
                ||p.level().getBlockEntity(gate.getBlockPos())!=gate||!gate.getConnectionState().isConnected()
                ||!walk.connection.equals(gate.getConnectionID())||Hk3StargateApi.openTime(network, walk.connection)<=0
                ||travels(p)!=walk.travels||walk.tick!=now-1||p.position().distanceToSqr(walk.previous)>=2.25
                ||!p.onGround()||p.getAbilities().flying||p.isPassenger()){
            WALKS.remove(p.getUUID());return;
        }
        double depth=depth(p,walk.registered);
        if(depth<.75||depth>3.25){WALKS.remove(p.getUUID());return;}
        int end=depth<=1.05?1:depth>=2.95?2:0;
        if(end!=0&&end!=walk.end){if(walk.end!=0)walk.crossings++;walk.end=end;}
        if(walk.crossings>=6){
            Hk3EggRuntime.observe(p,"open_gate_hesitation",Map.of("round_trips","3","teleported","false"));
            WALKS.remove(p.getUUID());return;
        }
        walk.previous=p.position();walk.tick=now;
    }
    @SubscribeEvent public static void logout(PlayerEvent.PlayerLoggedOutEvent e){WALKS.remove(e.getEntity().getUUID());}
    @SubscribeEvent public static void stopped(ServerStoppedEvent e){WALKS.entrySet().removeIf(v->v.getValue().gate.getLevel().getServer()==e.getServer());}
}
