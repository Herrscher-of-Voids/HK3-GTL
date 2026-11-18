package com.sirin.hk3gtl.client.review;

import com.mojang.blaze3d.vertex.PoseStack;
import com.mojang.blaze3d.vertex.VertexConsumer;
import net.minecraft.client.Camera;
import net.minecraft.client.renderer.LightTexture;
import net.minecraft.client.renderer.MultiBufferSource;
import net.minecraft.client.renderer.RenderType;
import net.minecraft.client.renderer.texture.OverlayTexture;
import net.minecraft.resources.ResourceLocation;
import org.joml.Vector3f;

import java.util.List;
import java.util.Random;

public final class Hk3CocoonAtmosphere {
    private static final RenderType GROUND=RenderType.entityCutoutNoCull(new ResourceLocation("hk3gtl","textures/effect/cocoon_white.png"));
    private static final Dust[] STARS=dust(1536,false);
    private static final Dust[] NEAR_DUST=dust(384,true);
    private static final Mist[] GROUND_MIST=mist();

    private record Dust(double x,double y,double z,float size,float phase,float speed,boolean cross,int hotspot,int red,int green,int blue) {}
    private record Mist(double x,double y,double z,float width,float depth,float phase,int red,int green,int blue) {}

    private Hk3CocoonAtmosphere() {}

    static void render(PoseStack pose,MultiBufferSource.BufferSource buffers,Camera camera,float time,List<Hk3CocoonGeometry.Hotspot> hotspots) {
        var matrix=pose.last();
        var ground=buffers.getBuffer(GROUND);
        for(int x=-384;x<384;x+=32)for(int z=-448;z<256;z+=32){
            int grain=Math.floorMod(x*734287+z*912271,17);
            int blue=40+grain,red=15+grain/3,green=8+grain/4;
            horizontal(ground,matrix,x+16,-.03,z+16,32,32,red,green,blue,255);
        }
        buffers.endBatch(GROUND);

        var right=new Vector3f(1,0,0).rotate(camera.rotation());
        var up=new Vector3f(0,1,0).rotate(camera.rotation());
        var soft=buffers.getBuffer(Hk3CocoonRenderTypes.SOFT);
        for(int i=0;i<hotspots.size();i++){
            var hotspot=hotspots.get(i);
            float pulse=.86f+.1f*(float)Math.sin(time*(.33+i*.047)+hotspot.phase())+.04f*(float)Math.sin(time*.91+hotspot.phase()*1.7);
            float radius=hotspot.radius();
            int alpha=(int)((i==0?.045:.09+hotspot.intensity()*.012)*pulse*255);
            billboard(soft,matrix,right,up,hotspot.x(),hotspot.y(),hotspot.z(),radius*(4+pulse*.2f),radius*(2.7f+pulse*.2f),hotspot.red(),hotspot.green(),hotspot.blue(),alpha);
        }
        for(var mist:GROUND_MIST){
            double drift=Math.sin(time*.035+mist.phase());
            int alpha=(int)(9+4*Math.sin(time*.11+mist.phase()));
            horizontal(soft,matrix,mist.x()+drift*8,mist.y(),mist.z()+Math.cos(time*.027+mist.phase())*12,mist.width(),mist.depth(),mist.red(),mist.green(),mist.blue(),alpha);
        }
        for(int i=0;i<18;i++){
            double x=-127+i*15;
            double shoulders=Math.exp(-Math.pow((x-64)/55,2))+Math.exp(-Math.pow((x+64)/55,2));
            double phase=i*.731;
            double y=10+Math.sin(phase)*5+Math.sin(time*.09+phase)*2;
            double z=-90-25*(1-Math.pow(Math.abs(x)/150,1.4));
            int alpha=(int)((10+24*shoulders)*(.8+.2*Math.sin(time*.13+phase)));
            billboard(soft,matrix,right,up,x,y,z,52,28,224,29,180,alpha);
        }
        buffers.endBatch(Hk3CocoonRenderTypes.SOFT);

        var pixels=buffers.getBuffer(Hk3CocoonRenderTypes.PIXEL);
        for(var star:STARS){
            int alpha=(int)(170+65*Math.sin(star.phase()+time*star.speed()));
            sparkle(pixels,matrix,right,up,star.x(),star.y(),star.z(),star.size(),star.red(),star.green(),star.blue(),alpha,star.cross());
        }
        for(var dust:NEAR_DUST){
            var hotspot=hotspots.get(dust.hotspot());
            double x=hotspot.x()+dust.x()*hotspot.radius()+Math.sin(time*dust.speed()*.63+dust.phase())*.9;
            double y=Math.max(1.2,hotspot.y()+dust.y()*hotspot.radius()+Math.sin(time*dust.speed()+dust.phase())*1.1);
            double z=hotspot.z()+dust.z()*hotspot.radius();
            int alpha=(int)(84+34*Math.sin(dust.phase()+time*dust.speed()));
            int red=(hotspot.red()*3+235)/4,green=(hotspot.green()*3+225)/4,blue=(hotspot.blue()*3+255)/4;
            sparkle(pixels,matrix,right,up,x,y,z,dust.size(),red,green,blue,alpha,dust.cross());
        }
        buffers.endBatch(Hk3CocoonRenderTypes.PIXEL);
    }

