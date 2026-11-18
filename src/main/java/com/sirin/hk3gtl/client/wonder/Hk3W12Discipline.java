package com.sirin.hk3gtl.client.wonder;

import com.mojang.blaze3d.platform.GlStateManager;
import com.mojang.blaze3d.systems.RenderSystem;
import com.mojang.blaze3d.vertex.*;
import net.minecraft.client.renderer.GameRenderer;
import net.minecraft.client.renderer.ShaderInstance;
import org.joml.Matrix4f;
import org.joml.Vector3f;
import java.util.ArrayList;
import java.util.Comparator;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

final class Hk3W12Discipline {
    private static final BufferBuilder BUILDER=new BufferBuilder(1024*1024);
    private static VertexBuffer wave,ribbons,particles,butterflies;
    private static ShaderInstance butterflyShader;
    private Hk3W12Discipline(){}
    static void butterflyShader(ShaderInstance value){butterflyShader=value;}
    static void clear(){
        if(wave!=null){wave.close();wave=null;}
        if(ribbons!=null){ribbons.close();ribbons=null;}
        if(particles!=null){particles.close();particles=null;}
        if(butterflies!=null){butterflies.close();butterflies=null;}
    }
    private static double hash(double n){double x=Math.sin(n*127.1+19.7)*43758.5453;return x-Math.floor(x);}
    private static double fract(double x){return x-Math.floor(x);}
    private static double smooth(double a,double b,double x){double t=Math.max(0,Math.min(1,(x-a)/(b-a)));return t*t*(3-2*t);}

    static void draw(Hk3W12FxModel model,Matrix4f origin,Matrix4f projection,Vector3f right,Vector3f up,
                     double flow,double seconds,double seed,boolean running){
        if(wave==null)createWave();
        var effects=model.data().effects();float[] center=effects.center();
        var target=new Vector3f(center[0],center[1],center[2]);
        float strength=running?1.2f:.55f;
        RenderSystem.enableDepthTest();RenderSystem.disableCull();RenderSystem.depthMask(false);RenderSystem.enableBlend();
        RenderSystem.blendFunc(GlStateManager.SourceFactor.SRC_ALPHA,GlStateManager.DestFactor.ONE);
        double cycle=seconds%10,radius=12+488*Math.min(cycle/7.8,1);
        float opacity=(float)((running?.15:.085)*Math.min(cycle/.5,1)*(1-smooth(7.8,10,cycle)));
        RenderSystem.setShaderColor(1,1,1,opacity);
        wave.bind();wave.drawWithShader(new Matrix4f(origin).translate(target).scale((float)radius),projection,GameRenderer.getPositionColorShader());
        RenderSystem.setShaderColor(1,1,1,1);
        BUILDER.begin(VertexFormat.Mode.QUADS,DefaultVertexFormat.POSITION_COLOR);
        for(float[] source:effects.beam_origins())ribbon(new Vector3f(source[0],source[1],source[2]),target,right,.28f,255,205,114,running?51:20);
        for(float[] source:effects.tower_origins())ribbon(new Vector3f(source[0],source[1],source[2]),towerEnd(source,target),right,.28f,255,235,187,running?66:36);
        float[] radii=effects.lance_energy_radii();
        int lanceAlpha=(int)((running?179:89)*(.8+.2*Math.sin(seconds*2.4)));
        for(float[] n:effects.lance_directions()){
            var direction=new Vector3f(n[0],n[1],n[2]);
            ribbon(new Vector3f(target).fma(radii[0],direction),new Vector3f(target).fma(radii[1],direction),right,.25f,255,227,161,lanceAlpha);
        }
        for(int band=0;band<6;band++){
            var normal=new Vector3f((float)Math.sin(band*2.3),(float)Math.cos(band*1.7),(float)Math.sin(band+1)).normalize();
            var u=new Vector3f(normal).cross(.1f,1,.2f).normalize();var v=new Vector3f(normal).cross(u);
            for(int i=0;i<26;i++){
                var a=arcPoint(u,v,i,band,seconds,target);var b=arcPoint(u,v,i+1,band,seconds,target);
                int alpha=(int)(255*(.12+.62*Math.pow(.5+.5*Math.sin(seconds*5+a.y*.4),7)));
                ribbon(a,b,right,.15f,255,245,212,alpha);
            }
        }
        if(ribbons==null)ribbons=new VertexBuffer(VertexBuffer.Usage.DYNAMIC);
        ribbons.bind();ribbons.upload(BUILDER.end());ribbons.drawWithShader(origin,projection,GameRenderer.getPositionColorShader());
        BUILDER.begin(VertexFormat.Mode.QUADS,DefaultVertexFormat.POSITION_COLOR);
        int sequence=0;
        for(float[] source:effects.beam_origins()){
            var start=new Vector3f(source[0],source[1],source[2]);
            var axis=new Vector3f(target).sub(start).normalize();var u=new Vector3f(axis).cross(.13f,1,.17f).normalize();var v=new Vector3f(axis).cross(u);
            for(int i=0;i<92;i++)streamPoint(start,target,u,v,i/92.,hash(++sequence+seed),flow,seconds,strength,.19,right,up);
            for(int i=0;i<24;i++){
                double phase=i/24.,random=hash(++sequence+seed),age=cycle-start.distance(target)/500.*7.8;
                if(age<0||age>=.85)continue;
                var direction=new Vector3f((float)Math.sin(random*187),(float)Math.cos(phase*48),(float)Math.sin(phase*139+random*3)).normalize();
                var point=new Vector3f(start).fma((float)(Math.sqrt(age)*23),direction).add(0,(float)(-16*age*age),0);
                particle(point,right,up,(float)(1.3+random*2),(float)(1-smooth(.05,.85,age)),random>=.76);
            }
        }
        for(float[] source:effects.tower_origins()){
            var start=new Vector3f(source[0],source[1],source[2]);var end=towerEnd(source,target);
            var axis=new Vector3f(end).sub(start).normalize();var u=new Vector3f(axis).cross(.13f,1,.17f).normalize();var v=new Vector3f(axis).cross(u);
            for(int i=0;i<64;i++)streamPoint(start,end,u,v,i/64.,hash(++sequence+seed),flow,seconds,strength,.11,right,up);
        }
        for(int i=0;i<720;i++){
            double phase=i/720.,random=hash(++sequence+seed),a=phase*Math.PI*2+flow*(.13+random*.12),b=random*Math.PI*2+flow*.17,r=13+3*Math.sin(random*93+seconds*.8);
            var point=new Vector3f(target).add((float)(Math.cos(a)*Math.cos(b)*r),(float)(Math.sin(b)*r),(float)(Math.sin(a)*Math.cos(b)*r));
            float light=(float)(.35+.65*Math.pow(.5+.5*Math.sin(seconds*2+random*34),2));
            particle(point,right,up,(float)(1+random*2),light,random>=.35);
        }
        if(particles==null)particles=new VertexBuffer(VertexBuffer.Usage.DYNAMIC);
        particles.bind();particles.upload(BUILDER.end());particles.drawWithShader(origin,projection,GameRenderer.getPositionColorShader());
        if(running)drawButterflies(target,right,up,origin,projection,seconds,seed);
        VertexBuffer.unbind();RenderSystem.defaultBlendFunc();RenderSystem.disableBlend();RenderSystem.depthMask(true);RenderSystem.enableCull();
    }

