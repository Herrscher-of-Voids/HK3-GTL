package com.sirin.hk3gtl.client.entity;



import com.mojang.blaze3d.vertex.PoseStack;
import com.mojang.math.Axis;
import com.sirin.hk3gtl.common.constants.Hk3Constants;
import com.sirin.hk3gtl.common.entity.SirinEntranceFeatures;
import com.sirin.hk3gtl.common.entity.VoidQueenSirinEntity;
import net.minecraft.client.Minecraft;
import net.minecraft.client.model.PlayerModel;
import net.minecraft.client.model.geom.ModelPart;
import net.minecraft.client.renderer.MultiBufferSource;
import net.minecraft.client.renderer.entity.RenderLayerParent;
import net.minecraft.client.renderer.entity.layers.RenderLayer;
import net.minecraft.client.renderer.texture.OverlayTexture;
import net.minecraft.client.resources.model.BakedModel;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.item.ItemDisplayContext;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;
import org.slf4j.Logger;
import com.mojang.logging.LogUtils;

import java.util.List;
import java.util.Map;

/**
 * 西琳翅膀渲染层 —— 参照 ExtraBotany CoreOfTheVoid Herrscher 的 BakedModel 渲染方式。
 *
 * 使用 item/generated JSON 模型将 2D 翅膀贴图自动烘焙为 3D 挤出几何体，
 * 渲染时通过 ItemRenderer 直接绘制预烘焙的 BakedModel，性能远优于逐帧逐像素构建。
 *
 * 左右两翼各 3 层 BakedModel；右翼贴图为左翼在资源文件中的水平翻转（见 tools/gen_right_wing.mjs）。
 * 不可对模型使用 scale(-1,1,1) 做镜像，否则会反转三角绕序导致背面剔除异常。
 */
public class SirinWingLayer extends RenderLayer<VoidQueenSirinEntity, PlayerModel<VoidQueenSirinEntity>> {

    private static final Logger LOGGER = LogUtils.getLogger();

    // ── 模型路径（对应 assets/hk3gtl/models/wing/*.json） ──
    // 修改要点：翅膀贴图/模型更换时，同步修改这里的路径和对应 JSON 文件
    private static final ResourceLocation LOC_L_BODY = prefix("wing/sirin_left_body");    // 左翼主体
    private static final ResourceLocation LOC_L_SEC  = prefix("wing/sirin_left_secondary"); // 左翼次要层
    private static final ResourceLocation LOC_L_CORE = prefix("wing/sirin_left_core");    // 左翼核心层
    private static final ResourceLocation LOC_R_BODY = prefix("wing/sirin_right_body");   // 右翼主体
    private static final ResourceLocation LOC_R_SEC  = prefix("wing/sirin_right_secondary"); // 右翼次要层
    private static final ResourceLocation LOC_R_CORE = prefix("wing/sirin_right_core");   // 右翼核心层

    /** 供 Hk3ClientSetup.onRegisterAdditionalModels 注册的全部翅膀模型列表 */
    public static final List<ResourceLocation> WING_MODELS = List.of(
            LOC_L_BODY, LOC_L_SEC, LOC_L_CORE,
            LOC_R_BODY, LOC_R_SEC, LOC_R_CORE
    );

    // 烘焙后的 BakedModel 缓存引用，由 onModelBake 回调填充
    private static BakedModel lBodyModel, lSecModel, lCoreModel;
    private static BakedModel rBodyModel, rSecModel, rCoreModel;

    /** 全亮光照值（翅膀自发光效果） */
    private static final int FULL_BRIGHT = 0xF000F0;
    /** ItemRenderer.render 需要一个 ItemStack，此处用木棍占位（不影响渲染结果） */
    private static final ItemStack DUMMY_STACK = new ItemStack(Items.STICK);

    public SirinWingLayer(
            RenderLayerParent<VoidQueenSirinEntity, PlayerModel<VoidQueenSirinEntity>> parent,
            ModelPart modelRoot) {
        super(parent);
    }

    private static ResourceLocation prefix(String path) {
        return new ResourceLocation(Hk3Constants.MOD_ID, path);
    }

