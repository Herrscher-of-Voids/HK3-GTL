package com.sirin.hk3gtl.client.farview;

import com.mojang.blaze3d.systems.RenderSystem;
import com.mojang.blaze3d.vertex.*;
import com.sirin.hk3gtl.common.farview.*;
import com.sirin.hk3gtl.common.network.Hk3Network;
import net.minecraft.client.Minecraft;
import net.minecraft.client.multiplayer.ClientLevel;
import net.minecraft.client.renderer.ShaderInstance;
import net.minecraft.client.renderer.FogRenderer;
import net.minecraft.client.renderer.culling.Frustum;
import net.minecraft.client.renderer.texture.DynamicTexture;
import net.minecraft.core.BlockPos;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.level.material.FogType;
import net.minecraft.world.phys.AABB;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.client.event.*;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import org.joml.Matrix4f;
import java.util.*;


/** 精确静态表面远景；同原版投影、近处遮罩、深度偏移与分帧上传共同保护交接。 */
@Mod.EventBusSubscriber(modid="hk3gtl",value=Dist.CLIENT)
public final class Hk3FarViewRenderer {
    private static final Map<Long,Tile> TILES=new HashMap<>();
    private static final Map<Long,Region> REGIONS=new HashMap<>();
    private static Hk3FarBatchWork work;
    private static final Hk3FarMaterials MATERIALS=new Hk3FarMaterials();
    private static Set<Long> members=Set.of();
    private static List<Map.Entry<Long,Region>> sorted=List.of();
    private static ClientLevel level;
    private static ShaderInstance shader;
    private static DynamicTexture mask;
    private static int maskX,maskZ,ticks,lastDistance=-1,drawn;
    private static boolean lastEnabled,maskValid,resort;
    private static long gpuBytes,session;
    private static final int MASK=128;
    private static final class Tile {
        Hk3FarSection.Snapshot section;
        Tile(Hk3FarSection.Snapshot section){this.section=section;}
    }
    private static final class Region {
        final Set<Long> sections=new HashSet<>();
        Hk3FarTileMesh mesh;
        long revision,built=-1;
        boolean limited;
        void invalidate(){revision++;limited=false;}
        void close(){if(mesh!=null){gpuBytes-=mesh.bytes;mesh.close();mesh=null;}}
    }
    private static long region(long key){return BlockPos.asLong(BlockPos.getX(key)>>2,BlockPos.getY(key)>>2,BlockPos.getZ(key)>>2);}
    private static void invalidate(long key){var group=REGIONS.get(region(key));if(group!=null)group.invalidate();}
    private Hk3FarViewRenderer() {}
    public static void accept(Hk3FarViewPacket packet) {
        var mc=Minecraft.getInstance();
        if(mc.level==null||!packet.dimension().equals(mc.level.dimension().location()))return;
        if(level!=mc.level){clear();level=mc.level;}
        if(packet.members()!=null){
            Set<Long> selected=new HashSet<>();for(long key:packet.members())selected.add(key);members=selected;
            var iterator=TILES.entrySet().iterator();
            while(iterator.hasNext()){
                var entry=iterator.next();if(!members.contains(entry.getKey())){
                    long key=entry.getKey();var group=REGIONS.get(region(key));group.sections.remove(key);group.invalidate();
                    iterator.remove();invalidateNeighbors(key);
                    if(group.sections.isEmpty()){group.close();REGIONS.remove(region(key));if(work!=null&&work.key==region(key))work=null;}
                }
            }
            resort=true;
        }
        for(var update:packet.updates())if(members.contains(update.key())) {
            var tile=TILES.computeIfAbsent(update.key(),key->new Tile(update.section()));
            tile.section=update.section();
            var group=REGIONS.computeIfAbsent(region(update.key()),key->new Region());group.sections.add(update.key());group.invalidate();
            invalidateNeighbors(update.key());resort=true;
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
        REGIONS.values().forEach(Region::close);REGIONS.clear();work=null;TILES.clear();members=Set.of();sorted=List.of();MATERIALS.close();
        level=null;lastDistance=-1;maskValid=false;session++;resort=true;
    }
    @SubscribeEvent public static void logout(ClientPlayerNetworkEvent.LoggingOut event){clear();}
    @SubscribeEvent public static void tick(TickEvent.ClientTickEvent event) {
        if(event.phase!=TickEvent.Phase.END)return;
        var mc=Minecraft.getInstance();if(mc.level==null||mc.player==null)return;
        if(level!=mc.level){clear();level=mc.level;}
        boolean enabled=Hk3FarViewConfig.ENABLED.get();int distance=Hk3FarViewConfig.DISTANCE.get();ticks++;
        if(lastDistance!=distance||lastEnabled!=enabled||ticks%100==0){
            Hk3Network.CHANNEL.sendToServer(new Hk3FarViewPacket.Request(enabled,distance,session));lastDistance=distance;lastEnabled=enabled;
            if(!enabled){REGIONS.values().forEach(Region::close);REGIONS.values().forEach(Region::invalidate);work=null;}
        }
        if(enabled&&ticks%5==0)updateMask(mc);
        if(ticks%10==0){resort=true;REGIONS.values().forEach(group->{if(group.limited)group.invalidate();});}
    }
    private static void updateMask(Minecraft mc) {
        if(mask==null){mask=new DynamicTexture(MASK,MASK,false);mc.getTextureManager().register("hk3gtl_far_chunk_mask",mask);}
        maskX=(mc.player.blockPosition().getX()>>4)-MASK/2;maskZ=(mc.player.blockPosition().getZ()>>4)-MASK/2;
        var pixels=mask.getPixels();if(pixels==null)return;int renderDistance=mc.options.getEffectiveRenderDistance();
        for(int x=0;x<MASK;x++)for(int z=0;z<MASK;z++)
            pixels.setPixelRGBA(x,z,Hk3FarViewMask.covered(mc.level.getChunkSource().hasChunk(maskX+x,maskZ+z),
                    x-MASK/2,z-MASK/2,renderDistance)?0xffffffff:0xff000000);
        mask.upload();maskValid=true;
    }
    @SubscribeEvent public static void fog(ViewportEvent.RenderFog event) {
        var mc=Minecraft.getInstance();
        if(event.getMode()!=FogRenderer.FogMode.FOG_TERRAIN||event.getType()!=FogType.NONE
                ||!Hk3FarViewConfig.ENABLED.get()||TILES.isEmpty()||mc.level==null||level!=mc.level||mc.player==null
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
        if(event.getStage()!=RenderLevelStageEvent.Stage.AFTER_TRANSLUCENT_BLOCKS)return;drawn=0;
        if(shader==null||!Hk3FarViewConfig.ENABLED.get()||TILES.isEmpty())return;
        var mc=Minecraft.getInstance();
        if(mc.level==null||mc.level!=level||mc.player==null||event.getCamera().getFluidInCamera()!=FogType.NONE
                ||mc.player.hasEffect(MobEffects.BLINDNESS)||mc.player.hasEffect(MobEffects.DARKNESS))return;
        if(mask==null||!maskValid)updateMask(mc);
        var camera=event.getCamera().getPosition();int distance=Hk3FarViewConfig.DISTANCE.get();
        if(resort){sorted=REGIONS.entrySet().stream().sorted(Comparator.comparingDouble(e->distance(e.getKey(),camera.x,camera.y,camera.z))).toList();resort=false;}
        // 投影直接复用原版；Mixin统一延长远裁面，不能给同一深度缓冲另造投影。
        Matrix4f projection=new Matrix4f(event.getProjectionMatrix());
        var frustum=new Frustum(event.getPoseStack().last().pose(),projection);frustum.prepare(camera.x,camera.y,camera.z);
        var visible=sorted.stream().filter(e->{
            long key=e.getKey();int x=BlockPos.getX(key)*64,y=BlockPos.getY(key)*64,z=BlockPos.getZ(key)*64;
            return distance(key,camera.x,camera.y,camera.z)<(double)(distance+64)*(distance+64)
                    &&frustum.isVisible(new AABB(x,y,z,x+64,y+64,z+64))&&!nativeCovered(key,mc,camera.x,camera.y,camera.z);
        }).toList();
        long budget=(long)Hk3FarViewConfig.GPU_MIB.get()*1024*1024;
        for(int i=sorted.size()-1;gpuBytes>budget&&i>=0;i--){var group=sorted.get(i).getValue();group.close();group.invalidate();}
        if(work==null)for(var entry:visible){
            var group=entry.getValue();if(group.built==group.revision||group.limited)continue;
            var sections=group.sections.stream().sorted().map(key->new Hk3FarBatchWork.Section(key,TILES.get(key).section)).toList();
            work=new Hk3FarBatchWork(entry.getKey(),group.revision,sections);break;
        }
        if(work!=null)try {
            if(work.advance(MATERIALS,Hk3FarViewRenderer::boundaries)) {
                var group=REGIONS.get(work.key);
                if(group!=null){
                    long required=Hk3FarTileMesh.estimate(work.pieces,MATERIALS);
                    for(int i=sorted.size()-1;gpuBytes-(group.mesh==null?0:group.mesh.bytes)+required>budget&&i>=0;i--) {
                        var candidate=sorted.get(i);var other=candidate.getValue();
                        if(other!=group&&other.mesh!=null&&distance(candidate.getKey(),camera.x,camera.y,camera.z)>distance(work.key,camera.x,camera.y,camera.z)){
                            other.close();other.built=other.revision;other.limited=true;
                        }
                    }
                    var mesh=Hk3FarTileMesh.upload(work.pieces,MATERIALS,budget-gpuBytes+(group.mesh==null?0:group.mesh.bytes));
                    if(mesh==null){group.limited=true;}
                    else {group.close();group.mesh=mesh;gpuBytes+=mesh.bytes;group.built=work.revision;}
                }
                work=null;
            }
        }catch(RuntimeException failure){
            var group=REGIONS.get(work.key);if(group!=null)group.built=group.revision;work=null;
            com.mojang.logging.LogUtils.getLogger().error("HK3GTL真实表面远景批次构建失败",failure);
        }
        // 全空气批次也会缓存空网格；没有真实面时尚未创建材质图集。
        if(visible.stream().noneMatch(e->e.getValue().mesh!=null&&e.getValue().mesh.bytes>0))return;
        int previous0=RenderSystem.getShaderTexture(0),previous1=RenderSystem.getShaderTexture(1);
        RenderSystem.setShaderTexture(0,MATERIALS.texture());RenderSystem.setShaderTexture(1,mask.getId());
        shader.safeGetUniform("ChunkOrigin").set((float)maskX,(float)maskZ);
        shader.safeGetUniform("FarLimit").set((float)distance);
        shader.safeGetUniform("NearLimit").set(Math.max(1,mc.options.getEffectiveRenderDistance()-2)*16f);
        shader.safeGetUniform("CameraOrigin").set((float)camera.x,(float)camera.y,(float)camera.z);
        RenderSystem.enableDepthTest();RenderSystem.disableCull();RenderSystem.enablePolygonOffset();RenderSystem.polygonOffset(1,1);
        try{
            for(int pass=0;pass<2;pass++){
                RenderSystem.depthMask(pass==0);
                if(pass==1){RenderSystem.enableBlend();RenderSystem.defaultBlendFunc();}else RenderSystem.disableBlend();
                for(int i=0;i<visible.size();i++){
                    var entry=visible.get(pass==0?i:visible.size()-1-i);var tile=entry.getValue();
                    if(tile.mesh==null||tile.mesh.buffers[pass]==null)continue;
                    long key=entry.getKey();int x=BlockPos.getX(key)*64,y=BlockPos.getY(key)*64,z=BlockPos.getZ(key)*64;
                    Matrix4f view=new Matrix4f(event.getPoseStack().last().pose()).translate((float)(x-camera.x),(float)(y-camera.y),(float)(z-camera.z));
                    shader.safeGetUniform("TileOrigin").set((float)x,(float)y,(float)z);
                    tile.mesh.buffers[pass].bind();tile.mesh.buffers[pass].drawWithShader(view,projection,shader);drawn++;
                }
            }
        }finally{
            VertexBuffer.unbind();RenderSystem.polygonOffset(0,0);RenderSystem.disablePolygonOffset();
            RenderSystem.depthMask(true);RenderSystem.disableBlend();RenderSystem.enableCull();
            RenderSystem.setShaderTexture(0,previous0);RenderSystem.setShaderTexture(1,previous1);
        }
    }
    private static int[][] boundaries(long key) {
        int[][] result=new int[6][256];
        for(int axis=0;axis<3;axis++)for(int sign:new int[]{-1,1}){
            var tile=TILES.get(neighbor(key,axis,sign));if(tile==null)continue;
            for(int u=0;u<16;u++)for(int v=0;v<16;v++){
                int p=sign<0?15:0,index=switch(axis){case 0->Hk3FarMesh.index(p,u,v);case 1->Hk3FarMesh.index(v,p,u);default->Hk3FarMesh.index(u,v,p);};
                int state=tile.section.state(index);if(state==0)continue;var material=MATERIALS.get(state);
                if(material.cube())result[axis*2+(sign>0?1:0)][u*16+v]=material.opaque()?state:-state;
            }
        }
        return result;
    }
    @SubscribeEvent public static void commands(RegisterClientCommandsEvent event) {
        event.getDispatcher().register(net.minecraft.commands.Commands.literal("hk3farview")
                .then(net.minecraft.commands.Commands.literal("status").executes(context->{
                    context.getSource().sendSuccess(()->net.minecraft.network.chat.Component.literal(
                            "HK3GTL逐格材质远景："+(Hk3FarViewConfig.ENABLED.get()?"开启":"关闭")+" · 距离 "+Hk3FarViewConfig.DISTANCE.get()
                                    +"格 · 分区 "+TILES.size()+" · 本帧绘制 "+drawn+"批 · 批次缓存 "+REGIONS.size()+" · 显存 "+gpuBytes/1024+"KiB · 限额等待 "+REGIONS.values().stream().filter(t->t.limited).count()),false);
                    return 1;
                }))
                .then(net.minecraft.commands.Commands.literal("on").executes(context->{setEnabled(true);return 1;}))
                .then(net.minecraft.commands.Commands.literal("off").executes(context->{setEnabled(false);return 1;})));

    }
    private static void setEnabled(boolean enabled) {
        Hk3FarViewConfig.ENABLED.set(enabled);Hk3FarViewConfig.SPEC.save();
        var player=Minecraft.getInstance().player;if(player!=null)player.displayClientMessage(net.minecraft.network.chat.Component.literal("HK3GTL远景已"+(enabled?"开启":"关闭")),false);
    }
    private static boolean nativeCovered(long key,Minecraft mc,double cx,double cy,double cz) {
        int x=BlockPos.getX(key)*64,y=BlockPos.getY(key)*64,z=BlockPos.getZ(key)*64;
        double dx=Math.max(Math.abs(x-cx),Math.abs(x+64-cx)),dy=Math.max(Math.abs(y-cy),Math.abs(y+64-cy)),dz=Math.max(Math.abs(z-cz),Math.abs(z+64-cz));
        double near=Math.max(1,mc.options.getEffectiveRenderDistance()-2)*16d;
        if(dx*dx+dy*dy+dz*dz>=near*near)return false;
        int px=mc.player.blockPosition().getX()>>4,pz=mc.player.blockPosition().getZ()>>4;
        for(int u=0;u<4;u++)for(int v=0;v<4;v++)if(!Hk3FarViewMask.covered(mc.level.getChunkSource().hasChunk((x>>4)+u,(z>>4)+v),
                (x>>4)+u-px,(z>>4)+v-pz,mc.options.getEffectiveRenderDistance()))return false;
        return true;
    }
    private static double distance(long key,double x,double y,double z){
        double dx=BlockPos.getX(key)*64+32-x,dy=BlockPos.getY(key)*64+32-y,dz=BlockPos.getZ(key)*64+32-z;return dx*dx+dy*dy+dz*dz;
    }
    @Mod.EventBusSubscriber(modid="hk3gtl",value=Dist.CLIENT,bus=Mod.EventBusSubscriber.Bus.MOD)
    public static final class Shaders {
        @SubscribeEvent public static void register(RegisterShadersEvent event) throws java.io.IOException{
            REGIONS.values().forEach(Region::close);REGIONS.values().forEach(Region::invalidate);work=null;MATERIALS.close();
            event.registerShader(new ShaderInstance(event.getResourceProvider(),new net.minecraft.resources.ResourceLocation("hk3gtl","farview"),DefaultVertexFormat.POSITION_COLOR_TEX),s->shader=s);
        }
    }
}
