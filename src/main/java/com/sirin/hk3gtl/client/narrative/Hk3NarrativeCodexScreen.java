package com.sirin.hk3gtl.client.narrative;



import com.sirin.hk3gtl.common.narrative.Hk3NarrativeFaction;
import com.sirin.hk3gtl.common.narrative.Hk3NarrativeLog;
import com.sirin.hk3gtl.common.narrative.Hk3NarrativeNode;
import com.sirin.hk3gtl.common.narrative.Hk3NarrativeNodes;
import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.client.gui.screens.Screen;
import net.minecraft.client.resources.language.I18n;
import net.minecraft.network.chat.Component;
import net.minecraft.util.Mth;
import net.minecraft.world.entity.player.Player;

import java.util.ArrayList;
import java.util.Collection;
import java.util.List;

/**
 * 《文明档案卷轴》阅读界面：
 * 左侧阵营筛选，中间节点列表，右侧详情，底部进度条。
 *
 * <p>2026-05-19 变更：
 * 新增彩蛋条件展示与可视化滚动条，便于 100 条彩蛋档案快速浏览。</p>
 */
public class Hk3NarrativeCodexScreen extends Screen {

    private static final int GUI_WIDTH = 420;
    private static final int GUI_HEIGHT = 320;
    private static final int LEFT_WIDTH = 90;
    private static final int MID_WIDTH = 120;
    private static final int BOTTOM_HEIGHT = 20;
    private static final int PADDING = 6;
    private static final int ROW_HEIGHT = 18;
    private static final int DETAIL_LINE_HEIGHT = 11;
    private static final int BG_ROOT = 0xB0000000;
    private static final int BG_PANEL = 0xF0141A22;
    private static final int BG_LIST = 0xD01B2430;
    private static final int BG_ENTRY = 0x8018212B;
    private static final int BG_ENTRY_SELECTED = 0xC0263342;
    private static final int BORDER = 0xFF54657A;
    private static final int TEXT_NORMAL = 0xFFE7EEF7;
    private static final int TEXT_LOCKED = 0xFF7E8794;
    private static final int TEXT_DIM = 0xFF9AA7B8;
    private static final int TEXT_TITLE = 0xFF69E6FF;
    private static final int SCROLL_TRACK = 0x7A1A2431;
    private static final int SCROLL_THUMB = 0xC05A6E86;
    private static final String LOCKED_PLACEHOLDER = "???";

    private static final FactionFilter ALL_FACTION = new FactionFilter(null, "全部");

    private int guiLeft;
    private int guiTop;
    private int guiWidth;
    private int guiHeight;
    private int contentTop;
    private int contentHeight;
    private int detailWidth;

    private final List<FactionFilter> factionFilters = new ArrayList<>();
    private final List<Hk3NarrativeNode> filteredNodes = new ArrayList<>();

    private Hk3NarrativeFaction selectedFaction;
    private Hk3NarrativeNode selectedNode;
    private int factionScroll;
    private int nodeScroll;
    private int detailScroll;
    private ScrollTarget draggingScroll = ScrollTarget.NONE;
    private int dragScrollAnchor;
    private double dragMouseAnchor;

    public Hk3NarrativeCodexScreen() {
        super(Component.literal("文明档案卷轴"));
        buildFactionFilters();
        applyFactionFilter(null);
    }

    public static void open(Player player) {
        Minecraft mc = Minecraft.getInstance();
        if (player == null) return;
        mc.execute(() -> mc.setScreen(new Hk3NarrativeCodexScreen()));
    }

    @Override
    protected void init() {
        guiWidth = Math.min(GUI_WIDTH, Math.max(240, width - 12));
        guiHeight = Math.min(GUI_HEIGHT, Math.max(160, height - 12));
        guiLeft = (width - guiWidth) / 2;
        guiTop = (height - guiHeight) / 2;
        contentTop = guiTop + PADDING;
        contentHeight = guiHeight - BOTTOM_HEIGHT - PADDING * 2;
        detailWidth = guiWidth - LEFT_WIDTH - MID_WIDTH - PADDING * 4;
        clearWidgets();
    }

