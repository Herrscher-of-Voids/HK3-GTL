package com.sirin.hk3gtl.client.farview;

import com.mojang.blaze3d.systems.RenderSystem;
import com.mojang.blaze3d.vertex.*;
import com.sirin.hk3gtl.common.farview.*;
import com.sirin.hk3gtl.common.network.Hk3Network;
import com.sirin.hk3gtl.client.wonder.Hk3W03FieldScenes;
import com.sirin.hk3gtl.client.wonder.Hk3W08FieldScenes;
import com.sirin.hk3gtl.client.wonder.Hk3W10FieldScenes;
import com.sirin.hk3gtl.client.wonder.Hk3W12FieldScenes;
import com.sirin.hk3gtl.client.wonder.Hk3W11FieldScenes;
import com.sirin.hk3gtl.client.wonder.Hk3W13FieldScenes;
import com.sirin.hk3gtl.client.wonder.Hk3WonderFxScenes;
import com.sirin.hk3gtl.client.wonder.Hk3W03FxRenderer;
import it.unimi.dsi.fastutil.longs.LongOpenHashSet;
import it.unimi.dsi.fastutil.longs.LongSet;
import net.minecraft.client.Minecraft;
import net.minecraft.client.multiplayer.ClientLevel;
import net.minecraft.client.renderer.ShaderInstance;
import net.minecraft.client.renderer.FogRenderer;
import net.minecraft.client.renderer.culling.Frustum;
import net.minecraft.core.BlockPos;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.level.material.FogType;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.phys.AABB;
import net.minecraft.world.phys.Vec3;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.client.event.*;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import org.joml.Matrix4f;
import java.util.*;


