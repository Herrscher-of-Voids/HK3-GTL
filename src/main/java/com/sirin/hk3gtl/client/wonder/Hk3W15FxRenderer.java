package com.sirin.hk3gtl.client.wonder;

import com.mojang.blaze3d.platform.GlStateManager;
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
import org.joml.Matrix3f;
import org.joml.Matrix4f;
import org.joml.Vector3f;
import java.util.HashMap;
import java.util.HashSet;
import java.util.Map;
import java.util.Set;
import java.util.concurrent.CompletableFuture;

@Mod.EventBusSubscriber(modid="hk3gtl",value=Dist.CLIENT)
public final class Hk3W15FxRenderer {
    private static final long DYNAMIC_REFRESH_NANOS=33_333_333L;
    private static final BufferBuilder BUILDER=new BufferBuilder(8*1024*1024);
    private static final Vector3f RIGHT=new Vector3f(),UP=new Vector3f();
    private static final DynamicBuffers PREVIEW_BUFFERS=new DynamicBuffers();
    private static final Map<Long,DynamicBuffers> SCENE_BUFFERS=new HashMap<>();
    private static CompletableFuture<Hk3W15FxGeometry> loading;
    private static Hk3W15FxGeometry geometry;
    private static VertexBuffer branches,spirals,water;
    private static ShaderInstance waterShader;
    private static boolean failed;
    private Hk3W15FxRenderer() {}

