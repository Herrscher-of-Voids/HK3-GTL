package com.sirin.hk3gtl.client.farview;

import com.sirin.hk3gtl.common.farview.Hk3FarViewConfig;
import net.minecraft.client.Minecraft;
import net.minecraft.client.multiplayer.ClientLevel;
import net.minecraft.core.BlockPos;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.chunk.LevelChunk;
import net.minecraft.world.level.chunk.LevelChunkSection;
import java.lang.ref.WeakReference;
import java.util.*;

/** 只消费客户端已收到的区块；卸载保留完整快照，不读磁盘、不请求或模拟远区块。 */
public final class Hk3WorldFarCapture {
    private static final int MAX_CHUNKS=1024,MAX_PENDING=512,MAX_CELLS=4096;
    private static final long BUDGET_NANOS=500_000L;
    private static final Hk3WorldFarCache CACHE=new Hk3WorldFarCache(Hk3WorldFarCache.MAX_BYTES/2,Hk3WorldFarCache.MAX_SECTIONS);
    private static final Hk3WorldFarSampler SAMPLER=new Hk3WorldFarSampler(MAX_PENDING);
    private static final LinkedHashMap<Long,WeakReference<LevelChunk>> LOADED=new LinkedHashMap<>();
    private static boolean enabled;
    private static final class ChunkSource implements Hk3WorldFarSampler.Source {
        private final WeakReference<LevelChunk> owner;
        private final long key;
        private final int sections;
        private LevelChunkSection sampled;
        ChunkSource(LevelChunk chunk){owner=new WeakReference<>(chunk);key=chunk.getPos().toLong();sections=chunk.getSections().length;}
        @Override public boolean valid(){
            var loaded=LOADED.get(key);var chunk=owner.get();
            return chunk!=null&&loaded!=null&&loaded.get()==chunk&&chunk.getLevel()==Minecraft.getInstance().level;
        }
        @Override public int sections(){return sections;}
        @Override public boolean empty(int section){sampled=owner.get().getSections()[section];return sampled.hasOnlyAir();}
        @Override public int state(int section,int index){
            var state=sampled.getBlockState(index/256,index/16%16,index%16);
            return state.isAir()?0:Block.getId(state)+1;
        }
        @Override public void publish(int section,Hk3WorldFarCache.Packed snapshot){
            var chunk=owner.get();long tile=BlockPos.asLong(chunk.getPos().x,chunk.getSectionYFromSectionIndex(section),chunk.getPos().z);
            if(snapshot.same(CACHE.get(tile)))return;
            CACHE.put(tile,snapshot,Hk3FarViewRenderer::removeWorld);
            if(CACHE.get(tile)!=null)Hk3FarViewRenderer.world(tile,snapshot);
        }
    }
    private Hk3WorldFarCapture(){}
    static boolean knownAir(long key){var snapshot=CACHE.get(key);return snapshot!=null&&snapshot.empty();}
    public static void received(ClientLevel level,LevelChunk chunk){
        if(chunk==null||Minecraft.getInstance().level!=level)return;
        Hk3FarViewRenderer.useLevel(level);
        long key=chunk.getPos().toLong();LOADED.remove(key);LOADED.put(key,new WeakReference<>(chunk));
        while(LOADED.size()>MAX_CHUNKS){long oldest=LOADED.keySet().iterator().next();LOADED.remove(oldest);SAMPLER.remove(oldest);}
        if(Hk3FarViewConfig.ENABLED.get()){
            Hk3WorldFarTerrain.received(chunk);
            SAMPLER.add(key,new ChunkSource(chunk));
        }
    }
    public static void changed(ClientLevel level,BlockPos pos){
        if(!Hk3FarViewConfig.ENABLED.get()||Minecraft.getInstance().level!=level)return;
        Hk3FarViewRenderer.useLevel(level);
        long key=net.minecraft.world.level.ChunkPos.asLong(pos.getX()>>4,pos.getZ()>>4);
        var reference=LOADED.get(key);var chunk=reference==null?null:reference.get();if(chunk==null)return;
        Hk3WorldFarTerrain.received(chunk);
        SAMPLER.changed(key,chunk.getSectionIndex(pos.getY()),new ChunkSource(chunk));
    }
    public static void unloaded(ClientLevel level,LevelChunk chunk){
        if(Minecraft.getInstance().level!=level)return;
        long key=chunk.getPos().toLong();
        if(Hk3FarViewConfig.ENABLED.get())Hk3WorldFarTerrain.unloaded(chunk);
        LOADED.remove(key);SAMPLER.remove(key);
        // 只取消未完成采样，不能删除已经交付的同一区块其他分区。
    }
    public static void tick(){
        boolean now=Hk3FarViewConfig.ENABLED.get();
        if(now!=enabled){
            enabled=now;
            if(!now){SAMPLER.clear();CACHE.clear();Hk3WorldFarTerrain.clear();Hk3FarViewRenderer.clearWorld();return;}
            for(var entry:LOADED.entrySet()){var chunk=entry.getValue().get();if(chunk!=null){Hk3WorldFarTerrain.received(chunk);SAMPLER.add(entry.getKey(),new ChunkSource(chunk));}}
        }
        if(now){
            long deadline=System.nanoTime()+BUDGET_NANOS;
            Hk3WorldFarTerrain.tick(deadline);
            SAMPLER.tick(deadline,MAX_CELLS,8,System::nanoTime);
        }
    }
    public static int sections(){return CACHE.size();}
    public static int bytes(){return CACHE.bytes()+Hk3WorldFarTerrain.bytes();}
    public static int pending(){return SAMPLER.pending();}
    public static void clear(){CACHE.clear();Hk3WorldFarTerrain.clear();LOADED.clear();SAMPLER.clear();enabled=false;}
}