    private static Dust[] dust(int count,boolean near) {
        var random=new Random(146283+(near?1:0));
        var particles=new Dust[count];
        for(int i=0;i<count;i++){
            double angle=random.nextDouble()*Math.PI*2;
            double x,y,z;
            int red,green,blue,hotspot;
            float size,speed;
            if(near){
                double radius=.25+Math.pow(random.nextDouble(),.7)*1.15;
                x=Math.cos(angle)*radius*1.3;y=(random.nextDouble()*2-1)*.32;z=Math.sin(angle)*radius*.65;
                red=green=blue=255;hotspot=1+random.nextInt(4);
                size=.3f+(float)Math.pow(random.nextDouble(),2)*1.4f;speed=.27f+random.nextFloat()*.65f;
            }else{
                y=.01+Math.pow(random.nextDouble(),1.3)*.98;
                double radius=Math.sqrt(1-y*y),distance=360+random.nextDouble()*540;
                x=Math.cos(angle)*radius*distance;z=Math.sin(angle)*radius*distance;y*=distance;
                boolean cyan=random.nextFloat()<.23f;
                red=cyan?142:201+random.nextInt(42);green=cyan?220:151+random.nextInt(58);blue=255;hotspot=-1;
                size=.65f+(float)Math.pow(random.nextDouble(),4)*2.4f;speed=.1f+random.nextFloat()*.19f;
            }
            particles[i]=new Dust(x,y,z,size,random.nextFloat()*(float)Math.PI*2,speed,random.nextFloat()>(near?.993f:.985f),hotspot,red,green,blue);
        }
        return particles;
    }

    private static Mist[] mist() {
        var random=new Random(146284);
        var patches=new Mist[36];
        float[] heights={.7f,1.8f,4.2f};
        for(int i=0;i<patches.length;i++){
            double x=(random.nextDouble()-.5)*560,z=(random.nextDouble()-.5)*440-25;
            boolean cyan=x<-75&&z<-100;
            patches[i]=new Mist(x,heights[i%3],z,90+random.nextFloat()*120,50+random.nextFloat()*130,random.nextFloat()*(float)Math.PI*2,cyan?19:105,cyan?121:14,cyan?177:158);
        }
        return patches;
    }

    private static void sparkle(VertexConsumer out,PoseStack.Pose pose,Vector3f right,Vector3f up,double x,double y,double z,float size,int red,int green,int blue,int alpha,boolean cross) {
        billboard(out,pose,right,up,x,y,z,size,size,red,green,blue,alpha);
        if(cross){
            billboard(out,pose,right,up,x,y,z,size*3,size*.6f,red,green,blue,alpha/2);
            billboard(out,pose,right,up,x,y,z,size*.6f,size*3,red,green,blue,alpha/2);
        }
    }

    private static void billboard(VertexConsumer out,PoseStack.Pose pose,Vector3f right,Vector3f up,double x,double y,double z,float width,float height,int red,int green,int blue,int alpha) {
        float rx=right.x()*width*.5f,ry=right.y()*width*.5f,rz=right.z()*width*.5f;
        float ux=up.x()*height*.5f,uy=up.y()*height*.5f,uz=up.z()*height*.5f;
        vertex(out,pose,x-rx-ux,y-ry-uy,z-rz-uz,0,1,red,green,blue,alpha,0,0,1);
        vertex(out,pose,x+rx-ux,y+ry-uy,z+rz-uz,1,1,red,green,blue,alpha,0,0,1);
        vertex(out,pose,x+rx+ux,y+ry+uy,z+rz+uz,1,0,red,green,blue,alpha,0,0,1);
        vertex(out,pose,x-rx+ux,y-ry+uy,z-rz+uz,0,0,red,green,blue,alpha,0,0,1);
    }

    private static void horizontal(VertexConsumer out,PoseStack.Pose pose,double x,double y,double z,float width,float depth,int red,int green,int blue,int alpha) {
        float w=width*.5f,d=depth*.5f;
        vertex(out,pose,x-w,y,z-d,0,0,red,green,blue,alpha,0,1,0);
        vertex(out,pose,x-w,y,z+d,0,1,red,green,blue,alpha,0,1,0);
        vertex(out,pose,x+w,y,z+d,1,1,red,green,blue,alpha,0,1,0);
        vertex(out,pose,x+w,y,z-d,1,0,red,green,blue,alpha,0,1,0);
    }

    private static void vertex(VertexConsumer out,PoseStack.Pose pose,double x,double y,double z,float u,float v,int red,int green,int blue,int alpha,float nx,float ny,float nz) {
        out.vertex(pose.pose(),(float)x,(float)y,(float)z).color(red,green,blue,alpha).uv(u,v)
                .overlayCoords(OverlayTexture.NO_OVERLAY).uv2(LightTexture.FULL_BRIGHT).normal(pose.normal(),nx,ny,nz).endVertex();
    }
}
