package com.sirin.hk3gtl.client.farview;

import com.sirin.hk3gtl.common.farview.Hk3WorldFarSurface;
import com.sirin.hk3gtl.common.farview.Hk3WorldFarSurfacePacket;
import net.minecraft.client.Minecraft;
import net.minecraft.client.multiplayer.ClientLevel;
import net.minecraft.client.renderer.culling.Frustum;
import net.minecraft.core.BlockPos;
import net.minecraft.world.level.ChunkPos;
import net.minecraft.world.level.chunk.LevelChunk;
import net.minecraft.world.phys.AABB;
import net.minecraft.world.phys.Vec3;

import java.lang.ref.WeakReference;
import java.util.*;
import java.util.concurrent.CompletableFuture;
import java.util.function.Supplier;

/** 多段剖面按距离和预算生成分级外壳，粗细区域保留逐格边界。 */
public final class Hk3WorldFarTerrain {
    private static final int CPU_LIMIT=32*1024*1024,MAX_CHUNKS=16384,PARTIAL_LIMIT=9*1024*1024;
    private static final class Region {
        final Set<Long> chunks=new HashSet<>();
        final AABB fullBounds;
        AABB bounds;
        Hk3FarTileMesh mesh;
        Hk3FarViewRenderer.Draw draw;
        long revision,built=-1,changedAt,dirtySince,capacity;
        int nonemptyChunks,centerY,targetStride=1,maxStride=16,maxQuads,builtTarget,builtQuads,meshStride=1,waitingBytes;
        boolean limited,visible,inRange,detail;
        Region(long key){
            int x=ChunkPos.getX(key)*64,z=ChunkPos.getZ(key)*64;var level=Minecraft.getInstance().level;
            bounds=fullBounds=new AABB(x,level.getMinBuildHeight(),z,x+64,level.getMaxBuildHeight(),z+64);
        }
        void dirty(){revision++;limited=false;bounds=fullBounds;changedAt=System.nanoTime();if(dirtySince==0)dirtySince=changedAt;}
        void close(){if(mesh!=null){gpuBytes-=mesh.bytes;mesh.close();mesh=null;draw=null;}}
    }
    private static final class Assembly {
        final List<Hk3WorldFarSurfacePacket.Entry> parts=new ArrayList<>();
        int columns,runs,bytes;
        void add(Hk3WorldFarSurfacePacket.Entry entry){
            parts.add(entry);columns+=entry.columnCount();runs+=entry.surface().states().length;bytes+=entry.surface().bytes();
        }
        Hk3WorldFarSurface finish(){
            int[] offsets=new int[257],states=new int[runs];short[] starts=new short[runs],ends=new short[runs];int at=0;
            for(var part:parts){
                var surface=part.surface();int count=surface.states().length;
                for(int column=part.firstColumn();column<part.firstColumn()+part.columnCount();column++)offsets[column]=at+surface.offsets()[column];
                System.arraycopy(surface.states(),0,states,at,count);
                System.arraycopy(surface.starts(),0,starts,at,count);System.arraycopy(surface.ends(),0,ends,at,count);at+=count;
            }
            offsets[256]=runs;return new Hk3WorldFarSurface(offsets,starts,ends,states);
        }
    }
    private record Capture(long key,ClientLevel level,CompletableFuture<Hk3WorldFarSurface> future){}
    private static final LinkedHashMap<Long,Hk3WorldFarSurface> SURFACES=new LinkedHashMap<>(16,.75f,true);
    private static final LinkedHashMap<Long,Assembly> ASSEMBLIES=new LinkedHashMap<>();
    private static final LinkedHashMap<Long,WeakReference<LevelChunk>> PENDING=new LinkedHashMap<>();
    private static final LinkedHashMap<Long,Supplier<Hk3WorldFarSurface>> RETIRED=new LinkedHashMap<>();
    private static final Map<Long,Region> REGIONS=new HashMap<>();
    private static final List<Map.Entry<Long,Region>> visible=new ArrayList<>();
    private static List<Map.Entry<Long,Region>> sorted=List.of();
    private static boolean resort=true,layoutDirty=true;
    private static int bytes,partialBytes,lastDistance=-1,lastNear=-1;
    private static long gpuBytes,lastPriority=Long.MIN_VALUE,lastBudget=-1;
    private static final Map<Long,Hk3WorldFarBuild> works=new LinkedHashMap<>();
    private static final Map<Long,Hk3WorldFarBuild> completed=new LinkedHashMap<>();
    private static Hk3WorldFarBuild uploading;
    private static final Map<Long,Capture> captures=new LinkedHashMap<>();

