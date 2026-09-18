package com.sirin.hk3gtl.client.badending;

import net.minecraft.client.gui.GuiGraphics;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.api.distmarker.OnlyIn;
import net.minecraftforge.client.gui.overlay.ForgeGui;
import net.minecraftforge.client.gui.overlay.IGuiOverlay;

/**
 * 坏结局全屏黑屏 Overlay —— 按 {@link Hk3BadEndingClientState#getAlpha()} 绘制渐进全黑遮罩。
 * 注册在所有 HUD 层之上（Hk3ClientSetup.registerAboveAll）。
 */
@OnlyIn(Dist.CLIENT)
public final class Hk3BadEndingBlackoutOverlay implements IGuiOverlay {

    public static final Hk3BadEndingBlackoutOverlay INSTANCE = new Hk3BadEndingBlackoutOverlay();

    private Hk3BadEndingBlackoutOverlay() {}

    @Override
    public void render(ForgeGui gui, GuiGraphics graphics, float partialTick, int screenWidth, int screenHeight) {
        if (!Hk3BadEndingClientState.isActive()) return;
        int alpha = (int) (Hk3BadEndingClientState.getAlpha() * 255.0F) & 0xFF;
        if (alpha <= 0) return;
        graphics.fill(0, 0, screenWidth, screenHeight, alpha << 24);
    }
}
