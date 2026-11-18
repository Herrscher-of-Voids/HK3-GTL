package com.sirin.hk3gtl.client.ae;

import appeng.client.gui.AESubScreen;
import appeng.client.gui.me.crafting.CraftAmountScreen;
import appeng.menu.me.crafting.CraftAmountMenu;
import com.sirin.hk3gtl.common.integration.ae.exact.Hk3ExactAmountMenu;
import com.sirin.hk3gtl.common.network.Hk3ProbabilityOrderStatusPacket;
import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.client.gui.components.Button;
import net.minecraft.client.gui.components.EditBox;
import net.minecraft.network.chat.Component;
import net.minecraft.util.FormattedCharSequence;
import org.lwjgl.glfw.GLFW;

import java.math.BigInteger;
import java.util.ArrayList;
import java.util.List;
import java.util.UUID;

public final class Hk3ProbabilityAmountScreen extends AESubScreen<CraftAmountMenu, CraftAmountScreen> {
    private EditBox amount;
    private EditBox attempts;
    private Button previousCandidate;
    private Button nextCandidate;
    private Button preview;
    private Button confirm;
    private Button previousOrder;
    private Button nextOrder;
    private final List<Button> actions = new ArrayList<>();
    private final List<Button> orderActions = new ArrayList<>();
    private String amountText = "1";
    private String attemptsText = "100";
    private String previewAmount = "";
    private String previewAttempts = "";
    private String status = "正在查找当前AE网络中可绑定的概率总成……";
    private List<FormattedCharSequence> statusLines = List.of();
    private UUID orderId;
    private int candidateCount;
    private int orderCount;
    private boolean previewReady;
    private boolean waiting;
    private boolean opened;
    private int cooldown;
    private int scroll;
    private int panelLeft;
    private int panelWidth;
    private int statusBottom;

    public Hk3ProbabilityAmountScreen(CraftAmountScreen parent, CraftAmountMenu menu) {
        super(parent, "/screens/craft_amount.json");
    }

    @Override
    protected void init() {
        clearWidgets();
        actions.clear();
        orderActions.clear();
        panelWidth = Math.max(240, Math.min(660, width - 24));
        panelLeft = (width - panelWidth) / 2;
        statusBottom = height - 30;
        int inputWidth = (panelWidth - 8) / 2;
        amount = numberBox("新增目标数量", panelLeft, inputWidth, 256, amountText);
        attempts = numberBox("最大尝试次数", panelLeft + inputWidth + 8, inputWidth, 256, attemptsText);
        amount.setResponder(value -> { amountText = value; changedInput(); });
        attempts.setResponder(value -> { attemptsText = value; changedInput(); });
        previousCandidate = button("上一绑定", 0, 0, () -> send("candidate_previous"));
        nextCandidate = button("下一绑定", 1, 0, () -> send("candidate_next"));
        button("重新查找", 2, 0, () -> send("scan"));
        button("返回 AE", 3, 0, this::onClose);
        preview = button("预览预算", 0, 1, () -> {
            previewAmount = amountText;
            previewAttempts = attemptsText;
            send("preview|" + amountText + "|" + attemptsText);
        });
        confirm = button("确认概率订单", 1, 1,
                () -> send("start|" + amountText + "|" + attemptsText));
        button("刷新状态", 2, 1, () -> send("status"));
        orderActions.add(button("取消订单", 3, 1, () -> send("cancel")));
        previousOrder = button("上一订单", 0, 2, () -> send("order_previous"));
        nextOrder = button("下一订单", 1, 2, () -> send("order_next"));
        orderActions.add(button("恢复订单", 2, 2, () -> send("resume")));
        orderActions.add(button("领取托管", 3, 2, () -> send("claim")));
        orderActions.add(button("清理终态记录", 0, 3, () -> send("forget")));
        button("下一附加产物", 1, 3, () -> send("goal_next"));
        button("设附加数量", 2, 3, () -> send("goal_set|" + amountText));
        button("移除附加目标", 3, 3, () -> send("goal_remove"));
        button("加入共享路线", 0, 4, () -> send("route_add"));
        button("移除当前路线", 1, 4, () -> send("route_remove"));
        wrapStatus();
        updateButtons();
        setInitialFocus(amount);
        if (!opened) {
            opened = true;
            send("open");
        }
    }

    private EditBox numberBox(String title, int x, int boxWidth, int maxLength, String value) {
        var box = new EditBox(font, x, 47, boxWidth, 20, Component.literal(title));
        box.setMaxLength(maxLength);
        box.setFilter(text -> text.chars().allMatch(c -> c >= '0' && c <= '9'));
        box.setValue(value);
        return addRenderableWidget(box);
    }

