package com.sirin.hk3gtl.common.farview;

import com.sirin.hk3gtl.common.network.Hk3Network;
import com.sirin.hk3gtl.mixin.Hk3WorldFarChunkMapAccess;
import net.minecraft.Util;
import net.minecraft.resources.ResourceKey;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.level.ChunkPos;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.chunk.ChunkStatus;
import net.minecraftforge.network.PacketDistributor;

import java.util.ArrayDeque;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.Iterator;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.UUID;
import java.util.concurrent.CompletableFuture;
import java.util.concurrent.CompletionException;

/** 只读已生成区块的竖向剖面，不建立区块票据、不运行地形生成。 */
public final class Hk3WorldFarSurfaceService {
    private static final int MAX_IO=2,MAX_CACHE=4096,MAX_BYTES=64*1024*1024,MAX_SENT=2048,MAX_ENTRIES=4,MAX_CHECKS=128;
    private static final long BUDGET_NANOS=500_000L;
    private record Key(ResourceKey<Level> dimension,long chunk){}
    private record Cached(Optional<Hk3WorldFarSurface> surface,long version,long expires){
        int bytes(){return 96+surface.map(Hk3WorldFarSurface::bytes).orElse(0);}
    }
    private record Read(CompletableFuture<Optional<Hk3WorldFarSurface>> future,int lifetime){}
    private record Delivery(long version,long tick){}
    private static final class Watch {
        final ServerLevel level;final long session;
        int distance,centerX,centerZ,ring,index;long waitUntil;
        Long candidate;
        long sendingChunk;
        Cached sending;
        int firstColumn;
        boolean nearTurn=true;
        final ArrayDeque<Long> nearby=new ArrayDeque<>(289);
        final ArrayDeque<Key> pending=new ArrayDeque<>();
        final LinkedHashMap<Long,Delivery> delivered=new LinkedHashMap<>(16,.75f,true);
        Watch(ServerPlayer player,int distance,long session){
            level=player.serverLevel();this.session=session;this.distance=distance;
            centerX=player.chunkPosition().x;centerZ=player.chunkPosition().z;
        }
        void reset(int x,int z){centerX=x;centerZ=z;ring=index=0;waitUntil=0;candidate=null;nearby.clear();nearTurn=true;pending.clear();sending=null;}
        void move(int x,int z){
            long dx=(long)x-centerX,dz=(long)z-centerZ;
            if((dx*dx+dz*dz)*1024>(long)distance*distance){reset(x,z);return;}
            centerX=x;centerZ=z;candidate=null;waitUntil=0;
            nearby.clear();nearTurn=true;nearby.addLast(chunkAt(0,0));
            for(int r=1;r<=8;r++)for(int i=0;i<8*r;i++)nearby.addLast(chunkAt(r,i));
        }
        Long next(long tick){
            if(candidate!=null)return candidate;
            int radius=(distance+15)/16;
            boolean farReady=tick>=waitUntil;
            if(farReady&&ring>radius){ring=index=0;waitUntil=tick+600;farReady=false;}
            if(!nearby.isEmpty()&&(nearTurn||!farReady)){
                nearTurn=false;candidate=nearby.removeFirst();return candidate;
            }
            if(!farReady)return null;
            nearTurn=true;candidate=chunkAt(ring,index);
            if(ring==0)ring=1;
            else if(++index==8*ring){ring++;index=0;}
            return candidate;
        }
        private long chunkAt(int ring,int index){
            int x=0,z=0;
            if(ring>0){
                int side=index/(2*ring),at=index%(2*ring);
                switch(side){
                    case 0->{x=-ring+at;z=-ring;}
                    case 1->{x=ring;z=-ring+at;}
                    case 2->{x=ring-at;z=ring;}
                    default->{x=-ring;z=ring-at;}
                }
            }
            return ChunkPos.asLong(centerX+x,centerZ+z);
        }
        boolean contains(long chunk){
            long x=(long)ChunkPos.getX(chunk)-centerX,z=(long)ChunkPos.getZ(chunk)-centerZ;
            return (x*x+z*z)*256<=(long)(distance+16)*(distance+16);
        }
    }
    private static final Map<UUID,Watch> WATCHES=new LinkedHashMap<>();
    private static final LinkedHashMap<Key,Cached> CACHE=new LinkedHashMap<>(16,.75f,true);
    private static final Map<Key,Read> READING=new HashMap<>();
    // 取消派生future不会终止原版磁盘读取；退休任务完成前继续占用并发名额。
    private static final List<CompletableFuture<Optional<Hk3WorldFarSurface>>> DRAINING=new ArrayList<>();
    private static int turn,cacheBytes;
    private static long version;
    private static boolean failureLogged;

