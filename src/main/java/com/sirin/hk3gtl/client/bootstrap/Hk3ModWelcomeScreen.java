package com.sirin.hk3gtl.client.bootstrap;

/**
 * 【变更记录 #3】2026-09-29 17:51:46（内测5修订93）
 * - 删除：旧正文活动引用被审核原文替代；保留历史资源和存档。
 * - 新增／修改：更新窗口接入审核正文与反馈QQ，完整换行；确认后记录已读，稍后阅读不记录。未实现系统的宣传不放进当前更新窗口。
 * - 用途：接通审核正文；其他系统触发及归属不据此宣称完成。
 */
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.client.gui.components.Button;
import net.minecraft.client.gui.screens.Screen;
import net.minecraft.client.resources.language.I18n;
import net.minecraft.network.chat.Component;

import java.util.ArrayList;
import java.util.List;

/**
 * 【文件职责】
 * - 内测进世界欢迎弹窗：注册自检 + 面向玩家的版本亮点（语言键，非内部 changelog.json）。
 *
 * 【变更记录 #1】2026-05-19（内测二首轮）
 *
 * 【变更记录 #2】2026-05-19 05:30:00（第 2 次备注 · 内测二第 7 次更新）
 * - 删除：直接解析 changelog.json 展示给玩家（含 revision/reason/技术条目）。
 * - 新增：按当前版本读取 hk3gtl.welcome.release.&lt;ver&gt;.* 玩家向说明。
 * - 用途：changelog.json 仅作开发审计，欢迎界面只展示「本版本新增什么」。
 */
/** 中文说明：该处说明已按当前代码行为整理。*/
/** 【变更记录 #4】2026-10-01 16:12:34（修订133）：删除逐行滚动及未调用的旧版本说明入口；新增分类整页阅读、独立历史说明、复制反馈信息、返回来源屏幕；修改登录展示交由队列、确认携带实际正文版本；用途：准确展示发布边界，加载检查不代表可通关。 */
/** 【变更记录 #5】2026-10-31 15:36:22（第5次备注 · 修订188）：删除健康警告的模糊子串匹配；新增带连接身份的网络包入口、返回来源读取及确认/关闭连接校验；修改连续手动重读保留手机父屏，只有六类注册检查的准确失败值触发警告；用途：防止旧会话页面影响新连接，并准确反映健康检查范围。 */
public class Hk3ModWelcomeScreen extends com.sirin.hk3gtl.client.gui.Hk3FittedScreen {
    private static final int PANEL_W = 420, PANEL_H = 310;
    private static final String[] TABS = {"current", "compatibility", "health", "history", "feedback"};
    private final String modVersion, contentId;
    private final List<String> statusLines;
    private final Screen parent;
    private final net.minecraft.client.multiplayer.ClientPacketListener connection;
    private final List<String> bodyLines = new ArrayList<>();
    private final List<net.minecraft.util.FormattedCharSequence> wrappedLines = new ArrayList<>();
    private int tab, page, history, perPage;

    public Hk3ModWelcomeScreen(String version, List<String> status, Screen parent) {
        super(Component.translatable("hk3gtl.welcome.title"), 444, 334);
        this.modVersion = version;
        this.statusLines = List.copyOf(status);
        this.parent = parent;
        this.connection = net.minecraft.client.Minecraft.getInstance().getConnection();
        this.contentId = status.stream().filter(s -> s.startsWith("content:")).map(s -> s.substring(8)).findFirst().orElse("");
    }

    public static void open(String version, List<String> status) { Hk3WelcomeClient.offer(version, status); }
    public static void open(String version, List<String> status, Object connection) { Hk3WelcomeClient.offer(version, status, connection); }
    Screen returnScreen() { return parent; }

