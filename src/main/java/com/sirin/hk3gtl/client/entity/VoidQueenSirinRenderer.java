package com.sirin.hk3gtl.client.entity;



import com.mojang.blaze3d.vertex.PoseStack;
import com.sirin.hk3gtl.common.constants.Hk3Constants;
import com.sirin.hk3gtl.common.entity.VoidQueenSirinEntity;
import net.minecraft.client.model.PlayerModel;
import net.minecraft.client.model.geom.ModelLayers;
import net.minecraft.client.renderer.entity.EntityRendererProvider;
import net.minecraft.client.renderer.entity.HumanoidMobRenderer;
import net.minecraft.resources.ResourceLocation;

/**
 * 空之律者·西琳渲染器 —— 使用标准 PlayerModel 皮肤，附加双翼渲染层。
 *
 * <h3>职责</h3>
 * 继承 HumanoidMobRenderer，使用玩家模型渲染西琳实体，叠加 SirinWingLayer 翅膀层。
 *
 * <h3>修改指南</h3>
 * <ul>
 *   <li>更换皮肤贴图：修改 TEXTURE 路径（对应 assets/hk3gtl/textures/entity/ 下的 PNG 文件）</li>
 *   <li>调整模型阴影大小：修改 super() 的第三个参数（当前 0.5F）</li>
 *   <li>新增渲染层（如光环/特效）：在构造器中调用 this.addLayer()</li>
 * </ul>
 */
public class VoidQueenSirinRenderer
        extends HumanoidMobRenderer<VoidQueenSirinEntity, PlayerModel<VoidQueenSirinEntity>> {

    /** 西琳实体皮肤贴图路径（assets/hk3gtl/textures/entity/void_queen_sirin.png） */
    private static final ResourceLocation TEXTURE =
            new ResourceLocation(Hk3Constants.MOD_ID, "textures/entity/void_queen_sirin.png");

    /** 构造渲染器：使用标准玩家模型 + 翅膀渲染层，阴影半径 0.5 */
    public VoidQueenSirinRenderer(EntityRendererProvider.Context context) {
        super(context, new PlayerModel<>(context.bakeLayer(ModelLayers.PLAYER), false), 0.5F);
        this.addLayer(new SirinWingLayer(this, context.bakeLayer(ModelLayers.PLAYER)));
    }

    /** 坏结局抓取阶段：按同步的坏结局缩放系数整体放大模型（含翅膀层）。 */
    @Override
    protected void scale(VoidQueenSirinEntity entity, PoseStack poseStack, float partialTick) {
        float badEndingScale = entity.getBadEndingScale();
        if (badEndingScale != 1.0F) {
            poseStack.scale(badEndingScale, badEndingScale, badEndingScale);
        }
        super.scale(entity, poseStack, partialTick);
    }

    @Override
    public ResourceLocation getTextureLocation(VoidQueenSirinEntity entity) {
        return TEXTURE;
    }
}
