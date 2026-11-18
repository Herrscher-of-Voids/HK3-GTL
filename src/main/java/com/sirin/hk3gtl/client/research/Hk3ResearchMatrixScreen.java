package com.sirin.hk3gtl.client.research;

import com.sirin.hk3gtl.common.constants.Hk3Values;
import com.sirin.hk3gtl.common.research.Hk3ResearchManager;
import com.sirin.hk3gtl.common.research.Hk3ResearchNode;
import com.sirin.hk3gtl.common.research.Hk3ResearchNodes;
import com.sirin.hk3gtl.common.research.Hk3ResearchRequirement;
import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.client.gui.components.Button;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.chat.Component;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;

import java.util.ArrayList;
import java.util.List;

 





public class Hk3ResearchMatrixScreen extends com.sirin.hk3gtl.client.gui.Hk3FittedScreen {

    private static final int ROOT_BG = 0xE0101016;
    private static final int FRAME_BG = 0xF01D1D23;
    private static final int PANEL_BG = 0xEE12161C;
    private static final int PANEL_BG_ALT = 0xEE0D1116;
    private static final int BORDER = 0xFF5C687A;
    private static final int ACCENT = 0xFF1FD8FF;
    private static final int ACCENT_DIM = 0x8820A8C8;
    private static final int TEXT = 0xFFE6EDF6;
    private static final int TEXT_DIM = 0xFF8F9BA8;
    private static final int TEXT_WARN = 0xFFFFC65A;
    private static final int TEXT_BAD = 0xFFFF6B6B;
    private static final int TEXT_OK = 0xFF62F5A6;

    private static final int MIN_GUI_WIDTH = 360;
    private static final int MAX_GUI_WIDTH = 920;
    private static final int MIN_GUI_HEIGHT = 260;
    private static final int MAX_GUI_HEIGHT = 560;
    private static final int HEADER_HEIGHT = 22;
    private static final int FOOTER_HEIGHT = 32;
    private static final int LIST_TOP_PADDING = 6;
    private static final int LIST_ITEM_HEIGHT = 36;

    private final List<Hk3ResearchNode> allNodes;

    private Hk3ResearchNode selectedNode;
    private Button submitButton;
    private int scrollOffset;

    private int guiLeft;
    private int guiTop;
    private int guiWidth;
    private int guiHeight;
    private int listWidth;
    private int detailWidth;
    private int footerLeftWidth;
    private int footerButtonWidth;

    public Hk3ResearchMatrixScreen() {
        super(Component.literal("旧版研究档案"), 620, 360);
        this.allNodes = Hk3ResearchNodes.allNodes();
        this.selectedNode = this.allNodes.isEmpty() ? null : this.allNodes.get(0);
    }

    public static void openFromPacket() {
        Minecraft minecraft = Minecraft.getInstance();
        minecraft.execute(() -> minecraft.setScreen(new Hk3ResearchMatrixScreen()));
    }

    @Override
    protected void initFitted() {
        guiWidth = clamp(this.width - 24, Math.min(MIN_GUI_WIDTH, this.width - 12), MAX_GUI_WIDTH);
        guiHeight = clamp(this.height - 24, Math.min(MIN_GUI_HEIGHT, this.height - 12), MAX_GUI_HEIGHT);
        guiLeft = (this.width - guiWidth) / 2;
        guiTop = (this.height - guiHeight) / 2;
        listWidth = clamp((int) (guiWidth * 0.30F), 128, 220);
        detailWidth = guiWidth - listWidth - 18;

        footerButtonWidth = clamp(detailWidth / 4, 90, 120);
        footerLeftWidth = Math.min(150, Math.max(96, detailWidth / 3));
        int submitWidth = footerButtonWidth;
        int submitX = guiLeft + listWidth + 12 + detailWidth - submitWidth - 6;
        int submitY = guiTop + guiHeight - FOOTER_HEIGHT + 6;
        if (submitButton == null) {
            submitButton = this.addRenderableWidget(Button.builder(
                            Component.literal("只读档案"), button -> {})
                    .bounds(submitX, submitY, submitWidth, 20)
                    .build());
        } else {
            this.addRenderableWidget(submitButton);
            submitButton.setX(submitX);
            submitButton.setY(submitY);
            submitButton.setWidth(submitWidth);
        }

        ensureSelectionVisible();
        refreshSubmitButton();
    }

