package com.sirin.hk3gtl.client.tree;

import com.mojang.blaze3d.systems.RenderSystem;
import com.mojang.blaze3d.vertex.*;
import com.mojang.logging.LogUtils;
import net.minecraft.client.Minecraft;
import net.minecraft.client.renderer.ShaderInstance;
import net.minecraft.resources.ResourceLocation;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.client.event.*;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.eventbus.api.EventPriority;
import net.minecraftforge.fml.common.Mod;
import org.joml.Matrix4f;
import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.CompletableFuture;

/** 已确认V1金白树影：静态曲线驻留GPU，720道光流只更新采样位置，不逐帧重建树。 */
@Mod.EventBusSubscriber(modid="hk3gtl",value=Dist.CLIENT)
public final class Hk3TreeProjectionRenderer {
    private record Batch(boolean points,VertexBuffer buffer){}
    private static final List<Batch> buffers=new ArrayList<>();
    private static final BufferBuilder builder=new BufferBuilder(4096*4*24);
    private static ShaderInstance pointShader,lineShader;
    private static VertexBuffer flowBuffer;
    private static CompletableFuture<Hk3TreeProjectionModel> loading;
    private static Hk3TreeProjectionModel model;
    private static int lineAt,pointAt;
    private static boolean failed;
    private Hk3TreeProjectionRenderer(){}
    private static void clear(){buffers.forEach(b->b.buffer.close());buffers.clear();if(flowBuffer!=null){flowBuffer.close();flowBuffer=null;}model=null;loading=null;lineAt=pointAt=0;failed=false;}
    @SubscribeEvent public static void logout(ClientPlayerNetworkEvent.LoggingOut e){Hk3TreeProjectionScenes.clear();clear();}
    @SubscribeEvent(priority=EventPriority.LOWEST) public static void render(RenderLevelStageEvent event){
        // 同阶段的远景实体先写深度；透明树影最后绘制，防止背景覆盖前方树干。
        if(event.getStage()!=RenderLevelStageEvent.Stage.AFTER_TRANSLUCENT_BLOCKS||pointShader==null||lineShader==null||failed)return;
        Hk3TreeProjectionScenes.maintain();var mc=Minecraft.getInstance();if(mc.level==null||Hk3TreeProjectionScenes.scenes().isEmpty())return;
        try{
            if(model==null){
                if(loading==null)loading=CompletableFuture.supplyAsync(()->{try{return Hk3TreeProjectionModel.read(Hk3TreeProjectionRenderer.class.getResourceAsStream("/assets/hk3gtl/effects/i34_tree.bin.gz"));}catch(Exception e){throw new IllegalStateException("I34树影读取失败",e);}});
                if(!loading.isDone())return;model=loading.join();loading=null;
            }
            long until=System.nanoTime()+2_000_000;
            do{if(lineAt>=model.positions().length/3&&pointAt>=model.points().length/6)break;upload();}while(System.nanoTime()<until);
            if(lineAt<model.positions().length/3||pointAt<model.points().length/6)return;
            var camera=event.getCamera().getPosition();
            RenderSystem.enableDepthTest();RenderSystem.depthMask(false);RenderSystem.enableBlend();RenderSystem.blendFunc(com.mojang.blaze3d.platform.GlStateManager.SourceFactor.SRC_ALPHA,com.mojang.blaze3d.platform.GlStateManager.DestFactor.ONE);RenderSystem.disableCull();
            try{for(var scene:Hk3TreeProjectionScenes.scenes()){
                var s=scene.state();if(camera.distanceToSqr(s.pos().getX(),s.pos().getY(),s.pos().getZ())>2048d*2048)continue;
                float angle=switch(s.facing()){case EAST->-90;case SOUTH->-180;case WEST->-270;default->0;};
                var origin=new Matrix4f(event.getPoseStack().last().pose()).translate((float)(s.pos().getX()-camera.x),(float)(s.pos().getY()-camera.y),(float)(s.pos().getZ()-camera.z));
                origin.translate(.5f,0,.5f).rotateY((float)Math.toRadians(angle)).translate(-.5f,49,148.5f).scale(.9f);
                float time=(s.clock()+(s.paused()?0:mc.level.getGameTime()-scene.received()+event.getPartialTick()))/20f;
                float power=s.mode()==2?1:.22f;pointShader.safeGetUniform("Time").set(time);pointShader.safeGetUniform("Power").set(power);
                pointShader.safeGetUniform("Viewport").set((float)mc.getWindow().getWidth(),(float)mc.getWindow().getHeight());
                lineShader.safeGetUniform("Power").set(power);
                for(var batch:buffers){batch.buffer.bind();batch.buffer.drawWithShader(origin,event.getProjectionMatrix(),batch.points?pointShader:lineShader);}
                if(s.mode()==2){RenderSystem.setShaderColor(1,1,1,1);drawFlows(time,origin,event.getProjectionMatrix());}
            }}finally{VertexBuffer.unbind();RenderSystem.setShaderColor(1,1,1,1);RenderSystem.depthMask(true);new com.mojang.blaze3d.shaders.BlendMode().apply();RenderSystem.defaultBlendFunc();RenderSystem.disableBlend();RenderSystem.enableCull();}
        }catch(RuntimeException e){failed=true;LogUtils.getLogger().error("I34树影绘制失败，未修改世界方块",e);}
    }
    private static void upload(){
        boolean points=lineAt>=model.positions().length/3;
        if(points){int stop=Math.min(pointAt+1024,model.points().length/6);builder.begin(VertexFormat.Mode.QUADS,DefaultVertexFormat.POSITION_COLOR_TEX);for(int i=pointAt;i<stop;i++){int a=i*6;var p=model.points();point(p[a],p[a+1],p[a+2],p[a+3],p[a+4],(int)p[a+5]);}pointAt=stop;}
        else{int stop=Math.min(lineAt+4096,model.positions().length/3);builder.begin(VertexFormat.Mode.DEBUG_LINES,DefaultVertexFormat.POSITION_COLOR);for(int i=lineAt;i<stop;i++){int a=i*3;var p=model.positions();var c=model.colors();builder.vertex(p[a],p[a+1],p[a+2]).color(clamp(c[a]/2),clamp(c[a+1]/2),clamp(c[a+2]/2),255).endVertex();}lineAt=stop;}
        var buffer=new VertexBuffer(VertexBuffer.Usage.STATIC);buffer.bind();buffer.upload(builder.end());VertexBuffer.unbind();buffers.add(new Batch(points,buffer));
    }
    private static int clamp(float x){return Math.max(0,Math.min(255,Math.round(x*255)));}
    private static void point(float x,float y,float z,float size,float seed,int type){
        // 尺寸与相位保留浮点精度；颜色通道仅标记类型，避免细尘被8位量化吞掉。
        for(int i=0;i<4;i++)builder.vertex(x,y,z).color(255,255,type*100,255).uv((i==1||i==2?1:-1)*size,(i>=2?1:-1)*(seed+1)).endVertex();
    }
    private static void drawFlows(float time,Matrix4f origin,Matrix4f projection){
        builder.begin(VertexFormat.Mode.QUADS,DefaultVertexFormat.POSITION_COLOR_TEX);
        for(var flow:model.flows()){
            double t=(time*flow.speed()+flow.offset())%1;float at=(float)t*64;int a=Math.min(63,(int)at)*3;float f=at-(int)at;var p=flow.samples();
            point(p[a]+(p[a+3]-p[a])*f,p[a+1]+(p[a+4]-p[a+1])*f,p[a+2]+(p[a+5]-p[a+2])*f,flow.size(),flow.seed(),0);
        }
        var buffer=builder.end();if(flowBuffer==null)flowBuffer=new VertexBuffer(VertexBuffer.Usage.DYNAMIC);
        try{flowBuffer.bind();flowBuffer.upload(buffer);flowBuffer.drawWithShader(origin,projection,pointShader);}finally{VertexBuffer.unbind();}
    }
    @Mod.EventBusSubscriber(modid="hk3gtl",value=Dist.CLIENT,bus=Mod.EventBusSubscriber.Bus.MOD)
    public static final class Resources{
        @SubscribeEvent public static void shaders(RegisterShadersEvent e)throws java.io.IOException{clear();e.registerShader(new ShaderInstance(e.getResourceProvider(),new ResourceLocation("hk3gtl","i34_tree"),DefaultVertexFormat.POSITION_COLOR_TEX),s->pointShader=s);e.registerShader(new ShaderInstance(e.getResourceProvider(),new ResourceLocation("hk3gtl","i34_tree_lines"),DefaultVertexFormat.POSITION_COLOR),s->lineShader=s);}
    }
}
