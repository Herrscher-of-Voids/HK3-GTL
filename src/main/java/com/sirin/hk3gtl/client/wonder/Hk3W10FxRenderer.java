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
import org.joml.Vector3f;
import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.CompletableFuture;

@Mod.EventBusSubscriber(modid="hk3gtl",value=Dist.CLIENT)
public final class Hk3W10FxRenderer {
    private static final ResourceLocation ATLAS=new ResourceLocation("hk3gtl","textures/effect/w10_a3_atlas.png");
    private static final int[][][] CORNERS={{{1,0,0},{1,1,0},{1,1,1},{1,0,1}},{{0,0,1},{0,1,1},{0,1,0},{0,0,0}},
            {{1,0,1},{1,1,1},{0,1,1},{0,0,1}},{{0,0,0},{0,1,0},{1,1,0},{1,0,0}},
            {{0,0,1},{0,0,0},{1,0,0},{1,0,1}},{{0,1,0},{0,1,1},{1,1,1},{1,1,0}}};
    private record Batch(int part,int material,VertexBuffer buffer) {}
    private static final List<Batch> BUFFERS=new ArrayList<>();
    private static final BufferBuilder BUILDER=new BufferBuilder(8192*4*24);
    private static ShaderInstance shader;
    private static CompletableFuture<Hk3W10FxModel> loading;
    private static Hk3W10FxModel model;
    private static Hk3W08Ports previewPorts;
    private static int partIndex,materialIndex,faceIndex,quadIndex;
    private static volatile boolean prepared;
    private static boolean failed;
    private Hk3W10FxRenderer(){}
    public static boolean ready(){return prepared;}
    public static boolean preparePreview(){
        if(shader==null||failed||!prepare())return false;
        if(previewPorts==null)previewPorts=new Hk3W08Ports(new int[0]);
        return true;
    }
    public static void drawPreview(double seconds){
        int[] offset=model.data().blueprint_to_export_offset_xyz();
        var origin=new Matrix4f(RenderSystem.getModelViewMatrix()).translate(offset[0],offset[1],offset[2]);
        var projection=new Matrix4f(RenderSystem.getProjectionMatrix());
        var inverse=new Matrix4f(origin).invert();
        var right=inverse.transformDirection(new Vector3f(1,0,0)).normalize();
        var up=inverse.transformDirection(new Vector3f(0,1,0)).normalize();
        RenderSystem.setShaderTexture(1,previewPorts.textureId());shader.getUniform("PortsCount").set(0);
        draw(origin,projection,seconds*1.8,seconds,true);
        Hk3W10Gravity.draw(model,origin,projection,right,up,seconds*1.8,seconds,10,true);
    }
    static Hk3W10FxModel.Data data(){return model.data();}
    private static boolean prepare(){
        if(prepared)return true;
        if(model==null){
            if(loading==null)loading=CompletableFuture.supplyAsync(Hk3W10FxModel::load).exceptionally(failure->{
                failed=true;LogUtils.getLogger().error("W10 A3动画资源加载失败",failure);return null;
            });
            if(!loading.isDone())return false;
            model=loading.join();loading=null;if(failed)return false;
        }
        long deadline=System.nanoTime()+2_000_000;
        do{if(partIndex==model.parts().length)break;upload();}while(System.nanoTime()<deadline);
        if(partIndex==model.parts().length){prepared=true;Hk3WonderSectionRefresh.request("W10");}
        return prepared;
    }
    private static void clearGeometry(boolean refresh){
        prepared=false;BUFFERS.forEach(batch->batch.buffer.close());BUFFERS.clear();
        if(previewPorts!=null){previewPorts.close();previewPorts=null;}
        model=null;loading=null;partIndex=materialIndex=faceIndex=quadIndex=0;Hk3W10Gravity.clear();
        var mc=Minecraft.getInstance();if(refresh&&mc.level!=null)mc.levelRenderer.allChanged();
    }
    @SubscribeEvent public static void logout(ClientPlayerNetworkEvent.LoggingOut event){
        Hk3W10FieldScenes.clear();clearGeometry(false);failed=false;
    }
    @SubscribeEvent public static void render(RenderLevelStageEvent event){
        if(event.getStage()!=RenderLevelStageEvent.Stage.AFTER_TRANSLUCENT_BLOCKS)return;
        Hk3W10FieldScenes.maintain();
        var mc=Minecraft.getInstance();
        if(mc.level==null||shader==null||failed||Hk3W10FieldScenes.scenes().isEmpty()||!prepare())return;
        if(!Hk3W10FieldScenes.active())return;
        var camera=event.getCamera().getPosition();var projection=new Matrix4f(event.getProjectionMatrix());
        for(var scene:Hk3W10FieldScenes.scenes()){
            var state=scene.state();var pos=state.pos();
            if(camera.distanceToSqr(pos.getX(),pos.getY(),pos.getZ())>2500d*2500)continue;
            float angle=switch(state.facing()){case EAST->-(float)Math.PI/2;case SOUTH->-(float)Math.PI;case WEST->-(float)Math.PI*1.5f;default->0;};
            var origin=new Matrix4f(event.getPoseStack().last().pose()).translate((float)(pos.getX()-camera.x),(float)(pos.getY()-camera.y),(float)(pos.getZ()-camera.z));
            origin.translate(.5f,0,.5f).rotateY(angle).translate(-.5f,0,-.5f);
            int[] control=model.data().controller_blueprint();origin.translate(-control[0],-control[1],-control[2]);
            double elapsed=(mc.level.getGameTime()-state.epoch()+event.getPartialTick())/20.;
            double phase=state.phase()+elapsed*(state.running()?1.8:1),flow=state.flow()+elapsed*(state.running()?1.8:1),seconds=state.age()/20.+elapsed;
            RenderSystem.setShaderTexture(1,scene.ports().textureId());shader.getUniform("PortsCount").set(scene.ports().count());
            draw(origin,projection,phase,seconds,state.running());
            var right=new Vector3f(1,0,0).rotate(event.getCamera().rotation()).rotateY(-angle);
            var up=new Vector3f(0,1,0).rotate(event.getCamera().rotation()).rotateY(-angle);
            Hk3W10Gravity.draw(model,origin,projection,right,up,flow,seconds,state.seed(),state.running());
        }
    }
    private static void draw(Matrix4f origin,Matrix4f projection,double phase,double seconds,boolean running){
        var transforms=new Matrix4f[model.parts().length];var motions=new Matrix4f[model.parts().length];
        for(int i=0;i<transforms.length;i++){
            var metadata=model.parts()[i].metadata();var motion=new Matrix4f();
            if(metadata.motion_speed()!=0){
                float[] p=metadata.pivot(),a=metadata.motion_axis();var axis=new Vector3f(a[0],a[1],a[2]).normalize();
                motion.translate(p[0],p[1],p[2]).rotate((float)(phase*metadata.motion_speed()),axis).translate(-p[0],-p[1],-p[2]);
            }
            motions[i]=motion;transforms[i]=new Matrix4f(origin).mul(motion);
        }
        int[] offset=model.data().blueprint_to_export_offset_xyz(),size=model.data().sizeXYZ();
        shader.getUniform("ExportOffset").set((float)offset[0],(float)offset[1],(float)offset[2]);
        shader.getUniform("SceneSize").set((float)size[0],(float)size[1],(float)size[2]);shader.getUniform("Time").set((float)seconds);
        RenderSystem.setShaderTexture(0,ATLAS);RenderSystem.setShaderColor(1,1,1,1);
        RenderSystem.enableDepthTest();RenderSystem.disableCull();RenderSystem.enableBlend();RenderSystem.defaultBlendFunc();RenderSystem.depthMask(true);
        for(var batch:BUFFERS)if(!model.materials()[batch.material].transparent()){
            setPart(batch,motions,seconds,running);batch.buffer.bind();batch.buffer.drawWithShader(transforms[batch.part],projection,shader);
        }
        RenderSystem.depthMask(false);
        for(var batch:BUFFERS)if(model.materials()[batch.material].transparent()){
            setPart(batch,motions,seconds,running);batch.buffer.bind();batch.buffer.drawWithShader(transforms[batch.part],projection,shader);
        }
        VertexBuffer.unbind();RenderSystem.depthMask(true);RenderSystem.disableBlend();RenderSystem.enableCull();
    }
    private static void setPart(Batch batch,Matrix4f[] motions,double seconds,boolean running){
        shader.getUniform("PartTransform").set(motions[batch.part]);shader.getUniform("VoidSurface").set("void".equals(model.parts()[batch.part].metadata().visual())?1:0);
        shader.getUniform("Glow").set(model.materials()[batch.material].emissive()?(float)(1+(running?.18:.04)*(1+Math.sin(seconds*2.5))):1f);
    }
    private static void upload(){
        int batchPart=partIndex,batchMaterial=materialIndex,count=0;
        var part=model.parts()[partIndex];int[] size=part.size(),origin=part.origin();var material=model.materials()[materialIndex];
        BUILDER.begin(VertexFormat.Mode.QUADS,DefaultVertexFormat.POSITION_COLOR_TEX);
        while(faceIndex<6&&count<8192){
            int[] starts=part.starts()[materialIndex][faceIndex];
            if(quadIndex==starts.length){quadIndex=0;faceIndex++;continue;}
            int index=starts[quadIndex],repeat=part.lengths()[materialIndex][faceIndex][quadIndex],span=part.spans()[materialIndex][faceIndex][quadIndex];
            int x=index%size[0]+origin[0],y=index/(size[0]*size[2])+origin[1],z=index/size[0]%size[2]+origin[2];
            int axis=faceIndex<2?2:0,cross=faceIndex<4?1:2,slot=materialIndex*6+faceIndex;
            int color=material.emissive()?255:faceIndex==5?255:faceIndex==4?155:faceIndex<2?205:230;
            for(int[] corner:CORNERS[faceIndex]){
                float px=x+corner[0]*(axis==0?repeat:cross==0?span:1),py=y+corner[1]*(axis==1?repeat:cross==1?span:1),pz=z+corner[2]*(axis==2?repeat:cross==2?span:1);
                BUILDER.vertex(px,py,pz).color(color,color,color,material.transparent()?148:255).uv(slot*2048f+corner[axis]*repeat,corner[cross]*span).endVertex();
            }
            quadIndex++;count++;
        }
        var rendered=BUILDER.end();
        if(count>0){var buffer=new VertexBuffer(VertexBuffer.Usage.STATIC);buffer.bind();buffer.upload(rendered);VertexBuffer.unbind();BUFFERS.add(new Batch(batchPart,batchMaterial,buffer));}
        else rendered.release();
        if(faceIndex==6){faceIndex=0;materialIndex++;if(materialIndex==model.materials().length){materialIndex=0;partIndex++;}}
    }
    @Mod.EventBusSubscriber(modid="hk3gtl",value=Dist.CLIENT,bus=Mod.EventBusSubscriber.Bus.MOD)
    public static final class Resources {
        @SubscribeEvent public static void shaders(RegisterShadersEvent event)throws java.io.IOException{
            clearGeometry(true);failed=false;
            event.registerShader(new ShaderInstance(event.getResourceProvider(),new ResourceLocation("hk3gtl","w10_a3"),DefaultVertexFormat.POSITION_COLOR_TEX),value->shader=value);
            event.registerShader(new ShaderInstance(event.getResourceProvider(),new ResourceLocation("hk3gtl","w10_gravity"),DefaultVertexFormat.POSITION_COLOR),Hk3W10Gravity::shader);
        }
    }
}
