package com.sirin.hk3gtl.client.ae;

import appeng.client.gui.AESubScreen;
import appeng.client.gui.me.crafting.CraftAmountScreen;
import appeng.menu.me.crafting.CraftAmountMenu;
import com.sirin.hk3gtl.common.integration.ae.exact.Hk3ExactAmountMenu;
import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.client.gui.components.Button;
import net.minecraft.client.gui.components.EditBox;
import net.minecraft.network.chat.Component;
import net.minecraft.util.FormattedCharSequence;
import org.lwjgl.glfw.GLFW;

import java.math.BigInteger;
import java.util.List;
import java.util.UUID;

/** 使用 AE 原生子界面保留数量菜单；返回和 ESC 均不关闭容器或取消订单。 */
public final class Hk3ExactAmountScreen extends AESubScreen<CraftAmountMenu, CraftAmountScreen> {
    private EditBox amount;
    private Button preview;
    private Button confirm;
    private Button refresh;
    private Button pause;
    private Button resume;
    private Button cancel;
    private Button cancelPreview;
    private UUID orderId;
    private String amountText = "1";
    private String status = "正在读取服务端订单状态……";
    private List<FormattedCharSequence> statusLines = List.of();
    private boolean waiting;
    private boolean planning;
    private boolean watching;
    private boolean initialStatusRequested;
    private int scroll;
    private int panelLeft;
    private int panelWidth;
    private int statusBottom;

    public Hk3ExactAmountScreen(CraftAmountScreen parent, CraftAmountMenu menu) {
        super(parent, "/screens/craft_amount.json");
        if (menu != parent.getMenu()) throw new IllegalArgumentException("订单子界面的菜单不匹配");
    }

    @Override
    protected void init() {
        clearWidgets();
        panelWidth = Math.max(240, Math.min(620, width - 24));
        panelLeft = (width - panelWidth) / 2;
        statusBottom = height - 30;
        wrapStatus();
        amount = new EditBox(font, panelLeft, 47, panelWidth, 20, Component.literal("订单数量"));
        amount.setMaxLength(256);
        amount.setFilter(value -> value.chars().allMatch(c -> c >= '0' && c <= '9'));
        amount.setValue(amountText);
        amount.setResponder(value -> {
            leave();
            amountText = value;
            orderId = null;
            updateButtons();
        });
        addRenderableWidget(amount);
        int cell = (panelWidth - 12) / 4;
        preview = actionButton("规划", 0, 0, cell, () -> send("preview:" + amount.getValue()));
        confirm = actionButton("确认订单", 1, 0, cell, () -> sendOrder("start"));
        refresh = actionButton("刷新状态", 2, 0, cell, () -> send("status"));
        pause = actionButton("暂停", 3, 0, cell, () -> sendOrder("pause"));
        resume = actionButton("继续", 0, 1, cell, () -> sendOrder("resume"));
        cancel = actionButton("取消订单", 1, 1, cell, () -> sendOrder("cancel"));
        cancelPreview = actionButton("取消规划", 2, 1, cell, () -> {
            planning = false;
            ((Hk3ExactAmountMenu) menu).hk3gtl$exactAction("cancel_preview");
            updateButtons();
        });
        actionButton("返回 AE", 3, 1, cell, this::onClose);
        updateButtons();
        setInitialFocus(amount);
        if (!initialStatusRequested) {
            initialStatusRequested = true;
            send("status");
        }
    }

    private Button actionButton(String label, int column, int row, int cell, Runnable action) {
        return addRenderableWidget(Button.builder(Component.literal(label), button -> action.run())
                .bounds(panelLeft + column * (cell + 4), 75 + row * 24, cell, 20).build());
    }

    private void sendOrder(String action) {
        if (orderId != null) send(action + ":" + orderId);
    }

    private void send(String action) {
        if (waiting || minecraft == null || minecraft.player == null || minecraft.player.containerMenu != menu) return;
        waiting = true;
        planning = action.startsWith("preview:");
        watching = true;
        ((Hk3ExactAmountMenu) menu).hk3gtl$exactAction(action);
        updateButtons();
    }

    private void updateButtons() {
        if (preview == null) return;
        boolean positive = !amountText.isEmpty() && new BigInteger(amountText).signum() > 0;
        preview.active = !waiting && positive;
        refresh.active = !waiting;
        confirm.active = pause.active = resume.active = cancel.active = !waiting && orderId != null;
        cancelPreview.active = planning;
        amount.setEditable(!waiting);
    }

    private void wrapStatus() {
        statusLines = font.split(Component.literal(status), panelWidth - 8);
    }

    public static void receiveStatus(int menuId, UUID orderId, String text) {
        Minecraft client = Minecraft.getInstance();
        if (client.screen instanceof Hk3ExactAmountScreen screen && screen.menu.containerId == menuId
                && client.player != null && client.player.containerMenu == screen.menu) {
            screen.orderId = orderId;
            if (!screen.status.equals(text)) {
                screen.status = text;
                screen.wrapStatus();
            }
            screen.waiting = false;
            screen.planning = false;
            screen.updateButtons();
        }
    }

    @Override
    public void containerTick() {
        amount.tick();
    }

    @Override
    public void render(GuiGraphics graphics, int mouseX, int mouseY, float partialTick) {
        renderBackground(graphics);
        graphics.drawCenteredString(font, "HK3 大数订单", width / 2, 12, 0xFFFFFF);
        graphics.drawString(font, "数量：最多 256 位十进制整数；先规划，再确认。", panelLeft, 32, 0xBFD8F0, false);
        graphics.fill(panelLeft - 3, 126, panelLeft + panelWidth + 3, statusBottom, 0xCC101820);
        int visible = Math.max(1, (statusBottom - 132) / font.lineHeight);
        scroll = Math.max(0, Math.min(scroll, Math.max(0, statusLines.size() - visible)));
        for (int i = 0; i < visible && scroll + i < statusLines.size(); i++) {
            graphics.drawString(font, statusLines.get(scroll + i), panelLeft + 4, 132 + i * font.lineHeight, 0xE6EEF7, false);
        }
        graphics.drawString(font, waiting ? "等待服务端响应……" : "滚轮查看状态；返回不会取消订单。",
                panelLeft, height - 20, 0xA4B8CD, false);
        for (var renderable : renderables) renderable.render(graphics, mouseX, mouseY, partialTick);
    }

    @Override
    public boolean mouseScrolled(double mouseX, double mouseY, double delta) {
        if (mouseY >= 126 && mouseY < statusBottom) {
            scroll = Math.max(0, scroll - (int) Math.signum(delta) * 3);
            return true;
        }
        return super.mouseScrolled(mouseX, mouseY, delta);
    }

    @Override
    public boolean keyPressed(int key, int scan, int modifiers) {
        if (key == GLFW.GLFW_KEY_ESCAPE) {
            onClose();
            return true;
        }
        if (amount.keyPressed(key, scan, modifiers)) return true;
        if (minecraft != null && minecraft.options.keyInventory.matches(key, scan)) return true;
        return super.keyPressed(key, scan, modifiers);
    }

    @Override
    public void onClose() {
        leave();
        if (minecraft != null && minecraft.player != null && minecraft.player.containerMenu == menu) returnToParent();
        else if (minecraft != null) minecraft.setScreen(null);
    }

    private void leave() {
        if (watching && minecraft != null && minecraft.player != null && minecraft.player.containerMenu == menu)
            ((Hk3ExactAmountMenu) menu).hk3gtl$exactAction("leave");
        watching = false;
    }
}
