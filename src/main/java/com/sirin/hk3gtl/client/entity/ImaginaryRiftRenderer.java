package com.sirin.hk3gtl.client.entity;

import com.sirin.hk3gtl.common.entity.ImaginaryRiftEntity;
import com.mojang.blaze3d.vertex.PoseStack;
import net.minecraft.client.renderer.MultiBufferSource;
import net.minecraft.client.renderer.entity.EntityRenderer;
import net.minecraft.client.renderer.entity.EntityRendererProvider;
import net.minecraft.resources.ResourceLocation;

/**
 * 裂隙无模型，仅服务端粒子；客户端不绘制实体本体。
 */
public class ImaginaryRiftRenderer extends EntityRenderer<ImaginaryRiftEntity> {

    private static final ResourceLocation DUMMY =
            new ResourceLocation("minecraft", "textures/misc/white.png");

    public ImaginaryRiftRenderer(EntityRendererProvider.Context context) {
        super(context);
    }

    @Override
    public void render(ImaginaryRiftEntity entity, float entityYaw, float partialTicks,
                       PoseStack poseStack, MultiBufferSource buffer, int packedLight) {
        // 粒子由服务端 sendParticles 同步，此处不绘制
    }

    @Override
    public ResourceLocation getTextureLocation(ImaginaryRiftEntity entity) {
        return DUMMY;
    }
}