    private static boolean prepare() {
        if(branches!=null)return true;
        if(failed)return false;
        if(geometry==null) {
            if(loading==null)loading=CompletableFuture.supplyAsync(Hk3W15FxGeometry::load).exceptionally(failure->{
                failed=true;LogUtils.getLogger().error("W15树海特效加载失败",failure);return null;
            });
            if(!loading.isDone())return false;
            geometry=loading.join();loading=null;
            if(failed)return false;
        }
        begin();lines(geometry.branches,.32,.66);lines(geometry.diamonds,.25,.6);branches=upload(null);
        begin();lines(geometry.spirals,.35,.1);spirals=upload(null);
        BUILDER.begin(VertexFormat.Mode.QUADS,DefaultVertexFormat.POSITION);
        for(int ring=0;ring<30;ring++)for(int j=0;j<144;j++) {
            waterVertex(ring,j);waterVertex(ring+1,j);waterVertex(ring+1,j+1);waterVertex(ring,j+1);
        }
        water=new VertexBuffer(VertexBuffer.Usage.STATIC);
        water.bind();water.upload(BUILDER.end());
        VertexBuffer.unbind();return true;
    }
    public static void drawPreview(double seconds) {
        draw(new Matrix4f(RenderSystem.getModelViewMatrix()).translate(550,-78,405),
                new Matrix4f(RenderSystem.getProjectionMatrix()),0,seconds,true,PREVIEW_BUFFERS);
    }
    @SubscribeEvent public static void render(RenderLevelStageEvent event) {
        if(event.getStage()!=RenderLevelStageEvent.Stage.AFTER_TRANSLUCENT_BLOCKS)return;
        Hk3W15FieldScenes.maintain();var mc=Minecraft.getInstance();
        var scenes=Hk3W15FieldScenes.scenes();
        if(mc.level==null||scenes.isEmpty()){clearSceneBuffers();return;}
        var camera=event.getCamera().getPosition();var projection=new Matrix4f(event.getProjectionMatrix());
        var active=new HashSet<Long>();
        for(var scene:scenes) {
            var state=scene.state();var pos=state.pos();
            if(camera.distanceToSqr(pos.getX(),pos.getY(),pos.getZ())>2500d*2500)continue;
            long key=pos.asLong();active.add(key);
            float angle=switch(state.facing()){case NORTH->(float)Math.PI;case EAST->(float)Math.PI/2;case WEST->-(float)Math.PI/2;default->0;};
            var origin=new Matrix4f(event.getPoseStack().last().pose()).translate((float)(pos.getX()-camera.x),(float)(pos.getY()-camera.y),(float)(pos.getZ()-camera.z));
            origin.translate(.5f,0,.5f).rotateY(angle).translate(-.5f,-153,-404.5f);
            double elapsed=(mc.level.getGameTime()-state.epoch()+event.getPartialTick())/20.;
            draw(origin,projection,state.idle()+(state.running()?0:elapsed),
                    state.work()+(state.running()?elapsed:0),state.running(),SCENE_BUFFERS.computeIfAbsent(key,ignored->new DynamicBuffers()));
        }
        SCENE_BUFFERS.keySet().removeIf(key->{if(active.contains(key))return false;SCENE_BUFFERS.get(key).close();return true;});
    }
    private static void draw(Matrix4f origin,Matrix4f projection,double idle,double work,boolean working,DynamicBuffers buffers) {
        if(!prepare())return;
        double time=idle+work;
        var inverse=new Matrix3f(origin).invert();inverse.transform(RIGHT.set(1,0,0)).normalize();inverse.transform(UP.set(0,1,0)).normalize();
        double power=working?1:.58;
        RenderSystem.enableDepthTest();RenderSystem.disableCull();RenderSystem.depthMask(false);RenderSystem.enableBlend();
        RenderSystem.setShaderColor(1,1,1,1);RenderSystem.defaultBlendFunc();
        waterShader.getUniform("Time").set((float)time);
        waterShader.getUniform("Power").set((float)power);
        water.bind();water.drawWithShader(origin,projection,waterShader);
        buffers.update(time,power,idle,work,working,System.nanoTime());
        RenderSystem.blendFunc(GlStateManager.SourceFactor.SRC_ALPHA,GlStateManager.DestFactor.ONE);
        RenderSystem.setShaderColor(1,1,1,working?1:.7f);drawBuffer(branches,origin,projection);drawBuffer(spirals,origin,projection);
        RenderSystem.setShaderColor(1,1,1,1);
        drawBuffer(buffers.additive,origin,projection);
        RenderSystem.defaultBlendFunc();drawBuffer(buffers.leaves,origin,projection);
        VertexBuffer.unbind();RenderSystem.disableBlend();RenderSystem.depthMask(true);RenderSystem.enableCull();
    }
    private static void waterVertex(int ring,int sector) {
        double angle=sector*Math.PI/72, radius=ring/30.;
        BUILDER.vertex(Math.cos(angle)*radius*630,0,Math.sin(angle)*radius*470).endVertex();
    }
    private static void waves(double time,double power) {
        var source=geometry.waves;float[] p=source.positions();
        for(int i=0;i<p.length;i+=6) {
            double ay=p[i+1]+Math.sin(Math.hypot(p[i],p[i+2])*.033-time*.4)*2;
            double by=p[i+4]+Math.sin(Math.hypot(p[i+3],p[i+5])*.033-time*.4)*2;
            line(p[i],ay,p[i+2],p[i+3],by,p[i+5],.42,source.colors()[i/3],.035+power*.045);
        }
    }
    private static void worlds(double time,double power) {
        double angle=time*.025,c=Math.cos(angle),s=Math.sin(angle);
        for(var world:geometry.worlds) {
            float[] p=world.lines().positions();double y=world.y()+Math.sin(time*.25+world.phase())*5;
            for(int i=0;i<p.length;i+=6)line(world.x()+p[i]*c+p[i+2]*s,y+p[i+1],world.z()+p[i+2]*c-p[i]*s,
                    world.x()+p[i+3]*c+p[i+5]*s,y+p[i+4],world.z()+p[i+5]*c-p[i+3]*s,.45,world.lines().colors()[i/3],.32*(.65+power*.35));
        }
    }
    private static void stars(Hk3W15FxGeometry.Dots dots,double time,double power,boolean nodes) {
        float[] p=dots.values();
        for(int i=0;i<p.length;i+=5)glow(p[i],p[i+1],p[i+2],p[i+3],0xffd173,(.78+.22*Math.sin(time*.7+p[i+4]))*power*(nodes?.85:.58));
    }
    private static void flows(double time,double power) {
        for(var flow:geometry.flows) {
            var path=geometry.paths[flow.path()];double t=fract(flow.phase()+time*flow.speed());
            if(path.inward())t=1-t;
            double at=t*64;int i=Math.min(63,(int)at)*3;double f=at-i/3.;float[] p=path.positions();
            glow(p[i]+(p[i+3]-p[i])*f,p[i+1]+(p[i+4]-p[i+1])*f,p[i+2]+(p[i+5]-p[i+2])*f,flow.size(),0xffdb83,power*.8);
        }
    }
    private static void glyphs(double time,double power) {
        for(var glyph:geometry.glyphs) {
            double t=fract(glyph.phase()+time*glyph.speed()),a=glyph.angle()+t*.9,x,y,z;
            if(t<.7){double q=t/.7,r=glyph.radius()*(1-q);x=Math.cos(a)*r;y=45+q*43;z=Math.sin(a)*r*.746-35*q;}
            else {double q=(t-.7)/.3;x=Math.sin(a)*7;y=88+q*102;z=-35+Math.cos(a)*7;}
            int color=mix(0x4d8fff,0xffd466,fract(glyph.seed()));double size=glyph.size(),alpha=.4+.4*power;
            billboard(x-UP.x*size*.38,y-UP.y*size*.38,z-UP.z*size*.38,size*.9,size*.11,color,alpha);
            billboard(x+UP.x*size*.38,y+UP.y*size*.38,z+UP.z*size*.38,size*.9,size*.11,color,alpha);
            billboard(x-RIGHT.x*size*.4,y-RIGHT.y*size*.4,z-RIGHT.z*size*.4,size*.11,size*.82,color,alpha);
            billboard(x+RIGHT.x*size*.4,y+RIGHT.y*size*.4,z+RIGHT.z*size*.4,size*.11,size*.82,color,alpha);
            billboard(x,y,z,size*.8,size*.18,color,alpha);
            if(fract(glyph.seed())>.5)billboard(x,y,z,size*.18,size*.78,color,alpha);
        }
    }
    private static void leaves(double time,double power) {
        float[] p=geometry.leaves.values();
        for(int i=0;i<p.length;i+=5) {
            double seed=p[i+4],x=p[i]+Math.sin(time*.25+seed)*1.6,y=p[i+1]+Math.cos(time*.18+seed)*1.1,z=p[i+2];
            double angle=seed+Math.sin(time*.23+seed)*.13,c=Math.cos(angle),s=Math.sin(angle),width=p[i+3]*.54,height=p[i+3]*.91;
            double rx=RIGHT.x*c+UP.x*s,ry=RIGHT.y*c+UP.y*s,rz=RIGHT.z*c+UP.z*s;
            double ux=UP.x*c-RIGHT.x*s,uy=UP.y*c-RIGHT.y*s,uz=UP.z*c-RIGHT.z*s;
            int color=mix(0xed7811,0xffcf4d,fract(seed*2.7));double alpha=(.3+.28*fract(seed))*(.75+power*.25);
            vertex(x+ux*height/2,y+uy*height/2,z+uz*height/2,color,alpha);
            vertex(x+rx*width/2,y+ry*width/2,z+rz*width/2,color,alpha);
            vertex(x-ux*height/2,y-uy*height/2,z-uz*height/2,color,alpha);
            vertex(x-rx*width/2,y-ry*width/2,z-rz*width/2,color,alpha);
            int vein=mix(color,0xffe8ac,.3);
            vertex(x-rx*width*.025-ux*height*.36,y-ry*width*.025-uy*height*.36,z-rz*width*.025-uz*height*.36,vein,alpha);
            vertex(x+rx*width*.025-ux*height*.36,y+ry*width*.025-uy*height*.36,z+rz*width*.025-uz*height*.36,vein,alpha);
            vertex(x+rx*width*.025+ux*height*.36,y+ry*width*.025+uy*height*.36,z+rz*width*.025+uz*height*.36,vein,alpha);
            vertex(x-rx*width*.025+ux*height*.36,y-ry*width*.025+uy*height*.36,z-rz*width*.025+uz*height*.36,vein,alpha);
        }
    }
    private static void writing(double time) {
        double z=-305+fract(time*.065)*610;
        for(int side=-1;side<=1;side+=2)for(int i=0;i<80;i++) {
            double x=(68+i*5)*side,next=(73+i*5)*side;
            vertex(x,pageHeight(x,z)+3,z,0xffcf66,.6);vertex(next,pageHeight(next,z)+3,z,0xffcf66,.6);
            vertex(next,pageHeight(next,z+2)+3,z+2,0xffcf66,.6);vertex(x,pageHeight(x,z+2)+3,z+2,0xffcf66,.6);
        }
    }
    private static double pageHeight(double x,double z) {return Math.round(185+88*Math.pow(Math.abs(x)/520,.76)+7*Math.pow(Math.abs(z)/360,6));}
    private static void begin() {BUILDER.begin(VertexFormat.Mode.QUADS,DefaultVertexFormat.POSITION_COLOR);}
    private static VertexBuffer upload(VertexBuffer buffer) {
        if(buffer==null)buffer=new VertexBuffer(VertexBuffer.Usage.DYNAMIC);
        buffer.bind();buffer.upload(BUILDER.end());return buffer;
    }
    private static void drawBuffer(VertexBuffer buffer,Matrix4f origin,Matrix4f projection) {buffer.bind();buffer.drawWithShader(origin,projection,GameRenderer.getPositionColorShader());}
    private static final class DynamicBuffers {
        private VertexBuffer additive,leaves;
        private long updated;
        void update(double time,double power,double idle,double work,boolean working,long now) {
            if(updated!=0&&now-updated<DYNAMIC_REFRESH_NANOS)return;
            begin();waves(time,power);worlds(time,power);stars(geometry.dust,time,power,false);stars(geometry.nodes,time,power,true);
            flows(work+idle*.32,power);glyphs(work+idle*.22,power);if(working)writing(work);additive=upload(additive);
            begin();leaves(time,power);leaves=upload(leaves);updated=now;
        }
        void close() {
            if(additive!=null){additive.close();additive=null;}
            if(leaves!=null){leaves.close();leaves=null;}
            updated=0;
        }
    }
    private static void lines(Hk3W15FxGeometry.Lines source,double width,double alpha) {
        float[] p=source.positions();
        for(int i=0;i<p.length;i+=6)line(p[i],p[i+1],p[i+2],p[i+3],p[i+4],p[i+5],width,source.colors()[i/3],alpha);
    }
    private static void line(double x,double y,double z,double a,double b,double c,double width,int color,double alpha) {
        double dx=a-x,dy=b-y,dz=c-z,length=Math.sqrt(dx*dx+dy*dy+dz*dz);dx/=length;dy/=length;dz/=length;
        double rx,ry,rz;
        if(Math.abs(dy)>.96){rx=0;ry=dz;rz=-dy;}else {rx=-dz;ry=0;rz=dx;}
        double scale=width*.5/Math.sqrt(rx*rx+ry*ry+rz*rz);rx*=scale;ry*=scale;rz*=scale;
        lineQuad(x,y,z,a,b,c,rx,ry,rz,color,alpha);
        lineQuad(x,y,z,a,b,c,dy*rz-dz*ry,dz*rx-dx*rz,dx*ry-dy*rx,color,alpha);
    }
    private static void lineQuad(double x,double y,double z,double a,double b,double c,double rx,double ry,double rz,int color,double alpha) {
        vertex(x-rx,y-ry,z-rz,color,alpha);vertex(a-rx,b-ry,c-rz,color,alpha);
        vertex(a+rx,b+ry,c+rz,color,alpha);vertex(x+rx,y+ry,z+rz,color,alpha);
    }
    private static void glow(double x,double y,double z,double size,int color,double alpha) {
        billboard(x,y,z,size,size,color,alpha*.22);billboard(x,y,z,size*.29,size*.29,0xffedb9,alpha*.82);
    }
    private static void billboard(double x,double y,double z,double width,double height,int color,double alpha) {
        double rx=RIGHT.x*width*.5,ry=RIGHT.y*width*.5,rz=RIGHT.z*width*.5,ux=UP.x*height*.5,uy=UP.y*height*.5,uz=UP.z*height*.5;
        vertex(x-rx-ux,y-ry-uy,z-rz-uz,color,alpha);vertex(x+rx-ux,y+ry-uy,z+rz-uz,color,alpha);
        vertex(x+rx+ux,y+ry+uy,z+rz+uz,color,alpha);vertex(x-rx+ux,y-ry+uy,z-rz+uz,color,alpha);
    }
    private static void vertex(double x,double y,double z,int color,double alpha) {BUILDER.vertex(x,y,z).color((color>>16)&255,(color>>8)&255,color&255,(int)(255*alpha)).endVertex();}
    private static int mix(int a,int b,double t) {
        int red=(int)(((a>>16)&255)*(1-t)+((b>>16)&255)*t),green=(int)(((a>>8)&255)*(1-t)+((b>>8)&255)*t),blue=(int)((a&255)*(1-t)+(b&255)*t);
        return (red<<16)|(green<<8)|blue;
    }
    private static double fract(double x) {return x-Math.floor(x);}
    private static void clear() {
        if(branches!=null){branches.close();branches=null;}
        if(spirals!=null){spirals.close();spirals=null;}
        if(water!=null){water.close();water=null;}
        clearSceneBuffers();PREVIEW_BUFFERS.close();
        geometry=null;loading=null;failed=false;
    }
    private static void clearSceneBuffers() {
        SCENE_BUFFERS.values().forEach(DynamicBuffers::close);SCENE_BUFFERS.clear();
    }
    @SubscribeEvent public static void logout(ClientPlayerNetworkEvent.LoggingOut event) {Hk3W15FieldScenes.clear();clear();}
    @Mod.EventBusSubscriber(modid="hk3gtl",value=Dist.CLIENT,bus=Mod.EventBusSubscriber.Bus.MOD)
    public static final class Resources {
        @SubscribeEvent public static void shaders(RegisterShadersEvent event) throws java.io.IOException {
            clear();
            event.registerShader(new ShaderInstance(event.getResourceProvider(),new ResourceLocation("hk3gtl","w15_sea"),DefaultVertexFormat.POSITION),shader->waterShader=shader);
        }
    }
}
