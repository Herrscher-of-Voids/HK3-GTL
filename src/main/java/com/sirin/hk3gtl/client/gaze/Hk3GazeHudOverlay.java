package com.sirin.hk3gtl.client.gaze;

import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.network.chat.Component;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.api.distmarker.OnlyIn;
import net.minecraftforge.client.gui.overlay.IGuiOverlay;

/**
 * 终焉注视度 HUD：屏幕左上角常驻，显示注视度数值、进度条与高注视变色预警。
 *
 * <h3>展示规则</h3>
 * <ul>
 *   <li>未同步（未进世界/未收到包）或注视度为 0 时不渲染，避免打扰前期玩家。</li>
 *   <li>进度条颜色按占比分级：低=青、中=黄、高=橙、临界=红闪，呼应“越强越被审视”的压迫感。</li>
 *   <li>缓冲单元激活时追加缓冲提示行。</li>
 * </ul>
 *
 * <p>纯读取 {@link Hk3ClientGazeState} 客户端缓存，不做任何计算，渲染线程安全。</p>
 */
@OnlyIn(Dist.CLIENT)
public final class Hk3GazeHudOverlay implements IGuiOverlay {

    public static final Hk3GazeHudOverlay INSTANCE = new Hk3GazeHudOverlay();

    private static final int X = 8;
    private static final int Y = 8;
    private static final int BAR_WIDTH = 80;
    private static final int BAR_HEIGHT = 6;

    private Hk3GazeHudOverlay() {}

    @Override
    public void render(net.minecraftforge.client.gui.overlay.ForgeGui gui, GuiGraphics graphics,
                       float partialTick, int screenWidth, int screenHeight) {
        Minecraft mc = Minecraft.getInstance();
        // 隐藏条件：调试屏开启、未同步、注视度为 0（前期无需干扰）。
        if (mc.options.renderDebug || !Hk3ClientGazeState.isSynced() || Hk3ClientGazeState.getGaze() <= 0) {
            return;
        }

        int gaze = Hk3ClientGazeState.getGaze();
        int max = Hk3ClientGazeState.getGazeMax();
        float ratio = Hk3ClientGazeState.getRatio();
        int barColor = colorForRatio(ratio);

        // 标题 + 数值
        Component label = Component.translatable("hk3gtl.hud.gaze.label", gaze, max);
        graphics.drawString(mc.font, label, X, Y, colorForRatio(ratio), true);

        // 进度条背景
        int barY = Y + 11;
        graphics.fill(X, barY, X + BAR_WIDTH, barY + BAR_HEIGHT, 0xAA000000);
        // 进度条填充
        int filled = Math.max(0, Math.min(BAR_WIDTH, Math.round(BAR_WIDTH * ratio)));
        graphics.fill(X, barY, X + filled, barY + BAR_HEIGHT, barColor);
        // 边框
        graphics.renderOutline(X, barY, BAR_WIDTH, BAR_HEIGHT, 0xFF2A2A2A);

        // 缓冲提示
        if (Hk3ClientGazeState.isBufferActive()) {
            graphics.drawString(mc.font, Component.translatable("hk3gtl.hud.gaze.buffer"),
                    X, barY + BAR_HEIGHT + 2, 0xFF55FFFF, true);
        }
    }

    /**
     * 注视度占比 → 进度条颜色（含 alpha）：
     * <0.3 青 / <0.6 黄 / <0.85 橙 / >=0.85 红闪（随游戏刻闪烁，强化临界预警）。
     */
    private static int colorForRatio(float ratio) {
        if (ratio < 0.3F) return 0xFF33CCFF;
        if (ratio < 0.6F) return 0xFFFFDD33;
        if (ratio < 0.85F) return 0xFFFF8800;
        // 临界：基于系统时间做简单闪烁，无需持久状态
        boolean blinkOn = (System.currentTimeMillis() / 400L) % 2L == 0L;
        return blinkOn ? 0xFFFF3333 : 0xFFAA0000;
    }
}
