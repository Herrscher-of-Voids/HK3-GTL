package com.sirin.hk3gtl.client.wonder;

import com.mojang.blaze3d.systems.RenderSystem;
import com.mojang.blaze3d.vertex.*;
import com.mojang.logging.LogUtils;
import net.minecraft.client.renderer.ShaderInstance;
import net.minecraft.resources.ResourceLocation;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.client.event.ClientPlayerNetworkEvent;
import net.minecraftforge.client.event.RegisterShadersEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import org.joml.Matrix4f;
import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.CompletableFuture;
import java.util.concurrent.CompletionException;

@Mod.EventBusSubscriber(modid="hk3gtl",value=Dist.CLIENT)
public final class Hk3W07SceneRenderer{
    private static final ResourceLocation ATLAS=new ResourceLocation("hk3gtl","textures/effect/w07_n2_atlas.png");
    private static final int[][][] CORNERS={{{1,0,0},{1,1,0},{1,1,1},{1,0,1}},{{0,0,1},{0,1,1},{0,1,0},{0,0,0}},
            {{1,0,1},{1,1,1},{0,1,1},{0,0,1}},{{0,0,0},{0,1,0},{1,1,0},{1,0,0}},
            {{0,0,1},{0,0,0},{1,0,0},{1,0,1}},{{0,1,0},{0,1,1},{1,1,1},{1,1,0}}};
    private record Batch(int material,VertexBuffer buffer){}
    private static final List<Batch> BUFFERS=new ArrayList<>(),LAYER_BUFFERS=new ArrayList<>();
    private static final BufferBuilder BUILDER=new BufferBuilder(8192*4*24);
    private static ShaderInstance shader;
    private static CompletableFuture<Hk3W07SceneModel> loading;
    private static Hk3W07SceneModel model;
    private static int part,material,face,quad,uploadedLayer=-1;
    private static long vertexBytes,layerBytes;
    private static boolean prepared,failed;
    private static float lightPulse=1;
    private Hk3W07SceneRenderer(){}
    public static boolean ready(){return prepared;}
    public static long vertexBytes(){return vertexBytes+layerBytes;}
    public static boolean preparePreview(){
        if(shader==null||failed)return false;
        if(prepared)return true;
        if(model==null){
            if(loading==null)loading=CompletableFuture.supplyAsync(Hk3W07SceneModel::load);
            if(!loading.isDone())return false;
            try{model=loading.join();}
            catch(CompletionException failure){failed=true;LogUtils.getLogger().error("W07完整场景加载失败",failure);return false;}
            finally{loading=null;}
        }
        long deadline=System.nanoTime()+2_000_000;
        do{if(part==model.parts().length)break;upload();}while(System.nanoTime()<deadline);
        prepared=part==model.parts().length;return prepared;
    }
    public static void drawPreview(int layer,double seconds,boolean effects){
        lightPulse=effects?1.04f+.035f*(float)Math.sin(seconds*1.2):1;
        shader.getUniform("PortsCount").set(0);
        int[] export=model.data().blueprint_to_export_offset_xyz();
        shader.getUniform("ExportOffset").set((float)export[0],(float)export[1],(float)export[2]);
        int[] offset=model.data().blueprint_to_export_offset_xyz(),grid=model.data().atlas_grid();
        var origin=new Matrix4f(RenderSystem.getModelViewMatrix()).translate(offset[0],offset[1],offset[2]);
        var projection=new Matrix4f(RenderSystem.getProjectionMatrix());
        shader.getUniform("AtlasGrid").set((float)grid[0],(float)grid[1]);
        RenderSystem.setShaderTexture(0,ATLAS);RenderSystem.setShaderColor(1,1,1,1);
        RenderSystem.enableDepthTest();RenderSystem.disableCull();RenderSystem.enableBlend();RenderSystem.defaultBlendFunc();
        if(layer>=0&&uploadedLayer!=layer)uploadLayer(layer);
        var batches=layer<0?BUFFERS:LAYER_BUFFERS;
        RenderSystem.depthMask(true);
        for(var batch:batches)if(!model.materials()[batch.material].transparent())drawBatch(batch,origin,projection);
        RenderSystem.depthMask(false);
        for(var batch:batches)if(model.materials()[batch.material].transparent())drawBatch(batch,origin,projection);
        VertexBuffer.unbind();RenderSystem.depthMask(true);RenderSystem.disableBlend();RenderSystem.enableCull();
    }
    static void drawLights(Matrix4f origin,Matrix4f projection,double seconds,Hk3W11Ports ports){
        if(!preparePreview())return;
        int[] grid=model.data().atlas_grid(),offset=model.data().blueprint_to_export_offset_xyz();
        shader.getUniform("AtlasGrid").set((float)grid[0],(float)grid[1]);
        shader.getUniform("ExportOffset").set((float)offset[0],(float)offset[1],(float)offset[2]);
        shader.getUniform("PortsCount").set(ports.count());
        shader.getUniform("Glow").set(.055f+.025f*(float)Math.sin(seconds*1.2));
        RenderSystem.setShaderTexture(0,ATLAS);RenderSystem.setShaderTexture(1,ports.textureId());
        RenderSystem.setShaderColor(1,1,1,1);RenderSystem.enableDepthTest();RenderSystem.disableCull();
        RenderSystem.depthMask(false);RenderSystem.enableBlend();
        RenderSystem.blendFunc(com.mojang.blaze3d.platform.GlStateManager.SourceFactor.SRC_ALPHA,com.mojang.blaze3d.platform.GlStateManager.DestFactor.ONE);
        RenderSystem.enablePolygonOffset();RenderSystem.polygonOffset(-1,-1);
        for(var batch:BUFFERS)if(model.materials()[batch.material].emissive()){
            batch.buffer.bind();batch.buffer.drawWithShader(origin,projection,shader);
        }
        VertexBuffer.unbind();RenderSystem.polygonOffset(0,0);RenderSystem.disablePolygonOffset();
        RenderSystem.defaultBlendFunc();RenderSystem.disableBlend();RenderSystem.depthMask(true);RenderSystem.enableCull();
    }
    private static void drawBatch(Batch batch,Matrix4f origin,Matrix4f projection){
        shader.getUniform("Glow").set(model.materials()[batch.material].emissive()?1.15f*lightPulse:1f);
        batch.buffer.bind();batch.buffer.drawWithShader(origin,projection,shader);
    }
    private static void uploadLayer(int layer){
        LAYER_BUFFERS.forEach(batch->batch.buffer.close());LAYER_BUFFERS.clear();uploadedLayer=layer;layerBytes=0;
        int y=layer-model.data().blueprint_to_export_offset_xyz()[1];
        var rectangles=model.layers()[layer].rectangles();
        for(int m=0;m<model.materials().length;m++){
            int count=0;BUILDER.begin(VertexFormat.Mode.QUADS,DefaultVertexFormat.POSITION_COLOR_TEX);
            for(int[] r:rectangles)if(r[0]==m){
                for(int[] c:CORNERS[5])BUILDER.vertex(r[1]+c[0]*r[3],y+1,r[2]+c[2]*r[4]).color(255,255,255,model.materials()[m].transparent()?148:255)
                        .uv((m*6+5)*2048f+c[0]*r[3],c[2]*r[4]).endVertex();
                count++;
            }
            layerBytes+=finishBatch(LAYER_BUFFERS,m,count);
        }
    }
    private static long finishBatch(List<Batch> target,int state,int count){
        var rendered=BUILDER.end();
        if(count==0){rendered.release();return 0;}
        var buffer=new VertexBuffer(VertexBuffer.Usage.STATIC);buffer.bind();buffer.upload(rendered);VertexBuffer.unbind();target.add(new Batch(state,buffer));
        return count*4L*24;
    }
    private static void upload(){
        int state=material,count=0;var source=model.parts()[part];int[] size=source.size(),origin=source.origin();var info=model.materials()[material];
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
        vertexBytes+=finishBatch(BUFFERS,state,count);
        if(face==6){face=0;material++;if(material==model.materials().length){material=0;part++;}}
    }
    private static void clear(){
        prepared=false;BUFFERS.forEach(batch->batch.buffer.close());BUFFERS.clear();LAYER_BUFFERS.forEach(batch->batch.buffer.close());LAYER_BUFFERS.clear();
        uploadedLayer=-1;vertexBytes=layerBytes=0;
        if(loading!=null)loading.cancel(true);
        loading=null;model=null;part=material=face=quad=0;failed=false;Hk3W07SceneModel.clearMetadata();
    }
    @SubscribeEvent public static void logout(ClientPlayerNetworkEvent.LoggingOut event){clear();}
    @Mod.EventBusSubscriber(modid="hk3gtl",value=Dist.CLIENT,bus=Mod.EventBusSubscriber.Bus.MOD)
    public static final class Resources{
        @SubscribeEvent public static void shaders(RegisterShadersEvent event)throws java.io.IOException{
            clear();event.registerShader(new ShaderInstance(event.getResourceProvider(),new ResourceLocation("hk3gtl","w07_n2"),DefaultVertexFormat.POSITION_COLOR_TEX),value->shader=value);
        }
    }
}
