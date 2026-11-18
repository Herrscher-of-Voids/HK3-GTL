package com.sirin.hk3gtl.client.wonder;

import com.mojang.blaze3d.platform.GlStateManager;
import com.mojang.blaze3d.systems.RenderSystem;
import com.mojang.blaze3d.vertex.*;
import net.minecraft.client.Minecraft;
import net.minecraft.client.renderer.GameRenderer;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.client.event.ClientPlayerNetworkEvent;
import net.minecraftforge.client.event.RegisterShadersEvent;
import net.minecraftforge.client.event.RenderLevelStageEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import org.joml.Matrix4f;

@Mod.EventBusSubscriber(modid="hk3gtl",value=Dist.CLIENT)
public final class Hk3W14FxRenderer {
    private static final int[][][] CORNERS={{{1,0,0},{1,1,0},{1,1,1},{1,0,1}},{{0,0,1},{0,1,1},{0,1,0},{0,0,0}},
            {{1,0,1},{1,1,1},{0,1,1},{0,0,1}},{{0,0,0},{0,1,0},{1,1,0},{1,0,0}},
            {{0,0,1},{0,0,0},{1,0,0},{1,0,1}},{{0,1,0},{0,1,1},{1,1,1},{1,1,0}}};
    private static final double[][] LAYERS={{26,20,300,40},{44,28,500,78},{48,24,680,108}};
    private static final int[][] DIMENSIONS={{-352,176,732},{-782,160,178},{-641,189,-511},{0,154,-810},
            {625,220,-499},{796,202,182},{351,184,728}};
    private static final int[] COLORS={0x8de7b1,0xcf9cff,0xff7435,0xcce6ff,0xff9262,0xffda79,0xd4b5ff};
    private static final BufferBuilder BUILDER=new BufferBuilder(2*1024*1024);
    private static VertexBuffer particles;
    private Hk3W14FxRenderer(){}
    public static void drawPreview(double seconds){
        draw(new Matrix4f(RenderSystem.getModelViewMatrix()).translate(878,0,894),
                new Matrix4f(RenderSystem.getProjectionMatrix()),seconds);
    }
    @SubscribeEvent public static void render(RenderLevelStageEvent event){
        if(event.getStage()!=RenderLevelStageEvent.Stage.AFTER_TRANSLUCENT_BLOCKS)return;
        Hk3W14FieldScenes.maintain();var mc=Minecraft.getInstance();
        if(mc.level==null)return;
        var camera=event.getCamera().getPosition();var projection=new Matrix4f(event.getProjectionMatrix());
        for(var scene:Hk3W14FieldScenes.scenes()){
            var state=scene.state();var pos=state.pos();
            if(!state.running()||camera.distanceToSqr(pos.getX(),pos.getY(),pos.getZ())>2500d*2500)continue;
            float angle=switch(state.facing()){case NORTH->(float)Math.PI;case EAST->(float)Math.PI/2;case WEST->-(float)Math.PI/2;default->0;};
            var origin=new Matrix4f(event.getPoseStack().last().pose()).translate((float)(pos.getX()-camera.x),(float)(pos.getY()-camera.y),(float)(pos.getZ()-camera.z));
            origin.translate(.5f,0,.5f).rotateY(angle).translate(-.5f,-44,-610.5f);
            double seconds=state.work()+(mc.level.getGameTime()-state.epoch()+event.getPartialTick())/20.;
            draw(origin,projection,seconds);
        }
    }
    private static void draw(Matrix4f origin,Matrix4f projection,double time){
        RenderSystem.enableDepthTest();RenderSystem.disableCull();RenderSystem.depthMask(false);RenderSystem.enableBlend();
        RenderSystem.blendFunc(GlStateManager.SourceFactor.SRC_ALPHA,GlStateManager.DestFactor.ONE);RenderSystem.setShaderColor(1,1,1,1);
        BUILDER.begin(VertexFormat.Mode.QUADS,DefaultVertexFormat.POSITION_COLOR);
        for(int layer=2;layer>=0;layer--){
            double[] shape=LAYERS[layer];double pulse=1+.035*Math.sin(time*9.5+layer);
            for(int slice=0;slice<(int)shape[0];slice++)for(int point=0;point<(int)shape[1];point++){
                double t=(slice+.16*Math.sin(time*12+point*.9))/shape[0],angle=point*2.399963+slice*.37+time*.24;
                double wave=1+Math.min(1,t*12)*(.09*Math.sin(t*35-time*8)+.055*Math.cos(point*1.7+time*11));
                double profile=(1-.97*t)*(1+.27*Math.exp(-Math.pow((t-.16)/.105,2)));
                double radial=layer==0?Math.sqrt((point+.5)/shape[1]):.87+.13*((point*17)%41)/41.;
                double radius=shape[3]*profile*radial*wave*pulse,cell=(layer==0?19:layer==1?18:17)*(1-.72*t);
                double light=.83+.17*Math.sin(point*1.3+slice*.73-time*6);
                double red=layer==0?.72+.23*(1-t):layer==1?.045+.08*t:1;
                double green=layer==0?.87+.13*(1-t):layer==1?.33+.23*(1-t):.15+.39*(1-t);
                double blue=layer==0?1:layer==1?.94:.012+.025*(1-t);
                box(Math.cos(angle)*radius+Math.sin(t*6+time*2)*11*t,334+Math.max(0,t)*shape[2],
                        Math.sin(angle)*radius+Math.cos(t*7+time*1.6)*8*t,cell,shape[2]/shape[0]*(layer==2?1.17:1.35),cell,
                        red*light,green*light,blue*light,layer==0?.92:layer==1?.68:.76);
            }
        }
        for(int i=0;i<192;i++){
            double t=fract(time*.24+i/192.),angle=i*2.399963+time*.16,radius=(148-100*t)*(.6+.4*((i*37)%193)/193.),size=(4+i%5)*(1-.5*t);
            int color=i%3==0?0xaedcff:0xffba56;
            box(Math.cos(angle)*radius+18*Math.sin(t*5+time)*t,365+t*680,Math.sin(angle)*radius,
                    size,size*(1.8+2*t),size,((color>>16)&255)/255.,((color>>8)&255)/255.,(color&255)/255.,.72);
        }
        for(int i=0;i<DIMENSIONS.length;i++)for(int j=0;j<9;j++){
            int[] center=DIMENSIONS[i];double t=fract(time*.16+j/9.+i*.11),size=2.7+Math.sin(t*Math.PI)*2;
            int color=COLORS[i];
            box(center[0]*(1-.43*t),center[1]+(42-center[1])*t+Math.sin(t*Math.PI)*31,center[2]*(1-.43*t),size,size,size,
                    ((color>>16)&255)/255.,((color>>8)&255)/255.,(color&255)/255.,.72);
        }
        if(particles==null)particles=new VertexBuffer(VertexBuffer.Usage.DYNAMIC);
        particles.bind();particles.upload(BUILDER.end());particles.drawWithShader(origin,projection,GameRenderer.getPositionColorShader());
        VertexBuffer.unbind();RenderSystem.defaultBlendFunc();RenderSystem.disableBlend();RenderSystem.depthMask(true);RenderSystem.enableCull();
    }
    private static double fract(double value){return value-Math.floor(value);}
    private static void box(double x,double y,double z,double width,double height,double depth,double red,double green,double blue,double alpha){
        for(int[][] face:CORNERS)for(int[] corner:face)
            BUILDER.vertex(x+(corner[0]-.5)*width,y+(corner[1]-.5)*height,z+(corner[2]-.5)*depth)
                    .color((int)(255*red),(int)(255*green),(int)(255*blue),(int)(255*alpha)).endVertex();
    }
    private static void clear(){if(particles!=null){particles.close();particles=null;}}
    @SubscribeEvent public static void logout(ClientPlayerNetworkEvent.LoggingOut event){Hk3W14FieldScenes.clear();clear();}
    @Mod.EventBusSubscriber(modid="hk3gtl",value=Dist.CLIENT,bus=Mod.EventBusSubscriber.Bus.MOD)
    public static final class Resources {
        @SubscribeEvent public static void shaders(RegisterShadersEvent event){clear();}
    }
}
