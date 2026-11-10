package com.sirin.hk3gtl.client.wonder;

import com.mojang.blaze3d.systems.RenderSystem;
import com.mojang.blaze3d.vertex.*;
import com.mojang.logging.LogUtils;
import net.minecraft.client.Minecraft;
import net.minecraft.client.renderer.ShaderInstance;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.phys.Vec3;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.client.event.*;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import org.joml.Matrix4f;
import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.CompletableFuture;

/** 游戏内C9特效试装：真实尺寸、33批GPU表面，既不搬动世界方块，也不伪造GT成型。 */
@Mod.EventBusSubscriber(modid="hk3gtl",value=Dist.CLIENT)
public final class Hk3W03FxRenderer {
    private static final ResourceLocation ATLAS=new ResourceLocation("hk3gtl","textures/effect/w03_c9_atlas.png");
    private record Batch(int group,VertexBuffer buffer) {}
    private static final List<Batch> BUFFERS=new ArrayList<>();
    private static final BufferBuilder BUILDER=new BufferBuilder(8192*4*24);
    private static ShaderInstance shader;
    private static CompletableFuture<Hk3W03FxModel> loading;
    private static Hk3W03FxModel model;
    private static Vec3 anchor;
    private static Object level;
    private static int uploadGroup,uploadFace,uploaded;
    private static long epoch,frames,started;
    private static double fixedTime=-1;
    private static boolean failed;
    private static volatile boolean prepared;
    private Hk3W03FxRenderer() {}