    @Override
    public void renderFitted(GuiGraphics gfx, int mouseX, int mouseY, float partialTick) {
        renderBackground(gfx);
        gfx.fill(0, 0, width, height, ROOT_BG);

        drawPanel(gfx, guiLeft, guiTop, guiWidth, guiHeight, FRAME_BG, BORDER);
        renderHeader(gfx);
        renderListPanel(gfx, mouseX, mouseY);
        renderDetailPanel(gfx);
        renderFooter(gfx);

        super.renderFitted(gfx, mouseX, mouseY, partialTick);
    }

    private void renderHeader(GuiGraphics gfx) {
        gfx.fill(guiLeft + 1, guiTop + 1, guiLeft + guiWidth - 1, guiTop + HEADER_HEIGHT, 0xFF05080C);
        gfx.fill(guiLeft + 2, guiTop + HEADER_HEIGHT - 1, guiLeft + guiWidth - 2, guiTop + HEADER_HEIGHT, ACCENT_DIM);
        gfx.drawString(font, Component.literal("旧版77题 · 只读档案"),
                guiLeft + 8, guiTop + 7, 0xFFFFFFFF, false);

        Player player = getLocalPlayer();
        int completed = 0;
        if (player != null) {
            for (Hk3ResearchNode node : allNodes) {
                if (Hk3ResearchManager.isCompleted(player, node.id())) completed++;
            }
        }
        String stats = completed + "/" + allNodes.size();
        String right = "历史完成 " + stats + "  |  " + matrixHeaderText();
        gfx.drawString(font, trimToWidth(right, Math.max(80, guiWidth - 180)),
                guiLeft + guiWidth - font.width(trimToWidth(right, Math.max(80, guiWidth - 180))) - 8,
                guiTop + 7, TEXT_DIM, false);
    }

    private void renderListPanel(GuiGraphics gfx, int mouseX, int mouseY) {
        int x = guiLeft + 6;
        int y = guiTop + HEADER_HEIGHT + 4;
        int h = guiHeight - HEADER_HEIGHT - FOOTER_HEIGHT - 8;
        drawPanel(gfx, x, y, listWidth, h, PANEL_BG, BORDER);

        int itemsY = y + LIST_TOP_PADDING;
        int maxVisible = getVisibleCount();
        for (int i = 0; i < maxVisible && i + scrollOffset < allNodes.size(); i++) {
            int nodeIndex = i + scrollOffset;
            Hk3ResearchNode node = allNodes.get(nodeIndex);
            int itemY = itemsY + i * LIST_ITEM_HEIGHT;
            renderListEntry(gfx, node, x + 4, itemY, listWidth - 8, node == getSelectedNode(), mouseX, mouseY);
        }

        if (allNodes.isEmpty()) {
            gfx.drawString(font, Component.translatable("hk3gtl.gui.research_matrix.no_results"),
                    x + 8, itemsY + 4, TEXT_DIM, false);
        }
    }