    private static Vector3f towerEnd(float[] source,Vector3f target){
        var radial=new Vector3f(source[0]-target.x,0,source[2]-target.z).normalize().mul(350);
        return new Vector3f(target.x+radial.x,327,target.z+radial.z);
    }
    private static Vector3f arcPoint(Vector3f u,Vector3f v,int i,int band,double seconds,Vector3f target){
        double a=i/26.*Math.PI*1.35+band,r=18+hash(i+band*93)*5;
        var point=new Vector3f(u).mul((float)(Math.cos(a)*r)).fma((float)(Math.sin(a)*r),v);
        return point.add((float)Math.sin(point.y*1.3+seconds*3)*1.2f,(float)Math.cos(point.z*1.7-seconds*4)*1.2f,(float)Math.sin(point.x*1.9-seconds*2)*1.2f).add(target);
    }
    private static void streamPoint(Vector3f start,Vector3f end,Vector3f u,Vector3f v,double phase,double random,
                                    double flow,double seconds,float strength,double speed,Vector3f right,Vector3f up){
        double t=fract(phase+flow*speed),a=random*62.83+seconds*2,r=.4+random*1.2;
        var point=new Vector3f(start).lerp(end,(float)t).fma((float)(Math.cos(a)*r),u).fma((float)(Math.sin(a)*r),v);
        particle(point,right,up,(float)(1.5+random*1.8),(float)((.28+.72*Math.sin(t*Math.PI))*strength),random>=.93);
    }
    private static void particle(Vector3f point,Vector3f right,Vector3f up,float size,float light,boolean white){
        int red=(int)(255*Math.min(1,light)),green=(int)(255*Math.min(1,(white?.95:.56)*light)),blue=(int)(255*Math.min(1,(white?.77:.11)*light));
        quad(point,right,up,size,size,red,green,blue,(int)(255*Math.min(1,light*.82)),false);
    }
    private static void ribbon(Vector3f start,Vector3f end,Vector3f right,float width,int red,int green,int blue,int alpha){
        for(int i=0;i<4;i++){
            var p=i<2?start:end;float side=i==1||i==2?width:-width;
            BUILDER.vertex(p.x+right.x*side,p.y+right.y*side,p.z+right.z*side).color(red,green,blue,alpha).endVertex();
        }
    }
    private static void quad(Vector3f point,Vector3f right,Vector3f up,float width,float height,int red,int green,int blue,int alpha,boolean textured){
        for(int i=0;i<4;i++){
            float x=i==1||i==2?.5f:-.5f,y=i>=2?.5f:-.5f;
            var vertex=BUILDER.vertex(point.x+right.x*x*width+up.x*y*height,point.y+right.y*x*width+up.y*y*height,point.z+right.z*x*width+up.z*y*height).color(red,green,blue,alpha);
            if(textured)vertex.uv(x+.5f,.5f-y);
            vertex.endVertex();
        }
    }
    private static void drawButterflies(Vector3f target,Vector3f right,Vector3f up,Matrix4f origin,Matrix4f projection,double seconds,double seed){
        BUILDER.begin(VertexFormat.Mode.QUADS,DefaultVertexFormat.POSITION_COLOR_TEX);
        for(int i=0;i<320;i++){
            double phase=hash(i*11.7+3+seed),random=hash(i*31.3+4+seed),fall=fract(phase+seconds*(.013+random*.009));
            var point=new Vector3f(target.x+(float)((hash(i*7.3+1+seed)-.5)*880+Math.sin(seconds*.21+random*87)*12),
                (float)(65+(1-fall)*245),target.z+(float)((hash(i*19.1+2+seed)-.5)*650+Math.cos(seconds*.17+phase*94)*9));
            double gold=smooth(.80,.92,fall),flap=.7+.3*Math.sin(seconds*(2.5+random)+phase*37);
            boolean warm=random>=.62;float size=(float)((11+random*11)*(1-smooth(.83,1,fall)*.84));
            int red=(int)(255*((warm?1:.19)*(1-gold)+gold));
            int green=(int)(255*((warm?.73:.66)*(1-gold)+.72*gold));
            int blue=(int)(255*((warm?.26:1)*(1-gold)+.18*gold));
            int alpha=(int)(255*smooth(0,.08,fall)*(1-smooth(.92,1,fall))*.75);
            quad(point,right,up,(float)(size*flap),size,red,green,blue,alpha,true);
        }
        if(butterflies==null)butterflies=new VertexBuffer(VertexBuffer.Usage.DYNAMIC);
        butterflies.bind();butterflies.upload(BUILDER.end());butterflies.drawWithShader(origin,projection,butterflyShader);
    }