    @Override
    public void render(GuiGraphics gui, int mouseX, int mouseY, float partialTick) {
        renderBackground(gui);
        gui.fill(0, 0, width, height, BG_ROOT);

        drawPanel(gui, guiLeft, guiTop, guiWidth, guiHeight, BG_PANEL, BORDER);
        drawFactionPanel(gui, mouseX, mouseY);
        drawNodePanel(gui, mouseX, mouseY);
        drawDetailPanel(gui);
        drawBottomProgress(gui);

        super.render(gui, mouseX, mouseY, partialTick);
    }

    @Override
    public boolean mouseClicked(double mouseX, double mouseY, int button) {
        if (button == 0) {
            ScrollTarget target = scrollTargetAt(mouseX, mouseY);
            if (target != ScrollTarget.NONE) {
                beginScrollDrag(target, mouseX, mouseY);
                return true;
            }
            if (isInsideFactionPanel(mouseX, mouseY)) {
                int index = factionIndexAt(mouseY);
                if (index >= 0 && index < factionFilters.size()) {
                    applyFactionFilter(factionFilters.get(index).faction());
                    return true;
                }
            }
            if (isInsideNodePanel(mouseX, mouseY)) {
                int index = nodeIndexAt(mouseY);
                if (index >= 0 && index < filteredNodes.size()) {
                    selectedNode = filteredNodes.get(index);
                    detailScroll = 0;
                    return true;
                }
            }
        }
        return super.mouseClicked(mouseX, mouseY, button);
    }

    @Override
    public boolean mouseReleased(double mouseX, double mouseY, int button) {
        if (button == 0 && draggingScroll != ScrollTarget.NONE) {
            draggingScroll = ScrollTarget.NONE;
            return true;
        }
        return super.mouseReleased(mouseX, mouseY, button);
    }

    @Override
    public boolean mouseDragged(double mouseX, double mouseY, int button, double dragX, double dragY) {
        if (button == 0 && draggingScroll != ScrollTarget.NONE) {
            applyScrollDrag(mouseY);
            return true;
        }
        return super.mouseDragged(mouseX, mouseY, button, dragX, dragY);
    }

    @Override
    public boolean mouseScrolled(double mouseX, double mouseY, double delta) {
        if (isInsideFactionPanel(mouseX, mouseY)) {
            int maxOffset = Math.max(0, factionFilters.size() - visibleFactionCount());
            factionScroll = Mth.clamp(factionScroll - (int) Math.signum(delta), 0, maxOffset);
            return true;
        }
        if (isInsideNodePanel(mouseX, mouseY)) {
            int maxOffset = Math.max(0, filteredNodes.size() - visibleNodeCount());
            nodeScroll = Mth.clamp(nodeScroll - (int) Math.signum(delta), 0, maxOffset);
            return true;
        }
        if (isInsideDetailPanel(mouseX, mouseY)) {
            int maxDetailScroll = maxDetailScrollLines();
            if (maxDetailScroll > 0) {
                detailScroll = Mth.clamp(detailScroll - (int) Math.signum(delta), 0, maxDetailScroll);
                return true;
            }
        }
        return super.mouseScrolled(mouseX, mouseY, delta);
    }

    @Override
    public boolean keyPressed(int keyCode, int scanCode, int modifiers) {
        if (keyCode == 256) {
            onClose();
            return true;
        }
        return super.keyPressed(keyCode, scanCode, modifiers);
    }

    @Override
    public boolean isPauseScreen() {
        return false;
    }

    private void buildFactionFilters() {
        factionFilters.clear();
        factionFilters.add(ALL_FACTION);
        factionFilters.add(new FactionFilter(
                Hk3NarrativeFaction.EASTER_EGG,
                I18n.get(Hk3NarrativeFaction.EASTER_EGG.titleKey)));
        for (Hk3NarrativeFaction faction : Hk3NarrativeFaction.values()) {
            if (faction == Hk3NarrativeFaction.EASTER_EGG) {
                continue;
            }
            factionFilters.add(new FactionFilter(faction, I18n.get(faction.titleKey)));
        }
    }

    private String buildFactionLabel(FactionFilter filter) {
        boolean selected = selectedFaction == filter.faction();
        return selected ? "▶ " + filter.label() : "  " + filter.label();
    }

    private void applyFactionFilter(Hk3NarrativeFaction faction) {
        selectedFaction = faction;
        filteredNodes.clear();

        if (faction == null) {
            Collection<Hk3NarrativeNode> all = Hk3NarrativeNodes.all();
            filteredNodes.addAll(all);
        } else {
            filteredNodes.addAll(Hk3NarrativeNodes.byFaction(faction));
        }

        factionScroll = 0;
        nodeScroll = 0;
        detailScroll = 0;
        if (selectedNode == null || !filteredNodes.contains(selectedNode)) {
            selectedNode = filteredNodes.isEmpty() ? null : filteredNodes.get(0);
        }
    }