    /** ModelEvent.ModifyBakingResult 回调：缓存烘焙后的 BakedModel */
    public static void onModelBake(Map<ResourceLocation, BakedModel> models) {
        lBodyModel = models.get(LOC_L_BODY);
        lSecModel  = models.get(LOC_L_SEC);
        lCoreModel = models.get(LOC_L_CORE);
        rBodyModel = models.get(LOC_R_BODY);
        rSecModel  = models.get(LOC_R_SEC);
        rCoreModel = models.get(LOC_R_CORE);

        int loaded = 0;
        for (BakedModel m : new BakedModel[]{lBodyModel, lSecModel, lCoreModel, rBodyModel, rSecModel, rCoreModel}) {
            if (m != null) loaded++;
        }
        LOGGER.info("[HK3GTL] 翅膀 BakedModel 已加载: {}/6", loaded);
    }

    // ══════════════════════════════════════
    //  渲染主入口
    // ══════════════════════════════════════

    @Override
    public void render(PoseStack ps, MultiBufferSource buffers, int light,
                       VoidQueenSirinEntity entity, float limbSwing, float limbSwingAmount,
                       float partialTick, float ageInTicks, float netHeadYaw, float headPitch) {
        if (!SirinEntranceFeatures.WING_LAYER_ENABLED) return;
        if (lBodyModel == null && rBodyModel == null) return;

        float flap = 12F + (float) ((Math.sin((entity.tickCount + partialTick) * 0.12) + 0.4) * 5.0);

        ps.pushPose();

        // 躯干局部位移/俯仰；yaw 由父级 PoseStack（实体朝向）承担，禁止 body.yRot 二次叠乘
        ModelPart body = getParentModel().body;
        float savedBodyY = body.yRot;
        body.yRot = 0.0F;
        body.translateAndRotate(ps);
        body.yRot = savedBodyY;

        ps.translate(0, -0.2F, 0.3F);

        // 右翼（观察者右侧）
        renderWingSide(ps, buffers, flap, false);

        // 左翼（观察者左侧，通过 Y 旋转 180° 实现镜像）
        renderWingSide(ps, buffers, flap, true);

        ps.popPose();
    }

    // ══════════════════════════════════════
    //  单翼渲染
    // ══════════════════════════════════════

    /**
     * 渲染一侧翅膀的 3 个层。
     * 参照 ExtraBotany Herrscher 的方式：
     * - 右翼使用 Y 轴正向旋转 + 展开偏移
     * - 左翼使用 Y 轴旋转 180° 实现镜像
     */
    private void renderWingSide(PoseStack ps, MultiBufferSource buffers, float flap, boolean isLeft) {
        // 两侧共用左翼模型，靠 Y 旋转 180° 差实现左右镜像（避免翻转贴图导致根/尖颠倒）
        BakedModel body = lBodyModel;
        BakedModel sec  = lSecModel;
        BakedModel core = lCoreModel;
        if (body == null) return;

        var itemRenderer = Minecraft.getInstance().getItemRenderer();

        ps.pushPose();

        // 扇翼动画
        float flapAngle = flap * 0.25F;
        if (isLeft) {
            ps.mulPose(Axis.YP.rotationDegrees(180F - flapAngle));
        } else {
            ps.mulPose(Axis.YP.rotationDegrees(flapAngle));
        }

        // 水平偏移使翅膀远离身体
        ps.translate(-1.2, 0, 0);

        // 缩放（负 Y/Z 翻转朝向，与 ExtraBotany 一致）
        ps.scale(1.7F, -1.7F, -1.7F);

        // 渲染 3 层
        itemRenderer.render(DUMMY_STACK, ItemDisplayContext.NONE, false,
                ps, buffers, FULL_BRIGHT, OverlayTexture.NO_OVERLAY, body);

        if (sec != null) {
            itemRenderer.render(DUMMY_STACK, ItemDisplayContext.NONE, false,
                    ps, buffers, FULL_BRIGHT, OverlayTexture.NO_OVERLAY, sec);
        }

        if (core != null) {
            itemRenderer.render(DUMMY_STACK, ItemDisplayContext.NONE, false,
                    ps, buffers, FULL_BRIGHT, OverlayTexture.NO_OVERLAY, core);
        }

        ps.popPose();
    }
}