    private void renderListEntry(GuiGraphics gfx, Hk3ResearchNode node, int x, int y, int w, boolean selected, int mouseX, int mouseY) {
        NodeState state = getNodeState(node);
        int bg = selected ? 0xFFE5E5E5 : 0xFFB8B8B8;
        if (mouseX >= x && mouseX <= x + w && mouseY >= y && mouseY <= y + LIST_ITEM_HEIGHT - 2) {
            bg = selected ? 0xFFF2F2F2 : 0xFFC6C6C6;
        }

        gfx.fill(x, y, x + w, y + LIST_ITEM_HEIGHT - 2, bg);
        gfx.fill(x + w - 2, y, x + w, y + LIST_ITEM_HEIGHT - 2, 0xFF777777);
        gfx.fill(x, y, x + 3, y + LIST_ITEM_HEIGHT - 2, state.barColor);
        gfx.fill(x + 34, y, x + w - 10, y + 1, 0x55FFFFFF);

        ItemStack icon = getNodeIcon(node, state);
        gfx.renderItem(icon, x + 8, y + 9);
        gfx.renderItemDecorations(font, icon, x + 8, y + 9);

        String title = trimToWidth(displayName(node), w - 38);
        String subtitle = trimToWidth(Component.translatable(node.typeDisplayKey()).getString() + " / " + state.shortLabel, w - 38);
        gfx.drawString(font, title, x + 30, y + 6, 0xFF3B3B3B, false);
        gfx.drawString(font, subtitle, x + 30, y + 19, 0xFF5A5A5A, false);
    }

    private void renderDetailPanel(GuiGraphics gfx) {
        int x = guiLeft + listWidth + 12;
        int y = guiTop + HEADER_HEIGHT + 4;
        int h = guiHeight - HEADER_HEIGHT - FOOTER_HEIGHT - 8;
        drawPanel(gfx, x, y, detailWidth, h, 0xF0060708, BORDER);

        Hk3ResearchNode node = getSelectedNode();
        if (node == null) {
            gfx.drawString(font, Component.translatable("hk3gtl.gui.research_matrix.empty_selection"), x + 10, y + 10, TEXT_DIM, false);
            return;
        }

        NodeState state = getNodeState(node);
        int cursorY = y + 8;

        gfx.drawString(font, trimToWidth(displayName(node), detailWidth - 130), x + 10, cursorY, ACCENT, false);
        Component tier = Component.translatable("hk3gtl.gui.research_matrix.voltage_level", voltageLabel(node));
        var tierLines = font.split(tier, Math.max(70, detailWidth / 3));
        if (!tierLines.isEmpty()) {
            var shownTier = tierLines.get(0);
            gfx.drawString(font, shownTier, x + detailWidth - font.width(shownTier) - 10, cursorY, TEXT_DIM, false);
        }
        cursorY += 14;
        gfx.fill(x + 10, cursorY, x + detailWidth - 10, cursorY + 1, ACCENT_DIM);
        cursorY += 8;

        renderInfoBlock(gfx, x + 10, cursorY, detailWidth - 20, 74, state, node);
        cursorY += 80;

        String effect = Component.translatable(node.effectKey()).getString();
        cursorY = renderTextSection(gfx, x + 10, cursorY, detailWidth - 20,
                Component.literal("旧版效果（不授予现行权限）"), effect);

        String unlock = Component.translatable(node.unlockDescriptionKey()).getString();
        cursorY = renderTextSection(gfx, x + 10, cursorY + 4, detailWidth - 20,
                Component.literal("旧版解锁说明（仅供查阅）"), unlock);

        cursorY += 4;
        renderRequirements(gfx, x + 10, cursorY, detailWidth - 20, node);
    }

    private void renderInfoBlock(GuiGraphics gfx, int x, int y, int w, int h, NodeState state, Hk3ResearchNode node) {
        int left = (w - 8) / 2;
        drawPanel(gfx, x, y, left, h, 0xF00B1216, 0xFF1C6C7A);
        drawPanel(gfx, x + left + 8, y, w - left - 8, h, 0xF00B1216, 0xFF1C6C7A);

        gfx.drawString(font, Component.translatable("hk3gtl.gui.research_matrix.section.status"), x + 8, y + 8, TEXT_DIM, false);
        gfx.drawString(font, state.label, x + 8, y + 22, state.textColor, false);
        gfx.drawString(font, Component.translatable(node.typeDisplayKey()), x + 8, y + 38, TEXT, false);
        gfx.drawString(font, trimToWidth("旧成果不自动兑换新课题", left - 16), x + 8, y + 54, TEXT_WARN, false);
        int rx = x + left + 16;
        gfx.drawString(font, Component.literal("历史条目摘要"), rx, y + 8, TEXT_DIM, false);
        gfx.drawString(font, Component.translatable("hk3gtl.gui.research_matrix.summary.prereq", node.prerequisites().size()), rx, y + 22, TEXT, false);
        gfx.drawString(font, Component.translatable("hk3gtl.gui.research_matrix.summary.materials", node.requirements().size()), rx, y + 38, TEXT, false);
        gfx.drawString(font, trimToWidth("现行研究请使用研究所", w - left - 24), rx, y + 54, ACCENT, false);
    }