    private void drawFactionPanel(GuiGraphics gui, int mouseX, int mouseY) {
        int x = guiLeft + PADDING;
        int y = contentTop;
        drawPanel(gui, x, y, LEFT_WIDTH, contentHeight, BG_LIST, BORDER);
        gui.drawString(font, "阵营", x + 4, y - 10, TEXT_DIM, false);

        int listTop = y + 4;
        int listWidth = LEFT_WIDTH - 8;
        int maxVisible = visibleFactionCount();

        for (int i = 0; i < maxVisible && factionScroll + i < factionFilters.size(); i++) {
            int index = factionScroll + i;
            FactionFilter filter = factionFilters.get(index);
            int rowY = listTop + i * ROW_HEIGHT;
            boolean selected = selectedFaction == filter.faction();
            int bg = selected ? BG_ENTRY_SELECTED : BG_ENTRY;
            if (mouseX >= x + 4 && mouseX <= x + LEFT_WIDTH - 4 && mouseY >= rowY && mouseY <= rowY + ROW_HEIGHT - 2) {
                bg = selected ? 0xD02D3E50 : 0xA0222F3E;
            }
            gui.fill(x + 4, rowY, x + LEFT_WIDTH - 4, rowY + ROW_HEIGHT - 2, bg);
            gui.drawString(font, trimToWidth(buildFactionLabel(filter), listWidth - 8), x + 8, rowY + 5,
                    selected ? TEXT_NORMAL : TEXT_DIM, false);
        }

        drawVerticalScrollbar(
                gui,
                x + LEFT_WIDTH - 6,
                listTop,
                contentHeight - 8,
                factionFilters.size(),
                maxVisible,
                factionScroll);
    }

    private void drawNodePanel(GuiGraphics gui, int mouseX, int mouseY) {
        int x = guiLeft + PADDING * 2 + LEFT_WIDTH;
        int y = contentTop;
        drawPanel(gui, x, y, MID_WIDTH, contentHeight, BG_LIST, BORDER);
        gui.drawString(font, "节点", x + 4, y - 10, TEXT_DIM, false);

        int maxVisible = visibleNodeCount();
        int listTop = y + 4;
        int listWidth = MID_WIDTH - 8;

        if (filteredNodes.isEmpty()) {
            gui.drawString(font, "无可显示节点", x + 6, listTop + 4, TEXT_LOCKED, false);
            return;
        }

        for (int i = 0; i < maxVisible && nodeScroll + i < filteredNodes.size(); i++) {
            int index = nodeScroll + i;
            Hk3NarrativeNode node = filteredNodes.get(index);
            int rowY = listTop + i * ROW_HEIGHT;
            boolean selected = node == selectedNode;
            boolean unlocked = isNodeUnlocked(node);
            int bg = selected ? BG_ENTRY_SELECTED : BG_ENTRY;
            if (mouseX >= x + 4 && mouseX <= x + MID_WIDTH - 4 && mouseY >= rowY && mouseY <= rowY + ROW_HEIGHT - 2) {
                bg = selected ? 0xD02D3E50 : 0xA0222F3E;
            }

            gui.fill(x + 4, rowY, x + MID_WIDTH - 4, rowY + ROW_HEIGHT - 2, bg);
            String title = unlocked ? I18n.get(node.titleKey()) : LOCKED_PLACEHOLDER;
            int color = unlocked ? TEXT_NORMAL : TEXT_LOCKED;
            gui.drawString(font, trimToWidth(title, listWidth - 8), x + 8, rowY + 5, color, false);
        }

        drawVerticalScrollbar(
                gui,
                x + MID_WIDTH - 6,
                listTop,
                contentHeight - 8,
                filteredNodes.size(),
                maxVisible,
                nodeScroll);
    }