    public static void show(Vec3 position) {
        var mc=Minecraft.getInstance();anchor=position;level=mc.level;epoch=mc.level.getGameTime();fixedTime=-1;
        frames=0;started=System.nanoTime();failed=false;
        if(model==null&&loading==null)loading=CompletableFuture.supplyAsync(Hk3W03FxModel::load);
    }
    public static void hide(){anchor=null;level=null;if(Hk3W03FieldScenes.scenes().isEmpty())clearGeometry();}
    public static boolean ready(){return prepared;}
    public static void seek(double seconds){fixedTime=seconds;}
    public static void play(){if(Minecraft.getInstance().level!=null){epoch=Minecraft.getInstance().level.getGameTime()-(long)(Math.max(0,fixedTime)*20);fixedTime=-1;}}
    public static String status(){return "W03 C9 · "+uploaded+"/517262面 · "+BUFFERS.size()+"批 · GPU "+(uploaded*96L/1048576)+"MiB · "
            +(fixedTime<0?"播放中":fixedTime+"秒定格")+" · 平均 "+(frames==0?0:Math.round(frames*1e9/(System.nanoTime()-started)))+"帧 · 服务器成型场 "+Hk3W03FieldScenes.scenes().size()+"座 · 调试命令不授予成型";}
    private static void clearGeometry(){prepared=false;BUFFERS.forEach(b->b.buffer.close());BUFFERS.clear();model=null;loading=null;uploadGroup=uploadFace=uploaded=0;}
    @SubscribeEvent public static void logout(ClientPlayerNetworkEvent.LoggingOut event){Hk3W03FieldScenes.clear();hide();}
    @SubscribeEvent public static void render(RenderLevelStageEvent event) {
        if(event.getStage()!=RenderLevelStageEvent.Stage.AFTER_TRANSLUCENT_BLOCKS||shader==null||failed)return;
        var mc=Minecraft.getInstance();Hk3W03FieldScenes.maintain();
        if(mc.level==null)return;
        if(anchor!=null&&mc.level!=level)hide();
        if(anchor==null&&Hk3W03FieldScenes.scenes().isEmpty())return;
        try {
            if(model==null) {
                if(loading==null)loading=CompletableFuture.supplyAsync(Hk3W03FxModel::load);
                if(!loading.isDone())return;model=loading.join();loading=null;
            }
            long until=System.nanoTime()+2_000_000;
            do {if(uploadGroup>=model.groups().length)break;upload();}while(System.nanoTime()<until);
            if(!prepared&&uploadGroup==model.groups().length){prepared=true;mc.levelRenderer.allChanged();if(started==0)started=System.nanoTime();}
            if(anchor!=null){double seconds=fixedTime>=0?fixedTime:((mc.level.getGameTime()-epoch)%7200+event.getPartialTick())/20.;draw(event,anchor,0,seconds);}
            if(prepared&&Hk3W03FieldScenes.maskReady())for(var scene:Hk3W03FieldScenes.scenes()){
                var state=scene.state();double ticks=state.elapsed()+(state.running()?mc.level.getGameTime()-state.epoch()+event.getPartialTick():0);
                float angle=switch(state.facing()){case EAST->-90;case SOUTH->-180;case WEST->-270;default->0;};
                draw(event,Vec3.atLowerCornerOf(state.pos()),angle,(ticks%7200)/20.);
            }
            frames++;
        }catch(RuntimeException failure) {
            failed=true;clearGeometry();mc.levelRenderer.allChanged();LogUtils.getLogger().error("W03 C9特效显示失败",failure);
            if(mc.player!=null)mc.player.displayClientMessage(Component.literal("W03 C9特效加载失败，详见日志；未更改世界方块。"),false);
        }
    }
    private static void draw(RenderLevelStageEvent event,Vec3 anchor,float angle,double seconds){
            var camera=event.getCamera().getPosition();
            if(camera.distanceToSqr(anchor)>2500*2500)return;
            var projection=new Matrix4f(event.getProjectionMatrix());
            var origin=new Matrix4f(event.getPoseStack().last().pose()).translate((float)(anchor.x-camera.x),(float)(anchor.y-camera.y),(float)(anchor.z-camera.z));
            origin.translate(.5f,0,.5f).rotateY((float)Math.toRadians(angle)).translate(-.5f,0,-.5f);
            var control=model.metadata().controller();origin.translate(-control[0],-control[1],-control[2]);
            var matrices=new Matrix4f[33];
            for(int i=0;i<matrices.length;i++) {
                matrices[i]=Hk3W03FxMotion.matrix(model.metadata().components()[i],seconds,origin);
            }
            // drawWithShader会从RenderSystem重设Sampler0，必须先绑定该槽位。
            RenderSystem.setShaderTexture(0,ATLAS);
            RenderSystem.enableDepthTest();RenderSystem.disableBlend();RenderSystem.disableCull();RenderSystem.depthMask(true);
            try {for(var batch:BUFFERS){batch.buffer.bind();batch.buffer.drawWithShader(matrices[batch.group],projection,shader);}}
            finally{VertexBuffer.unbind();RenderSystem.enableCull();}
    }
    private static int u16(byte[] data,int offset){return (data[offset]&255)<<8|data[offset+1]&255;}
    private static void upload() {
        byte[] data=model.groups()[uploadGroup];int count=Math.min(8192,data.length/10-uploadFace);
        BUILDER.begin(VertexFormat.Mode.QUADS,DefaultVertexFormat.POSITION_COLOR_TEX);
        for(int i=uploadFace;i<uploadFace+count;i++) {
            int at=i*10,x=u16(data,at),y=u16(data,at+2),z=u16(data,at+4),n=u16(data,at+6),slot=data[at+8]&255,face=data[at+9]&255;
            int color=face==5?255:face==4?155:face<2?205:230;
            float[][] points=switch(face) {
                case 0->new float[][]{{x+1,y,z+n},{x+1,y,z},{x+1,y+1,z},{x+1,y+1,z+n}};
                case 1->new float[][]{{x,y,z},{x,y,z+n},{x,y+1,z+n},{x,y+1,z}};
                case 2->new float[][]{{x,y,z+1},{x+n,y,z+1},{x+n,y+1,z+1},{x,y+1,z+1}};
                case 3->new float[][]{{x+n,y,z},{x,y,z},{x,y+1,z},{x+n,y+1,z}};
                case 4->new float[][]{{x,y,z},{x+n,y,z},{x+n,y,z+1},{x,y,z+1}};
                default->new float[][]{{x,y+1,z+1},{x+n,y+1,z+1},{x+n,y+1,z},{x,y+1,z}};
            };
            for(int v=0;v<4;v++)BUILDER.vertex(points[v][0],points[v][1],points[v][2]).color(color,color,color,255)
                .uv(slot*2048f+(v==1||v==2?n:0),v>=2?1:0).endVertex();
        }
        var buffer=new VertexBuffer(VertexBuffer.Usage.STATIC);buffer.bind();buffer.upload(BUILDER.end());VertexBuffer.unbind();
        BUFFERS.add(new Batch(uploadGroup,buffer));uploaded+=count;uploadFace+=count;
        if(uploadFace*10==data.length){uploadFace=0;uploadGroup++;}
    }
    @Mod.EventBusSubscriber(modid="hk3gtl",value=Dist.CLIENT,bus=Mod.EventBusSubscriber.Bus.MOD)
    public static final class Resources {
        @SubscribeEvent public static void shaders(RegisterShadersEvent event)throws java.io.IOException {
            clearGeometry();event.registerShader(new ShaderInstance(event.getResourceProvider(),new ResourceLocation("hk3gtl","w03_c9"),DefaultVertexFormat.POSITION_COLOR_TEX),s->shader=s);
        }
    }
}