    private Hk3WorldFarTerrain(){}
    static int chunks(){return SURFACES.size();}
    static int bytes(){return bytes+partialBytes;}
    static long gpuBytes(){return gpuBytes;}
    static boolean empty(){return SURFACES.isEmpty();}
    static int stateAt(int x,int y,int z){
        var surface=SURFACES.get(ChunkPos.asLong(x>>4,z>>4));
        if(surface==null)return -1;
        int column=(x&15)*16+(z&15);
        for(int run=surface.offsets()[column];run<surface.offsets()[column+1];run++){
            if(y<surface.starts()[run])break;
            if(y<surface.ends()[run])return surface.states()[run];
        }
        return 0;
    }
    static long budget(long total){return total/2;}
    static void layoutChanged(){layoutDirty=true;}
    static boolean blendReady(int x,int z){
        long key=ChunkPos.asLong(x>>6,z>>6);var group=REGIONS.get(key);
        return group==null||group.mesh==null||group.built==group.revision||!Hk3FarViewRenderer.exactRequired(key);
    }
    private static long region(long chunk){return ChunkPos.asLong(ChunkPos.getX(chunk)>>2,ChunkPos.getZ(chunk)>>2);}
    private static void invalidate(long key){var group=REGIONS.get(key);if(group!=null)group.dirty();}
    private static void cancel(long key){
        var build=works.remove(key);if(build!=null)build.cancel();
        build=completed.remove(key);if(build!=null){build.cancel();if(uploading==build)uploading=null;}
    }
    static void exactChanged(long key){
        layoutDirty=true;
        int x=BlockPos.getX(key),z=BlockPos.getZ(key);long column=ChunkPos.asLong(x,z);invalidate(column);
        invalidate(ChunkPos.asLong(x-1,z));invalidate(ChunkPos.asLong(x+1,z));
        invalidate(ChunkPos.asLong(x,z-1));invalidate(ChunkPos.asLong(x,z+1));
    }
    private static void invalidateNeighbors(long key){
        int x=ChunkPos.getX(key),z=ChunkPos.getZ(key),rx=x>>2,rz=z>>2;
        if((x&3)==0)invalidate(ChunkPos.asLong(rx-1,rz));
        if((x&3)==3)invalidate(ChunkPos.asLong(rx+1,rz));
        if((z&3)==0)invalidate(ChunkPos.asLong(rx,rz-1));
        if((z&3)==3)invalidate(ChunkPos.asLong(rx,rz+1));
    }
    private static void removed(long key,Hk3WorldFarSurface surface){
        Hk3FarViewRenderer.terrainChanged(key);
        long at=region(key);var owner=REGIONS.get(at);owner.chunks.remove(key);owner.dirty();layoutDirty=true;
        if(!surface.empty())owner.nonemptyChunks--;
        if(owner.chunks.isEmpty()){owner.close();REGIONS.remove(at);cancel(at);resort=true;}
        invalidateNeighbors(key);
    }
    static void received(LevelChunk chunk){
        PENDING.put(chunk.getPos().toLong(),new WeakReference<>(chunk));
        while(PENDING.size()>1024)PENDING.remove(PENDING.keySet().iterator().next());
    }
    static void unloaded(LevelChunk chunk){
        long key=chunk.getPos().toLong();
        if(PENDING.remove(key)!=null){
            RETIRED.put(key,Hk3WorldFarSurface.snapshot(chunk));
            while(RETIRED.size()>8)RETIRED.remove(RETIRED.keySet().iterator().next());
        }
    }
    static void tick(long deadline){
        long until=Math.min(deadline,System.nanoTime()+250_000L);
        var level=Minecraft.getInstance().level;
        for(var iterator=captures.entrySet().iterator();iterator.hasNext()&&System.nanoTime()<until;){
            var capture=iterator.next().getValue();
            if(!capture.future.isDone())continue;
            if(capture.level==level)store(capture.key,capture.future.join());
            iterator.remove();
        }
        while(captures.size()<Hk3FarTileMesh.workers()&&Hk3FarTileMesh.availableSlots()>0&&System.nanoTime()<until){
            boolean scheduled=false;
            for(var iterator=RETIRED.entrySet().iterator();iterator.hasNext();){
                var next=iterator.next();if(captures.containsKey(next.getKey()))continue;
                var future=Hk3FarTileMesh.prepareSurface(next.getValue());
                if(future!=null){captures.put(next.getKey(),new Capture(next.getKey(),level,future));iterator.remove();scheduled=true;}
                break;
            }
            if(scheduled)continue;
            for(var iterator=PENDING.entrySet().iterator();iterator.hasNext();){
                var next=iterator.next();if(captures.containsKey(next.getKey()))continue;
                var chunk=next.getValue().get();
                if(chunk!=null&&chunk.getLevel()==level){
                    var future=Hk3FarTileMesh.prepareSurface(Hk3WorldFarSurface.snapshot(chunk));
                    if(future!=null){captures.put(next.getKey(),new Capture(next.getKey(),level,future));iterator.remove();scheduled=true;}
                }else iterator.remove();
                break;
            }
            if(!scheduled)break;
        }
    }
    private static void discardAssembly(long key){var old=ASSEMBLIES.remove(key);if(old!=null)partialBytes-=old.bytes;}
    public static void accept(Hk3WorldFarSurfacePacket packet){
        if(!Hk3FarViewRenderer.accepts(packet.dimension(),packet.session()))return;
        var level=Minecraft.getInstance().level;
        for(var entry:packet.entries()){
            long key=entry.chunk();
            if(SURFACES.containsKey(key)&&level.getChunkSource().hasChunk(ChunkPos.getX(key),ChunkPos.getZ(key))){discardAssembly(key);continue;}
            if(entry.firstColumn()==0){
                discardAssembly(key);
                if(entry.columnCount()==256){store(key,entry.surface());continue;}
                ASSEMBLIES.put(key,new Assembly());
            }
            var assembly=ASSEMBLIES.get(key);
            if(assembly==null||assembly.columns!=entry.firstColumn()){discardAssembly(key);continue;}
            assembly.add(entry);partialBytes+=entry.surface().bytes();
            if(assembly.columns==256){var snapshot=assembly.finish();discardAssembly(key);store(key,snapshot);}
            while(partialBytes>PARTIAL_LIMIT||ASSEMBLIES.size()>4)discardAssembly(ASSEMBLIES.keySet().iterator().next());
        }
    }
    private static void store(long key,Hk3WorldFarSurface snapshot){
        var previous=SURFACES.get(key);
        if(previous!=null&&previous.same(snapshot))return;
        if(previous!=null)bytes-=previous.bytes();
        SURFACES.put(key,snapshot);bytes+=snapshot.bytes();
        Hk3FarViewRenderer.terrainChanged(key);
        var group=REGIONS.computeIfAbsent(region(key),at->{resort=true;return new Region(at);});group.chunks.add(key);group.dirty();invalidateNeighbors(key);
        if(previous==null||previous.empty()!=snapshot.empty())layoutDirty=true;
        if(previous!=null&&!previous.empty())group.nonemptyChunks--;
        if(!snapshot.empty())group.nonemptyChunks++;
        while(bytes>CPU_LIMIT||SURFACES.size()>MAX_CHUNKS){
            var camera=Minecraft.getInstance().gameRenderer.getMainCamera().getPosition();
            var farthest=REGIONS.entrySet().stream().max(Comparator.comparingDouble(entry->distance(entry.getKey(),camera))).orElseThrow();
            for(long evicted:List.copyOf(farthest.getValue().chunks)){
                var surface=SURFACES.remove(evicted);bytes-=surface.bytes();removed(evicted,surface);
            }
        }
    }
    static void prepare(Vec3 camera,Frustum frustum,int distance,long limit,Hk3FarMaterials materials){
        long priority=ChunkPos.asLong((int)Math.floor(camera.x/16),(int)Math.floor(camera.z/16));
        int near=Math.max(128,Minecraft.getInstance().options.getEffectiveRenderDistance()*16+64);
        boolean replan=layoutDirty||resort||lastPriority!=priority||lastBudget!=limit||lastDistance!=distance||lastNear!=near;
        if(lastPriority!=priority||lastBudget!=limit){
            resort|=lastPriority!=priority;
            REGIONS.values().forEach(group->group.limited=false);
            lastPriority=priority;lastBudget=limit;
        }
        if(resort){sorted=REGIONS.entrySet().stream().sorted(Comparator.comparingDouble(e->distance(e.getKey(),camera))).toList();resort=false;}
        double rangeLimit=(double)(distance+64)*(distance+64);
        int weight=0;visible.clear();
        for(var entry:sorted){
            var group=entry.getValue();
            if(replan){
                double squared=distance(entry.getKey(),camera);group.inRange=group.nonemptyChunks>0&&squared<rangeLimit;
                if(group.inRange){
                    boolean detail=Hk3FarViewRenderer.detailRequired(entry.getKey());int maxStride=16;
                    int target=detail?1:targetStride(squared,near,group.targetStride,maxStride);
                    if(group.detail!=detail||group.targetStride!=target||group.maxStride!=maxStride){group.limited=false;group.detail=detail;group.targetStride=target;group.maxStride=maxStride;}
                }
            }
            if(!group.inRange){group.close();group.built=-1;group.visible=false;continue;}
            group.visible=frustum.isVisible(group.bounds);
            weight+=weight(group.targetStride);
            if(group.visible)visible.add(entry);
        }
        if(replan)for(var entry:sorted){
            var group=entry.getValue();
            if(!group.inRange)continue;
            int quads=(int)Math.min(Math.min(limit,CPU_LIMIT)/96,group.detail?limit/96:Math.max(8192,limit*weight(group.targetStride)/weight/96));
            if(group.maxQuads!=quads){group.maxQuads=quads;group.limited=false;}
        }
        layoutDirty=false;lastDistance=distance;lastNear=near;
        for(int pass=0;pass<2;pass++)for(int i=sorted.size()-1;gpuBytes>limit&&i>=0;i--){
            var group=sorted.get(i).getValue();if(pass==0&&group.visible)continue;group.close();group.built=-1;
        }
        materials.priority(true);
        long committed=0;
        for(var entry:sorted){
            var group=entry.getValue();
            group.capacity=limit-committed;
            if(group.visible&&group.mesh!=null)committed+=group.mesh.bytes;
            if(group.visible&&group.limited&&group.waitingBytes>0&&group.capacity>=group.waitingBytes){group.limited=false;group.waitingBytes=0;}
        }
        discardInvalid(works);discardInvalid(completed);
        long now=System.nanoTime(),deadline=now+500_000L;
        boolean uploaded=false;
        if(uploading!=null){
            var group=REGIONS.get(uploading.key);
            if(!group.visible){uploading.upload.close();uploading.upload=null;uploading=null;}
            else if(upload(uploading,group,limit,deadline)){completed.remove(uploading.key);uploading=null;uploaded=true;}
            else if(uploading.upload==null)uploading=null;
        }
        if(uploading==null&&!uploaded)for(var entry:visible){
            if(System.nanoTime()>=deadline)break;
            var build=completed.get(entry.getKey());if(build==null)continue;
            if(upload(build,entry.getValue(),limit,deadline)){completed.remove(entry.getKey());break;}
            if(build.upload!=null){uploading=build;break;}
        }
        for(var iterator=works.entrySet().iterator();iterator.hasNext()&&System.nanoTime()<deadline;){
            var entry=iterator.next();var build=entry.getValue();
            if(!build.advance(materials,deadline))continue;
            completed.put(entry.getKey(),build);iterator.remove();
        }
        trimCompleted(camera);
        int maxBuilds=Hk3FarTileMesh.workers();
        for(int pass=0;pass<2&&works.size()<maxBuilds&&System.nanoTime()<deadline;pass++)for(var entry:visible){
            var group=entry.getValue();long key=entry.getKey();
            if(works.containsKey(key)||completed.containsKey(key)||group.limited||group.capacity<=0)continue;
            if(group.built==group.revision&&group.mesh!=null&&group.meshStride<=group.maxStride
                    &&(group.meshStride==group.targetStride||group.builtTarget==group.targetStride&&group.maxQuads<=group.builtQuads))continue;
            if(now-group.changedAt<75_000_000L&&now-group.dirtySince<500_000_000L)continue;
            if(pass==0&&(group.mesh==null||group.mesh.bytes<=group.maxQuads*96L&&group.meshStride>=group.targetStride))continue;
            if(!makeRoom(key,camera,maxBuilds*2))continue;
            int originX=ChunkPos.getX(key)*64,originZ=ChunkPos.getZ(key)*64;
            Map<Long,Hk3WorldFarSurface> chunks=new LinkedHashMap<>();
            for(int x=(originX>>4)-1;x<=(originX>>4)+4;x++)for(int z=(originZ>>4)-1;z<=(originZ>>4)+4;z++){
                long chunk=ChunkPos.asLong(x,z);var surface=SURFACES.get(chunk);
                if(surface!=null)chunks.put(chunk,surface);
            }
            var build=new Hk3WorldFarBuild(key,group.revision,group.targetStride,group.maxStride,group.maxQuads,chunks);
            works.put(key,build);build.advance(materials,deadline);
            if(works.size()>=maxBuilds||System.nanoTime()>=deadline)break;
        }
    }
    private static void discardInvalid(Map<Long,Hk3WorldFarBuild> builds){
        for(var iterator=builds.entrySet().iterator();iterator.hasNext();){
            var entry=iterator.next();var build=entry.getValue();var group=REGIONS.get(entry.getKey());
            if(group==null||!group.inRange||group.revision!=build.revision||group.targetStride!=build.targetStride
                    ||group.maxStride!=build.maxStride){
                build.cancel();if(uploading==build)uploading=null;iterator.remove();
            }
        }
    }
    private static boolean makeRoom(long key,Vec3 camera,int maximum){
        if(works.size()+completed.size()<maximum)return true;
        var farthest=completed.entrySet().stream().filter(entry->entry.getValue()!=uploading)
                .max(Comparator.comparingDouble(entry->distance(entry.getKey(),camera))).orElse(null);
        if(farthest==null||distance(farthest.getKey(),camera)<=distance(key,camera))return false;
        discardCompleted(farthest.getKey());return true;
    }
    private static void trimCompleted(Vec3 camera){
        long cached=0;
        for(var build:completed.values()){var shell=build.future.join();if(shell!=null)cached+=shell.quads().size()*96L;}
        while(cached>CPU_LIMIT){
            var farthest=completed.entrySet().stream().filter(entry->entry.getValue()!=uploading)
                    .max(Comparator.comparingDouble(entry->distance(entry.getKey(),camera))).orElseThrow();
            var shell=farthest.getValue().future.join();if(shell!=null)cached-=shell.quads().size()*96L;
            discardCompleted(farthest.getKey());
        }
    }
    private static void discardCompleted(long key){
        completed.remove(key).cancel();var group=REGIONS.get(key);group.limited=false;group.waitingBytes=0;
    }
    private static int weight(int stride){return 5-Integer.numberOfTrailingZeros(stride);}
    private static int targetStride(double squared,int near,int previous,int maximum){
        int stride=Math.min(previous,maximum);
        while(stride<maximum){double edge=near*stride*1.15;if(squared<=edge*edge)break;stride*=2;}
        while(stride>1){double edge=near*(stride/2)*.85;if(squared>=edge*edge)break;stride/=2;}
        return stride;
    }
    private static boolean upload(Hk3WorldFarBuild build,Region group,long limit,long deadline){
        var shell=build.future.join();
        group.waitingBytes=0;
        if(shell==null){
            group.limited=true;
            return true;
        }
        long required=shell.quads().size()*96L;
        if(required>group.capacity){
            group.limited=true;group.waitingBytes=(int)required;
            if(build.upload!=null){build.upload.close();build.upload=null;}
            return false;
        }
        if(build.upload==null){
            var pieces=List.of(new Hk3FarTileMesh.Piece(null,shell.quads(),List.of(),0,0,0,build.models));
            build.upload=Hk3FarTileMesh.beginUpload(pieces,required);
        }
        if(!build.upload.active())return false;
        var camera=Minecraft.getInstance().gameRenderer.getMainCamera().getPosition();
        for(int pass=0;pass<2;pass++)for(int i=sorted.size()-1;gpuBytes-(group.mesh==null?0:group.mesh.bytes)+required>limit&&i>=0;i--){
            var candidate=sorted.get(i);var other=candidate.getValue();
            if(other!=group&&other.mesh!=null&&(pass==0?!other.visible:other.visible&&distance(candidate.getKey(),camera)>distance(build.key,camera))){
                other.waitingBytes=other.mesh.bytes;other.limited=true;other.close();other.built=-1;
            }
        }
        if(required>limit-gpuBytes+(group.mesh==null?0:group.mesh.bytes)){
            group.limited=true;group.waitingBytes=(int)required;build.upload.close();build.upload=null;return false;
        }
        if(!build.upload.advance(deadline))return false;
        var mesh=build.upload.finish();build.upload=null;
        group.close();group.mesh=mesh;gpuBytes+=mesh.bytes;group.built=build.revision;group.limited=false;
        group.builtTarget=build.targetStride;group.builtQuads=build.maxQuads;group.meshStride=shell.stride();
        group.dirtySince=0;
        int low=Math.min(mesh.minY[0],mesh.minY[1]),high=Math.max(mesh.maxY[0],mesh.maxY[1]);
        if(mesh.bytes>0){
            group.centerY=(low+high)/2;
            group.bounds=new AABB(group.fullBounds.minX,low,group.fullBounds.minZ,group.fullBounds.maxX,high,group.fullBounds.maxZ);
        }
        group.draw=new Hk3FarViewRenderer.Draw(mesh,ChunkPos.getX(build.key)*64,0,ChunkPos.getZ(build.key)*64,true,0);
        return true;
    }
    static void draws(List<Hk3FarViewRenderer.Draw> draws,Vec3 camera){
        for(var entry:visible){
            var group=entry.getValue();if(group.mesh==null)continue;
            double dy=group.centerY-camera.y;group.draw.distance=distance(entry.getKey(),camera)+dy*dy;draws.add(group.draw);
        }
    }
    static boolean ready(){return visible.stream().anyMatch(entry->entry.getValue().mesh!=null&&entry.getValue().mesh.bytes>0);}
    static long limited(){return REGIONS.values().stream().filter(group->group.limited).count();}
    static String lodStatus(){
        var text=new StringJoiner("/");
        for(int stride=1;stride<=16;stride*=2){
            int step=stride;text.add(Long.toString(REGIONS.values().stream().filter(group->group.mesh!=null&&group.mesh.bytes>0&&group.meshStride==step).count()));
        }
        return text.toString();
    }
    private static double distance(long key,Vec3 camera){
        double x=ChunkPos.getX(key)*64+32-camera.x,z=ChunkPos.getZ(key)*64+32-camera.z;return x*x+z*z;
    }
    static void reload(){
        REGIONS.values().forEach(group->{group.close();group.built=-1;group.limited=false;group.bounds=group.fullBounds;});
        works.values().forEach(Hk3WorldFarBuild::cancel);completed.values().forEach(Hk3WorldFarBuild::cancel);
        works.clear();completed.clear();uploading=null;visible.clear();layoutDirty=true;
    }
    static void clear(){reload();captures.values().forEach(capture->capture.future.cancel(false));REGIONS.clear();SURFACES.clear();ASSEMBLIES.clear();PENDING.clear();RETIRED.clear();captures.clear();sorted=List.of();resort=true;bytes=partialBytes=0;lastPriority=Long.MIN_VALUE;lastBudget=-1;lastDistance=lastNear=-1;}
}