    private void drawDetailPanel(GuiGraphics gui) {
        int x = guiLeft + PADDING * 3 + LEFT_WIDTH + MID_WIDTH;
        int y = contentTop;
        drawPanel(gui, x, y, detailWidth, contentHeight, BG_LIST, BORDER);
        gui.drawString(font, "档案详情", x + 4, y - 10, TEXT_DIM, false);

        if (selectedNode == null) {
            gui.drawString(font, "未选择节点", x + 6, y + 8, TEXT_LOCKED, false);
            return;
        }

        if (!isNodeUnlocked(selectedNode)) {
            gui.drawString(font, "该节点尚未解锁", x + 6, y + 8, TEXT_LOCKED, false);
            return;
        }

        int textX = x + 6;
        int textY = y + 8;
        int textWidth = detailWidth - 12;

        String title = I18n.get(selectedNode.titleKey());
        gui.drawString(font, trimToWidth(title, textWidth), textX, textY, TEXT_TITLE, false);
        textY += 13;

        if (selectedNode.hasAuthor()) {
            String author = I18n.get(selectedNode.authorKey());
            gui.drawString(font, trimToWidth(author, textWidth), textX, textY, TEXT_DIM, false);
            textY += 12;
        }
        if (selectedNode.hasCondition()) {
            String condition = "触发条件: " + I18n.get(selectedNode.conditionKey());
            gui.drawString(font, trimToWidth(condition, textWidth), textX, textY, 0xFFC9D6E6, false);
            textY += 12;
        }
        gui.fill(textX, textY, textX + textWidth, textY + 1, 0x7054657A);
        textY += 6;

        List<String> lines = detailLines(selectedNode, textWidth);
        int visibleLines = Math.max(1, (contentHeight - (textY - y) - 6) / DETAIL_LINE_HEIGHT);
        int start = Mth.clamp(detailScroll, 0, Math.max(0, lines.size() - visibleLines));
        for (int i = 0; i < visibleLines && start + i < lines.size(); i++) {
            gui.drawString(font, lines.get(start + i), textX, textY + i * DETAIL_LINE_HEIGHT, TEXT_NORMAL, false);
        }
        drawVerticalScrollbar(
                gui,
                x + detailWidth - 6,
                y + 6,
                contentHeight - 12,
                lines.size(),
                visibleLines,
                start);
    }

    private void drawBottomProgress(GuiGraphics gui) {
        int x = guiLeft + PADDING;
        int y = guiTop + guiHeight - BOTTOM_HEIGHT - PADDING + 2;
        int w = guiWidth - PADDING * 2;
        int h = BOTTOM_HEIGHT - 4;

        drawPanel(gui, x, y, w, h, 0xD010141B, BORDER);

        Player player = Minecraft.getInstance().player;
        int total = Hk3NarrativeNodes.totalCount();
        int unlocked = player == null ? 0 : Hk3NarrativeLog.unlockedCount(player);
        int fillWidth = total <= 0 ? 0 : (int) ((w - 2) * (unlocked / (double) total));
        gui.fill(x + 1, y + 1, x + 1 + fillWidth, y + h - 1, 0xA036B7D9);

        String progress = "进度: " + unlocked + "/" + total;
        gui.drawCenteredString(font, progress, x + w / 2, y + 4, 0xFFFFFFFF);
    }

    private boolean isNodeUnlocked(Hk3NarrativeNode node) {
        Player player = Minecraft.getInstance().player;
        return player != null && Hk3NarrativeLog.isUnlocked(player, node.id());
    }

    private List<String> detailLines(Hk3NarrativeNode node, int width) {
        List<String> out = new ArrayList<>();
        for (String bodyKey : node.bodyKeys()) {
            String paragraph = I18n.get(bodyKey);
            out.addAll(wrapParagraph(paragraph, width));
            out.add("");
        }
        if (!out.isEmpty() && out.get(out.size() - 1).isEmpty()) {
            out.remove(out.size() - 1);
        }
        return out;
    }

    private List<String> wrapParagraph(String text, int maxWidth) {
        List<String> lines = new ArrayList<>();
        if (text == null || text.isEmpty()) {
            lines.add("");
            return lines;
        }
        String remaining = text;
        while (!remaining.isEmpty()) {
            String line = font.plainSubstrByWidth(remaining, maxWidth);
            if (line.isEmpty()) {
                break;
            }
            lines.add(line);
            remaining = remaining.substring(line.length());
        }
        if (lines.isEmpty()) {
            lines.add(remaining);
        }
        return lines;
    }

    private int visibleFactionCount() {
        return Math.max(1, (contentHeight - 8) / ROW_HEIGHT);
    }

