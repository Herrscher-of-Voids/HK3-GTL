package com.sirin.hk3gtl.client.wonder;

import com.mojang.blaze3d.platform.GlStateManager;
import com.mojang.blaze3d.systems.RenderSystem;
import com.mojang.blaze3d.vertex.*;
import net.minecraft.client.renderer.GameRenderer;
import net.minecraft.client.renderer.ShaderInstance;
import org.joml.Matrix4f;
import org.joml.Vector3f;

final class Hk3W10Gravity {
    private static final BufferBuilder BUILDER=new BufferBuilder(1024*1024);
    private static VertexBuffer stars,beams,particles;
    private static ShaderInstance shader;
    private Hk3W10Gravity(){}
    static void shader(ShaderInstance value){shader=value;}
    static void clear(){
        if(stars!=null){stars.close();stars=null;}
        if(beams!=null){beams.close();beams=null;}
        if(particles!=null){particles.close();particles=null;}
    }
    private static double hash(double value){double n=Math.sin(value)*43758.5453;return n-Math.floor(n);}
    private static double fract(double value){return value-Math.floor(value);}
    private static double smooth(double low,double high,double value){double t=Math.max(0,Math.min(1,(value-low)/(high-low)));return t*t*(3-2*t);}

    static void draw(Hk3W10FxModel model,Matrix4f origin,Matrix4f projection,Vector3f right,Vector3f up,
                     double flow,double seconds,double seed,boolean running){
        var effects=model.data().effects();float[] center=effects.center(),jet=effects.jet_y_range();
        float[][] sources=effects.beam_origins();float strength=running?1.35f:.82f;
        var forward=new Vector3f(right).cross(up);var target=new Vector3f(center[0],center[1],center[2]);
        RenderSystem.enableDepthTest();RenderSystem.disableCull();RenderSystem.depthMask(false);RenderSystem.enableBlend();RenderSystem.defaultBlendFunc();RenderSystem.setShaderColor(1,1,1,1);
        shader.getUniform("Time").set((float)seconds);shader.getUniform("Seed").set((float)fract(seed));
        shader.getUniform("LensStrength").set(running?1.1f:.82f);shader.getUniform("LensPass").set(1);
        var starCenter=new Vector3f(target).fma(-effects.void_radius()*1.8f,forward);float half=effects.void_radius()*3.4f;
        BUILDER.begin(VertexFormat.Mode.QUADS,DefaultVertexFormat.POSITION_COLOR);
        for(int i=0;i<4;i++){
            float r=i==1||i==2?half:-half,u=i>=2?half:-half;
            BUILDER.vertex(starCenter.x+right.x*r+up.x*u,starCenter.y+right.y*r+up.y*u,starCenter.z+right.z*r+up.z*u)
                    .color(i==1||i==2?255:0,i>=2?255:0,255,255).endVertex();
        }
        if(stars==null)stars=new VertexBuffer(VertexBuffer.Usage.DYNAMIC);
        stars.bind();stars.upload(BUILDER.end());stars.drawWithShader(origin,projection,shader);
        shader.getUniform("LensPass").set(0);
        BUILDER.begin(VertexFormat.Mode.QUADS,DefaultVertexFormat.POSITION_COLOR);
        for(float[] source:sources){
            for(int i=0;i<4;i++){
                float[] p=i<2?source:center;float width=i==1||i==2?.4f:-.4f;
                BUILDER.vertex(p[0]+right.x*width,p[1]+right.y*width,p[2]+right.z*width).color(13,5,21,224).endVertex();
            }
        }
        if(beams==null)beams=new VertexBuffer(VertexBuffer.Usage.DYNAMIC);
        beams.bind();beams.upload(BUILDER.end());beams.drawWithShader(origin,projection,GameRenderer.getPositionColorShader());
        var u=new Vector3f[sources.length];var v=new Vector3f[sources.length];
        for(int i=0;i<sources.length;i++){
            float[] source=sources[i];var axis=new Vector3f(target).sub(source[0],source[1],source[2]).normalize();
            u[i]=new Vector3f(axis).cross(.13f,1,.07f).normalize();v[i]=new Vector3f(axis).cross(u[i]);
        }
        int beamEnd=sources.length*600,ringEnd=beamEnd+256,fragmentEnd=ringEnd+384,count=fragmentEnd+880;
        BUILDER.begin(VertexFormat.Mode.QUADS,DefaultVertexFormat.POSITION_COLOR);
        for(int i=0;i<count;i++){
            double random=hash(i*127.1+9.7+seed),x,y,z,light,size;boolean gold;
            if(i<beamEnd){
                int beam=i/600;double phase=(i%600)/600.,t=fract(phase+flow*.09),angle=phase*100+seconds*.6,radius=4.6*Math.sqrt(random);
                double a=Math.cos(angle)*radius,b=Math.sin(angle)*radius;float[] source=sources[beam];
                x=source[0]+(center[0]-source[0])*t+u[beam].x*a+v[beam].x*b;
                y=source[1]+(center[1]-source[1])*t+u[beam].y*a+v[beam].y*b;
                z=source[2]+(center[2]-source[2])*t+u[beam].z*a+v[beam].z*b;
                light=(.25+.75*Math.sqrt(Math.sin(t*Math.PI)))*(.45+.55*Math.sin(random*60+seconds*2));gold=random>=.89;size=gold?1.9:2.8;
            }else if(i<fragmentEnd){
                double t=(seconds%10)/4.8;if(t>1)continue;
                double phase=i<ringEnd?(i-beamEnd)/256.:hash(i*37.9+seed),angle=phase*Math.PI*2+flow*.12,radius=50;
                y=jet[0]+(jet[1]-jet[0])*(1-t);
                if(i>=ringEnd){radius+=random*18;y+=(random*80+5)*Math.sin(t*Math.PI);angle+=random*3*t;}
                x=center[0]+Math.cos(angle)*radius;z=center[2]+Math.sin(angle)*radius;
                light=smooth(0,.08,t)*(1-smooth(.84,1,t));gold=true;size=i<ringEnd?3.5:1+random*3;
            }else{
                double phase=(i-fragmentEnd)/880.,t=fract(phase+flow*.16),angle=random*Math.PI*20+flow*.8,radius=Math.sqrt(random)*4;
                x=center[0]+Math.cos(angle)*radius;y=jet[0]+t*(jet[1]-jet[0]);z=center[2]+Math.sin(angle)*radius;
                light=.5+.5*Math.pow(Math.sin(random*81+seconds*3)*.5+.5,2);gold=true;size=1.8+random*1.6;
            }
            light*=strength;if(light<.01)continue;
            int red=(int)(255*Math.min(1,(gold?1:.19)*light)),green=(int)(255*Math.min(1,(gold?.69:.035)*light)),blue=(int)(255*Math.min(1,(gold?.21:.31)*light));
            quad(right,up,(float)x,(float)y,(float)z,(float)size,red,green,blue,(int)(255*Math.min(1,light*(gold?.8:.36))));
        }
        if(particles==null)particles=new VertexBuffer(VertexBuffer.Usage.DYNAMIC);
        RenderSystem.blendFunc(GlStateManager.SourceFactor.SRC_ALPHA,GlStateManager.DestFactor.ONE);
        particles.bind();particles.upload(BUILDER.end());particles.drawWithShader(origin,projection,shader);
        VertexBuffer.unbind();RenderSystem.defaultBlendFunc();RenderSystem.disableBlend();RenderSystem.depthMask(true);RenderSystem.enableCull();
    }
    private static void quad(Vector3f right,Vector3f up,float x,float y,float z,float size,int red,int green,int blue,int alpha){
        float half=size*.5f;
        for(int i=0;i<4;i++){
            float r=i==1||i==2?half:-half,u=i>=2?half:-half;
            BUILDER.vertex(x+right.x*r+up.x*u,y+right.y*r+up.y*u,z+right.z*r+up.z*u).color(red,green,blue,alpha).endVertex();
        }
    }
}