    private int renderTextSection(GuiGraphics gfx, int x, int y, int w, Component title, String body) {
        gfx.drawString(font, title, x, y, ACCENT, false);
        y += 12;
        for (String line : wrapText(body, w)) {
            gfx.drawString(font, line, x + 4, y, TEXT, false);
            y += 11;
        }
        return y;
    }

    private void renderRequirements(GuiGraphics gfx, int x, int y, int w, Hk3ResearchNode node) {
        gfx.drawString(font, Component.literal("旧版材料记录（不再收取）"), x, y, ACCENT, false);
        y += 12;

        if (node.requirements().isEmpty()) {
            gfx.drawString(font, Component.translatable("hk3gtl.gui.research_matrix.no_materials"), x + 4, y, TEXT_DIM, false);
            return;
        }

        int cols = Math.max(1, Math.min(6, w / 56));
        int maxRows = Math.max(1, (guiTop + guiHeight - FOOTER_HEIGHT - 8 - y) / 42);
        int maxItems = cols * maxRows;
        for (int i = 0; i < node.requirements().size(); i++) {
            if (i >= maxItems) {
                gfx.drawString(font, Component.literal("+" + (node.requirements().size() - i) + "..."),
                        x + (i % cols) * 56 + 4, y + (i / cols) * 42 + 10, TEXT_DIM, false);
                break;
            }
            Hk3ResearchRequirement requirement = node.requirements().get(i);
            ItemStack stack = requirement.createStack();
            int col = i % cols;
            int row = i / cols;
            int boxX = x + col * 56;
            int boxY = y + row * 42;

            gfx.fill(boxX, boxY, boxX + 52, boxY + 38, 0xCC191F27);
            drawBorder(gfx, boxX, boxY, 52, 38, BORDER);
            gfx.renderItem(stack, boxX + 4, boxY + 4);
            gfx.renderItemDecorations(font, stack, boxX + 4, boxY + 4);

            String count = "x" + stack.getCount();
            gfx.drawString(font, count, boxX + 24, boxY + 4, TEXT_OK, false);
            String label = Component.translatable(requirement.descriptionKey()).getString();
            if (requirement.hasAlternatives()) label = "*" + label;
            gfx.drawString(font, trimToWidth(label, 46), boxX + 4, boxY + 24, TEXT_DIM, false);
        }
    }

    private void renderFooter(GuiGraphics gfx) {
        int x = guiLeft + listWidth + 12;
        int y = guiTop + guiHeight - FOOTER_HEIGHT;
        int w = detailWidth;
        drawPanel(gfx, x, y, w, FOOTER_HEIGHT - 4, PANEL_BG_ALT, BORDER);

        NodeState state = selectedNode == null ? NodeState.ARCHIVED : getNodeState(selectedNode);
        gfx.drawString(font, trimToWidth("现行研究请使用研究所", footerLeftWidth - 12), x + 10, y + 6, ACCENT, false);
        gfx.drawString(font, trimToWidth(state.label, footerLeftWidth - 12), x + 10, y + 18, state.textColor, false);

        int buttonArea = footerButtonWidth + 14;
        int progressX = x + footerLeftWidth + 8;
        int progressW = Math.max(40, w - footerLeftWidth - buttonArea - 18);
        renderMatrixProgress(gfx, progressX, y + 6, progressW, 16);
    }

