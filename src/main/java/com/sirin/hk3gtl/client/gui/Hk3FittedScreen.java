package com.sirin.hk3gtl.client.gui;

import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.client.gui.screens.Screen;
import net.minecraft.network.chat.Component;

/** 中文说明：该处说明已按当前代码行为整理。*/
public abstract class Hk3FittedScreen extends Screen {
    private final int minimumWidth, minimumHeight;
    private double scale = 1;

    protected Hk3FittedScreen(Component title, int minimumWidth, int minimumHeight) {
        super(title);
        this.minimumWidth = minimumWidth;
        this.minimumHeight = minimumHeight;
    }

    /** 中文说明：该处说明已按当前代码行为整理。*/
    @Override protected final void init() {
        int realWidth = Math.max(1, minecraft.getWindow().getGuiScaledWidth());
        int realHeight = Math.max(1, minecraft.getWindow().getGuiScaledHeight());
        scale = Math.min(1, Math.min((double) realWidth / minimumWidth, (double) realHeight / minimumHeight));
        width = (int) Math.floor(realWidth / scale);
        height = (int) Math.floor(realHeight / scale);
        initFitted();
    }
    protected void initFitted() { super.init(); }

    /** 中文说明：该处说明已按当前代码行为整理。*/
    @Override public final void render(GuiGraphics graphics, int x, int y, float partial) {
        graphics.pose().pushPose();
        try {
            graphics.pose().scale((float) scale, (float) scale, 1);
            renderFitted(graphics, (int) Math.floor(x / scale), (int) Math.floor(y / scale), partial);
        } finally { graphics.pose().popPose(); }
    }
    protected void renderFitted(GuiGraphics graphics, int x, int y, float partial) { super.render(graphics, x, y, partial); }

    /** 中文说明：该处说明已按当前代码行为整理。*/
    protected final void fittedScissor(GuiGraphics graphics, int left, int top, int right, int bottom) {
        graphics.enableScissor((int) Math.floor(left * scale), (int) Math.floor(top * scale),
                (int) Math.ceil(right * scale), (int) Math.ceil(bottom * scale));
    }

    // 所有鼠标坐标及拖动距离只转换一次；滚轮步数和键盘输入不缩放。
    // 中文备注：该处说明已按当前代码行为整理。
    @Override public final boolean mouseClicked(double x, double y, int button) { return clickFitted(x / scale, y / scale, button); }
    protected boolean clickFitted(double x, double y, int button) { return super.mouseClicked(x, y, button); }
    @Override public final boolean mouseReleased(double x, double y, int button) { return releaseFitted(x / scale, y / scale, button); }
    protected boolean releaseFitted(double x, double y, int button) { return super.mouseReleased(x, y, button); }
    @Override public final boolean mouseDragged(double x, double y, int button, double dx, double dy) { return dragFitted(x / scale, y / scale, button, dx / scale, dy / scale); }
    protected boolean dragFitted(double x, double y, int button, double dx, double dy) { return super.mouseDragged(x, y, button, dx, dy); }
    @Override public final boolean mouseScrolled(double x, double y, double delta) { return scrollFitted(x / scale, y / scale, delta); }
    protected boolean scrollFitted(double x, double y, double delta) { return super.mouseScrolled(x, y, delta); }
    @Override public final void mouseMoved(double x, double y) { super.mouseMoved(x / scale, y / scale); }
}