    private int visibleNodeCount() {
        return Math.max(1, (contentHeight - 8) / ROW_HEIGHT);
    }

    private int factionIndexAt(double mouseY) {
        int listTop = contentTop + 4;
        int relY = (int) mouseY - listTop;
        if (relY < 0) {
            return -1;
        }
        return factionScroll + relY / ROW_HEIGHT;
    }

    private int nodeIndexAt(double mouseY) {
        int listTop = contentTop + 4;
        int relY = (int) mouseY - listTop;
        if (relY < 0) {
            return -1;
        }
        return nodeScroll + relY / ROW_HEIGHT;
    }

    private boolean isInsideFactionPanel(double mouseX, double mouseY) {
        int x = guiLeft + PADDING;
        int y = contentTop;
        return mouseX >= x && mouseX <= x + LEFT_WIDTH && mouseY >= y && mouseY <= y + contentHeight;
    }

    private enum ScrollTarget {
        NONE, FACTION, NODE, DETAIL
    }

    private ScrollTarget scrollTargetAt(double mouseX, double mouseY) {
        if (isOnScrollbar(mouseX, mouseY, ScrollTarget.FACTION)) {
            return ScrollTarget.FACTION;
        }
        if (isOnScrollbar(mouseX, mouseY, ScrollTarget.NODE)) {
            return ScrollTarget.NODE;
        }
        if (isOnScrollbar(mouseX, mouseY, ScrollTarget.DETAIL)) {
            return ScrollTarget.DETAIL;
        }
        return ScrollTarget.NONE;
    }

    private boolean isOnScrollbar(double mouseX, double mouseY, ScrollTarget target) {
        ScrollMetrics metrics = scrollMetrics(target);
        if (metrics == null || metrics.totalRows <= metrics.visibleRows) {
            return false;
        }
        int trackX = metrics.trackX;
        int trackY = metrics.trackY;
        int trackH = metrics.trackH;
        int thumbH = Math.max(8, (int) (trackH * (metrics.visibleRows / (double) metrics.totalRows)));
        int maxScroll = Math.max(1, metrics.totalRows - metrics.visibleRows);
        int maxThumbOffset = Math.max(1, trackH - thumbH);
        int thumbOffset = (int) Math.round((metrics.scroll / (double) maxScroll) * maxThumbOffset);
        return mouseX >= trackX && mouseX <= trackX + 4
                && mouseY >= trackY + thumbOffset
                && mouseY <= trackY + thumbOffset + thumbH;
    }

    private void beginScrollDrag(ScrollTarget target, double mouseX, double mouseY) {
        ScrollMetrics metrics = scrollMetrics(target);
        if (metrics == null) {
            return;
        }
        draggingScroll = target;
        dragScrollAnchor = metrics.scroll;
        dragMouseAnchor = mouseY;
    }

    private void applyScrollDrag(double mouseY) {
        ScrollMetrics metrics = scrollMetrics(draggingScroll);
        if (metrics == null || metrics.totalRows <= metrics.visibleRows) {
            return;
        }
        int thumbH = Math.max(8, (int) (metrics.trackH * (metrics.visibleRows / (double) metrics.totalRows)));
        int maxScroll = Math.max(1, metrics.totalRows - metrics.visibleRows);
        int maxThumbOffset = Math.max(1, metrics.trackH - thumbH);
        double deltaRows = (mouseY - dragMouseAnchor) / maxThumbOffset * maxScroll;
        int next = Mth.clamp((int) Math.round(dragScrollAnchor + deltaRows), 0, maxScroll);
        switch (draggingScroll) {
            case FACTION -> factionScroll = next;
            case NODE -> nodeScroll = next;
            case DETAIL -> detailScroll = next;
            default -> {
            }
        }
    }

