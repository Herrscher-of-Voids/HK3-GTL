package com.sirin.hk3gtl.client.preview;

import com.gregtechceu.gtceu.api.gui.GuiTextures;
import com.lowdragmc.lowdraglib.utils.Position;
import com.lowdragmc.lowdraglib.utils.Size;
import com.mojang.blaze3d.systems.RenderSystem;
import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.client.gui.screens.Screen;
import net.minecraft.network.chat.Component;
import net.minecraft.world.item.ItemStack;

import java.util.Optional;

/** 全屏借用当前JEI场景；返回时只恢复布局，不重建模型或显存。 */
public final class Hk3PreviewFullscreenScreen extends Screen {
    private final Screen parent;
    private final Hk3W01PreviewWidget preview;
    private final Runnable keepAlive;
    private final Position originalParent;
    private final Position originalPosition;
    private final Size originalSize;

    private Hk3PreviewFullscreenScreen(Screen parent, Hk3W01PreviewWidget preview, Runnable keepAlive) {
        super(Component.translatable("hk3gtl.preview.title"));
        this.parent = parent;
        this.preview = preview;
        this.keepAlive = keepAlive;
        originalParent = preview.getParentPosition();
        originalPosition = preview.getSelfPosition();
        originalSize = preview.getSize();
    }

    public static void open(Hk3W01PreviewWidget preview, Runnable keepAlive) {
        var minecraft = Minecraft.getInstance();
        if (minecraft.screen instanceof Hk3PreviewFullscreenScreen fullscreen) {
            fullscreen.onClose();
            return;
        }
        keepAlive.run();
        preview.fullscreenLease(true);
        minecraft.setScreen(new Hk3PreviewFullscreenScreen(minecraft.screen, preview, keepAlive));
    }

    @Override protected void init() {
        preview.setParentPosition(Position.ORIGIN);
        preview.setSelfPosition(8, 8);
        preview.resizePreview(width - 16, height - 16);
        keepAlive.run();
    }

    @Override public void render(GuiGraphics graphics, int mouseX, int mouseY, float partialTicks) {
        keepAlive.run();
        renderBackground(graphics);
        GuiTextures.BACKGROUND.draw(graphics, mouseX, mouseY, 8, 8, width - 16, height - 16);
        var container = preview.getGui().getModularUIGui();
        container.tooltipTexts = null;
        container.tooltipComponent = null;
        container.tooltipFont = null;
        container.tooltipStack = ItemStack.EMPTY;
        preview.drawInBackground(graphics, mouseX, mouseY, partialTicks);
        preview.drawInForeground(graphics, mouseX, mouseY, partialTicks);
        if (com.lowdragmc.lowdraglib.LDLib.isJeiLoaded())
            com.sirin.hk3gtl.client.compat.Hk3PreviewJeiPlugin.present(preview);
        RenderSystem.depthMask(true);
        RenderSystem.enableDepthTest();
        if (container.tooltipTexts != null && !container.tooltipTexts.isEmpty()) {
            graphics.renderTooltip(container.tooltipFont == null ? font : container.tooltipFont,
                    container.tooltipTexts, Optional.ofNullable(container.tooltipComponent), mouseX, mouseY);
        }
        graphics.flush();
        RenderSystem.depthMask(true);
        RenderSystem.enableDepthTest();
        RenderSystem.setShaderColor(1, 1, 1, 1);
    }

    @Override public void tick() {
        keepAlive.run();
        preview.updateScreen();
    }

    @Override public boolean mouseClicked(double x, double y, int button) {
        return preview.mouseClicked(x, y, button) || super.mouseClicked(x, y, button);
    }

    @Override public boolean mouseReleased(double x, double y, int button) {
        return preview.mouseReleased(x, y, button) || super.mouseReleased(x, y, button);
    }

    @Override public boolean mouseDragged(double x, double y, int button, double dx, double dy) {
        return preview.mouseDragged(x, y, button, dx, dy) || super.mouseDragged(x, y, button, dx, dy);
    }

    @Override public boolean mouseScrolled(double x, double y, double delta) {
        return preview.mouseWheelMove(x, y, delta) || super.mouseScrolled(x, y, delta);
    }

    @Override public void onClose() {
        minecraft.setScreen(parent);
    }

    @Override public void removed() {
        preview.mouseReleased(-1, -1, 0);
        preview.mouseReleased(-1, -1, 1);
        preview.resizePreview(originalSize.width, originalSize.height);
        preview.setSelfPosition(originalPosition);
        preview.setParentPosition(originalParent);
        preview.fullscreenLease(false);
        keepAlive.run();
    }

    @Override public boolean isPauseScreen() { return false; }
}