    @Override protected void initFitted() {
        clearWidgets();
        int x = (width - PANEL_W) / 2, y = (height - PANEL_H) / 2;
        for (int i = 0; i < TABS.length; i++) {
            final int selected = i;
            var button = addRenderableWidget(Button.builder(Component.translatable("hk3gtl.welcome.tab." + TABS[i]), b -> {
                tab = selected; page = 0; initFitted();
            }).bounds(x + 12 + i * 80, y + 39, 76, 20).build());
            button.active = tab != i;
        }
        buildBodyLines();
        wrappedLines.clear();
        for (String line : bodyLines) {
            if (line.isEmpty()) wrappedLines.add(net.minecraft.util.FormattedCharSequence.EMPTY);
            else wrappedLines.addAll(font.split(Component.literal(line), PANEL_W - 24));
        }
        perPage = Math.max(1, 170 / (font.lineHeight + 2));
        page = Math.max(0, Math.min(page, pages() - 1));
        addRenderableWidget(Button.builder(Component.translatable("hk3gtl.welcome.previous"), b -> turn(-1))
                .bounds(x + 190, y + 244, 100, 20).build()).active = page > 0;
        addRenderableWidget(Button.builder(Component.translatable("hk3gtl.welcome.next"), b -> turn(1))
                .bounds(x + 302, y + 244, 106, 20).build()).active = page + 1 < pages();
        if (tab == 3) {
            addRenderableWidget(Button.builder(Component.translatable("hk3gtl.welcome.history_switch", historyVersion()), b -> {
                history = (history + 1) % com.sirin.hk3gtl.common.bootstrap.Hk3WelcomeState.HISTORY.size();
                page = 0; initFitted();
            }).bounds(x + 12, y + 244, 162, 20).build());
        } else if (tab == 4) {
            addRenderableWidget(Button.builder(Component.translatable("hk3gtl.welcome.copy_feedback"), b -> {
                if (minecraft != null) minecraft.keyboardHandler.setClipboard(I18n.get("hk3gtl.welcome.feedback_template", modVersion));
                b.setMessage(Component.translatable("hk3gtl.welcome.copied"));
            }).bounds(x + 12, y + 244, 162, 20).build());
        }
        addRenderableWidget(Button.builder(Component.translatable(parent == null ? "hk3gtl.prose.update_ack" : "hk3gtl.welcome.ack_return"), b -> {
            if (minecraft != null && connection != null && minecraft.getConnection() == connection && !contentId.isEmpty()) {
                minecraft.getConnection().sendCommand("hk3updates acknowledge " + contentId);
                onClose();
            }
        }).bounds(x + 12, y + 278, 194, 20).build()).active = tab != 3 && !contentId.isEmpty();
        addRenderableWidget(Button.builder(Component.translatable(parent == null ? "hk3gtl.prose.update_later" : "hk3gtl.welcome.return"), b -> onClose())
                .bounds(x + 214, y + 278, 194, 20).build());
    }

    private int pages() { return com.sirin.hk3gtl.common.phone.Hk3PhoneLayout.pages(wrappedLines.size(), perPage); }
    private void turn(int delta) { page = Math.max(0, Math.min(page + delta, pages() - 1)); initFitted(); }
    private String historyVersion() { return com.sirin.hk3gtl.common.bootstrap.Hk3WelcomeState.HISTORY.get(history); }

    @Override public void renderFitted(GuiGraphics gui, int mouseX, int mouseY, float partialTick) {
        renderBackground(gui);
        int x = (width - PANEL_W) / 2, y = (height - PANEL_H) / 2;
        gui.fill(x, y, x + PANEL_W, y + PANEL_H, 0xF010141B);
        gui.fill(x, y, x + PANEL_W, y + 1, 0xFF54657A);
        gui.fill(x, y + PANEL_H - 1, x + PANEL_W, y + PANEL_H, 0xFF54657A);
        gui.drawCenteredString(font, title, width / 2, y + 8, 0xFF69E6FF);
        gui.drawCenteredString(font, Component.translatable("hk3gtl.welcome.subtitle", modVersion), width / 2, y + 22, 0xFF9AA7B8);
        fittedScissor(gui, x + 12, y + 66, x + PANEL_W - 12, y + 236);
        int from = page * perPage, to = Math.min(wrappedLines.size(), from + perPage);
        for (int i = from; i < to; i++) gui.drawString(font, wrappedLines.get(i), x + 12, y + 66 + (i - from) * (font.lineHeight + 2), 0xFFE7EEF7, false);
        gui.disableScissor();
        gui.drawCenteredString(font, Component.translatable("hk3gtl.phone.pages", page + 1, pages()), width / 2, y + 267, 0xFF9AA7B8);
        if (hasFailure()) gui.drawString(font, Component.translatable("hk3gtl.welcome.health_warning"), x + 12, y + 232, 0xFFFF8B8B, false);
        super.renderFitted(gui, mouseX, mouseY, partialTick);
    }