    private ScrollMetrics scrollMetrics(ScrollTarget target) {
        return switch (target) {
            case FACTION -> new ScrollMetrics(
                    guiLeft + PADDING + LEFT_WIDTH - 6,
                    contentTop + 4,
                    contentHeight - 8,
                    factionFilters.size(),
                    visibleFactionCount(),
                    factionScroll);
            case NODE -> new ScrollMetrics(
                    guiLeft + PADDING * 2 + LEFT_WIDTH + MID_WIDTH - 6,
                    contentTop + 4,
                    contentHeight - 8,
                    filteredNodes.size(),
                    visibleNodeCount(),
                    nodeScroll);
            case DETAIL -> {
                if (selectedNode == null || !isNodeUnlocked(selectedNode)) {
                    yield null;
                }
                int x = guiLeft + PADDING * 3 + LEFT_WIDTH + MID_WIDTH;
                int y = contentTop;
                int textY = y + 8 + 13;
                if (selectedNode.hasAuthor()) {
                    textY += 12;
                }
                if (selectedNode.hasCondition()) {
                    textY += 12;
                }
                textY += 7;
                int textWidth = detailWidth - 12;
                List<String> lines = detailLines(selectedNode, textWidth);
                int visibleLines = Math.max(1, (contentHeight - (textY - y) - 6) / DETAIL_LINE_HEIGHT);
                yield new ScrollMetrics(
                        x + detailWidth - 6,
                        y + 6,
                        contentHeight - 12,
                        lines.size(),
                        visibleLines,
                        detailScroll);
            }
            default -> null;
        };
    }

    private record ScrollMetrics(int trackX, int trackY, int trackH, int totalRows, int visibleRows, int scroll) {}

    private int maxDetailScrollLines() {
        if (selectedNode == null || !isNodeUnlocked(selectedNode)) {
            return 0;
        }
        int x = guiLeft + PADDING * 3 + LEFT_WIDTH + MID_WIDTH;
        int y = contentTop;
        int textY = y + 8 + 13;
        if (selectedNode.hasAuthor()) {
            textY += 12;
        }
        if (selectedNode.hasCondition()) {
            textY += 12;
        }
        textY += 7;
        int textWidth = detailWidth - 12;
        List<String> lines = detailLines(selectedNode, textWidth);
        int visibleLines = Math.max(1, (contentHeight - (textY - y) - 6) / DETAIL_LINE_HEIGHT);
        return Math.max(0, lines.size() - visibleLines);
    }

    private boolean isInsideNodePanel(double mouseX, double mouseY) {
        int x = guiLeft + PADDING * 2 + LEFT_WIDTH;
        int y = contentTop;
        return mouseX >= x && mouseX <= x + MID_WIDTH && mouseY >= y && mouseY <= y + contentHeight;
    }

    private boolean isInsideDetailPanel(double mouseX, double mouseY) {
        int x = guiLeft + PADDING * 3 + LEFT_WIDTH + MID_WIDTH;
        int y = contentTop;
        return mouseX >= x && mouseX <= x + detailWidth && mouseY >= y && mouseY <= y + contentHeight;
    }

    private String trimToWidth(String text, int maxWidth) {
        if (font.width(text) <= maxWidth) return text;
        String suffix = "...";
        String result = text;
        while (!result.isEmpty() && font.width(result + suffix) > maxWidth) {
            result = result.substring(0, result.length() - 1);
        }
        return result.isEmpty() ? suffix : result + suffix;
    }

    private void drawPanel(GuiGraphics gui, int x, int y, int w, int h, int bg, int border) {
        gui.fill(x, y, x + w, y + h, bg);
        gui.fill(x, y, x + w, y + 1, border);
        gui.fill(x, y + h - 1, x + w, y + h, border);
        gui.fill(x, y, x + 1, y + h, border);
        gui.fill(x + w - 1, y, x + w, y + h, border);
    }

    private void drawVerticalScrollbar(GuiGraphics gui, int x, int y, int h, int totalRows, int visibleRows, int scroll) {
        if (h <= 8 || totalRows <= 0 || visibleRows <= 0) {
            return;
        }
        int trackWidth = 3;
        gui.fill(x, y, x + trackWidth, y + h, SCROLL_TRACK);
        if (totalRows <= visibleRows) {
            gui.fill(x, y, x + trackWidth, y + h, SCROLL_THUMB);
            return;
        }

        int thumbHeight = Math.max(8, (int) (h * (visibleRows / (double) totalRows)));
        int maxScroll = Math.max(1, totalRows - visibleRows);
        int maxThumbOffset = Math.max(1, h - thumbHeight);
        int thumbOffset = (int) Math.round((scroll / (double) maxScroll) * maxThumbOffset);
        gui.fill(x, y + thumbOffset, x + trackWidth, y + thumbOffset + thumbHeight, SCROLL_THUMB);
    }

    private record FactionFilter(Hk3NarrativeFaction faction, String label) {}
}
