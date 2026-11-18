package com.sirin.hk3gtl.client.wonder;

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
public final class Hk3W07FxRenderer {
    private static final int[][][] CORNERS={{{1,0,0},{1,1,0},{1,1,1},{1,0,1}},{{0,0,1},{0,1,1},{0,1,0},{0,0,0}},
            {{1,0,1},{1,1,1},{0,1,1},{0,0,1}},{{0,0,0},{0,1,0},{1,1,0},{1,0,0}},
            {{0,0,1},{0,0,0},{1,0,0},{1,0,1}},{{0,1,0},{0,1,1},{1,1,1},{1,1,0}}};
    private static final BufferBuilder BUILDER=new BufferBuilder(512*1024);
    private static VertexBuffer particles;
    private Hk3W07FxRenderer(){}
    public static void drawPreview(double seconds){
        draw(new Matrix4f(RenderSystem.getModelViewMatrix()).translate(240,-43,613),
                new Matrix4f(RenderSystem.getProjectionMatrix()),seconds);
    }
    @SubscribeEvent public static void render(RenderLevelStageEvent event){
        if(event.getStage()!=RenderLevelStageEvent.Stage.AFTER_TRANSLUCENT_BLOCKS)return;
        Hk3W07FieldScenes.maintain();var mc=Minecraft.getInstance();
        if(mc.level==null)return;
        var camera=event.getCamera().getPosition();var projection=new Matrix4f(event.getProjectionMatrix());
        for(var scene:Hk3W07FieldScenes.scenes()){
            var state=scene.state();var pos=state.pos();
            if(!state.running()||camera.distanceToSqr(pos.getX(),pos.getY(),pos.getZ())>2500d*2500)continue;
            float angle=switch(state.facing()){case NORTH->(float)Math.PI;case EAST->(float)Math.PI/2;case WEST->-(float)Math.PI/2;default->0;};
            var origin=new Matrix4f(event.getPoseStack().last().pose()).translate((float)(pos.getX()-camera.x),(float)(pos.getY()-camera.y),(float)(pos.getZ()-camera.z));
            origin.translate(.5f,0,.5f).rotateY(angle).translate(-.5f,-260,-537.5f);
            double seconds=state.work()+(mc.level.getGameTime()-state.epoch()+event.getPartialTick())/20.;
            draw(origin,projection,seconds);
            Hk3W07SceneRenderer.drawLights(origin,projection,seconds,scene.ports());
        }
    }
    private static void draw(Matrix4f origin,Matrix4f projection,double time){
        RenderSystem.enableDepthTest();RenderSystem.disableCull();RenderSystem.depthMask(false);
        RenderSystem.enableBlend();RenderSystem.defaultBlendFunc();RenderSystem.setShaderColor(1,1,1,1);
        BUILDER.begin(VertexFormat.Mode.QUADS,DefaultVertexFormat.POSITION_COLOR);
        for(int i=0;i<224;i++){
            double t=fract(time*.095+i/224.),arc=Math.sin(t*Math.PI);
            double z=26.5+(((i*53)%227)/227.-.5)*1279*.78;
            double radius=485*.44*(.28+((i*37)%223)/223.*.7),y=175+(i*29)%71,size=1.3+(i%4)*.65;
            box(-radius*(1-t)-3,y+(200-y)*t+arc*13,z+arc*9,size*(1-.4*t),
                    i*.7+t*.4,i*.3+t*.8,i*.2,i%5==0?0x64516a:0x27212b,.9f);
            box(3+radius*t,200+(y-200)*t+arc*18,z-arc*9,size*(.65+.35*t),
                    i*.4-t*.5,i*.8,i*.3+t*.3,i%5==0?0xe6d095:0xfff8eb,.86f);
        }
        if(particles==null)particles=new VertexBuffer(VertexBuffer.Usage.DYNAMIC);
        particles.bind();particles.upload(BUILDER.end());particles.drawWithShader(origin,projection,GameRenderer.getPositionColorShader());
        VertexBuffer.unbind();RenderSystem.disableBlend();RenderSystem.depthMask(true);RenderSystem.enableCull();
    }
    private static double fract(double value){return value-Math.floor(value);}
    private static void box(double x,double y,double z,double size,double rx,double ry,double rz,int color,float alpha){
        var transform=new Matrix4f().translation((float)x,(float)y,(float)z).rotateXYZ((float)rx,(float)ry,(float)rz).scale((float)size);
        for(int[][] face:CORNERS)for(int[] corner:face)
            BUILDER.vertex(transform,corner[0]-.5f,corner[1]-.5f,corner[2]-.5f)
                    .color((color>>16)&255,(color>>8)&255,color&255,(int)(alpha*255)).endVertex();
    }
    private static void clear(){if(particles!=null){particles.close();particles=null;}}
    @SubscribeEvent public static void logout(ClientPlayerNetworkEvent.LoggingOut event){Hk3W07FieldScenes.clear();clear();}
    @Mod.EventBusSubscriber(modid="hk3gtl",value=Dist.CLIENT,bus=Mod.EventBusSubscriber.Bus.MOD)
    public static final class Resources {
        @SubscribeEvent public static void shaders(RegisterShadersEvent event){clear();}
    }
}