    private Button button(String title, int column, int row, Runnable action) {
        int cell = (panelWidth - 12) / 4;
        var button = addRenderableWidget(Button.builder(Component.literal(title), ignored -> action.run())
                .bounds(panelLeft + column * (cell + 4), 75 + row * 24, cell, 20).build());
        actions.add(button);
        return button;
    }

    private void changedInput() {
        previewReady = false;
        updateButtons();
    }

    private void send(String action) {
        if (waiting || cooldown > 0 || minecraft.player == null || minecraft.player.containerMenu != menu) return;
        waiting = true;
        cooldown = 10;
        ((Hk3ExactAmountMenu) menu).hk3gtl$exactAction("probability|" + action);
        updateButtons();
    }

    private void updateButtons() {
        boolean ready = !waiting && cooldown == 0;
        actions.forEach(button -> button.active = ready);
        previousCandidate.active = nextCandidate.active = ready && candidateCount > 1;
        previousOrder.active = nextOrder.active = ready && orderCount > 1;
        boolean valid = !amountText.isEmpty() && new BigInteger(amountText).signum() > 0
                && !attemptsText.isEmpty() && new BigInteger(attemptsText).signum() > 0;
        preview.active = ready && candidateCount > 0 && valid;
        confirm.active = ready && previewReady && valid;
        orderActions.forEach(button -> button.active = ready && orderId != null);
        amount.setEditable(!waiting);
        attempts.setEditable(!waiting);
    }

    public static void receiveStatus(Hk3ProbabilityOrderStatusPacket packet) {
        Minecraft client = Minecraft.getInstance();
        if (client.screen instanceof Hk3ProbabilityAmountScreen screen
                && screen.menu.containerId == packet.menuId() && client.player != null
                && client.player.containerMenu == screen.menu) {
            screen.orderId = packet.orderId();
            screen.candidateCount = packet.candidateCount();
            screen.orderCount = packet.orderCount();
            screen.previewReady = packet.previewReady() && screen.amountText.equals(screen.previewAmount)
                    && screen.attemptsText.equals(screen.previewAttempts);
            if (!screen.status.equals(packet.text())) {
                screen.status = packet.text();
                screen.wrapStatus();
            }
            screen.waiting = false;
            screen.updateButtons();
        }
    }

    private void wrapStatus() {
        statusLines = font.split(Component.literal(status), panelWidth - 8);
    }

    @Override
    public void containerTick() {
        amount.tick();
        attempts.tick();
        if (cooldown > 0 && --cooldown == 0) updateButtons();
    }

    @Override
    public void render(GuiGraphics graphics, int mouseX, int mouseY, float partialTick) {
        renderBackground(graphics);
        graphics.drawCenteredString(font, "HK3 概率订单", width / 2, 12, 0xFFFFFF);
        graphics.drawString(font, "新增目标数量（最多256位）", panelLeft, 32, 0xBFD8F0, false);
        graphics.drawString(font, "最大尝试次数（消耗上限）", panelLeft + (panelWidth - 8) / 2 + 8, 32, 0xBFD8F0, false);
        graphics.fill(panelLeft - 3, 197, panelLeft + panelWidth + 3, statusBottom, 0xCC101820);
        int visible = Math.max(1, (statusBottom - 203) / font.lineHeight);
        scroll = Math.max(0, Math.min(scroll, Math.max(0, statusLines.size() - visible)));
        for (int i = 0; i < visible && scroll + i < statusLines.size(); i++)
            graphics.drawString(font, statusLines.get(scroll + i), panelLeft + 4,
                    203 + i * font.lineHeight, 0xE6EEF7, false);
        graphics.drawString(font, waiting ? "等待服务端响应……" : "滚轮查看；返回保留已确认订单与原尝试预算。",
                panelLeft, height - 20, 0xA4B8CD, false);
        for (var renderable : renderables) renderable.render(graphics, mouseX, mouseY, partialTick);
    }

    @Override
    public boolean mouseScrolled(double mouseX, double mouseY, double delta) {
        if (mouseY >= 197 && mouseY < statusBottom) {
            scroll = Math.max(0, scroll - (int) Math.signum(delta) * 3);
            return true;
        }
        return super.mouseScrolled(mouseX, mouseY, delta);
    }

    @Override
    public boolean keyPressed(int key, int scan, int modifiers) {
        if (key == GLFW.GLFW_KEY_ESCAPE) { onClose(); return true; }
        if (amount.keyPressed(key, scan, modifiers) || attempts.keyPressed(key, scan, modifiers)) return true;
        if (minecraft.options.keyInventory.matches(key, scan)) return true;
        return super.keyPressed(key, scan, modifiers);
    }

    @Override
    public void onClose() {
        if (minecraft.player != null && minecraft.player.containerMenu == menu) {
            ((Hk3ExactAmountMenu) menu).hk3gtl$exactAction("probability|leave");
            returnToParent();
        } else minecraft.setScreen(null);
    }
}
