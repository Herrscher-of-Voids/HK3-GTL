package com.sirin.hk3gtl.client.entity;

import com.sirin.hk3gtl.common.entity.Hk3KianaReviewEntity;
import net.minecraft.client.model.PlayerModel;
import net.minecraft.client.model.geom.ModelLayers;
import net.minecraft.client.renderer.entity.EntityRendererProvider;
import net.minecraft.client.renderer.entity.LivingEntityRenderer;
import net.minecraft.resources.ResourceLocation;

 





 
public final class Hk3KianaReviewRenderer extends LivingEntityRenderer<Hk3KianaReviewEntity, PlayerModel<Hk3KianaReviewEntity>> {
    private static final ResourceLocation SKIN = new ResourceLocation("hk3gtl", "textures/entity/kiana_review.png");
    public Hk3KianaReviewRenderer(EntityRendererProvider.Context context) {
        super(context, new PlayerModel<>(context.bakeLayer(ModelLayers.PLAYER_SLIM), true), .35F);
        addLayer(new Hk3KianaEquipmentLayer(this));
    }
    @Override public ResourceLocation getTextureLocation(Hk3KianaReviewEntity entity) { return SKIN; }
}
