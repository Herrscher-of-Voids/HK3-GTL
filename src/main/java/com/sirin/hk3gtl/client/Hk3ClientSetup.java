package com.sirin.hk3gtl.client;


/**
 * 【文件职责】
 * - 负责 Hk3ClientSetup 客户端渲染或 UI 逻辑。
 * - 关键调用链：由上层系统入口调用 -> 本文件核心方法 -> 下游模块。
 *
 * 【变更记录】2026-05-19
 * - 删除：
 *   1) 初始归档备注：自 v0.3 基线梳理，无本次 diff。
 * - 新增：
 *   1) 新增统一变更备注块，便于后续维护与审计追踪。
 * - 修改：
 *   1) 未改动业务逻辑，仅补充文件级职责与维护注释模板。
 * - 用途：
 *   1) 帮助维护者快速理解文件职责、变更背景与风险点。
 *
 * 【段内说明】
 * - 复杂方法补充“干什么 / 边界 / 线程侧”精简中文注释。
 */
import com.sirin.hk3gtl.client.badending.Hk3BadEndingBlackoutOverlay;
import com.sirin.hk3gtl.client.entity.SirinWingLayer;
import com.sirin.hk3gtl.client.entity.ImaginaryRiftRenderer;
import com.sirin.hk3gtl.client.entity.VoidQueenSirinRenderer;
import com.sirin.hk3gtl.client.gaze.Hk3GazeHudOverlay;
import com.sirin.hk3gtl.common.block.StructureBlocks;
import com.sirin.hk3gtl.common.constants.Hk3Constants;
import com.sirin.hk3gtl.common.entity.Hk3Entities;
import net.minecraft.client.renderer.ItemBlockRenderTypes;
import net.minecraft.client.renderer.RenderType;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.client.event.EntityRenderersEvent;
import net.minecraftforge.client.event.ModelEvent;
import net.minecraftforge.client.event.RegisterGuiOverlaysEvent;
import net.minecraftforge.client.gui.overlay.VanillaGuiOverlay;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import net.minecraftforge.fml.event.lifecycle.FMLClientSetupEvent;

/**
 * 客户端初始化入口 —— 注册方块渲染类型、实体渲染器、额外模型。
 *
 * <h3>职责</h3>
 * <ul>
 *   <li>设置特殊方块的渲染类型（如半透明玻璃）</li>
 *   <li>注册自定义实体渲染器（西琳）</li>
 *   <li>注册翅膀 BakedModel 并在烘焙完成后缓存引用</li>
 * </ul>
 *
 * <h3>修改指南</h3>
 * <ul>
 *   <li>新增方块渲染类型：在 onClientSetup 的 enqueueWork 中调用 setRenderLayer</li>
 *   <li>新增实体渲染器：在 onRegisterRenderers 中调用 registerEntityRenderer</li>
 *   <li>新增额外模型：在 onRegisterAdditionalModels 中注册，在 onModifyBakingResult 中缓存</li>
 * </ul>
 */
@Mod.EventBusSubscriber(modid = Hk3Constants.MOD_ID, bus = Mod.EventBusSubscriber.Bus.MOD, value = Dist.CLIENT)
/** 【变更记录 #3】2026-10-01 19:03:37（修订141）：删除：无；新增／修改：注册琪亚娜细手臂渲染器；用途：琪亚娜二审形象和终审统一称谓，保留其他会话行为。 */
/** 【变更记录 #4】2026-10-01 19:18:39（修订143）：删除：无；新增／修改：额外模型注册与重载回调加入琪亚娜左右三层；用途：琪亚娜三层星海翅膀。 */
public class Hk3ClientSetup {

    /** 设置方块渲染类型（在主线程上执行，通过 enqueueWork 保证安全） */
    @SubscribeEvent
    public static void onClientSetup(FMLClientSetupEvent event) {
        event.enqueueWork(() -> {
            ItemBlockRenderTypes.setRenderLayer(
                    StructureBlocks.GLASS_HONKAI_STABILIZED.get(),
                    RenderType.translucent()
            );
        });
    }

    /** 注册实体渲染器。修改要点：新增实体时在此添加 registerEntityRenderer 调用 */
    @SubscribeEvent
    public static void onRegisterRenderers(EntityRenderersEvent.RegisterRenderers event) {
        event.registerEntityRenderer(Hk3Entities.KIANA_REVIEW.get(), com.sirin.hk3gtl.client.entity.Hk3KianaReviewRenderer::new);
        event.registerEntityRenderer(Hk3Entities.VOID_QUEEN_SIRIN.get(), VoidQueenSirinRenderer::new);
        event.registerEntityRenderer(Hk3Entities.IMAGINARY_RIFT.get(), ImaginaryRiftRenderer::new);
    }

    /** 注册翅膀的额外 BakedModel（item/generated 自动 3D 挤出） */
    @SubscribeEvent
    public static void onRegisterAdditionalModels(ModelEvent.RegisterAdditional event) {
        SirinWingLayer.WING_MODELS.forEach(event::register);
        com.sirin.hk3gtl.client.entity.Hk3KianaEquipmentLayer.WING_MODELS.forEach(event::register);
    }

    /** 烘焙完成后将 BakedModel 引用传递给翅膀渲染层 */
    @SubscribeEvent
    public static void onModifyBakingResult(ModelEvent.ModifyBakingResult event) {
        SirinWingLayer.onModelBake(event.getModels());
        com.sirin.hk3gtl.client.entity.Hk3KianaEquipmentLayer.onModelBake(event.getModels());
    }

    /** 注册终焉注视度 HUD overlay（置于原版热键提示层之上）。 */
    @SubscribeEvent
    public static void onRegisterOverlays(RegisterGuiOverlaysEvent event) {
        event.registerAbove(VanillaGuiOverlay.HOTBAR.id(), "hk3gtl_gaze", Hk3GazeHudOverlay.INSTANCE);
        // 【变更记录 #2】2026-09-29 18:57:18（内测5修订95）：右侧短通知，不占聊天框。
        event.registerAboveAll("hk3gtl_phone_toast", (gui, graphics, partial, width, height) ->
                com.sirin.hk3gtl.client.phone.Hk3PhoneScreen.renderToast(graphics));
        // 坏结局黑屏遮罩：置于所有 HUD 层之上，保证全屏覆盖
        event.registerAboveAll("hk3gtl_badending_blackout", Hk3BadEndingBlackoutOverlay.INSTANCE);
    }
}
