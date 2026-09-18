package com.sirin.hk3gtl.client;



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
        event.registerEntityRenderer(Hk3Entities.VOID_QUEEN_SIRIN.get(), VoidQueenSirinRenderer::new);
        event.registerEntityRenderer(Hk3Entities.IMAGINARY_RIFT.get(), ImaginaryRiftRenderer::new);
    }

    /** 注册翅膀的额外 BakedModel（item/generated 自动 3D 挤出） */
    @SubscribeEvent
    public static void onRegisterAdditionalModels(ModelEvent.RegisterAdditional event) {
        SirinWingLayer.WING_MODELS.forEach(event::register);
    }

    /** 烘焙完成后将 BakedModel 引用传递给翅膀渲染层 */
    @SubscribeEvent
    public static void onModifyBakingResult(ModelEvent.ModifyBakingResult event) {
        SirinWingLayer.onModelBake(event.getModels());
    }

    /** 注册终焉注视度 HUD overlay（置于原版热键提示层之上）。 */
    @SubscribeEvent
    public static void onRegisterOverlays(RegisterGuiOverlaysEvent event) {
        event.registerAbove(VanillaGuiOverlay.HOTBAR.id(), "hk3gtl_gaze", Hk3GazeHudOverlay.INSTANCE);
        // 坏结局黑屏遮罩：置于所有 HUD 层之上，保证全屏覆盖
        event.registerAboveAll("hk3gtl_badending_blackout", Hk3BadEndingBlackoutOverlay.INSTANCE);
    }
}
