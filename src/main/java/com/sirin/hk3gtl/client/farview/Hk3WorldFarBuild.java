package com.sirin.hk3gtl.client.farview;

import com.sirin.hk3gtl.client.wonder.Hk3W03FieldScenes;
import com.sirin.hk3gtl.client.wonder.Hk3W08FieldScenes;
import com.sirin.hk3gtl.client.wonder.Hk3W10FieldScenes;
import com.sirin.hk3gtl.client.wonder.Hk3W12FieldScenes;
import com.sirin.hk3gtl.client.wonder.Hk3WonderFxScenes;
import com.sirin.hk3gtl.client.wonder.Hk3W11FieldScenes;
import com.sirin.hk3gtl.client.wonder.Hk3W13FieldScenes;
import com.sirin.hk3gtl.common.farview.Hk3WorldFarSurface;
import it.unimi.dsi.fastutil.ints.IntArrayList;
import it.unimi.dsi.fastutil.shorts.ShortArrayList;
import net.minecraft.core.BlockPos;
import net.minecraft.world.level.ChunkPos;
import net.minecraft.world.level.block.Block;

import java.util.HashMap;
import java.util.HashSet;
import java.util.Iterator;
import java.util.Map;
import java.util.Set;
import java.util.concurrent.CompletableFuture;

final class Hk3WorldFarBuild {
    final long key,revision;
    final int targetStride,maxStride,maxQuads;
    final Map<Integer,Hk3FarMaterials.Material> models=new HashMap<>();
    CompletableFuture<Hk3FarTileMesh.Shell> future;
    Hk3FarTileMesh.Upload upload;

    private final int originX,originZ;
    private final Iterator<Map.Entry<Long,Hk3WorldFarSurface>> sources;
    private final Map<Long,Hk3WorldFarSurface> chunks=new java.util.LinkedHashMap<>();
    private final Map<Integer,Integer> colors=new HashMap<>();
    private final Set<Integer> translucent=new HashSet<>();
    private final BlockPos.MutableBlockPos pos=new BlockPos.MutableBlockPos();
    private Hk3WorldFarSurface surface;
    private long chunkKey;
    private int stateIndex,column;
    private boolean mask,exact,filter;
    private int[] offsets;
    private ShortArrayList starts,ends;
    private IntArrayList states;

    Hk3WorldFarBuild(long key,long revision,int targetStride,int maxStride,int maxQuads,
                     Map<Long,Hk3WorldFarSurface> sources){
        this.key=key;this.revision=revision;
        this.targetStride=targetStride;this.maxStride=maxStride;this.maxQuads=maxQuads;
        originX=ChunkPos.getX(key)*64;originZ=ChunkPos.getZ(key)*64;
        this.sources=sources.entrySet().iterator();
    }

    boolean advance(Hk3FarMaterials materials,long deadline){
        if(future!=null)return future.isDone();
        while(surface!=null||sources.hasNext()){
            if(surface==null){
                var next=sources.next();chunkKey=next.getKey();surface=next.getValue();
                stateIndex=column=0;
                long columnKey=ChunkPos.asLong(ChunkPos.getX(chunkKey)>>2,ChunkPos.getZ(chunkKey)>>2);
                mask=Hk3FarViewRenderer.maskRequired(columnKey);exact=Hk3FarViewRenderer.exactRequired(columnKey);filter=mask;
            }
            while(stateIndex<surface.states().length){
                int state=surface.states()[stateIndex++];
                if(!colors.containsKey(state)){
                    var model=materials.surface(state);
                    models.put(state,model);
                    colors.put(state,model.cube()?(model.opaque()?state:-state):0);
                    if(model.translucent())translucent.add(state);
                    filter|=exact&&model.translucent();
                    if(System.nanoTime()>=deadline)return false;
                }
                filter|=exact&&translucent.contains(state);
                if((stateIndex&63)==0&&System.nanoTime()>=deadline)return false;
            }
            if(!filter){chunks.put(chunkKey,surface);surface=null;}
            else{
                if(offsets==null){
                    offsets=new int[257];starts=new ShortArrayList();ends=new ShortArrayList();states=new IntArrayList();
                }
                int chunkX=ChunkPos.getX(chunkKey)*16,chunkZ=ChunkPos.getZ(chunkKey)*16;
                while(column<256){
                    offsets[column]=states.size();int x=chunkX+column/16,z=chunkZ+column%16;
                    for(int run=surface.offsets()[column];run<surface.offsets()[column+1];run++){
                        int state=surface.states()[run],low=surface.starts()[run],high=surface.ends()[run],start=low;
                        boolean blend=exact&&translucent.contains(state);var block=mask?Block.stateById(state-1):null;
                        if(mask||blend)for(int y=low;y<high;y++){
                            if(!(mask&&(Hk3W03FieldScenes.hidden(pos.set(x,y,z),block)||Hk3W08FieldScenes.hidden(pos,block)||Hk3W10FieldScenes.hidden(pos,block)||Hk3W12FieldScenes.hidden(pos,block)||Hk3W11FieldScenes.hidden(pos,block)||Hk3W13FieldScenes.hidden(pos,block)||Hk3WonderFxScenes.hidden(pos,block)))
                                    &&!(blend&&Hk3FarViewRenderer.exactReady(x,y,z,state)))continue;
                            if(start<y){starts.add((short)start);ends.add((short)y);states.add(state);}start=y+1;
                        }
                        if(start<high){starts.add((short)start);ends.add((short)high);states.add(state);}
                    }
                    column++;
                    // 按列让出时间片，单次模型读取或整列过滤仍可能超过目标时长。
                    if(System.nanoTime()>=deadline)return false;
                }
                offsets[256]=states.size();
                chunks.put(chunkKey,new Hk3WorldFarSurface(offsets,starts.toShortArray(),ends.toShortArray(),states.toIntArray()));
                surface=null;offsets=null;starts=null;ends=null;states=null;
            }
            if(System.nanoTime()>=deadline)return false;
        }
        future=Hk3FarTileMesh.prepareShell(originX,originZ,chunks,colors,targetStride,maxStride,maxQuads);
        return future!=null&&future.isDone();
    }
    void cancel(){if(future!=null)future.cancel(false);if(upload!=null)upload.close();}
}