/** 精确静态表面远景；同原版投影、深度偏移与分帧上传共同保护交接。 */
@Mod.EventBusSubscriber(modid="hk3gtl",value=Dist.CLIENT)
public final class Hk3FarViewRenderer {
    private static final Map<Long,Tile> TILES=new HashMap<>();
    private static final Map<Long,Region> REGIONS=new HashMap<>();
    private static final Map<Long,Set<Region>> REGION_COLUMNS=new HashMap<>();
    private static final Map<Long,Integer> exactColumns=new HashMap<>();
    private static final Map<Long,Hk3FarBatchWork> works=new LinkedHashMap<>();
    private static final Hk3FarMaterials MATERIALS=new Hk3FarMaterials();
    private static Set<Long> members=Set.of();
    private static Set<Long> detailColumns=Set.of();
    private static Set<Long> dynamicColumns=Set.of();
    private static boolean detailDirty;
    private static List<Map.Entry<Long,Region>> sorted=List.of();
    private static final List<Map.Entry<Long,Region>> visible=new ArrayList<>();
    private static final List<Draw> frameDraws=new ArrayList<>(),drawCandidates=new ArrayList<>();
    private static final Comparator<Draw> DRAW_ORDER=Comparator.comparingDouble(Draw::distance);
    private static Vec3 drawCamera;
    private static int drawFrame;
    private static boolean frameReady;
    private static final float[] NATIVE_SECTIONS=new float[65];
    private static final LongSet NATIVE_VISIBLE=new LongOpenHashSet();
    private static NativeVisibility nativeVisibility;
    private static ClientLevel level;
    private static ShaderInstance shader;
    private static int ticks,lastDistance=-1,drawn,buildTurn;
    private static boolean lastEnabled,resort;
    private static long gpuBytes,session;
    private static long dynamicMaskSignature;
    private static long lastPriority=Long.MIN_VALUE,lastGpuBudget=-1;
    private static boolean dynamicMask;
    private static final class Tile {
        final Hk3FarTileSource source=new Hk3FarTileSource();
    }
    private static final class Region {
        final long key;
        final long column;
        final AABB bounds;
        final Set<Long> sections=new HashSet<>();
        Hk3FarTileMesh mesh;
        Draw draw;
        long revision,built=-1;
        boolean limited,structure;
        Region(long key){
            this.key=key;column=net.minecraft.world.level.ChunkPos.asLong(BlockPos.getX(key),BlockPos.getZ(key));
            int x=BlockPos.getX(key)*64,y=BlockPos.getY(key)*64,z=BlockPos.getZ(key)*64;
            bounds=new AABB(x,y,z,x+64,y+64,z+64);
            REGION_COLUMNS.computeIfAbsent(column,ignored->new HashSet<>()).add(this);resort=true;
        }
        void invalidate(){revision++;limited=false;}
        void close(){
            if(mesh==null)return;
            if(mesh.bytes>0){
                long column=net.minecraft.world.level.ChunkPos.asLong(BlockPos.getX(key),BlockPos.getZ(key));
                int count=exactColumns.get(column);
                if(count==1)exactColumns.remove(column);else exactColumns.put(column,count-1);
            }
            gpuBytes-=mesh.bytes;mesh.close();mesh=null;draw=null;Hk3WorldFarTerrain.exactChanged(key);
        }
    }
    static final class Draw {
        final Hk3FarTileMesh mesh;
        final int x,y,z;
        final boolean terrain;
        double distance;
        int frame;
        Draw(Hk3FarTileMesh mesh,int x,int y,int z,boolean terrain,double distance){
            this.mesh=mesh;this.x=x;this.y=y;this.z=z;this.terrain=terrain;this.distance=distance;
        }
        double distance(){return distance;}
    }
    public interface NativeVisibility { boolean hk3gtl$visible(int x,int y,int z); }
    public static void nativeFrame(){NATIVE_VISIBLE.clear();nativeVisibility=null;}
    public static void nativeSection(BlockPos origin){
        if(Hk3FarViewConfig.ENABLED.get())NATIVE_VISIBLE.add(BlockPos.asLong(origin.getX()>>4,origin.getY()>>4,origin.getZ()>>4));
    }
    public static void nativeVisibility(NativeVisibility visibility){nativeVisibility=visibility;}
    private static boolean nativeVisible(int x,int y,int z){
        return nativeVisibility==null?NATIVE_VISIBLE.contains(BlockPos.asLong(x,y,z)):nativeVisibility.hk3gtl$visible(x,y,z);
    }
    private static long region(long key){return BlockPos.asLong(BlockPos.getX(key)>>2,BlockPos.getY(key)>>2,BlockPos.getZ(key)>>2);}
    private static void invalidate(long key){var group=REGIONS.get(region(key));if(group!=null)group.invalidate();}
    private static void discardWork(long key){var build=works.remove(key);if(build!=null)build.cancel();}
    private static void clearWorks(){works.values().forEach(Hk3FarBatchWork::cancel);works.clear();}
    private static void removeRegion(Region group){
        REGIONS.remove(group.key);var column=REGION_COLUMNS.get(group.column);column.remove(group);
        if(column.isEmpty())REGION_COLUMNS.remove(group.column);resort=true;
    }
    static void terrainChanged(long chunk){
        int x=net.minecraft.world.level.ChunkPos.getX(chunk),z=net.minecraft.world.level.ChunkPos.getZ(chunk);
        for(int gx=(x-1)>>2;gx<=(x+1)>>2;gx++)for(int gz=(z-1)>>2;gz<=(z+1)>>2;gz++){
            var column=REGION_COLUMNS.get(net.minecraft.world.level.ChunkPos.asLong(gx,gz));
            if(column!=null)for(var group:column)group.invalidate();
        }
    }
    private Hk3FarViewRenderer() {}
    public static void useLevel(ClientLevel next){if(level!=next){clear();level=next;}}
    static boolean accepts(ResourceLocation dimension,long requestSession){
        var mc=Minecraft.getInstance();
        return mc.level!=null&&mc.level==level&&dimension.equals(level.dimension().location())
                &&requestSession==session&&Hk3FarViewConfig.ENABLED.get();
    }
    public static void accept(Hk3FarViewPacket packet) {
        var mc=Minecraft.getInstance();
        if(!Hk3FarViewConfig.ENABLED.get()||mc.level==null||!packet.dimension().equals(mc.level.dimension().location()))return;
        useLevel(mc.level);
        boolean membershipChanged=packet.members()!=null&&packet.members().length!=members.size();
        if(packet.members()!=null&&!membershipChanged)for(long key:packet.members())if(!members.contains(key)){membershipChanged=true;break;}
        if(membershipChanged){
            Set<Long> selected=new HashSet<>();for(long key:packet.members())selected.add(key);members=selected;detailDirty=true;Hk3WorldFarTerrain.layoutChanged();
            var iterator=TILES.entrySet().iterator();
            while(iterator.hasNext()){
                var entry=iterator.next();if(!members.contains(entry.getKey())&&entry.getValue().source.hasStructure()){
                    long key=entry.getKey();entry.getValue().source.structure(null);
                    var group=REGIONS.get(region(key));group.close();group.invalidate();
                    if(entry.getValue().source.empty()){
                        group.sections.remove(key);iterator.remove();
                        discardWork(group.key);
                        if(group.sections.isEmpty())removeRegion(group);
                    }
                    group.structure=group.sections.stream().anyMatch(section->TILES.get(section).source.hasStructure());
                    invalidateNeighbors(key);
                }
            }
        }
        for(var update:packet.updates())if(members.contains(update.key())) {
            var tile=TILES.computeIfAbsent(update.key(),key->new Tile());
            tile.source.structure(update.section());
            var group=REGIONS.computeIfAbsent(region(update.key()),Region::new);group.sections.add(update.key());group.structure=true;group.invalidate();discardWork(group.key);
            invalidateNeighbors(update.key());
        }
    }
    public static void world(long key,Hk3WorldFarCache.Packed snapshot){
        if(snapshot.empty()){removeWorld(key);return;}
        var tile=TILES.computeIfAbsent(key,ignored->new Tile());tile.source.world(snapshot);
        var group=REGIONS.computeIfAbsent(region(key),Region::new);group.sections.add(key);group.invalidate();discardWork(group.key);
        invalidateNeighbors(key);
    }
    public static void removeWorld(long key){
        var tile=TILES.get(key);
        if(tile!=null){
            tile.source.world(null);
            var group=REGIONS.get(region(key));group.close();group.invalidate();
            if(tile.source.empty()){
                TILES.remove(key);group.sections.remove(key);
                discardWork(group.key);
                if(group.sections.isEmpty())removeRegion(group);
            }
        }
        invalidateNeighbors(key);
    }
    public static void clearWorld(){for(long key:List.copyOf(TILES.keySet()))removeWorld(key);}
    static boolean exactReady(int x,int y,int z,int state){
        long key=BlockPos.asLong(x>>4,y>>4,z>>4);var tile=TILES.get(key);if(tile==null)return false;
        var group=REGIONS.get(region(key));
        return group.mesh!=null&&group.mesh.bytes>0&&group.built==group.revision
                &&tile.source.state(Hk3FarMesh.index(x&15,y&15,z&15))==state;
    }
    static boolean maskRequired(long key){return dynamicColumns.contains(key);}
    static boolean exactRequired(long key){return exactColumns.containsKey(key);}
    static boolean detailRequired(long key){
        if(detailDirty){
            Set<Long> next=new HashSet<>();
            for(long section:members)next.add(net.minecraft.world.level.ChunkPos.asLong(BlockPos.getX(section)>>2,BlockPos.getZ(section)>>2));
            detailColumns=next;detailDirty=false;
        }
        if(exactColumns.containsKey(key))return true;
        if(detailColumns.contains(key))return true;
        return dynamicColumns.contains(key);
    }
    private static Hk3FarSection.Snapshot snapshot(long key,Tile tile){
        if(!dynamicMask||!maskRequired(net.minecraft.world.level.ChunkPos.asLong(BlockPos.getX(key)>>2,BlockPos.getZ(key)>>2)))return tile.source.snapshot(null);
        var pos=new BlockPos.MutableBlockPos();int x=BlockPos.getX(key)*16,y=BlockPos.getY(key)*16,z=BlockPos.getZ(key)*16;
        return tile.source.snapshot(index->{
            var world=pos.set(x+index/256,y+index/16%16,z+index%16);var state=Block.stateById(tile.source.state(index)-1);
            return Hk3W03FieldScenes.hidden(world,state)||Hk3W08FieldScenes.hidden(world,state)||Hk3W10FieldScenes.hidden(world,state)||Hk3W12FieldScenes.hidden(world,state)||Hk3W11FieldScenes.hidden(world,state)||Hk3W13FieldScenes.hidden(world,state)||Hk3WonderFxScenes.hidden(world,state);
        });
    }
    private static void updateDynamicMask(){
        boolean active=Hk3W03FxRenderer.ready()&&Hk3W03FieldScenes.maskReady()&&!Hk3W03FieldScenes.scenes().isEmpty()||Hk3W08FieldScenes.active()||Hk3W10FieldScenes.active()||Hk3W12FieldScenes.active()||Hk3W11FieldScenes.active()||Hk3W13FieldScenes.active()||Hk3WonderFxScenes.active();
        long signature=active?1:0;
        if(active)for(var scene:Hk3W03FieldScenes.scenes())signature=signature*31+scene.state().pos().asLong()*7+scene.state().facing().ordinal();
        signature=signature*31+Hk3W08FieldScenes.signature();
        signature=signature*31+Hk3W10FieldScenes.signature();
        signature=signature*31+Hk3W12FieldScenes.signature();
        signature=signature*31+Hk3W11FieldScenes.signature();
        signature=signature*31+Hk3W13FieldScenes.signature();
        signature=signature*31+Hk3WonderFxScenes.signature();
        if(signature==dynamicMaskSignature)return;
        dynamicMaskSignature=signature;dynamicMask=active;
        Set<Long> dirtyColumns=new HashSet<>(dynamicColumns);
        if(active){
            Set<Long> selected=new HashSet<>();
            for(var scene:Hk3W03FieldScenes.scenes()){
                var state=scene.state();var pos=state.pos();int minX,maxX,minZ,maxZ;
                switch(state.facing()){
                    case NORTH->{minX=pos.getX()-416;maxX=pos.getX()+416;minZ=pos.getZ()-187;maxZ=pos.getZ()+645;}
                    case SOUTH->{minX=pos.getX()-416;maxX=pos.getX()+416;minZ=pos.getZ()-645;maxZ=pos.getZ()+187;}
                    case EAST->{minX=pos.getX()-187;maxX=pos.getX()+645;minZ=pos.getZ()-416;maxZ=pos.getZ()+416;}
                    default->{minX=pos.getX()-645;maxX=pos.getX()+187;minZ=pos.getZ()-416;maxZ=pos.getZ()+416;}
                }
                minX>>=6;maxX>>=6;minZ>>=6;maxZ>>=6;
                for(int x=minX;x<=maxX;x++)for(int z=minZ;z<=maxZ;z++)selected.add(net.minecraft.world.level.ChunkPos.asLong(x,z));
            }
            Hk3W08FieldScenes.addColumns(selected);Hk3W10FieldScenes.addColumns(selected);Hk3W12FieldScenes.addColumns(selected);Hk3W11FieldScenes.addColumns(selected);Hk3W13FieldScenes.addColumns(selected);Hk3WonderFxScenes.addColumns(selected);dynamicColumns=selected;
        }else dynamicColumns=Set.of();
        dirtyColumns.addAll(dynamicColumns);
        Set<Long> affected=new HashSet<>(dirtyColumns);
        for(long column:dirtyColumns){
            int x=net.minecraft.world.level.ChunkPos.getX(column),z=net.minecraft.world.level.ChunkPos.getZ(column);
            for(int dx=-1;dx<=1;dx++)for(int dz=-1;dz<=1;dz++)affected.add(net.minecraft.world.level.ChunkPos.asLong(x+dx,z+dz));
        }
        Hk3WorldFarTerrain.maskChanged(affected);
        for(var group:REGIONS.values()){
            long column=net.minecraft.world.level.ChunkPos.asLong(BlockPos.getX(group.key),BlockPos.getZ(group.key));
            if(affected.contains(column)){group.close();group.invalidate();discardWork(group.key);}
        }
    }
    private static long neighbor(long key,int axis,int sign) {
        int x=BlockPos.getX(key),y=BlockPos.getY(key),z=BlockPos.getZ(key);
        return BlockPos.asLong(x+(axis==0?sign:0),y+(axis==1?sign:0),z+(axis==2?sign:0));
    }
    private static void invalidateNeighbors(long key) {
        for(int axis=0;axis<3;axis++)for(int sign:new int[]{-1,1}){
            invalidate(neighbor(key,axis,sign));
        }
    }
    private static void clear(){
        REGIONS.values().forEach(Region::close);REGIONS.clear();REGION_COLUMNS.clear();exactColumns.clear();clearWorks();TILES.clear();members=Set.of();detailColumns=Set.of();dynamicColumns=Set.of();detailDirty=false;sorted=List.of();visible.clear();frameDraws.clear();drawCandidates.clear();drawCamera=null;frameReady=false;gpuBytes=0;drawn=0;MATERIALS.close();
        Hk3WorldFarCapture.clear();nativeFrame();dynamicMask=false;dynamicMaskSignature=0;
        level=null;lastDistance=-1;session++;resort=true;lastPriority=Long.MIN_VALUE;lastGpuBudget=-1;
    }
    @SubscribeEvent public static void logout(ClientPlayerNetworkEvent.LoggingOut event){clear();}
    @SubscribeEvent public static void tick(TickEvent.ClientTickEvent event) {
        if(event.phase!=TickEvent.Phase.END)return;
        var mc=Minecraft.getInstance();if(mc.level==null||mc.player==null)return;
        useLevel(mc.level);Hk3WorldFarCapture.tick();
        boolean enabled=Hk3FarViewConfig.ENABLED.get();int distance=Hk3FarViewConfig.DISTANCE.get();ticks++;
        if(lastDistance!=distance||lastEnabled!=enabled||ticks%100==0){
            Hk3Network.CHANNEL.sendToServer(new Hk3FarViewPacket.Request(enabled,distance,session));lastDistance=distance;lastEnabled=enabled;
            if(!enabled){REGIONS.values().forEach(Region::close);REGIONS.values().forEach(Region::invalidate);clearWorks();frameDraws.clear();frameReady=false;MATERIALS.close();}
        }
    }
    @SubscribeEvent public static void fog(ViewportEvent.RenderFog event) {
        var mc=Minecraft.getInstance();
        if(event.getMode()!=FogRenderer.FogMode.FOG_TERRAIN||event.getType()!=FogType.NONE
                ||!Hk3FarViewConfig.ENABLED.get()||TILES.isEmpty()&&Hk3WorldFarTerrain.empty()||mc.level==null||level!=mc.level||mc.player==null
                ||mc.player.hasEffect(MobEffects.BLINDNESS)||mc.player.hasEffect(MobEffects.DARKNESS)
                ||mc.level.effects().isFoggyAt(mc.player.getBlockX(),mc.player.getBlockZ())
                ||mc.gui.getBossOverlay().shouldCreateWorldFog())return;
        float distance=Hk3FarViewConfig.DISTANCE.get();
        if(distance<=mc.options.getEffectiveRenderDistance()*16)return;
        // 近景已经写入深度，远景不能补画被原版短距离雾染成天空的表面；统一雾距，不扩大区块加载。
        event.setNearPlaneDistance(Math.max(event.getNearPlaneDistance(),distance));
        event.setFarPlaneDistance(Math.max(event.getFarPlaneDistance(),distance+128f));
        event.setCanceled(true);
    }
    @SubscribeEvent public static void render(RenderLevelStageEvent event) {
        boolean opaque=event.getStage()==RenderLevelStageEvent.Stage.AFTER_CUTOUT_BLOCKS;
        if(!opaque&&event.getStage()!=RenderLevelStageEvent.Stage.AFTER_BLOCK_ENTITIES)return;
        if(opaque){drawn=0;frameReady=false;Hk3FarTileMesh.beginFrame();}
        if(shader==null||!Hk3FarViewConfig.ENABLED.get()||TILES.isEmpty()&&Hk3WorldFarTerrain.empty())return;
        var mc=Minecraft.getInstance();
        if(mc.level==null||mc.level!=level||mc.player==null||event.getCamera().getFluidInCamera()!=FogType.NONE
                ||mc.player.hasEffect(MobEffects.BLINDNESS)||mc.player.hasEffect(MobEffects.DARKNESS))return;
        if(!opaque){draw(event,1);return;}
        updateDynamicMask();
        var camera=event.getCamera().getPosition();int distance=Hk3FarViewConfig.DISTANCE.get();
        long priority=BlockPos.asLong((int)Math.floor(camera.x/16),(int)Math.floor(camera.y/16),(int)Math.floor(camera.z/16));
        if(priority!=lastPriority)resort=true;
        if(resort){sorted=REGIONS.entrySet().stream().sorted(Comparator.comparingDouble(e->distance(e.getKey(),camera.x,camera.y,camera.z))).toList();resort=false;}
        // 投影直接复用原版；Mixin统一延长远裁面，不能给同一深度缓冲另造投影。
        Matrix4f projection=new Matrix4f(event.getProjectionMatrix());
        var frustum=new Frustum(event.getPoseStack().last().pose(),projection);frustum.prepare(camera.x,camera.y,camera.z);
        visible.clear();double range=(double)(distance+64)*(distance+64);
        for(var entry:sorted)if(distance(entry.getKey(),camera.x,camera.y,camera.z)<range&&frustum.isVisible(entry.getValue().bounds))visible.add(entry);
        long totalBudget=(long)Hk3FarViewConfig.GPU_MIB.get()*1024*1024;
        long terrainBudget=Hk3WorldFarTerrain.budget(totalBudget),budget=totalBudget-terrainBudget;
        Hk3WorldFarTerrain.prepare(camera,frustum,distance,terrainBudget,MATERIALS);
        if(priority!=lastPriority||budget!=lastGpuBudget){
            lastPriority=priority;lastGpuBudget=budget;
            REGIONS.values().forEach(group->{if(group.limited)group.invalidate();});
        }
        for(int i=sorted.size()-1;gpuBytes>budget&&i>=0;i--){var group=sorted.get(i).getValue();group.close();group.invalidate();}
        works.entrySet().removeIf(entry->{
            var group=REGIONS.get(entry.getKey());
            if(group!=null&&distance(entry.getKey(),camera.x,camera.y,camera.z)<range&&group.revision==entry.getValue().revision)return false;
            entry.getValue().cancel();return true;
        });
        long buildDeadline=System.nanoTime()+500_000L;
        int buildLimit=Hk3FarTileMesh.workers();
        while(works.size()<buildLimit&&System.nanoTime()<buildDeadline){
            boolean worldTurn=buildTurn%3==2;Map.Entry<Long,Region> next=null;
            for(var entry:visible){
                var group=entry.getValue();if(works.containsKey(entry.getKey())||group.built==group.revision||group.limited)continue;
                if(next==null)next=entry;
                if(hasStructure(group)!=worldTurn){next=entry;break;}
            }
            if(next==null)break;
            var group=next.getValue();
            var sections=group.sections.stream().sorted().map(key->{
                var tile=TILES.get(key);return new Hk3FarBatchWork.Section(key,()->snapshot(key,tile));
            }).toList();
            works.put(next.getKey(),new Hk3FarBatchWork(next.getKey(),group.revision,sections));buildTurn++;
        }
        int perBuild=Math.max(1,(buildLimit+Math.max(1,works.size())-1)/Math.max(1,works.size()));
        for(var iterator=works.entrySet().iterator();iterator.hasNext()&&System.nanoTime()<buildDeadline;){
            var entry=iterator.next();var build=entry.getValue();var group=REGIONS.get(entry.getKey());
            if(group==null){build.cancel();iterator.remove();continue;}
            boolean structure=hasStructure(group);MATERIALS.priority(structure);
            try{
                if(!build.advance(MATERIALS,Hk3FarViewRenderer::boundaries,buildDeadline,perBuild))continue;
                if(group.revision!=build.revision){build.cancel();iterator.remove();continue;}
                if(!upload(build,group,sorted,camera,budget,structure,buildDeadline))continue;
                iterator.remove();
                break;
            }catch(RuntimeException failure){
                group.built=group.revision;build.cancel();iterator.remove();
                com.mojang.logging.LogUtils.getLogger().error("HK3GTL真实表面远景批次构建失败",failure);
            }
        }
        // 全空气批次也会缓存空网格；没有真实面时尚未创建材质图集。
        if(!Hk3WorldFarTerrain.ready()&&visible.stream().noneMatch(e->e.getValue().mesh!=null&&e.getValue().mesh.bytes>0))return;
        drawCandidates.clear();Hk3WorldFarTerrain.draws(drawCandidates,camera);
        for(var entry:visible){
            var group=entry.getValue();var mesh=group.mesh;if(mesh==null||mesh.bytes==0)continue;
            long key=entry.getKey();
            group.draw.distance=distance(key,camera.x,camera.y,camera.z);drawCandidates.add(group.draw);
        }
        boolean changed=drawCandidates.size()!=frameDraws.size();drawFrame++;
        for(var draw:drawCandidates){changed|=draw.frame!=drawFrame-1;draw.frame=drawFrame;}
        if(changed){frameDraws.clear();frameDraws.addAll(drawCandidates);}
        if(changed||!camera.equals(drawCamera))frameDraws.sort(DRAW_ORDER);
        drawCamera=camera;frameReady=true;draw(event,0);
    }
    private static boolean upload(Hk3FarBatchWork build,Region group,List<Map.Entry<Long,Region>> sorted,net.minecraft.world.phys.Vec3 camera,
                                  long budget,boolean structure,long deadline){
        long required=build.required;
        if(build.upload==null)build.upload=Hk3FarTileMesh.beginUpload(build.pieces,required);
        if(!build.upload.active())return false;
        for(int i=sorted.size()-1;gpuBytes-(group.mesh==null?0:group.mesh.bytes)+required>budget&&i>=0;i--){
            var candidate=sorted.get(i);var other=candidate.getValue();
            if(other==group||other.mesh==null)continue;
            boolean otherStructure=hasStructure(other);
            if(!otherStructure&&structure
                    ||otherStructure==structure&&distance(candidate.getKey(),camera.x,camera.y,camera.z)>distance(build.key,camera.x,camera.y,camera.z)){
                other.close();other.built=other.revision;other.limited=true;
            }
        }
        if(required>budget-gpuBytes+(group.mesh==null?0:group.mesh.bytes)){group.limited=true;build.cancel();return true;}
        if(!build.upload.advance(deadline))return false;
        var mesh=build.upload.finish();
        group.close();group.mesh=mesh;gpuBytes+=mesh.bytes;group.built=build.revision;
        group.draw=new Draw(mesh,BlockPos.getX(group.key)*64,BlockPos.getY(group.key)*64,BlockPos.getZ(group.key)*64,false,0);
        if(mesh.bytes>0){long column=net.minecraft.world.level.ChunkPos.asLong(BlockPos.getX(group.key),BlockPos.getZ(group.key));exactColumns.merge(column,1,Integer::sum);}
        Hk3WorldFarTerrain.exactChanged(build.key);
        return true;
    }
    private static void draw(RenderLevelStageEvent event,int pass){
        if(!frameReady||frameDraws.isEmpty())return;
        var camera=event.getCamera().getPosition();var projection=new Matrix4f(event.getProjectionMatrix());
        int previous=RenderSystem.getShaderTexture(0);
        RenderSystem.setShaderTexture(0,MATERIALS.texture());
        shader.setSampler("Sampler0",RenderSystem.getShaderTexture(0));
        shader.PROJECTION_MATRIX.set(projection);
        shader.safeGetUniform("FarLimit").set((float)Hk3FarViewConfig.DISTANCE.get());
        shader.safeGetUniform("CameraOrigin").set((float)camera.x,(float)camera.y,(float)camera.z);
        // 不透明面先写主深度，远处透明面先于原版透明层混合；已编译的近景由原版接管。
        RenderSystem.enableDepthTest();RenderSystem.enablePolygonOffset();RenderSystem.polygonOffset(1,1);
        try{
            RenderSystem.depthMask(pass==0);
            if(pass==1)RenderSystem.disableCull();else RenderSystem.enableCull();
            for(int i=0;i<frameDraws.size();i++){
                var draw=frameDraws.get(pass==0?i:frameDraws.size()-1-i);if(draw.mesh.buffers.get(pass).isEmpty())continue;
                if(pass==1&&!draw.terrain&&!Hk3WorldFarTerrain.blendReady(draw.x,draw.z))continue;
                shader.safeGetUniform("NativeMask").set(nativeMask(draw,pass,camera)?1:0);
                RenderSystem.polygonOffset(draw.terrain?2:1,draw.terrain?2:1);
                Matrix4f view=new Matrix4f(event.getPoseStack().last().pose()).translate((float)(draw.x-camera.x),(float)(draw.y-camera.y),(float)(draw.z-camera.z));
                shader.safeGetUniform("TileOrigin").set((float)draw.x,(float)draw.y,(float)draw.z);
                shader.MODEL_VIEW_MATRIX.set(view);shader.apply();
                if(pass==1){RenderSystem.enableBlend();RenderSystem.defaultBlendFunc();}else RenderSystem.disableBlend();
                for(var buffer:draw.mesh.buffers.get(pass)){buffer.bind();buffer.draw();drawn++;}
                shader.clear();
            }
        }finally{
            VertexBuffer.unbind();RenderSystem.polygonOffset(0,0);RenderSystem.disablePolygonOffset();
            RenderSystem.depthMask(true);RenderSystem.disableBlend();RenderSystem.enableCull();
            RenderSystem.setShaderTexture(0,previous);
        }
    }
    private static boolean nativeMask(Draw draw,int pass,net.minecraft.world.phys.Vec3 camera){
        var mc=Minecraft.getInstance();int radius=mc.options.getEffectiveRenderDistance();
        int cx=(int)Math.floor(camera.x/16),cy=(int)Math.floor(camera.y/16),cz=(int)Math.floor(camera.z/16);
        if((draw.x>>4)>cx+radius||((draw.x+63)>>4)<cx-radius
                ||(draw.z>>4)>cz+radius||((draw.z+63)>>4)<cz-radius)return false;
        int first=Math.max((draw.y+draw.mesh.minY[pass]-1)>>4,Math.max(cy-radius,mc.level.getMinSection()));
        int last=Math.min((draw.y+draw.mesh.maxY[pass]+1)>>4,Math.min(cy+radius,mc.level.getMaxSection()-1));
        if(first>last)return false;
        Arrays.fill(NATIVE_SECTIONS,0f);
        double range=radius*16d;boolean covered=false;
        for(int x=0;x<4;x++)for(int z=0;z<4;z++){
            int sx=(draw.x>>4)+x,sz=(draw.z>>4)+z;
            if(Math.abs(sx-cx)>radius||Math.abs(sz-cz)>radius)continue;
            double dx=Math.max(0,Math.max(sx*16-camera.x,camera.x-(sx*16+16)));
            double dz=Math.max(0,Math.max(sz*16-camera.z,camera.z-(sz*16+16)));
            if(dx*dx+dz*dz>=range*range)continue;
            for(int y=first;y<=last;y++){
                double dy=Math.max(0,Math.max(y*16-camera.y,camera.y-(y*16+16)));
                // 只有本帧进入原生可见列表且网格就绪的分区才能接管，编译缓存不代表已绘制。
                if(dy<range&&nativeVisible(sx,y,sz)){
                    int at=y-first;NATIVE_SECTIONS[at]=(int)NATIVE_SECTIONS[at]|1<<(x*4+z);covered=true;
                }
            }
        }
        if(covered){
            shader.safeGetUniform("NativeBaseY").set((float)(first-(draw.y>>4)));
            shader.safeGetUniform("NativeSections").set(NATIVE_SECTIONS);
        }
        return covered;
    }
    private static int[][] boundaries(long key) {
        int[][] result=new int[6][256];
        for(int axis=0;axis<3;axis++)for(int sign:new int[]{-1,1}){
            long adjacent=neighbor(key,axis,sign);var tile=TILES.get(adjacent);
            boolean air=Hk3WorldFarCapture.knownAir(adjacent);
            for(int u=0;u<16;u++)for(int v=0;v<16;v++){
                int p=sign<0?15:0,index=switch(axis){case 0->Hk3FarMesh.index(p,u,v);case 1->Hk3FarMesh.index(v,p,u);default->Hk3FarMesh.index(u,v,p);};
                int x=BlockPos.getX(adjacent)*16+index/256,y=BlockPos.getY(adjacent)*16+index/16%16,z=BlockPos.getZ(adjacent)*16+index%16;
                int state=tile!=null&&tile.source.known(index)?tile.source.state(index):air?0:Hk3WorldFarTerrain.stateAt(x,y,z);
                if(state<=0)continue;
                if(dynamicMask&&(Hk3W03FieldScenes.hidden(new BlockPos(x,y,z),Block.stateById(state-1))
                        ||Hk3W08FieldScenes.hidden(new BlockPos(x,y,z),Block.stateById(state-1))
                        ||Hk3W10FieldScenes.hidden(new BlockPos(x,y,z),Block.stateById(state-1))||Hk3W12FieldScenes.hidden(new BlockPos(x,y,z),Block.stateById(state-1))||Hk3W11FieldScenes.hidden(new BlockPos(x,y,z),Block.stateById(state-1))||Hk3W13FieldScenes.hidden(new BlockPos(x,y,z),Block.stateById(state-1))||Hk3WonderFxScenes.hidden(new BlockPos(x,y,z),Block.stateById(state-1))))continue;
                var material=MATERIALS.get(state);
                if(material.cube())result[axis*2+(sign>0?1:0)][u*16+v]=material.opaque()?state:-state;
            }
        }
        return result;
    }
    private static boolean hasStructure(Region group){return group.structure;}
    @SubscribeEvent public static void commands(RegisterClientCommandsEvent event) {
        event.getDispatcher().register(net.minecraft.commands.Commands.literal("hk3farview")
                .then(net.minecraft.commands.Commands.literal("status").executes(context->{
                    context.getSource().sendSuccess(()->net.minecraft.network.chat.Component.literal(
                            "HK3GTL分级材质远景："+(Hk3FarViewConfig.ENABLED.get()?"开启":"关闭")+" · 距离 "+Hk3FarViewConfig.DISTANCE.get()
                                    +"格 · 巨构分区 "+members.size()+" · 世界分区 "+Hk3WorldFarCapture.sections()+"（仅本次会话）"
                                    +" · 地表区块 "+Hk3WorldFarTerrain.chunks()
                                    +" · 地表LOD 1/2/4/8/16格批次 "+Hk3WorldFarTerrain.lodStatus()
                                    +" · 网格CPU "+Hk3FarTileMesh.workerStatus()
                                    +" · 世界CPU "+Hk3WorldFarCapture.bytes()/1024+"/8192KiB · 待采区块 "+Hk3WorldFarCapture.pending()
                                    +" · 本帧绘制 "+drawn+"批 · 顶点显存 "+(gpuBytes+Hk3WorldFarTerrain.gpuBytes())/1024+"/"+(Hk3FarViewConfig.GPU_MIB.get()*1024)+"KiB（图集与驱动另计） · 限额等待 "+(REGIONS.values().stream().filter(t->t.limited).count()+Hk3WorldFarTerrain.limited())
                                    +" · 材质降级 "+MATERIALS.limited()),false);
                    return 1;
                }))
                .then(net.minecraft.commands.Commands.literal("on").executes(context->{setEnabled(true);return 1;}))
                .then(net.minecraft.commands.Commands.literal("off").executes(context->{setEnabled(false);return 1;})));

    }
    private static void setEnabled(boolean enabled) {
        if(Hk3FarViewConfig.ENABLED.get()!=enabled){session++;lastDistance=-1;}
        Hk3FarViewConfig.ENABLED.set(enabled);Hk3FarViewConfig.SPEC.save();
        var player=Minecraft.getInstance().player;if(player!=null)player.displayClientMessage(net.minecraft.network.chat.Component.literal("HK3GTL远景已"+(enabled?"开启":"关闭")),false);
    }
    private static double distance(long key,double x,double y,double z){
        double dx=BlockPos.getX(key)*64+32-x,dy=BlockPos.getY(key)*64+32-y,dz=BlockPos.getZ(key)*64+32-z;return dx*dx+dy*dy+dz*dz;
    }
    @Mod.EventBusSubscriber(modid="hk3gtl",value=Dist.CLIENT,bus=Mod.EventBusSubscriber.Bus.MOD)
    public static final class Shaders {
        @SubscribeEvent public static void register(RegisterShadersEvent event) throws java.io.IOException{
            REGIONS.values().forEach(Region::close);REGIONS.values().forEach(Region::invalidate);clearWorks();frameDraws.clear();frameReady=false;Hk3WorldFarTerrain.reload();MATERIALS.close();
            event.registerShader(new ShaderInstance(event.getResourceProvider(),new net.minecraft.resources.ResourceLocation("hk3gtl","farview"),DefaultVertexFormat.POSITION_COLOR_TEX),s->shader=s);
        }
    }
}
