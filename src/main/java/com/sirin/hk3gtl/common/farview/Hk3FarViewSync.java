package com.sirin.hk3gtl.common.farview;

import com.sirin.hk3gtl.common.network.Hk3Network;
import net.minecraft.core.BlockPos;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.event.entity.player.PlayerEvent;
import net.minecraftforge.event.level.LevelEvent;
import net.minecraftforge.event.server.ServerStoppedEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import net.minecraftforge.network.PacketDistributor;
import java.util.*;

@Mod.EventBusSubscriber(modid="hk3gtl")
public final class Hk3FarViewSync {
    private static final Map<UUID,Watch> WATCHES=new HashMap<>();
    private static final class Watch {
        ServerLevel level;int distance=2048,cursor,remaining,sectionX,sectionY,sectionZ;
        long requestAt=Long.MIN_VALUE,session,revision=-1,membershipRevision=-1;
        List<Long> selected=List.of();Set<Long> members=Set.of();Map<Long,Long> versions=new HashMap<>();
        boolean membershipPending=true,selectionPending=true;
    }
    private Hk3FarViewSync() {}
    public static void request(ServerPlayer player,boolean enabled,int distance,long session) {
        if(!enabled){WATCHES.remove(player.getUUID());Hk3WorldFarSurfaceService.remove(player.getUUID());return;}
        var old=WATCHES.get(player.getUUID());long tick=player.server.getTickCount();
        if(old!=null&&tick-old.requestAt<20)return;
        var watch=WATCHES.computeIfAbsent(player.getUUID(),u->new Watch());watch.requestAt=tick;
        if(watch.session!=session){watch.session=session;watch.versions.clear();watch.members=Set.of();watch.membershipPending=true;watch.selectionPending=true;}
        if(watch.distance!=distance)watch.selectionPending=true;
        watch.distance=Math.max(256,Math.min(4096,distance));
        Hk3WorldFarSurfaceService.request(player,true,watch.distance,session);
    }
    @SubscribeEvent public static void load(LevelEvent.Load event){if(event.getLevel() instanceof ServerLevel level)Hk3FarViewData.get(level);}
    @SubscribeEvent public static void unload(LevelEvent.Unload event){if(event.getLevel() instanceof ServerLevel level){Hk3FarViewCapture.unload(level);Hk3WorldFarSurfaceService.unload(level);}}
    @SubscribeEvent public static void logout(PlayerEvent.PlayerLoggedOutEvent event){WATCHES.remove(event.getEntity().getUUID());Hk3WorldFarSurfaceService.remove(event.getEntity().getUUID());}
    @SubscribeEvent public static void stop(ServerStoppedEvent event){Hk3FarViewCapture.stop(event.getServer());WATCHES.clear();Hk3FarViewData.clear();Hk3WorldFarSurfaceService.clear();}
    @SubscribeEvent public static void serverTick(TickEvent.ServerTickEvent event){if(event.phase==TickEvent.Phase.END){Hk3FarViewCapture.tick(event.getServer());Hk3WorldFarSurfaceService.tick(event.getServer());}}
    @SubscribeEvent public static void worldTick(TickEvent.LevelTickEvent event) {
        if(event.phase!=TickEvent.Phase.END||!(event.level instanceof ServerLevel level))return;
        var data=Hk3FarViewData.get(level);
        data.refresh(level);
        if(level.getServer().getTickCount()%2!=0)return;
        for(var player:level.players()) {
            Watch watch=WATCHES.get(player.getUUID());if(watch==null)continue;
            if(watch.level!=level){watch.level=level;watch.versions.clear();watch.selected=List.of();watch.members=Set.of();watch.membershipPending=true;watch.selectionPending=true;watch.revision=-1;}
            var pos=player.blockPosition();
            if(watch.selectionPending||level.getServer().getTickCount()%20==0&&(watch.membershipRevision!=data.membershipRevision()
                    ||watch.sectionX!=pos.getX()>>4||watch.sectionY!=pos.getY()>>4||watch.sectionZ!=pos.getZ()>>4))select(data,player,watch);
            if(watch.revision!=data.revision()){watch.revision=data.revision();watch.remaining=watch.selected.size();}
            if(watch.remaining==0&&!watch.membershipPending)continue;
            List<Hk3FarViewPacket.Entry> updates=new ArrayList<>();
            for(int n=0;n<1024&&watch.remaining>0&&updates.size()<4;n++,watch.remaining--) {
                if(watch.cursor>=watch.selected.size())watch.cursor=0;
                long key=watch.selected.get(watch.cursor++);var tile=data.tiles.get(key);
                if(tile!=null&&!Objects.equals(watch.versions.get(key),tile.version)) {
                    updates.add(new Hk3FarViewPacket.Entry(key,tile.section.snapshot()));watch.versions.put(key,tile.version);
                }
            }
            if(!updates.isEmpty()||watch.membershipPending) {
                long[] members=watch.membershipPending?watch.selected.stream().mapToLong(Long::longValue).toArray():null;
                watch.membershipPending=false;
                Hk3Network.CHANNEL.send(PacketDistributor.PLAYER.with(()->player),
                        new Hk3FarViewPacket(level.dimension().location(),members,List.copyOf(updates)));
            }
        }
    }
    private static void select(Hk3FarViewData data,ServerPlayer player,Watch watch) {
        double distance=(double)(watch.distance+16)*(watch.distance+16);
        var selected=data.tiles.keySet().longStream().boxed().filter(k->distance(player,k)<=distance)
                .sorted(Comparator.comparingDouble(k->distance(player,k))).limit(Hk3FarViewData.MAX_TILES).toList();
        var membership=new HashSet<>(selected);
        if(!membership.equals(watch.members)){watch.membershipPending=true;watch.versions.keySet().retainAll(membership);watch.members=membership;}
        watch.selected=selected;watch.cursor=0;watch.remaining=selected.size();watch.selectionPending=false;
        var pos=player.blockPosition();watch.sectionX=pos.getX()>>4;watch.sectionY=pos.getY()>>4;watch.sectionZ=pos.getZ()>>4;
        watch.membershipRevision=data.membershipRevision();
    }
    private static double distance(ServerPlayer player,long key){return player.distanceToSqr(BlockPos.getX(key)*16+8,BlockPos.getY(key)*16+8,BlockPos.getZ(key)*16+8);}
}
