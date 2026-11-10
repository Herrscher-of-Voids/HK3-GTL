package com.sirin.hk3gtl.client.badending;

import com.mojang.math.Axis;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.api.distmarker.OnlyIn;
import net.minecraftforge.client.gui.overlay.ForgeGui;
import net.minecraftforge.client.gui.overlay.IGuiOverlay;

/** Full-screen bad-ending transition, drawn with bounded HUD geometry. */
@OnlyIn(Dist.CLIENT)
public final class Hk3BadEndingBlackoutOverlay implements IGuiOverlay {

    public static final Hk3BadEndingBlackoutOverlay INSTANCE = new Hk3BadEndingBlackoutOverlay();
    private static final int RAY_COUNT = 12;

    private Hk3BadEndingBlackoutOverlay() {}

    @Override
    public void render(ForgeGui gui, GuiGraphics graphics, float partialTick, int screenWidth, int screenHeight) {
        if (!Hk3BadEndingClientState.isActive()) return;
        float progress = Hk3BadEndingClientState.getProgress(partialTick);
        int darkness = (int) (Hk3BadEndingClientState.getAlpha(partialTick) * 255.0F);
        graphics.fill(0, 0, screenWidth, screenHeight, darkness << 24);
        if (progress >= 0.85F) return;

        int cx = screenWidth / 2;
        int cy = screenHeight / 2;
        int span = Math.max(16, Math.min(screenWidth, screenHeight));
        float collapse = Math.min(1.0F, progress / 0.72F);
        int radius = Math.max(8, (int) (span * (0.48F - collapse * 0.34F)));
        int violet = argb((int) (150 * (1.0F - collapse * 0.4F)), 161, 108, 235);
        int gold = argb((int) (170 * collapse), 255, 221, 151);

        // Contracting frames and radial tears imply a collapsing space without particles or textures.
        for (int ring = 0; ring < 3; ring++) {
            int r = radius + ring * Math.max(5, span / 24);
            int color = ring == 0 ? gold : violet;
            frame(graphics, cx - r, cy - r, cx + r, cy + r, Math.max(1, span / 220), color);
        }
        graphics.pose().pushPose();
        graphics.pose().translate(cx, cy, 0);
        for (int ray = 0; ray < RAY_COUNT; ray++) {
            graphics.pose().pushPose();
            graphics.pose().mulPose(Axis.ZP.rotationDegrees(ray * (360.0F / RAY_COUNT) + progress * 32.0F));
            int inner = Math.max(3, radius / 3);
            int outer = radius + (int) (span * (0.14F + collapse * 0.12F));
            graphics.fill(-1, inner, 2, outer, ray % 3 == 0 ? gold : violet);
            graphics.pose().popPose();
        }
        graphics.pose().popPose();

        if (progress > 0.68F) {
            float impact = Math.max(0.0F, 1.0F - Math.abs(progress - 0.76F) / 0.09F);
            graphics.fill(0, 0, screenWidth, screenHeight, argb((int) (impact * 190), 255, 238, 202));
        }
    }

    private static void frame(GuiGraphics graphics, int left, int top, int right, int bottom,
                              int thickness, int color) {
        graphics.fill(left, top, right, top + thickness, color);
        graphics.fill(left, bottom - thickness, right, bottom, color);
        graphics.fill(left, top, left + thickness, bottom, color);
        graphics.fill(right - thickness, top, right, bottom, color);
    }

    private static int argb(int alpha, int red, int green, int blue) {
        return (Math.min(255, Math.max(0, alpha)) << 24) | (red << 16) | (green << 8) | blue;
    }
}
