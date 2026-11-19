package com.sirin.hk3gtl.client.wonder;

import com.mojang.blaze3d.systems.RenderSystem;
import com.mojang.blaze3d.vertex.*;
import com.mojang.logging.LogUtils;
import net.minecraft.client.Minecraft;
import net.minecraft.client.renderer.ShaderInstance;
import net.minecraft.resources.ResourceLocation;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.client.event.ClientPlayerNetworkEvent;
import net.minecraftforge.client.event.RegisterShadersEvent;
import net.minecraftforge.client.event.RenderLevelStageEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import org.joml.Matrix4f;
import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.CompletableFuture;

@Mod.EventBusSubscriber(modid="hk3gtl",value=Dist.CLIENT)
public final class Hk3W13FxRenderer{
    private static final ResourceLocation ATLAS=new ResourceLocation("hk3gtl","textures/effect/w13_t2_m1_atlas.png");
    private static final int[][][] CORNERS={{{1,0,0},{1,1,0},{1,1,1},{1,0,1}},{{0,0,1},{0,1,1},{0,1,0},{0,0,0}},
            {{1,0,1},{1,1,1},{0,1,1},{0,0,1}},{{0,0,0},{0,1,0},{1,1,0},{1,0,0}},
            {{0,0,1},{0,0,0},{1,0,0},{1,0,1}},{{0,1,0},{0,1,1},{1,1,1},{1,1,0}}};
    private record Batch(int part,int material,VertexBuffer buffer){}
    private static final List<Batch> BUFFERS=new ArrayList<>(),LAYER_BUFFERS=new ArrayList<>();
    private static final BufferBuilder BUILDER=new BufferBuilder(8192*4*24);
    private static ShaderInstance shader;
    private static CompletableFuture<Hk3W13FxModel> loading,loadingLayers;
    private static Hk3W13FxModel model,layerModel;
    private static Hk3W13Puppetry puppetry;
    private static Hk3W11Ports previewPorts;
    private static int part,material,face,quad,uploadedLayer=-10000;
    private static long vertexBytes,layerBytes;
    private static volatile boolean prepared;
    private static boolean failed,preview,layersFailed;
    private Hk3W13FxRenderer(){}
    public static boolean ready(){return prepared;}
    public static boolean previewReady(int layer){return prepared&&(layer<0?preview:layerModel!=null);}
    public static Hk3W13FxModel.Data data(){return model.data();}
    public static long vertexBytes(){return vertexBytes+layerBytes;}
    public static boolean preparePreview(){return preparePreview(-1);}
    public static boolean preparePreview(int layer){
        if(shader==null)return false;
        if(layer<0&&!preview){clear(false);preview=true;Hk3WonderSectionRefresh.request("W13");}
        return prepare()&&(layer<0||prepareLayers());
    }
    private static boolean prepare(){
        if(prepared)return true;
        if(failed)return false;
        if(model==null){
            if(loading==null)loading=CompletableFuture.supplyAsync(preview?Hk3W13FxModel::loadPreview:Hk3W13FxModel::load).exceptionally(failure->{
                failed=true;LogUtils.getLogger().error("W13动画资源加载失败",failure);return null;
            });
            if(!loading.isDone())return false;
            model=loading.join();loading=null;if(failed)return false;puppetry=new Hk3W13Puppetry(model);
        }
        long deadline=System.nanoTime()+2_000_000;
        do{if(part==model.parts().length)break;upload();}while(System.nanoTime()<deadline);
        if(part==model.parts().length){prepared=true;var mc=Minecraft.getInstance();if(mc.level!=null)Hk3WonderSectionRefresh.request("W13");}
        return prepared;
    }
    private static boolean prepareLayers(){
        if(layerModel!=null)return true;
        if(layersFailed)return false;
        if(loadingLayers==null)loadingLayers=CompletableFuture.supplyAsync(Hk3W13FxModel::loadLayers).exceptionally(failure->{
            layersFailed=true;LogUtils.getLogger().error("W13剖面资源加载失败",failure);return null;
        });
        if(!loadingLayers.isDone())return false;
        layerModel=loadingLayers.join();loadingLayers=null;return !layersFailed;
    }
    public static void drawPreview(double seconds,boolean animate,int layer){
        int[] offset=model.data().blueprint_to_export_offset_xyz();
        var origin=new Matrix4f(RenderSystem.getModelViewMatrix()).translate(offset[0],offset[1],offset[2]);
        if(previewPorts==null)previewPorts=new Hk3W11Ports(new int[0]);
        RenderSystem.setShaderTexture(1,previewPorts.textureId());shader.getUniform("PortsCount").set(0);
        draw(origin,new Matrix4f(RenderSystem.getProjectionMatrix()),seconds,animate,true,layer<0?-10000:layer-offset[1]);
    }
    @SubscribeEvent public static void render(RenderLevelStageEvent event){
        if(event.getStage()!=RenderLevelStageEvent.Stage.AFTER_TRANSLUCENT_BLOCKS)return;
        Hk3W13FieldScenes.maintain();var mc=Minecraft.getInstance();
        if(mc.level==null||shader==null||Hk3W13FieldScenes.scenes().isEmpty()||!prepare()||!Hk3W13FieldScenes.active())return;
        var camera=event.getCamera().getPosition();var projection=new Matrix4f(event.getProjectionMatrix());
        for(var scene:Hk3W13FieldScenes.scenes()){
            var state=scene.state();var pos=state.pos();
            if(!state.running()||camera.distanceToSqr(pos.getX(),pos.getY(),pos.getZ())>3500d*3500)continue;
            float angle=switch(state.facing()){case NORTH->(float)Math.PI;case EAST->(float)Math.PI/2;case WEST->-(float)Math.PI/2;default->0;};
            var origin=new Matrix4f(event.getPoseStack().last().pose()).translate((float)(pos.getX()-camera.x),(float)(pos.getY()-camera.y),(float)(pos.getZ()-camera.z));
            origin.translate(.5f,0,.5f).rotateY(angle).translate(-.5f,0,-.5f);
            int[] control=model.data().controller_blueprint();origin.translate(-control[0],-control[1],-control[2]);
            double seconds=state.seconds()+(mc.level.getGameTime()-state.epoch()+event.getPartialTick())/20.;
            RenderSystem.setShaderTexture(1,scene.ports().textureId());shader.getUniform("PortsCount").set(scene.ports().count());
            draw(origin,projection,seconds,true,false,-10000);
        }
    }
    private static boolean visible(int mode,boolean animate,boolean full){return full?mode==0||(animate?mode>=2:mode==1):animate&&mode>=2;}
    private static void draw(Matrix4f origin,Matrix4f projection,double seconds,boolean animate,boolean full,int layer){
        var transforms=puppetry.frame(animate?seconds:0);int[] offset=model.data().blueprint_to_export_offset_xyz(),grid=model.data().atlas_grid();
        shader.getUniform("ExportOffset").set((float)offset[0],(float)offset[1],(float)offset[2]);
        shader.getUniform("AtlasGrid").set((float)grid[0],(float)grid[1]);shader.getUniform("LayerY").set((float)layer);
        RenderSystem.setShaderTexture(0,ATLAS);RenderSystem.setShaderColor(1,1,1,1);
        RenderSystem.enableDepthTest();RenderSystem.disableCull();RenderSystem.enableBlend();RenderSystem.defaultBlendFunc();RenderSystem.depthMask(true);
        if(layer>-9999){drawLayer(origin,projection,layer);RenderSystem.depthMask(true);RenderSystem.disableBlend();RenderSystem.enableCull();return;}
        for(var batch:BUFFERS)if(!model.materials()[batch.material].transparent()&&visible(model.parts()[batch.part].metadata().mode(),animate,full))drawBatch(batch,transforms,origin,projection);
        RenderSystem.depthMask(false);
        for(var batch:BUFFERS)if(model.materials()[batch.material].transparent()&&visible(model.parts()[batch.part].metadata().mode(),animate,full))drawBatch(batch,transforms,origin,projection);
        VertexBuffer.unbind();RenderSystem.depthMask(true);RenderSystem.disableBlend();RenderSystem.enableCull();
    }
    private static void drawBatch(Batch batch,Matrix4f[] transforms,Matrix4f origin,Matrix4f projection){
        var metadata=model.parts()[batch.part].metadata();
        shader.getUniform("PartTransform").set(transforms[batch.part]);shader.getUniform("RestTransform").set(new Matrix4f().set(metadata.rest_matrix()));
        shader.getUniform("Glow").set(model.materials()[batch.material].emissive()?1.15f:1f);
        batch.buffer.bind();batch.buffer.drawWithShader(new Matrix4f(origin).mul(transforms[batch.part]),projection,shader);
    }
    private static void drawLayer(Matrix4f origin,Matrix4f projection,int layer){
        if(uploadedLayer!=layer){
            LAYER_BUFFERS.forEach(b->b.buffer.close());LAYER_BUFFERS.clear();uploadedLayer=layer;layerBytes=0;
            var rectangles=layerModel.layers()[layer+model.data().blueprint_to_export_offset_xyz()[1]].rectangles();
            for(int m=0;m<model.materials().length;m++){
                int count=0;BUILDER.begin(VertexFormat.Mode.QUADS,DefaultVertexFormat.POSITION_COLOR_TEX);
                for(int[] r:rectangles)if(r[0]==m){
                    for(int[] c:CORNERS[5])BUILDER.vertex(r[1]+c[0]*r[3],layer+1,r[2]+c[2]*r[4]).color(255,255,255,255)
                            .uv((m*6+5)*2048f+c[0]*r[3],c[2]*r[4]).endVertex();
                    count++;
                }
                var rendered=BUILDER.end();
                if(count>0){var buffer=new VertexBuffer(VertexBuffer.Usage.STATIC);buffer.bind();buffer.upload(rendered);VertexBuffer.unbind();LAYER_BUFFERS.add(new Batch(0,m,buffer));layerBytes+=count*4L*24;}else rendered.release();
            }
        }
        shader.getUniform("PartTransform").set(new Matrix4f());shader.getUniform("RestTransform").set(new Matrix4f());
        for(var batch:LAYER_BUFFERS){shader.getUniform("Glow").set(model.materials()[batch.material].emissive()?1.15f:1f);batch.buffer.bind();batch.buffer.drawWithShader(origin,projection,shader);}
        VertexBuffer.unbind();
    }
    private static void upload(){
        int batchPart=part,batchMaterial=material,count=0;var source=model.parts()[part];int[] size=source.size();float[] origin=source.origin();var info=model.materials()[material];
        BUILDER.begin(VertexFormat.Mode.QUADS,DefaultVertexFormat.POSITION_COLOR_TEX);
        while(face<6&&count<8192){
            int[] starts=source.starts()[material][face];
            if(quad==starts.length){quad=0;face++;continue;}
            int at=starts[quad],repeat=source.lengths()[material][face][quad],span=source.spans()[material][face][quad];
            float x=at%size[0]+origin[0],y=at/(size[0]*size[2])+origin[1],z=at/size[0]%size[2]+origin[2];
            int axis=face<2?2:0,cross=face<4?1:2,slot=material*6+face,color=info.emissive()?255:face==5?255:face==4?155:face<2?205:230;
            for(int[] c:CORNERS[face])BUILDER.vertex(x+c[0]*(axis==0?repeat:cross==0?span:1),y+c[1]*(axis==1?repeat:cross==1?span:1),z+c[2]*(axis==2?repeat:cross==2?span:1))
                    .color(color,color,color,info.transparent()?148:255).uv(slot*2048f+c[axis]*repeat,c[cross]*span).endVertex();
            quad++;count++;
        }
        var rendered=BUILDER.end();
        if(count>0){var buffer=new VertexBuffer(VertexBuffer.Usage.STATIC);buffer.bind();buffer.upload(rendered);VertexBuffer.unbind();BUFFERS.add(new Batch(batchPart,batchMaterial,buffer));vertexBytes+=count*4L*24;}else rendered.release();
        if(face==6){face=0;material++;if(material==model.materials().length){material=0;part++;}}
    }
    private static void clear(boolean refresh){
        prepared=false;BUFFERS.forEach(batch->batch.buffer.close());BUFFERS.clear();LAYER_BUFFERS.forEach(batch->batch.buffer.close());LAYER_BUFFERS.clear();uploadedLayer=-10000;vertexBytes=layerBytes=0;
        if(previewPorts!=null){previewPorts.close();previewPorts=null;}
        if(loading!=null)loading.cancel(true);
        if(loadingLayers!=null)loadingLayers.cancel(true);
        loading=loadingLayers=null;model=layerModel=null;puppetry=null;part=material=face=quad=0;failed=preview=layersFailed=false;Hk3W13FxModel.clearMetadata();
        var mc=Minecraft.getInstance();if(refresh&&mc.level!=null)mc.levelRenderer.allChanged();
    }
    @SubscribeEvent public static void logout(ClientPlayerNetworkEvent.LoggingOut event){Hk3W13FieldScenes.clear();clear(false);}
    @Mod.EventBusSubscriber(modid="hk3gtl",value=Dist.CLIENT,bus=Mod.EventBusSubscriber.Bus.MOD)
    public static final class Resources{
        @SubscribeEvent public static void shaders(RegisterShadersEvent event)throws java.io.IOException{
            clear(true);event.registerShader(new ShaderInstance(event.getResourceProvider(),new ResourceLocation("hk3gtl","w13_t2_m1"),DefaultVertexFormat.POSITION_COLOR_TEX),value->shader=value);
        }
    }
}