    @Override
    public boolean clickFitted(double mouseX, double mouseY, int button) {
        // 优先把点击交给 widget（含提交按钮），避免被自定义列表区误吞。
        if (super.clickFitted(mouseX, mouseY, button)) return true;

        int listX = guiLeft + 6;
        int listY = guiTop + HEADER_HEIGHT + 4 + LIST_TOP_PADDING;
        int maxVisible = getVisibleCount();
        int listH = maxVisible * LIST_ITEM_HEIGHT;
        if (mouseX >= listX && mouseX <= listX + listWidth - 2
                && mouseY >= listY && mouseY <= listY + listH) {
            int relY = (int) mouseY - listY;
            int index = relY / LIST_ITEM_HEIGHT + scrollOffset;
            if (index >= 0 && index < allNodes.size()) {
                selectedNode = allNodes.get(index);
                refreshSubmitButton();
                return true;
            }
        }
        return false;
    }

    @Override
    public boolean scrollFitted(double mouseX, double mouseY, double delta) {
        int listX = guiLeft + 6;
        int listY = guiTop + HEADER_HEIGHT + 4;
        int listH = guiHeight - HEADER_HEIGHT - FOOTER_HEIGHT - 8;
        if (mouseX >= listX && mouseX <= listX + listWidth && mouseY >= listY && mouseY <= listY + listH) {
            int maxOffset = Math.max(0, allNodes.size() - getVisibleCount());
            scrollOffset = Math.max(0, Math.min(scrollOffset - (int) delta, maxOffset));
            return true;
        }
        return super.scrollFitted(mouseX, mouseY, delta);
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

    private void refreshSubmitButton() {
        submitButton.active = false;
    }

    private int getVisibleCount() {
        int listH = guiHeight - HEADER_HEIGHT - FOOTER_HEIGHT - 8 - LIST_TOP_PADDING;
        return Math.max(1, listH / LIST_ITEM_HEIGHT);
    }

    private void ensureSelectionVisible() {
        Hk3ResearchNode node = getSelectedNode();
        if (node == null) {
            scrollOffset = 0;
            return;
        }
        int index = allNodes.indexOf(node);
        if (index < 0) {
            scrollOffset = 0;
            return;
        }
        int visible = getVisibleCount();
        if (index < scrollOffset) scrollOffset = index;
        if (index >= scrollOffset + visible) scrollOffset = Math.max(0, index - visible + 1);
    }

    private Hk3ResearchNode getSelectedNode() {
        if (selectedNode != null) return selectedNode;
        if (allNodes.isEmpty()) return null;
        selectedNode = allNodes.get(0);
        return selectedNode;
    }

    private Player getLocalPlayer() {
        return Minecraft.getInstance().player;
    }

    private CompoundTag matrixTag() {
        Player player = getLocalPlayer();
        if (player == null) return new CompoundTag();
        return player.getPersistentData().getCompound("hk3gtl_research_matrix");
    }

    private String matrixHeaderText() {
        return matrixTag().getString("research").isEmpty() ? "旧版已退役" : "原在途任务已封存";
    }

    private static Component voltageLabel(Hk3ResearchNode node) {
        int tier = clamp((int) Math.floor(node.tier()), 0, 30);
        return tier >= 15 ? Component.literal(Hk3Values.getVN(tier)).withStyle(style ->
                style.withColor(com.sirin.hk3gtl.common.constants.Hk3VoltagePalette.text(tier)).withBold(true))
                : Component.literal(Hk3Values.getVNF(tier));
    }

    /** 剥掉节点中文名中可能存在的 "R-AB-001 " 等内部编号前缀。 */
    private String displayName(Hk3ResearchNode node) {
        return Hk3ResearchNodes.stripIdPrefix(Component.translatable(node.nameKey()).getString());
    }

    private void renderMatrixProgress(GuiGraphics gfx, int x, int y, int w, int h) {
        CompoundTag tag = matrixTag();
        gfx.fill(x, y, x + w, y + h, 0xFF090D10);
        drawBorder(gfx, x, y, w, h, 0xFF1C6C7A);
        if (tag.getString("research").isEmpty()) {
            gfx.drawString(font, trimToWidth(matrixHeaderText(), w - 10), x + 5, y + 4, TEXT_DIM, false);
            return;
        }
        int progress = tag.getInt("progress");
        int total = Math.max(1, tag.getInt("total"));
        int fill = Math.max(0, Math.min(w - 2, (int) ((w - 2) * (progress / (double) total))));
        gfx.fill(x + 1, y + 1, x + 1 + fill, y + h - 1, 0xAA1FD8FF);
        String label = "已封存 " + progress + "/" + total + " tick";
        gfx.drawString(font, trimToWidth(label, w - 10), x + 5, y + 4, 0xFFFFFFFF, false);
    }

    private boolean isCompleted(Hk3ResearchNode node) {
        Player player = getLocalPlayer();
        return player != null && Hk3ResearchManager.isCompleted(player, node.id());
    }

    private NodeState getNodeState(Hk3ResearchNode node) {
        if (isCompleted(node)) return NodeState.COMPLETED;
        if (node.id().equals(matrixTag().getString("research"))) return NodeState.SEALED;
        return NodeState.ARCHIVED;
    }

    private ItemStack getNodeIcon(Hk3ResearchNode node, NodeState state) {
        if (!node.requirements().isEmpty()) return node.requirements().get(0).createStack();
        return switch (state) {
            case COMPLETED -> new ItemStack(Items.KNOWLEDGE_BOOK);
            case SEALED -> new ItemStack(Items.CLOCK);
            case ARCHIVED -> new ItemStack(Items.BOOK);
        };
    }

    private String trimToWidth(String text, int maxWidth) {
        if (font.width(text) <= maxWidth) return text;
        String ellipsis = "...";
        String result = text;
        while (!result.isEmpty() && font.width(result + ellipsis) > maxWidth) {
            result = result.substring(0, result.length() - 1);
        }
        return result.isEmpty() ? ellipsis : result + ellipsis;
    }

    private String[] wrapText(String text, int maxWidth) {
        if (font.width(text) <= maxWidth) return new String[]{text};
        List<String> lines = new ArrayList<>();
        StringBuilder current = new StringBuilder();
        for (char c : text.toCharArray()) {
            current.append(c);
            if (font.width(current.toString()) > maxWidth) {
                String s = current.toString();
                lines.add(s.substring(0, s.length() - 1));
                current = new StringBuilder().append(c);
            }
        }
        if (!current.isEmpty()) lines.add(current.toString());
        return lines.toArray(new String[0]);
    }

    private void drawPanel(GuiGraphics gfx, int x, int y, int w, int h, int bg, int border) {
        gfx.fill(x, y, x + w, y + h, bg);
        drawBorder(gfx, x, y, w, h, border);
    }

    private void drawBorder(GuiGraphics gfx, int x, int y, int w, int h, int color) {
        gfx.fill(x, y, x + w, y + 1, color);
        gfx.fill(x, y + h - 1, x + w, y + h, color);
        gfx.fill(x, y, x + 1, y + h, color);
        gfx.fill(x + w - 1, y, x + w, y + h, color);
    }

    private static int clamp(int value, int min, int max) {
        return Math.max(min, Math.min(max, value));
    }

    private enum NodeState {
        COMPLETED("旧版已完成", "历史完成", TEXT_OK, 0xAA2FBF79),
        SEALED("原在途任务已封存", "已封存", TEXT_WARN, 0xAA8A7644),
        ARCHIVED("旧版只读档案", "只读", TEXT_DIM, 0xAA5C687A);

        final String label;
        final String shortLabel;
        final int textColor;
        final int barColor;

        NodeState(String label, String shortLabel, int textColor, int barColor) {
            this.label = label;
            this.shortLabel = shortLabel;
            this.textColor = textColor;
            this.barColor = barColor;
        }
    }
}