    private static int midpoint(List<Vector3f> vertices,Map<Long,Integer> cache,int a,int b){
        long key=((long)Math.min(a,b)<<32)|Math.max(a,b);
        return cache.computeIfAbsent(key,k->{vertices.add(new Vector3f(vertices.get(a)).add(vertices.get(b)).normalize());return vertices.size()-1;});
    }
    private static void createWave(){
        float phi=(1+(float)Math.sqrt(5))/2;
        var vertices=new ArrayList<Vector3f>();
        for(float[] p:new float[][]{{-1,phi,0},{1,phi,0},{-1,-phi,0},{1,-phi,0},{0,-1,phi},{0,1,phi},{0,-1,-phi},{0,1,-phi},{phi,0,-1},{phi,0,1},{-phi,0,-1},{-phi,0,1}})vertices.add(new Vector3f(p[0],p[1],p[2]).normalize());
        List<int[]> faces=new ArrayList<>(List.of(new int[][]{{0,11,5},{0,5,1},{0,1,7},{0,7,10},{0,10,11},{1,5,9},{5,11,4},{11,10,2},{10,7,6},{7,1,8},{3,9,4},{3,4,2},{3,2,6},{3,6,8},{3,8,9},{4,9,5},{2,4,11},{6,2,10},{8,6,7},{9,8,1}}));
        for(int level=0;level<3;level++){
            var cache=new HashMap<Long,Integer>();var next=new ArrayList<int[]>();
            for(int[] f:faces){int a=midpoint(vertices,cache,f[0],f[1]),b=midpoint(vertices,cache,f[1],f[2]),c=midpoint(vertices,cache,f[2],f[0]);next.add(new int[]{f[0],a,c});next.add(new int[]{f[1],b,a});next.add(new int[]{f[2],c,b});next.add(new int[]{a,b,c});}
            faces=next;
        }
        List<List<Vector3f>> cells=new ArrayList<>();for(var vertex:vertices)cells.add(new ArrayList<>());
        for(int[] face:faces){var p=new Vector3f(vertices.get(face[0])).add(vertices.get(face[1])).add(vertices.get(face[2])).normalize();for(int index:face)cells.get(index).add(p);}
        BUILDER.begin(VertexFormat.Mode.DEBUG_LINES,DefaultVertexFormat.POSITION_COLOR);
        for(int i=0;i<vertices.size();i++){
            var n=vertices.get(i);var u=new Vector3f(n).cross(.19f,1,.13f).normalize();var v=new Vector3f(n).cross(u);var cell=cells.get(i);
            cell.sort(Comparator.comparingDouble(p->Math.atan2(p.dot(v),p.dot(u))));
            for(int j=0;j<cell.size();j++)for(var p:new Vector3f[]{cell.get(j),cell.get((j+1)%cell.size())})BUILDER.vertex(p.x,p.y,p.z).color(255,204,105,255).endVertex();
        }
        wave=new VertexBuffer(VertexBuffer.Usage.STATIC);wave.bind();wave.upload(BUILDER.end());VertexBuffer.unbind();
    }
}
