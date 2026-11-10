package com.sirin.hk3gtl.client.entity;

import com.sirin.hk3gtl.common.entity.Hk3KianaReviewEntity;
import net.minecraft.client.model.PlayerModel;
import net.minecraft.client.model.geom.ModelLayers;
import net.minecraft.client.renderer.entity.EntityRendererProvider;
import net.minecraft.client.renderer.entity.LivingEntityRenderer;
import net.minecraft.resources.ResourceLocation;

/**
 * 【变更记录 #1】2026-10-01 19:03:37（修订141）
 * - 删除：无；新增：128像素皮肤的细手臂渲染器及手工配件层。
 * - 修改：保持标准64单位UV，采样128像素高清贴图，无缩图损失。
 * - 用途：二审形象独立于空律实体；身体及配件使用同一姿态与可见性。
 */
/** 【变更记录 #2】2026-10-01 19:18:39（修订143）：删除：无；新增／修改：配件改由模型重载回调提供，不再读取方块几何JSON；用途：琪亚娜三层星海翅膀。 */
public final class Hk3KianaReviewRenderer extends LivingEntityRenderer<Hk3KianaReviewEntity, PlayerModel<Hk3KianaReviewEntity>> {
    private static final ResourceLocation SKIN = new ResourceLocation("hk3gtl", "textures/entity/kiana_review.png");
    public Hk3KianaReviewRenderer(EntityRendererProvider.Context context) {
        super(context, new PlayerModel<>(context.bakeLayer(ModelLayers.PLAYER_SLIM), true), .35F);
        addLayer(new Hk3KianaEquipmentLayer(this));
    }
    @Override public ResourceLocation getTextureLocation(Hk3KianaReviewEntity entity) { return SKIN; }
}
