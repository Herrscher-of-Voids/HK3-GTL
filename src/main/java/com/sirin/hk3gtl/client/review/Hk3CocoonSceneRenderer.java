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

/**
 * 【文件职责】仅在一审独立空间绘制球形终焉之茧，不注册人形实体、不操作世界方块。
 * 【变更记录 #1】2026-10-01 20:00:40（内测5修订146）
 * - 删除：无；新增：球壳、亮核、碎片与光环的场景绘制，读取Hk3CocoonGeometry快照。
 * - 修改：沿用512格房间布局；用途：每场会面的玩家共同看到固定在前上方的茧。
 * - 边界：其他维度不绘制，离开会面自动消失；先画不透明面再画薄光环，不改审查或结算。
 */
/** 【变更记录 #2】2026-10-01 20:04:51（修订146追加）：删除：小尺度展示假设；新增：200格球体支持；修改：面数上限45000及场景512格距离边界，渲染器临时延长远裁面并还原雾与投影；用途：落实玩家百倍尺度与菱形核心，不让低视距截断球体。 */
@Mod.EventBusSubscriber(modid="hk3gtl", value=Dist.CLIENT)
public final class Hk3CocoonSceneRenderer {
    private static final ResourceLocation DIMENSION=new ResourceLocation("hk3gtl","cocoon_review");
    private static final ResourceLocation WHITE=new ResourceLocation("hk3gtl","textures/effect/cocoon_white.png");
    private static final RenderType SOLID=RenderType.entityCutoutNoCull(WHITE);
    private static final RenderType GLOW=RenderType.entityTranslucentEmissive(WHITE);
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
        float wave=(float)Math.sin(time*Math.PI*2/data.period());
        var pose=event.getPoseStack();var buffers=mc.renderBuffers().bufferSource();
        float fogStart=RenderSystem.getShaderFogStart(),fogEnd=RenderSystem.getShaderFogEnd();
        var projection=new Matrix4f(RenderSystem.getProjectionMatrix());var sorting=RenderSystem.getVertexSorting();
        pose.pushPose();
        try{
            // 茧是远处的200格天体；仅自身绘制临时延长远裁面、移走距离雾，随后完整恢复。
            if(mc.gameRenderer.getDepthFar()<1024 && Math.abs(projection.m23()+1)<.001f){
                float near=projection.m32()/(projection.m22()-1),far=1024;
                RenderSystem.setProjectionMatrix(new Matrix4f(projection).m22(-(far+near)/(far-near)).m32(-2*far*near/(far-near)),sorting);
            }
            RenderSystem.setShaderFogStart(900);RenderSystem.setShaderFogEnd(1024);
            pose.translate(x-camera.x,data.y()+data.bob()*wave-camera.y,z-camera.z);
            pose.mulPose(Axis.YP.rotation(data.yaw()*wave));
            for(boolean glow:new boolean[]{false,true}){
                var type=glow?GLOW:SOLID;var consumer=buffers.getBuffer(type);
                for(var part:data.parts()){
                    if(part.kind().equals("glow")!=glow)continue;
                    pose.pushPose();
                    pose.translate(part.x(),part.y()+part.bob()*Math.sin(time*.55+part.phase()),part.z());
                    if(part.speed()!=0)pose.mulPose(Axis.YP.rotation(time*part.speed()+part.phase()));
                    float brightness=part.kind().equals("pulse")?.91f+.09f*wave:1f;
                    int alpha=glow?(int)(72+18*wave):255;
                    for(var face:part.faces())draw(consumer,pose.last(),face,brightness,alpha);
                    pose.popPose();
                }
                buffers.endBatch(type);
            }
        }finally{
            pose.popPose();RenderSystem.setProjectionMatrix(projection,sorting);
            RenderSystem.setShaderFogStart(fogStart);RenderSystem.setShaderFogEnd(fogEnd);
        }
    }
    /** 原版实体格式为四边形；重复末点准确表达三角面，不产生额外可见面。 */
    private static void draw(VertexConsumer out,PoseStack.Pose pose,Hk3CocoonGeometry.Face face,float light,int alpha){
        for(int i=0;i<4;i++){
            int p=Math.min(i,2)*3;
            out.vertex(pose.pose(),face.xyz()[p],face.xyz()[p+1],face.xyz()[p+2])
                    .color((int)(face.red()*light),(int)(face.green()*light),(int)(face.blue()*light),alpha)
                    .uv(.5f,.5f).overlayCoords(OverlayTexture.NO_OVERLAY).uv2(LightTexture.FULL_BRIGHT)
                    .normal(pose.normal(),face.nx(),face.ny(),face.nz()).endVertex();
        }
    }
}
