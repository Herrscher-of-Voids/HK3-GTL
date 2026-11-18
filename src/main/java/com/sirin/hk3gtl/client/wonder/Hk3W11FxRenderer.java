package com.sirin.hk3gtl.client.wonder;

import com.mojang.blaze3d.systems.RenderSystem;
import com.mojang.blaze3d.vertex.*;
import com.mojang.logging.LogUtils;
import net.minecraft.client.Minecraft;
import net.minecraft.client.renderer.GameRenderer;
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
public final class Hk3W11FxRenderer{
    private static final ResourceLocation ATLAS=new ResourceLocation("hk3gtl","textures/effect/w11_f5_atlas.png");
    private static final int[][][] CORNERS={{{1,0,0},{1,1,0},{1,1,1},{1,0,1}},{{0,0,1},{0,1,1},{0,1,0},{0,0,0}},
            {{1,0,1},{1,1,1},{0,1,1},{0,0,1}},{{0,0,0},{0,1,0},{1,1,0},{1,0,0}},
            {{0,0,1},{0,0,0},{1,0,0},{1,0,1}},{{0,1,0},{0,1,1},{1,1,1},{1,1,0}}};
    private record Batch(int part,int material,VertexBuffer buffer){}
    private static final List<Batch> BUFFERS=new ArrayList<>();
    private static final List<Batch> LAYER_BUFFERS=new ArrayList<>();
    private static final BufferBuilder BUILDER=new BufferBuilder(8192*4*24);
    private static ShaderInstance shader;
    private static CompletableFuture<Hk3W11FxModel> loading, loadingLayers;
    private static Hk3W11FxModel model, layerModel;
    private static Hk3W11Puppetry puppetry;
    private static Hk3W11Ports previewPorts;
    private static VertexBuffer strings;
    private static int part,material,face,quad;
    private static int uploadedLayer=-10000;
    private static long vertexBytes;
    private static long layerBytes;
    private static volatile boolean prepared;
    private static boolean failed, layersFailed;
    private Hk3W11FxRenderer(){}
    public static boolean ready(){return prepared;}
    public static Hk3W11FxModel.Data data(){return model.data();}
    public static long vertexBytes(){return vertexBytes+layerBytes;}
    public static boolean previewReady(int layer){return layer<0?prepared:layerModel!=null;}
    public static boolean previewFailed(int layer){return shader==null||(layer<0?failed:layersFailed);}
    public static boolean preparePreview(int layer){
        if(shader==null)return false;
        if(layer<0)return prepare()||!BUFFERS.isEmpty();
        if(layerModel!=null)return true;
        if(layersFailed)return false;
        if(loadingLayers==null)loadingLayers=loadAsync(Hk3W11FxModel::loadLayers,"剖面");
        if(!loadingLayers.isDone())return false;
        layerModel=loadingLayers.join();loadingLayers=null;layersFailed=layerModel==null;
        return !layersFailed;
    }
    private static CompletableFuture<Hk3W11FxModel> loadAsync(java.util.function.Supplier<Hk3W11FxModel> source,String kind){
        return CompletableFuture.supplyAsync(source).exceptionally(failure->{
            LogUtils.getLogger().error("W11{}资源加载失败",kind,failure);return null;
        });
    }
    private static boolean prepare(){
        if(prepared)return true;
        if(failed)return false;
        if(model==null){
            if(loading==null)loading=loadAsync(Hk3W11FxModel::load,"总览与动画");
            if(!loading.isDone())return false;
            model=loading.join();loading=null;
            if(model==null){failed=true;return false;}
            puppetry=new Hk3W11Puppetry(model);
        }
        long deadline=System.nanoTime()+2_000_000;
        do{if(part==model.parts().length)break;upload();}while(System.nanoTime()<deadline);
        if(part==model.parts().length){prepared=true;var mc=Minecraft.getInstance();if(mc.level!=null&&!Hk3W11FieldScenes.scenes().isEmpty())mc.levelRenderer.allChanged();}
        return prepared;
    }
    public static void drawPreview(double seconds,boolean animate,int layer){
        var data=layer<0?model.data():layerModel.data();
        int[] offset=data.blueprint_to_export_offset_xyz();
        var origin=new Matrix4f(RenderSystem.getModelViewMatrix()).translate(offset[0],offset[1],offset[2]);
        var projection=new Matrix4f(RenderSystem.getProjectionMatrix());
        if(previewPorts==null)previewPorts=new Hk3W11Ports(new int[0]);
        RenderSystem.setShaderTexture(1,previewPorts.textureId());shader.getUniform("PortsCount").set(0);
        if(layer<0){draw(origin,projection,animate?seconds:0,true);return;}
        begin(data,layer-offset[1]);
        drawLayer(origin,projection,layer);
        end();
    }
    @SubscribeEvent public static void render(RenderLevelStageEvent event){
        if(event.getStage()!=RenderLevelStageEvent.Stage.AFTER_TRANSLUCENT_BLOCKS)return;
        Hk3W11FieldScenes.maintain();var mc=Minecraft.getInstance();
        if(mc.level==null||shader==null||Hk3W11FieldScenes.scenes().isEmpty()||!prepare()||!Hk3W11FieldScenes.active())return;
        var camera=event.getCamera().getPosition();var projection=new Matrix4f(event.getProjectionMatrix());
        for(var scene:Hk3W11FieldScenes.scenes()){
            var state=scene.state();var pos=state.pos();
            if(camera.distanceToSqr(pos.getX(),pos.getY(),pos.getZ())>3500d*3500)continue;
            float angle=switch(state.facing()){case NORTH->(float)Math.PI;case EAST->(float)Math.PI/2;case WEST->-(float)Math.PI/2;default->0;};
            var origin=new Matrix4f(event.getPoseStack().last().pose()).translate((float)(pos.getX()-camera.x),(float)(pos.getY()-camera.y),(float)(pos.getZ()-camera.z));
            origin.translate(.5f,0,.5f).rotateY(angle).translate(-.5f,0,-.5f);
            int[] control=model.data().controller_blueprint();origin.translate(-control[0],-control[1],-control[2]);
            double seconds=state.seconds()+(state.running()?(mc.level.getGameTime()-state.epoch()+event.getPartialTick())/20.:0);
            RenderSystem.setShaderTexture(1,scene.ports().textureId());shader.getUniform("PortsCount").set(scene.ports().count());
            draw(origin,projection,seconds,false);
        }
    }
    private static void begin(Hk3W11FxModel.Data data,int layer){
        int[] offset=data.blueprint_to_export_offset_xyz(),grid=data.atlas_grid();
        shader.getUniform("ExportOffset").set((float)offset[0],(float)offset[1],(float)offset[2]);
        shader.getUniform("AtlasGrid").set((float)grid[0],(float)grid[1]);shader.getUniform("LayerY").set((float)layer);
        RenderSystem.setShaderTexture(0,ATLAS);RenderSystem.setShaderColor(1,1,1,1);
        RenderSystem.enableDepthTest();RenderSystem.disableCull();RenderSystem.enableBlend();RenderSystem.defaultBlendFunc();RenderSystem.depthMask(true);
    }
    private static void end(){
        RenderSystem.depthMask(true);RenderSystem.disableBlend();RenderSystem.enableCull();
    }
    private static void draw(Matrix4f origin,Matrix4f projection,double seconds,boolean full){
        var frame=puppetry.frame(seconds);
        begin(model.data(),-10000);
        for(var batch:BUFFERS)if(!model.materials()[batch.material].transparent()&&(full||model.parts()[batch.part].metadata().dynamic()))drawBatch(batch,frame.transforms(),origin,projection);
        RenderSystem.depthMask(false);
        for(var batch:BUFFERS)if(model.materials()[batch.material].transparent()&&(full||model.parts()[batch.part].metadata().dynamic()))drawBatch(batch,frame.transforms(),origin,projection);
        VertexBuffer.unbind();
        drawStrings(frame.threads(),origin,projection);
        end();
    }
    private static void drawBatch(Batch batch,Matrix4f[] transforms,Matrix4f origin,Matrix4f projection){
        shader.getUniform("PartTransform").set(transforms[batch.part]);shader.getUniform("Glow").set(model.materials()[batch.material].emissive()?1.15f:1f);
        batch.buffer.bind();batch.buffer.drawWithShader(new Matrix4f(origin).mul(transforms[batch.part]),projection,shader);
    }
    private static void drawLayer(Matrix4f origin,Matrix4f projection,int layer){
        int exportY=layer-layerModel.data().blueprint_to_export_offset_xyz()[1];
        if(uploadedLayer!=layer){
            LAYER_BUFFERS.forEach(b->b.buffer.close());LAYER_BUFFERS.clear();uploadedLayer=layer;layerBytes=0;
            var rectangles=layerModel.layers()[layer].rectangles();
            for(int m=0;m<layerModel.materials().length;m++){
                int count=0;BUILDER.begin(VertexFormat.Mode.QUADS,DefaultVertexFormat.POSITION_COLOR_TEX);
                for(int[] r:rectangles)if(r[0]==m){
                    for(int[] c:CORNERS[5])BUILDER.vertex(r[1]+c[0]*r[3],exportY+1,r[2]+c[2]*r[4]).color(255,255,255,255)
                            .uv((m*6+5)*2048f+c[0]*r[3],c[2]*r[4]).endVertex();
                    count++;
                }
                var rendered=BUILDER.end();
                if(count>0){var buffer=new VertexBuffer(VertexBuffer.Usage.STATIC);buffer.bind();buffer.upload(rendered);VertexBuffer.unbind();LAYER_BUFFERS.add(new Batch(0,m,buffer));layerBytes+=count*4L*24;}else rendered.release();
            }
        }
        shader.getUniform("PartTransform").set(new Matrix4f());
        for(var batch:LAYER_BUFFERS){shader.getUniform("Glow").set(layerModel.materials()[batch.material].emissive()?1.15f:1f);batch.buffer.bind();batch.buffer.drawWithShader(origin,projection,shader);}
        VertexBuffer.unbind();
    }
    private static void drawStrings(Hk3W11Puppetry.Thread[] lines,Matrix4f origin,Matrix4f projection){
        BUILDER.begin(VertexFormat.Mode.DEBUG_LINES,DefaultVertexFormat.POSITION_COLOR);
        for(var line:lines){
            BUILDER.vertex(line.top().x,line.top().y,line.top().z).color(255,215,129,217).endVertex();
            BUILDER.vertex(line.bottom().x,line.bottom().y,line.bottom().z).color(255,215,129,217).endVertex();
        }
        if(strings==null)strings=new VertexBuffer(VertexBuffer.Usage.DYNAMIC);
        RenderSystem.lineWidth(1);strings.bind();strings.upload(BUILDER.end());strings.drawWithShader(origin,projection,GameRenderer.getPositionColorShader());VertexBuffer.unbind();
    }
    private static void upload(){
        int batchPart=part,batchMaterial=material,count=0;var source=model.parts()[part];int[] size=source.size(),origin=source.origin();var info=model.materials()[material];
        while(face<6&&source.starts()[material][face].length==0)face++;
        if(face==6){nextMaterial();return;}
        BUILDER.begin(VertexFormat.Mode.QUADS,DefaultVertexFormat.POSITION_COLOR_TEX);
        while(face<6&&count<8192){
            int[] starts=source.starts()[material][face];
            if(quad==starts.length){quad=0;face++;continue;}
            int at=starts[quad],repeat=source.lengths()[material][face][quad],span=source.spans()[material][face][quad];
            int x=at%size[0]+origin[0],y=at/(size[0]*size[2])+origin[1],z=at/size[0]%size[2]+origin[2];
            int axis=face<2?2:0,cross=face<4?1:2,slot=material*6+face,color=info.emissive()?255:face==5?255:face==4?155:face<2?205:230;
            for(int[] c:CORNERS[face])BUILDER.vertex(x+c[0]*(axis==0?repeat:cross==0?span:1),y+c[1]*(axis==1?repeat:cross==1?span:1),z+c[2]*(axis==2?repeat:cross==2?span:1))
                    .color(color,color,color,info.transparent()?148:255).uv(slot*2048f+c[axis]*repeat,c[cross]*span).endVertex();
            quad++;count++;
        }
        var rendered=BUILDER.end();
        if(count>0){var buffer=new VertexBuffer(VertexBuffer.Usage.STATIC);buffer.bind();buffer.upload(rendered);VertexBuffer.unbind();BUFFERS.add(new Batch(batchPart,batchMaterial,buffer));vertexBytes+=count*4L*24;}else rendered.release();
        if(face==6)nextMaterial();
    }
    private static void nextMaterial(){
        face=0;if(++material==model.materials().length){material=0;part++;}
    }
    private static void clear(){
        prepared=false;BUFFERS.forEach(batch->batch.buffer.close());BUFFERS.clear();
        LAYER_BUFFERS.forEach(batch->batch.buffer.close());LAYER_BUFFERS.clear();uploadedLayer=-10000;vertexBytes=layerBytes=0;
        if(strings!=null){strings.close();strings=null;}
        if(previewPorts!=null){previewPorts.close();previewPorts=null;}
        if(loading!=null)loading.cancel(true);
        if(loadingLayers!=null)loadingLayers.cancel(true);
        loading=loadingLayers=null;model=layerModel=null;puppetry=null;part=material=face=quad=0;failed=layersFailed=false;Hk3W11FxModel.clearMetadata();
        var mc=Minecraft.getInstance();if(mc.level!=null)mc.levelRenderer.allChanged();
    }
    @SubscribeEvent public static void logout(ClientPlayerNetworkEvent.LoggingOut event){Hk3W11FieldScenes.clear();clear();}
    @Mod.EventBusSubscriber(modid="hk3gtl",value=Dist.CLIENT,bus=Mod.EventBusSubscriber.Bus.MOD)
    public static final class Resources{
        @SubscribeEvent public static void shaders(RegisterShadersEvent event)throws java.io.IOException{
            clear();event.registerShader(new ShaderInstance(event.getResourceProvider(),new ResourceLocation("hk3gtl","w11_f5"),DefaultVertexFormat.POSITION_COLOR_TEX),value->shader=value);
        }
    }
}
