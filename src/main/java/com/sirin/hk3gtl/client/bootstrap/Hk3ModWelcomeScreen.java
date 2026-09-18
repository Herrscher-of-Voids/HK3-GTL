package com.sirin.hk3gtl.client.bootstrap;

import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.client.gui.components.Button;
import net.minecraft.client.gui.screens.Screen;
import net.minecraft.client.resources.language.I18n;
import net.minecraft.network.chat.Component;
import net.minecraft.util.Mth;

import java.util.ArrayList;
import java.util.List;
import java.util.Locale;


public class Hk3ModWelcomeScreen extends Screen {

    private static final int PANEL_W = 420;
    private static final int PANEL_H = 280;

    private final String modVersion;
    private final List<String> statusLines;
    private final List<String> bodyLines = new ArrayList<>();
    private int scroll;
    private int contentHeight;
    private int viewportHeight;

    public Hk3ModWelcomeScreen(String modVersion, List<String> statusLines) {
        super(Component.translatable("hk3gtl.welcome.title"));
        this.modVersion = modVersion;
        this.statusLines = statusLines;
    }

    public static void open(String modVersion, List<String> statusLines) {
        net.minecraft.client.Minecraft mc = net.minecraft.client.Minecraft.getInstance();
        if (mc.player == null) {
            return;
        }
        mc.execute(() -> mc.setScreen(new Hk3ModWelcomeScreen(modVersion, statusLines)));
    }

    @Override
    protected void init() {
        int panelX = (width - PANEL_W) / 2;
        int panelY = (height - PANEL_H) / 2;
        addRenderableWidget(Button.builder(Component.translatable("gui.ok"), b -> onClose())
                .bounds(panelX + PANEL_W / 2 - 40, panelY + PANEL_H - 28, 80, 20)
                .build());
        buildBodyLines();
        viewportHeight = PANEL_H - 56;
        contentHeight = bodyLines.size() * (font.lineHeight + 2);
        scroll = 0;
    }

    @Override
    public void render(GuiGraphics gui, int mouseX, int mouseY, float partialTick) {
        renderBackground(gui);
        int x = (width - PANEL_W) / 2;
        int y = (height - PANEL_H) / 2;
        gui.fill(x, y, x + PANEL_W, y + PANEL_H, 0xE010141B);
        gui.fill(x, y, x + PANEL_W, y + 1, 0xFF54657A);
        gui.fill(x, y + PANEL_H - 1, x + PANEL_W, y + PANEL_H, 0xFF54657A);

        gui.drawCenteredString(font, title, width / 2, y + 8, 0xFF69E6FF);
        gui.drawCenteredString(font, Component.translatable("hk3gtl.welcome.subtitle", modVersion),
                width / 2, y + 22, 0xFF9AA7B8);

        int textX = x + 12;
        int textY = y + 38;
        int textW = PANEL_W - 24;
        int maxScroll = Math.max(0, contentHeight - viewportHeight);
        scroll = Mth.clamp(scroll, 0, maxScroll);

        gui.enableScissor(textX, textY, textX + textW, textY + viewportHeight);
        int lineY = textY - scroll;
        for (String line : bodyLines) {
            gui.drawString(font, Component.literal(font.plainSubstrByWidth(line, textW)), textX, lineY, 0xFFE7EEF7, false);
            lineY += font.lineHeight + 2;
        }
        gui.disableScissor();

        super.render(gui, mouseX, mouseY, partialTick);
    }

    @Override
    public boolean mouseScrolled(double mouseX, double mouseY, double delta) {
        scroll = Mth.clamp(scroll - (int) Math.signum(delta) * (font.lineHeight + 2), 0,
                Math.max(0, contentHeight - viewportHeight));
        return true;
    }

    @Override
    public boolean isPauseScreen() {
        return false;
    }

    private void buildBodyLines() {
        bodyLines.clear();
        bodyLines.add(I18n.get("hk3gtl.welcome.intro"));
        bodyLines.add("");

        bodyLines.add("§6" + I18n.get("hk3gtl.welcome.health_header"));
        for (String raw : statusLines) {
            if (raw.startsWith("version:")) {
                continue;
            }
            String[] parts = raw.split(":", 3);
            if (parts.length >= 2) {
                String key = "hk3gtl.welcome.status." + parts[0];
                String state = "ok".equals(parts[1])
                        ? I18n.get("hk3gtl.welcome.status_ok")
                        : I18n.get("hk3gtl.welcome.status_fail");
                String extra = parts.length >= 3 ? " (" + parts[2] + ")" : "";
                bodyLines.add("  " + I18n.get(key) + ": " + state + extra);
            }
        }
        bodyLines.add("");

        appendPlayerReleaseNotes();
    }

    /** 玩家向版本说明：hk3gtl.welcome.release.&lt;0_2_0&gt;.title / .1 / .2 … */
    private void appendPlayerReleaseNotes() {
        bodyLines.add("§6" + I18n.get("hk3gtl.welcome.whats_new_header"));
        String verSlug = modVersion.replace('.', '_');
        String titleKey = "hk3gtl.welcome.release." + verSlug + ".title";
        if (!I18n.exists(titleKey)) {
            bodyLines.add("  " + I18n.get("hk3gtl.welcome.release.unknown", modVersion));
            bodyLines.add("");
            bodyLines.add("§7" + I18n.get("hk3gtl.welcome.feedback_hint"));
            return;
        }
        bodyLines.add("§b" + I18n.get(titleKey));
        for (int i = 1; i <= 16; i++) {
            String lineKey = String.format(Locale.ROOT, "hk3gtl.welcome.release.%s.%d", verSlug, i);
            if (!I18n.exists(lineKey)) {
                break;
            }
            bodyLines.add("  • " + I18n.get(lineKey));
        }
        bodyLines.add("");
        bodyLines.add("§7" + I18n.get("hk3gtl.welcome.feedback_hint"));
    }
}