    private Hk3WorldFarSurfaceService(){}
    public static void request(ServerPlayer player,boolean enabled,int distance,long session){
        UUID id=player.getUUID();
        if(!enabled){WATCHES.remove(id);return;}
        distance=Math.max(256,Math.min(4096,distance));
        var watch=WATCHES.get(id);
        if(watch==null||watch.session!=session||watch.level!=player.serverLevel())WATCHES.put(id,new Watch(player,distance,session));
        else if(watch.distance!=distance){watch.distance=distance;watch.reset(player.chunkPosition().x,player.chunkPosition().z);}
    }
    public static void remove(UUID player){WATCHES.remove(player);}
    public static void unload(ServerLevel level){
        WATCHES.values().removeIf(watch->watch.level==level);
        CACHE.entrySet().removeIf(entry->{
            if(!entry.getKey().dimension.equals(level.dimension()))return false;
            cacheBytes-=entry.getValue().bytes();return true;
        });
        var iterator=READING.entrySet().iterator();
        while(iterator.hasNext()){
            var entry=iterator.next();
            if(entry.getKey().dimension.equals(level.dimension())){DRAINING.add(entry.getValue().future);iterator.remove();}
        }
    }
    public static void clear(){
        WATCHES.clear();CACHE.clear();READING.values().forEach(read->DRAINING.add(read.future));READING.clear();turn=cacheBytes=0;version=0;failureLogged=false;
    }
    public static void tick(MinecraftServer server){
        long deadline=System.nanoTime()+BUDGET_NANOS;
        long tick=server.getTickCount();
        finishReads(tick);
        WATCHES.entrySet().removeIf(entry->{var player=server.getPlayerList().getPlayer(entry.getKey());return player==null||player.serverLevel()!=entry.getValue().level;});
        if(WATCHES.isEmpty())return;
        var watches=new ArrayList<>(WATCHES.entrySet());int entriesLeft=MAX_ENTRIES,checksLeft=MAX_CHECKS;
        int bytesLeft=Hk3WorldFarSurfacePacket.MAX_PACKET_BYTES;
        for(int n=0;n<watches.size()&&entriesLeft>0&&checksLeft>0&&System.nanoTime()<deadline;n++){
            var entry=watches.get((turn+n)%watches.size());var watch=entry.getValue();
            var player=server.getPlayerList().getPlayer(entry.getKey());var pos=player.chunkPosition();
            if(pos.x!=watch.centerX||pos.z!=watch.centerZ)watch.move(pos.x,pos.z);
            List<Hk3WorldFarSurfacePacket.Entry> updates=new ArrayList<>();
            int budget=bytesLeft-Hk3WorldFarSurfacePacket.HEADER_BYTES;
            if(watch.sending!=null&&!watch.contains(watch.sendingChunk))watch.sending=null;
            budget-=append(watch,updates,budget);
            for(Iterator<Key> iterator=watch.pending.iterator();watch.sending==null&&iterator.hasNext()&&updates.size()<entriesLeft&&System.nanoTime()<deadline;){
                var key=iterator.next();var cached=CACHE.get(key);
                if(cached!=null&&cached.expires>tick){
                    offer(watch,key.chunk,cached);budget-=append(watch,updates,budget);iterator.remove();
                }
                else if(!READING.containsKey(key))iterator.remove();
            }
            while(watch.sending==null&&updates.size()<entriesLeft&&checksLeft-->0&&watch.pending.size()<MAX_IO&&System.nanoTime()<deadline){
                Long chunk=watch.next(tick);if(chunk==null)break;
                if(!watch.contains(chunk)){watch.candidate=null;continue;}
                var key=new Key(watch.level.dimension(),chunk);var cached=CACHE.get(key);
                if(cached!=null&&cached.expires>tick){
                    offer(watch,chunk,cached);budget-=append(watch,updates,budget);watch.candidate=null;continue;
                }
                if(!READING.containsKey(key)){
                    if(READING.size()+DRAINING.size()>=MAX_IO)break;
                    var loaded=watch.level.getChunkSource().getChunkNow(ChunkPos.getX(chunk),ChunkPos.getZ(chunk));
                    if(loaded!=null){
                        READING.put(key,new Read(Hk3WorldFarSurface.captureAsync(loaded).thenApply(Optional::of),200));
                    }else{
                        int min=watch.level.getMinBuildHeight(),height=watch.level.getHeight();
                        var storage=(Hk3WorldFarChunkMapAccess)(Object)watch.level.getChunkSource().chunkMap;
                        READING.put(key,new Read(storage.hk3gtl$readChunk(new ChunkPos(chunk)).thenApplyAsync(tag->tag
                                .filter(nbt->ChunkStatus.byName(nbt.getString("Status"))==ChunkStatus.FULL)
                                .map(nbt->Hk3WorldFarSurface.read(nbt,min,height)),Util.backgroundExecutor()),600));
                    }
                }
                watch.pending.addLast(key);watch.candidate=null;
            }
            if(!updates.isEmpty()){
                Hk3Network.CHANNEL.send(PacketDistributor.PLAYER.with(()->player),
                        new Hk3WorldFarSurfacePacket(watch.level.dimension().location(),watch.session,List.copyOf(updates)));
                entriesLeft-=updates.size();
                bytesLeft=budget;
            }
        }
        turn=(turn+1)%watches.size();
    }
    private static Cached cache(Key key,Optional<Hk3WorldFarSurface> surface,long expires){
        var previous=CACHE.get(key);
        boolean unchanged=previous!=null&&previous.surface.isPresent()==surface.isPresent()
                &&(surface.isEmpty()||previous.surface.get().same(surface.get()));
        var cached=new Cached(unchanged?previous.surface:surface,unchanged?previous.version:++version,expires);CACHE.put(key,cached);
        if(previous!=null)cacheBytes-=previous.bytes();
        cacheBytes+=cached.bytes();
        while(CACHE.size()>MAX_CACHE||cacheBytes>MAX_BYTES){
            var iterator=CACHE.entrySet().iterator();cacheBytes-=iterator.next().getValue().bytes();iterator.remove();
        }
        return cached;
    }
    private static void offer(Watch watch,long chunk,Cached cached){
        if(cached.surface.isEmpty()||!watch.contains(chunk))return;
        var delivered=watch.delivered.get(chunk);
        // 客户端可按内存预算逐出表面，低频重发允许恢复已逐出的同版本数据。
        if(delivered!=null&&delivered.version==cached.version&&watch.level.getServer().getTickCount()-delivered.tick<600)return;
        watch.sending=cached;watch.sendingChunk=chunk;watch.firstColumn=0;
    }
    private static int append(Watch watch,List<Hk3WorldFarSurfacePacket.Entry> updates,int budget){
        if(watch.sending==null)return 0;
        var surface=watch.sending.surface.orElseThrow();
        int columns=Hk3WorldFarSurfacePacket.columns(surface,watch.firstColumn,budget+Hk3WorldFarSurfacePacket.HEADER_BYTES);
        if(columns==0)return 0;
        int bytes=Hk3WorldFarSurfacePacket.bytes(surface,watch.firstColumn,columns);
        updates.add(new Hk3WorldFarSurfacePacket.Entry(watch.sendingChunk,watch.firstColumn,columns,surface));
        watch.firstColumn+=columns;
        if(watch.firstColumn==256){
            watch.delivered.put(watch.sendingChunk,new Delivery(watch.sending.version,watch.level.getServer().getTickCount()));watch.sending=null;
            while(watch.delivered.size()>MAX_SENT)watch.delivered.remove(watch.delivered.keySet().iterator().next());
        }
        return bytes;
    }
    private static void finishReads(long tick){
        DRAINING.removeIf(CompletableFuture::isDone);
        var iterator=READING.entrySet().iterator();
        while(iterator.hasNext()){
            var entry=iterator.next();var read=entry.getValue();var future=read.future;if(!future.isDone())continue;
            try{cache(entry.getKey(),future.join(),tick+read.lifetime);}
            catch(CompletionException failure){
                cache(entry.getKey(),Optional.empty(),tick+1200);
                if(!failureLogged){failureLogged=true;com.mojang.logging.LogUtils.getLogger().warn("HK3GTL远景无法读取已生成区块；该区块延后重试",failure.getCause());}
            }
            iterator.remove();
        }
    }
}
