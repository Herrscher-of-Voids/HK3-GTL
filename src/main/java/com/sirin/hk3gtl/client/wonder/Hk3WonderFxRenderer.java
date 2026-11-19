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
import java.util.Map;
import java.util.concurrent.CompletableFuture;
import java.util.concurrent.ConcurrentHashMap;

@Mod.EventBusSubscriber(modid="hk3gtl",value=Dist.CLIENT)
public final class Hk3WonderFxRenderer {
    private static final int[][][] CORNERS={{{1,0,0},{1,1,0},{1,1,1},{1,0,1}},{{0,0,1},{0,1,1},{0,1,0},{0,0,0}},
            {{1,0,1},{1,1,1},{0,1,1},{0,0,1}},{{0,0,0},{0,1,0},{1,1,0},{1,0,0}},
            {{0,0,1},{0,0,0},{1,0,0},{1,0,1}},{{0,1,0},{0,1,1},{1,1,1},{1,1,0}}};
    private record Batch(int part,int material,VertexBuffer buffer){}
    private static final class Geometry {
        final String role;
        final ResourceLocation atlas;
        final List<Batch> buffers=new ArrayList<>();
        CompletableFuture<Hk3WonderFxModel> loading;
        Hk3WonderFxModel model;
        int part,material,face,quad;
        volatile boolean prepared;
        boolean failed;
        Geometry(String role){this.role=role;atlas=new ResourceLocation("hk3gtl","textures/effect/"+Hk3WonderFxModel.resource(role)+"_atlas.png");}
        boolean prepare(){
            if(prepared)return true;
            if(failed)return false;
            if(model==null){
                if(loading==null)loading=CompletableFuture.supplyAsync(()->Hk3WonderFxModel.load(role)).exceptionally(failure->{
                    failed=true;LogUtils.getLogger().error("{}动画资源加载失败",role,failure);return null;
                });
                if(!loading.isDone())return false;
                model=loading.join();loading=null;if(failed)return false;
            }
            long deadline=System.nanoTime()+2_000_000;
            do{if(part==model.parts().length)break;upload(this);}while(System.nanoTime()<deadline);
            if(part==model.parts().length){prepared=true;var mc=Minecraft.getInstance();if(mc.level!=null)Hk3WonderSectionRefresh.request(role);}
            return prepared;
        }
        void close(){prepared=false;buffers.forEach(b->b.buffer.close());buffers.clear();}
    }
    private static final Map<String,Geometry> GEOMETRIES=new ConcurrentHashMap<>();
    private static final BufferBuilder BUILDER=new BufferBuilder(8192*4*24);
    private static ShaderInstance shader;
    private static Hk3W08Ports previewPorts;
    private Hk3WonderFxRenderer(){}
    public static boolean ready(String role){var g=GEOMETRIES.get(role);return g!=null&&g.prepared;}
    static Hk3WonderFxModel.Data data(String role){return GEOMETRIES.get(role).model.data();}
    public static boolean preparePreview(String role){return shader!=null&&GEOMETRIES.computeIfAbsent(role,Geometry::new).prepare()&&Hk3WonderFxScenes.prepareMask(role);}
    public static void drawPreview(String role,double seconds){
        var g=GEOMETRIES.get(role);int[] offset=g.model.data().blueprint_to_export_offset_xyz();
        var origin=new Matrix4f(RenderSystem.getModelViewMatrix()).translate(offset[0],offset[1],offset[2]);
        var projection=new Matrix4f(RenderSystem.getProjectionMatrix());
        if(previewPorts==null)previewPorts=new Hk3W08Ports(new int[0]);
        RenderSystem.setShaderTexture(1,previewPorts.textureId());shader.getUniform("PortsCount").set(0);
        var inverse=new Matrix4f(origin).invert();
        var right=inverse.transformDirection(new Vector3f(1,0,0)).normalize();var up=inverse.transformDirection(new Vector3f(0,1,0)).normalize();
        draw(g,origin,projection,0,seconds,seconds,true,right,up,0);
    }
    @SubscribeEvent public static void logout(ClientPlayerNetworkEvent.LoggingOut event){Hk3WonderFxScenes.clear();clearGeometry(false);}
    private static void clearGeometry(boolean refresh){
        GEOMETRIES.values().forEach(Geometry::close);GEOMETRIES.clear();Hk3WindFrostEffects.clear();
        if(previewPorts!=null){previewPorts.close();previewPorts=null;}
        var mc=Minecraft.getInstance();if(refresh&&mc.level!=null)mc.levelRenderer.allChanged();
    }
    @SubscribeEvent public static void render(RenderLevelStageEvent event){
        if(event.getStage()!=RenderLevelStageEvent.Stage.AFTER_TRANSLUCENT_BLOCKS)return;
        Hk3WonderFxScenes.maintain();var mc=Minecraft.getInstance();
        if(mc.level==null||shader==null)return;
        var camera=event.getCamera().getPosition();var projection=new Matrix4f(event.getProjectionMatrix());
        for(var scene:Hk3WonderFxScenes.scenes()){
            var state=scene.state();var pos=state.pos();String role=state.role();
            if(camera.distanceToSqr(pos.getX(),pos.getY(),pos.getZ())>2500d*2500||!preparePreview(role)||!Hk3WonderFxScenes.active(role))continue;
            float angle=switch(state.facing()){case EAST->-(float)Math.PI/2;case SOUTH->-(float)Math.PI;case WEST->-(float)Math.PI*1.5f;default->0;};
            var origin=new Matrix4f(event.getPoseStack().last().pose()).translate((float)(pos.getX()-camera.x),(float)(pos.getY()-camera.y),(float)(pos.getZ()-camera.z));
            origin.translate(.5f,0,.5f).rotateY(angle).translate(-.5f,0,-.5f);
            int[] control=data(role).controller_blueprint();origin.translate(-control[0],-control[1],-control[2]);
            double elapsed=(mc.level.getGameTime()-state.epoch()+event.getPartialTick())/20.;
            double idle=state.idle()+(state.running()?0:elapsed),work=state.work()+(state.running()?elapsed:0),seconds=state.age()/20.+elapsed;
            var right=new Vector3f(1,0,0).rotate(event.getCamera().rotation()).rotateY(-angle);
            var up=new Vector3f(0,1,0).rotate(event.getCamera().rotation()).rotateY(-angle);
            RenderSystem.setShaderTexture(1,scene.ports().textureId());shader.getUniform("PortsCount").set(scene.ports().count());
            draw(GEOMETRIES.get(role),origin,projection,idle,work,seconds,state.running(),right,up,state.seed());
        }
    }
    private static void draw(Geometry g,Matrix4f origin,Matrix4f projection,double idle,double work,double seconds,boolean running,Vector3f right,Vector3f up,double seed){
        var transforms=new Matrix4f[g.model.parts().length];var motions=new Matrix4f[transforms.length];
        for(int i=0;i<transforms.length;i++){
            var m=g.model.parts()[i].metadata();var motion=new Matrix4f();
            if("bob".equals(m.motion_kind()))motion.translate(0,(float)(m.amplitude()*Math.sin(seconds*m.frequency())),0);
            else{
                float[] p=m.pivot(),a=m.motion_axis();
                motion.translate(p[0],p[1],p[2]).rotate((float)(idle*m.idle_speed()+work*m.running_speed()),new Vector3f(a[0],a[1],a[2]).normalize()).translate(-p[0],-p[1],-p[2]);
            }
            motions[i]=motion;transforms[i]=new Matrix4f(origin).mul(motion);
        }
        int[] offset=g.model.data().blueprint_to_export_offset_xyz(),size=g.model.data().sizeXYZ();
        shader.getUniform("ExportOffset").set((float)offset[0],(float)offset[1],(float)offset[2]);shader.getUniform("SceneSize").set((float)size[0],(float)size[1],(float)size[2]);
        shader.getUniform("Time").set((float)seconds);shader.getUniform("VoidSurface").set(0);
        RenderSystem.setShaderTexture(0,g.atlas);RenderSystem.setShaderColor(1,1,1,1);
        RenderSystem.enableDepthTest();RenderSystem.disableCull();RenderSystem.enableBlend();RenderSystem.defaultBlendFunc();RenderSystem.depthMask(true);
        for(var b:g.buffers)if(!g.model.materials()[b.material].transparent())drawBatch(g,b,motions,transforms,projection,seconds,running);
        RenderSystem.depthMask(false);
        for(var b:g.buffers)if(g.model.materials()[b.material].transparent())drawBatch(g,b,motions,transforms,projection,seconds,running);
        VertexBuffer.unbind();RenderSystem.depthMask(true);RenderSystem.disableBlend();RenderSystem.enableCull();
        Hk3WindFrostEffects.draw(g.role,g.model.data().effects(),origin,projection,right,up,idle,work,seconds,seed,running);
    }
    private static void drawBatch(Geometry g,Batch b,Matrix4f[] motions,Matrix4f[] transforms,Matrix4f projection,double seconds,boolean running){
        boolean core=g.role.equals("W05")&&g.model.parts()[b.part].id().equals("herren_core"),frost=g.role.equals("W06")&&b.material==7;
        shader.getUniform("CoreSurface").set(core?1:0);shader.getUniform("Working").set(running?1:0);
        shader.getUniform("ScrollUV").set((float)(seconds*(core?.025:frost?.018:0)),(float)(core?Math.sin(seconds*.3)*.06:frost?Math.sin(seconds*.23)*.04:0));
        shader.getUniform("PartTransform").set(motions[b.part]);shader.getUniform("Glow").set(g.model.materials()[b.material].emissive()?(float)(1+(running?.18:.04)*(1+Math.sin(seconds*2.5))):1f);
        b.buffer.bind();b.buffer.drawWithShader(transforms[b.part],projection,shader);
    }
    private static void upload(Geometry g){
        int batchPart=g.part,batchMaterial=g.material,count=0;var part=g.model.parts()[g.part];int[] size=part.size(),origin=part.origin();var material=g.model.materials()[g.material];
        BUILDER.begin(VertexFormat.Mode.QUADS,DefaultVertexFormat.POSITION_COLOR_TEX);
        while(g.face<6&&count<8192){
            int[] starts=part.starts()[g.material][g.face];
            if(g.quad==starts.length){
                part.starts()[g.material][g.face]=null;
                part.lengths()[g.material][g.face]=null;
                part.spans()[g.material][g.face]=null;
                g.quad=0;g.face++;continue;
            }
            int index=starts[g.quad],repeat=part.lengths()[g.material][g.face][g.quad],span=part.spans()[g.material][g.face][g.quad];
            int x=index%size[0]+origin[0],y=index/(size[0]*size[2])+origin[1],z=index/size[0]%size[2]+origin[2];
            int axis=g.face<2?2:0,cross=g.face<4?1:2,slot=g.material*6+g.face,color=material.emissive()?255:g.face==5?255:g.face==4?155:g.face<2?205:230;
            for(int[] c:CORNERS[g.face])BUILDER.vertex(x+c[0]*(axis==0?repeat:cross==0?span:1),y+c[1]*(axis==1?repeat:cross==1?span:1),z+c[2]*(axis==2?repeat:cross==2?span:1))
                    .color(color,color,color,material.transparent()?148:255).uv(slot*2048f+c[axis]*repeat,c[cross]*span).endVertex();
            g.quad++;count++;
        }
        var rendered=BUILDER.end();
        if(count>0){var buffer=new VertexBuffer(VertexBuffer.Usage.STATIC);buffer.bind();buffer.upload(rendered);VertexBuffer.unbind();g.buffers.add(new Batch(batchPart,batchMaterial,buffer));}else rendered.release();
        if(g.face==6){g.face=0;g.material++;if(g.material==g.model.materials().length){g.material=0;g.part++;}}
    }
    @Mod.EventBusSubscriber(modid="hk3gtl",value=Dist.CLIENT,bus=Mod.EventBusSubscriber.Bus.MOD)
    public static final class Resources {
        @SubscribeEvent public static void shaders(RegisterShadersEvent event)throws java.io.IOException{
            clearGeometry(true);event.registerShader(new ShaderInstance(event.getResourceProvider(),new ResourceLocation("hk3gtl","wonder_fx"),DefaultVertexFormat.POSITION_COLOR_TEX),value->shader=value);
        }
    }
}
