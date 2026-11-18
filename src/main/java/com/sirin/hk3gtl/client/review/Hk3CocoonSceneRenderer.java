package com.sirin.hk3gtl.client.review;

import com.mojang.blaze3d.vertex.PoseStack;
import com.mojang.blaze3d.vertex.VertexConsumer;
import com.mojang.math.Axis;
import com.mojang.blaze3d.systems.RenderSystem;
import org.joml.Matrix4f;
import net.minecraft.client.Minecraft;
import net.minecraft.client.renderer.LightTexture;
import net.minecraft.client.renderer.RenderType;
import net.minecraft.client.renderer.texture.OverlayTexture;
import net.minecraft.resources.ResourceLocation;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.client.event.RenderLevelStageEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;









@Mod.EventBusSubscriber(modid="hk3gtl", value=Dist.CLIENT)
public final class Hk3CocoonSceneRenderer {
    private static final ResourceLocation DIMENSION=new ResourceLocation("hk3gtl","cocoon_review");
    private static final RenderType ROCK=RenderType.entityCutoutNoCull(new ResourceLocation("hk3gtl","textures/effect/cocoon_rock.png"));
    private Hk3CocoonSceneRenderer(){}
    @SubscribeEvent public static void render(RenderLevelStageEvent event){
        if(event.getStage()!=RenderLevelStageEvent.Stage.AFTER_TRANSLUCENT_BLOCKS)return;
        var mc=Minecraft.getInstance();var data=Hk3CocoonGeometry.current();
        if(data==null||mc.level==null||mc.player==null||!mc.level.dimension().location().equals(DIMENSION))return;
        var camera=event.getCamera().getPosition();
        double x=Math.floor(mc.player.getX()/data.spacing()+.5)*data.spacing()+data.x();
        double z=Math.floor(mc.player.getZ()/data.spacing()+.5)*data.spacing()+data.z();
        if(camera.distanceToSqr(x,data.y(),z)>512*512)return;
        float time=(mc.level.getGameTime()%240000+event.getPartialTick())/20f;
        Hk3CocoonRenderTypes.time(time);
        float wave=(float)Math.sin(time*Math.PI*2/data.period());
        var pose=event.getPoseStack();var buffers=mc.renderBuffers().bufferSource();
        float fogStart=RenderSystem.getShaderFogStart(),fogEnd=RenderSystem.getShaderFogEnd();
        var projection=new Matrix4f(RenderSystem.getProjectionMatrix());var sorting=RenderSystem.getVertexSorting();
        pose.pushPose();
        try{
            // 仅此隔离场景延长远裁面，绘制后恢复世界投影和距离雾。
            if(mc.gameRenderer.getDepthFar()<1024 && Math.abs(projection.m23()+1)<.001f){
                float near=projection.m32()/(projection.m22()-1),far=1024;
                RenderSystem.setProjectionMatrix(new Matrix4f(projection).m22(-(far+near)/(far-near)).m32(-2*far*near/(far-near)),sorting);
            }
            RenderSystem.setShaderFogStart(900);RenderSystem.setShaderFogEnd(1024);
            pose.translate(x-camera.x,data.y()+data.bob()*wave-camera.y,z-camera.z);
            pose.mulPose(Axis.YP.rotation(data.yaw()*wave));
            for(int pass=0;pass<3;pass++){
                var type=pass==0?ROCK:pass==1?Hk3CocoonRenderTypes.LIGHT:Hk3CocoonRenderTypes.GLOW;
                var consumer=buffers.getBuffer(type);
                for(var part:data.parts()){
                    if((part.rock()?0:part.opacity()<1?2:1)!=pass)continue;
                    boolean moving=part.group().equals("debris");
                    pose.pushPose();
                    double bob=moving?part.bob()*(Math.sin(time*(.19+(part.phase()%1)*.23)+part.phase())+.16*Math.sin(time*.61+part.phase()*1.7)):0;
                    pose.translate(part.x(),part.y()+bob,part.z());
                    if(moving&&part.speed()!=0)pose.mulPose(Axis.YP.rotation(time*part.speed()+part.phase()));
                    float brightness=part.kind().equals("pulse")&&!part.flow()&&!part.soft()?
                            (float)(.94+.045*Math.sin(time*(part.group().equals("core")?.34:.57)+part.phase())+.015*Math.sin(time*.97+part.phase()*2.1)):1;
                    int mode=(part.flow()?1:0)+(part.soft()?2:0);
                    int overlay=(Math.round(part.flowWidth()*100)*4+mode)|(Math.round(part.intensity()*1000)<<16);
                    int metadata=(Math.round(part.phase()*1000)&65535)|(Math.round(part.speed()*10000)<<16);
                    for(var face:part.faces())draw(consumer,pose.last(),part,face,brightness,overlay,metadata);
                    pose.popPose();
                }
                buffers.endBatch(type);
            }
            Hk3CocoonAtmosphere.render(pose,buffers,event.getCamera(),time,data.hotspots());
        }finally{
            pose.popPose();RenderSystem.setProjectionMatrix(projection,sorting);
            RenderSystem.setShaderFogStart(fogStart);RenderSystem.setShaderFogEnd(fogEnd);
        }
    }
    /** 原版实体格式为四边形；重复末点准确表达三角面，不产生额外可见面。 */
    private static void draw(VertexConsumer out,PoseStack.Pose pose,Hk3CocoonGeometry.Part part,Hk3CocoonGeometry.Face face,float light,int overlay,int metadata){
        for(int i=0;i<4;i++){
            int vertex=Math.min(i,2),p=vertex*3;
            float u=face.travel()[vertex],v=face.across()[vertex];
            if(part.rock()){
                float x=(float)(face.xyz()[p]+part.x()),y=(float)(face.xyz()[p+1]+part.y()),z=(float)(face.xyz()[p+2]+part.z());
                if(Math.abs(face.ny())>=Math.max(Math.abs(face.nx()),Math.abs(face.nz()))){u=x/32;v=z/32;}
                else if(Math.abs(face.nx())>Math.abs(face.nz())){u=z/32;v=y/32;}
                else{u=x/32;v=y/32;}
            }
            out.vertex(pose.pose(),face.xyz()[p],face.xyz()[p+1],face.xyz()[p+2])
                    .color((int)(face.red()*light),(int)(face.green()*light),(int)(face.blue()*light),Math.round(part.opacity()*255))
                    .uv(u,v).overlayCoords(part.rock()?OverlayTexture.NO_OVERLAY:overlay).uv2(part.rock()?LightTexture.FULL_BRIGHT:metadata)
                    .normal(pose.normal(),face.nx(),face.ny(),face.nz()).endVertex();
        }
    }
}