    private boolean hasFailure() { return statusLines.stream().anyMatch(s -> s.matches("(?:items|blocks|fluids|industrial_machines|recipe_types|gtceu):fail(?::.*)?")); }
    @Override public boolean scrollFitted(double x, double y, double delta) { return false; }
    @Override public boolean keyPressed(int key, int scan, int modifiers) {
        if (key == 266 || key == 267) { turn(key == 266 ? -1 : 1); return true; }
        return super.keyPressed(key, scan, modifiers);
    }
    @Override public void onClose() { if (minecraft != null && minecraft.getConnection() == connection) minecraft.setScreen(parent); }
    @Override public boolean isPauseScreen() { return false; }

    private void buildBodyLines() {
        bodyLines.clear();
        switch (tab) {
            case 0 -> {
                add("§6" + I18n.get("hk3gtl.welcome.release.0_5_0.title"));
                for (int i = 1; i <= 6; i++) add(I18n.get("hk3gtl.welcome.release.0_5_0." + i));
                appendApproved(statusLines.contains("welcome:first") ? "U02" : "U03");
                com.sirin.hk3gtl.common.bootstrap.Hk3WelcomeState.CURRENT_PROSE.forEach(this::appendApproved);
            }
            case 1 -> {
                add(I18n.get("hk3gtl.welcome.current_limits"));
                com.sirin.hk3gtl.common.bootstrap.Hk3WelcomeState.COMPATIBILITY_PROSE.forEach(this::appendApproved);
            }
            case 2 -> {
                add(I18n.get("hk3gtl.welcome.health_scope"));
                for (String raw : statusLines) {
                    String[] parts = raw.split(":", 3);
                    if (parts.length < 2 || !(parts[1].equals("ok") || parts[1].equals("fail"))) continue;
                    String key = "hk3gtl.welcome.status." + parts[0];
                    String label = I18n.exists(key) ? I18n.get(key) : parts[0];
                    String state = I18n.get(parts[1].equals("ok") ? "hk3gtl.welcome.status_ok" : "hk3gtl.welcome.status_fail");
                    add(label + ": " + state + (parts.length == 3 ? " (" + parts[2] + ")" : ""));
                }
            }
            case 3 -> {
                appendApproved("U37");
                String base = "hk3gtl.welcome.release." + historyVersion().replace('.', '_');
                add("§6" + I18n.get(base + ".title"));
                for (int i = 1; i <= 16 && I18n.exists(base + "." + i); i++) add(I18n.get(base + "." + i));
            }
            case 4 -> {
                appendApproved("U29");
                add(I18n.get("hk3gtl.welcome.feedback_local"));
                add(I18n.get("hk3gtl.welcome.reopen"));
            }
            default -> throw new IllegalStateException("更新详情分类无效");
        }
    }
    private void add(String line) { bodyLines.add(line); bodyLines.add(""); }
    private void appendApproved(String id) {
        var entry = com.sirin.hk3gtl.common.narrative.Hk3ApprovedProse.get("update." + id);
        bodyLines.add("§6" + I18n.get(entry.key() + ".title"));
        for (int i = 0; i < entry.lineCount(); i++) bodyLines.add(I18n.get(entry.key() + ".line." + i));
        bodyLines.add("");
    }
}
