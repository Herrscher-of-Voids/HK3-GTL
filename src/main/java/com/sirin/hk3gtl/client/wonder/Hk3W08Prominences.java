package com.sirin.hk3gtl.client.wonder;

import com.mojang.blaze3d.platform.GlStateManager;
import com.mojang.blaze3d.systems.RenderSystem;
import com.mojang.blaze3d.vertex.*;
import net.minecraft.client.renderer.ShaderInstance;
import org.joml.Matrix4f;
import org.joml.Vector3f;

final class Hk3W08Prominences {
    private static final BufferBuilder BUILDER=new BufferBuilder(1024*1024);
    private static final float[][] LAYERS={{255,57,24,6,.16f},{255,140,32,3.5f,.42f},{255,229,126,1.7f,.95f}};
    private static final float[] X=new float[2880],Y=new float[2880],Z=new float[2880],LIGHT=new float[2880],SIZE=new float[2880];
    private static VertexBuffer buffer;
    private static ShaderInstance shader;
    private Hk3W08Prominences(){}
    static void shader(ShaderInstance value){shader=value;}
    static void clear(){if(buffer!=null){buffer.close();buffer=null;}}
    private static double hash(double value){double n=Math.sin(value)*43758.5453;return n-Math.floor(n);}
    private static double smooth(double value){double t=Math.max(0,Math.min(1,value));return t*t*(3-2*t);}

    static void draw(Hk3W08FxModel model,Matrix4f origin,Matrix4f projection,Vector3f right,Vector3f up,
                     double phase,double flow,double seconds,double seed){
        var normals=new Vector3f[3];var masks=new Hk3W08FxModel.Mask[3];
        for(var part:model.parts())if(part.id().startsWith("star_ring_")){
            int i=part.id().charAt(part.id().length()-1)-'1';float[] axis=part.metadata().motion_axis();
            normals[i]=new Vector3f(axis[0],axis[1],axis[2]).rotate(Hk3W08FxMotion.rotation(i,phase));masks[i]=part.metadata().effect_mask();
        }
        for(int slot=0;slot<12;slot++){
            double base=seed+slot*127.1,cycle=11+6*hash(base+3),clock=seconds+cycle*hash(base+9),epoch=Math.floor(clock/cycle),key=base+epoch*311.7;
            double duration=4+4.5*hash(key+17),age=clock-epoch*cycle-(.5+1.2*hash(key+23)),progress=age/duration;
            double y=1-2*hash(key+31),longitude=2*Math.PI*hash(key+43),radius=Math.sqrt(1-y*y),angle=2*Math.PI*hash(key+59);
            var normal=new Vector3f((float)(radius*Math.cos(longitude)),(float)y,(float)(radius*Math.sin(longitude)));
            var u=new Vector3f(normal).cross(.17f,1,.08f).normalize();var v=new Vector3f(normal).cross(u);
            var tangent=new Vector3f(u).mul((float)Math.cos(angle)).fma((float)Math.sin(angle),v);
            v.set(normal).cross(tangent);
            double growth=smooth(progress/.28)*(1-smooth((progress-.7)/.3)),opacity=smooth(progress/.12)*(1-smooth((progress-.7)/.3)),offset=hash(key+71);
            for(int p=0;p<240;p++){
                int index=slot*240+p;double particleSeed=(Math.sin(index*127.1+9.7)*43758.5453)%1,t=p/240.+flow+offset;t-=Math.floor(t);
                double sine=Math.sin(t*Math.PI),bend=(-.42+.84*t+.24*Math.sin(t*2*Math.PI))*growth,rise=Math.pow(sine,1.15)*growth;
                float distance=(float)(model.data().star_radius()+(model.data().corona_radius()-model.data().star_radius())*rise);
                var point=new Vector3f(normal).mul((float)Math.cos(bend)).fma((float)Math.sin(bend),tangent).fma((float)(.05*Math.sin(t*4*Math.PI)),v).normalize().mul(distance);
                double jitter=Math.sin(particleSeed*72+t*40+seconds*1.5);
                point.fma((float)(jitter*1.8*rise),tangent).fma((float)(Math.cos(particleSeed*91+seconds*1.2)*1.8*rise),v);
                double intensity=opacity*(.25+.75*Math.sqrt(sine))*(.45+.55*Math.pow(.5+.5*Math.sin(t*38-seconds*5+slot),2));
                for(int i=0;i<3;i++){
                    float axial=point.dot(normals[i]);float radial=(float)Math.sqrt(Math.max(0,point.lengthSquared()-axial*axial));var mask=masks[i];
                    float clearance=Math.max(Math.max(mask.radial_min()-radial,radial-mask.radial_max()),Math.max(mask.axial_min()-axial,axial-mask.axial_max()));
                    intensity*=smooth((clearance-3)/3);
                }
                X[index]=point.x;Y[index]=point.y;Z[index]=point.z;LIGHT[index]=(float)intensity;SIZE[index]=.65f+.35f*(float)Math.abs(particleSeed);
            }
        }
        BUILDER.begin(VertexFormat.Mode.QUADS,DefaultVertexFormat.POSITION_COLOR);
        for(float[] layer:LAYERS)for(int i=0;i<2880;i++)if(LIGHT[i]>.002f){
            float light=LIGHT[i],size=layer[3]*SIZE[i];int red=(int)(layer[0]*light),green=(int)(layer[1]*light),blue=(int)(layer[2]*light);
            quad(right,up,X[i],Y[i],Z[i],size,red,green,blue,(int)(255*layer[4]*light*.55f));
            quad(right,up,X[i],Y[i],Z[i],size*.5f,red,green,blue,(int)(255*layer[4]*light*.45f));
        }
        if(buffer==null)buffer=new VertexBuffer(VertexBuffer.Usage.DYNAMIC);
        RenderSystem.enableDepthTest();RenderSystem.disableCull();RenderSystem.depthMask(false);RenderSystem.enableBlend();
        RenderSystem.blendFunc(GlStateManager.SourceFactor.SRC_ALPHA,GlStateManager.DestFactor.ONE);RenderSystem.setShaderColor(1,1,1,1);
        buffer.bind();buffer.upload(BUILDER.end());float[] center=model.data().star_center();
        buffer.drawWithShader(new Matrix4f(origin).translate(center[0],center[1],center[2]),projection,shader);
        VertexBuffer.unbind();RenderSystem.defaultBlendFunc();RenderSystem.disableBlend();RenderSystem.depthMask(true);RenderSystem.enableCull();
    }
    private static void quad(Vector3f right,Vector3f up,float x,float y,float z,float size,int red,int green,int blue,int alpha){
        float half=size*.5f;
        for(int i=0;i<4;i++){
            float r=(i==1||i==2?half:-half),u=i>=2?half:-half;
            BUILDER.vertex(x+right.x*r+up.x*u,y+right.y*r+up.y*u,z+right.z*r+up.z*u).color(red,green,blue,alpha).endVertex();
        }
    }
}
