package com.sirin.hk3gtl.client.entity;

import com.mojang.blaze3d.vertex.PoseStack;
import com.mojang.math.Axis;
import com.sirin.hk3gtl.common.entity.Hk3KianaReviewEntity;
import net.minecraft.client.Minecraft;
import net.minecraft.client.model.PlayerModel;
import net.minecraft.client.renderer.LightTexture;
import net.minecraft.client.renderer.MultiBufferSource;
import net.minecraft.client.renderer.entity.RenderLayerParent;
import net.minecraft.client.renderer.entity.layers.RenderLayer;
import net.minecraft.client.renderer.texture.OverlayTexture;
import net.minecraft.client.resources.model.BakedModel;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.item.ItemDisplayContext;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;
import java.util.List;
import java.util.Map;

/**
 * 【变更记录 #1】2026-10-01 19:03:37（修订141）
 * - 删除：无；新增：从同源几何资源烘焙双翼、枪、剑，按材质分组绘制。
 * - 修改：配件绑身体与左右手臂，翼根缓慢摆动；星点和核心局部自亮。
 * - 用途：参照用户选择的方块造型；仅重载时解析模型，不在逐帧期间构建方块或读取磁盘。
 */
/** 【变更记录 #2】2026-10-01 19:10:52（修订142）：删除：二审武器展示；新增：无；修改：配件资源仅保留双翼，撤下武器手臂绑定分支，二审双手保持空手；用途：遵循负责人只保留琪亚娜和翅膀的最新决定。 */
/** 【变更记录 #3】2026-10-01 19:18:39（修订143）：删除：逐像素方块配件烘焙路径；新增：两侧各三层像素BakedModel缓存；修改：外框、星海、星点独立挤出，动态图集控制错峰闪烁；用途：保留二审翼形，减少零散方块并使紫色内翼呈现星海。 */
/** 【变更记录 #4】2026-10-01 19:30:16（修订144）：删除：三层同心嵌套；新增：五层独立Z位置及间距；修改：外框1、星海1、星点、星海2、外框2，星海采用半透图集材质；用途：消除体积穿插及共面竞争，让中央星点从两面可见。 */
/** 【变更记录 #5】2026-10-01 19:47:01（修订145）：删除：过大翼瓣展开比例；新增：参考轮廓对应尺度；修改：宽中翼与短下翼收拢、五层总厚度收至0.66模型像素；用途：符合用户新参考中的紧凑翼形，不改变二审业务。 */
public final class Hk3KianaEquipmentLayer extends RenderLayer<Hk3KianaReviewEntity, PlayerModel<Hk3KianaReviewEntity>> {
    public static final List<ResourceLocation> WING_MODELS = List.of(
            model("left_frame1"), model("left_galaxy1"), model("left_stars"), model("left_galaxy2"), model("left_frame2"),
            model("right_frame1"), model("right_galaxy1"), model("right_stars"), model("right_galaxy2"), model("right_frame2"));
    private static volatile List<BakedModel> baked = List.of();
    private static final ItemStack DUMMY = new ItemStack(Items.STICK);
    private static final float[] DEPTH = {.06F, .04F, .04F, .04F, .06F};
    private static final float[] Z = {-.3F, -.15F, 0, .15F, .3F};

    public Hk3KianaEquipmentLayer(RenderLayerParent<Hk3KianaReviewEntity, PlayerModel<Hk3KianaReviewEntity>> parent) {
        super(parent);
    }
    private static ResourceLocation model(String suffix) {
        return new ResourceLocation("hk3gtl", "wing/kiana_" + suffix);
    }
    /** 资源重载时替换整组缓存；任何一层缺失时不绘制残缺翅膀。 */
    public static void onModelBake(Map<ResourceLocation, BakedModel> models) {
        var next = WING_MODELS.stream().map(models::get).toList();
        if (next.stream().anyMatch(java.util.Objects::isNull)) {
            baked = List.of();
            com.mojang.logging.LogUtils.getLogger().error("[HK3GTL] 琪亚娜五层翅膀模型不完整，保留人物渲染");
        } else {
            baked = List.copyOf(next);
            com.mojang.logging.LogUtils.getLogger().info("[HK3GTL] 琪亚娜五层翅膀模型已加载：10/10");
        }
    }
    @Override public void render(PoseStack pose, MultiBufferSource buffers, int light, Hk3KianaReviewEntity entity,
                                 float swing, float amount, float partial, float age, float yaw, float pitch) {
        List<BakedModel> models = baked;
        if (entity.isInvisible() || models.size() != 10) return;
        var renderer = Minecraft.getInstance().getItemRenderer();
        pose.pushPose();
        getParentModel().body.translateAndRotate(pose);
        for (int side = 0; side < 2; side++) {
            float sign = side == 0 ? 1 : -1;
            pose.pushPose();
            pose.translate(0, 0, 3.8 / 16.0);
            pose.mulPose(Axis.YP.rotation(sign * (.10F + .035F * (float)Math.sin(age * .045F))));
            pose.translate(sign * 1.325, .30, 0);
            for (int layer = 0; layer < 5; layer++) {
                pose.pushPose();
                // 五个独立厚度区间，不再套在同一中心；两层半透星海保留中央星点可见性。
                pose.translate(0, 0, Z[layer] / 16.0);
                pose.scale(2.4F, -2.4F, -DEPTH[layer]);
                renderer.render(DUMMY, ItemDisplayContext.NONE, false, pose, buffers,
                        (layer == 0 || layer == 4) ? light : LightTexture.FULL_BRIGHT, OverlayTexture.NO_OVERLAY,
                        models.get(side * 5 + layer));
                pose.popPose();
            }
            pose.popPose();
        }
        pose.popPose();
    }
}
