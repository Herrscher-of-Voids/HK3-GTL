package com.sirin.hk3gtl.client.research;



import com.sirin.hk3gtl.common.network.Hk3Network;
import com.sirin.hk3gtl.common.network.ResearchSubmitPacket;
import com.sirin.hk3gtl.common.constants.Hk3Values;
import com.sirin.hk3gtl.common.machine.research.ResearchDifficulty;
import com.sirin.hk3gtl.common.research.Hk3ResearchManager;
import com.sirin.hk3gtl.common.research.Hk3ResearchNode;
import com.sirin.hk3gtl.common.research.Hk3ResearchNodes;
import com.sirin.hk3gtl.common.research.Hk3ResearchRequirement;
import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.client.gui.components.Button;
import net.minecraft.client.gui.screens.Screen;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.chat.Component;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;

import java.util.ArrayList;
import java.util.List;

/**
 * 海渊研究终端 GUI（v0.4 重构）。
 *
 * <h3>本轮重构点</h3>
 * <ol>
 *   <li>删除左上角搜索栏（项目并未实装搜索逻辑，纯占位）。</li>
 *   <li>所有节点显示名都剥掉 {@code R-XX-NNN} 内部编号，仅显示中文名。</li>
 *   <li>"终端状态"块的"需要"那一行：有前置时显示"前置研究：xxx"；
 *       无前置时回退为"海渊研究解析矩阵已激活"。</li>
 *   <li>提交按钮每帧重算 {@code active}，避免选中后偶发失活；
 *       同时把列表点击的 {@code listMaxY} 收口到实际可见行末，
 *       不再吃掉下方区域防止误选影响按钮判定。</li>
 *   <li>底栏原本写死的"终端：在线/在线"那一行换成"研究时间 / 剩余时间"实时倒计时。</li>
 * </ol>
 */
public class Hk3ResearchMatrixScreen extends Screen {

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
        super(Component.translatable("hk3gtl.gui.research_matrix.title"));
        this.allNodes = Hk3ResearchNodes.allNodes();
        this.selectedNode = this.allNodes.isEmpty() ? null : this.allNodes.get(0);
    }

    public static void openFromPacket() {
        Minecraft minecraft = Minecraft.getInstance();
        minecraft.execute(() -> minecraft.setScreen(new Hk3ResearchMatrixScreen()));
    }

    @Override
    protected void init() {
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
                            Component.translatable("hk3gtl.gui.research_matrix.submit"),
                            button -> submitSelectedResearch())
                    .bounds(submitX, submitY, submitWidth, 20)
                    .build());
        } else {
            submitButton.setX(submitX);
            submitButton.setY(submitY);
            submitButton.setWidth(submitWidth);
        }

        ensureSelectionVisible();
        refreshSubmitButton();
    }

    @Override
    public void render(GuiGraphics gfx, int mouseX, int mouseY, float partialTick) {
        // 每帧重新计算按钮可用状态，防止选中后偶发失活。
        refreshSubmitButton();

        renderBackground(gfx);
        gfx.fill(0, 0, width, height, ROOT_BG);

        drawPanel(gfx, guiLeft, guiTop, guiWidth, guiHeight, FRAME_BG, BORDER);
        renderHeader(gfx);
        renderListPanel(gfx, mouseX, mouseY);
        renderDetailPanel(gfx);
        renderFooter(gfx);

        super.render(gfx, mouseX, mouseY, partialTick);
    }

    private void renderHeader(GuiGraphics gfx) {
        gfx.fill(guiLeft + 1, guiTop + 1, guiLeft + guiWidth - 1, guiTop + HEADER_HEIGHT, 0xFF05080C);
        gfx.fill(guiLeft + 2, guiTop + HEADER_HEIGHT - 1, guiLeft + guiWidth - 2, guiTop + HEADER_HEIGHT, ACCENT_DIM);
        gfx.drawString(font, Component.translatable("hk3gtl.gui.research_matrix.terminal_name"),
                guiLeft + 8, guiTop + 7, 0xFFFFFFFF, false);

        Player player = getLocalPlayer();
        int completed = 0;
        if (player != null) {
            for (Hk3ResearchNode node : allNodes) {
                if (Hk3ResearchManager.isCompleted(player, node.id())) completed++;
            }
        }
        String stats = completed + "/" + allNodes.size();
        String right = Component.translatable("hk3gtl.gui.research_matrix.progress", stats).getString()
                + "  |  " + matrixHeaderText();
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
        String tier = Component.translatable("hk3gtl.gui.research_matrix.voltage_level", voltageLabel(node)).getString();
        gfx.drawString(font, trimToWidth(tier, Math.max(70, detailWidth / 3)),
                x + detailWidth - font.width(trimToWidth(tier, Math.max(70, detailWidth / 3))) - 10,
                cursorY, TEXT_DIM, false);
        cursorY += 14;
        gfx.fill(x + 10, cursorY, x + detailWidth - 10, cursorY + 1, ACCENT_DIM);
        cursorY += 8;

        renderInfoBlock(gfx, x + 10, cursorY, detailWidth - 20, 74, state, node);
        cursorY += 80;

        String effect = Component.translatable(node.effectKey()).getString();
        cursorY = renderTextSection(gfx, x + 10, cursorY, detailWidth - 20,
                Component.translatable("hk3gtl.gui.research_matrix.section.effect"), effect);

        String unlock = Component.translatable(node.unlockDescriptionKey()).getString();
        cursorY = renderTextSection(gfx, x + 10, cursorY + 4, detailWidth - 20,
                Component.translatable("hk3gtl.gui.research_matrix.section.unlock"), unlock);

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
        // 第 4 行：有前置 → 显示前置研究名；没前置 → 回退为"海渊研究解析矩阵已激活"
        Component requireLine;
        int requireColor;
        if (!node.prerequisites().isEmpty()) {
            requireLine = Component.translatable("hk3gtl.gui.research_matrix.requires_prereq",
                    formatPrerequisiteNames(node, left - 16));
            requireColor = TEXT_WARN;
        } else {
            requireLine = Component.translatable("hk3gtl.gui.research_matrix.requires_matrix");
            requireColor = node.requiresEvent() ? TEXT_WARN : TEXT_DIM;
        }
        gfx.drawString(font, requireLine, x + 8, y + 54, requireColor, false);
        int rx = x + left + 16;
        gfx.drawString(font, Component.translatable("hk3gtl.gui.research_matrix.section.summary"), rx, y + 8, TEXT_DIM, false);
        gfx.drawString(font, Component.translatable("hk3gtl.gui.research_matrix.summary.prereq", node.prerequisites().size()), rx, y + 22, TEXT, false);
        gfx.drawString(font, Component.translatable("hk3gtl.gui.research_matrix.summary.materials", node.requirements().size()), rx, y + 38, TEXT, false);
        gfx.drawString(font, node.isAutoComplete()
                ? Component.translatable("hk3gtl.gui.research_matrix.summary.auto")
                : Component.translatable("hk3gtl.gui.research_matrix.summary.manual"), rx, y + 54, ACCENT, false);
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
        gfx.drawString(font, Component.translatable("hk3gtl.gui.research_matrix.section.materials"), x, y, ACCENT, false);
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

        NodeState state = selectedNode == null ? NodeState.LOCKED : getNodeState(selectedNode);
        // 左半区：研究时间 / 剩余时间（实时倒计时）
        Hk3ResearchNode node = getSelectedNode();
        String timeTitle;
        String timeValue;
        int timeColor = TEXT;
        if (node == null || node.isAutoComplete()) {
            timeTitle = Component.translatable("hk3gtl.gui.research_matrix.research_time", "—").getString();
            timeValue = state.label;
            timeColor = state.textColor;
        } else if (state == NodeState.COMPLETED) {
            timeTitle = "";
            timeValue = state.label;
            timeColor = state.textColor;
        } else if (isMatrixBusyForSelected()) {
            int remaining = computeRemainingSeconds();
            timeTitle = Component.translatable("hk3gtl.gui.research_matrix.research_remaining", remaining).getString();
            timeValue = state.label;
            timeColor = state.textColor;
        } else if (isMatrixBusyForOtherSelected()) {
            timeTitle = Component.translatable("hk3gtl.gui.research_matrix.busy_other").getString();
            timeValue = state.label;
            timeColor = state.textColor;
        } else {
            int seconds = Math.max(1, ResearchDifficulty.durationTicks(node) / 20);
            timeTitle = Component.translatable("hk3gtl.gui.research_matrix.research_time", seconds).getString();
            timeValue = state.label;
            timeColor = state.textColor;
        }
        if (!timeTitle.isEmpty()) {
            gfx.drawString(font, trimToWidth(timeTitle, footerLeftWidth - 12), x + 10, y + 6, ACCENT, false);
        }
        gfx.drawString(font, trimToWidth(timeValue, footerLeftWidth - 12), x + 10, y + 18, timeColor, false);

        int buttonArea = footerButtonWidth + 14;
        int progressX = x + footerLeftWidth + 8;
        int progressW = Math.max(40, w - footerLeftWidth - buttonArea - 18);
        renderMatrixProgress(gfx, progressX, y + 6, progressW, 16);
    }

    @Override
    public boolean mouseClicked(double mouseX, double mouseY, int button) {
        // 优先把点击交给 widget（含提交按钮），避免被自定义列表区误吞。
        if (super.mouseClicked(mouseX, mouseY, button)) return true;

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
    public boolean mouseScrolled(double mouseX, double mouseY, double delta) {
        int listX = guiLeft + 6;
        int listY = guiTop + HEADER_HEIGHT + 4;
        int listH = guiHeight - HEADER_HEIGHT - FOOTER_HEIGHT - 8;
        if (mouseX >= listX && mouseX <= listX + listWidth && mouseY >= listY && mouseY <= listY + listH) {
            int maxOffset = Math.max(0, allNodes.size() - getVisibleCount());
            scrollOffset = Math.max(0, Math.min(scrollOffset - (int) delta, maxOffset));
            return true;
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

    private void submitSelectedResearch() {
        Hk3ResearchNode node = getSelectedNode();
        if (node != null) {
            Hk3Network.CHANNEL.sendToServer(new ResearchSubmitPacket(node.id()));
        }
    }

    private void refreshSubmitButton() {
        if (submitButton == null) return;
        Hk3ResearchNode node = getSelectedNode();
        NodeState state = node == null ? NodeState.LOCKED : getNodeState(node);
        boolean canSubmit = node != null && node.isManualResearch() && state == NodeState.READY;
        submitButton.visible = canSubmit;
        submitButton.active = canSubmit;
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

    private boolean matrixOnline() {
        return matrixTag().getBoolean("present");
    }

    private String matrixHeaderText() {
        CompoundTag tag = matrixTag();
        if (!tag.getBoolean("present")) return Component.translatable("hk3gtl.gui.research_matrix.matrix.offline").getString();
        if (tag.getBoolean("busy")) return Component.translatable("hk3gtl.gui.research_matrix.matrix.busy").getString();
        return Component.translatable("hk3gtl.gui.research_matrix.matrix.online").getString();
    }

    private static String voltageLabel(Hk3ResearchNode node) {
        int tier = clamp((int) Math.floor(node.tier()), 0, 30);
        return Hk3Values.getVNF(tier).replace("§", "\u00a7");
    }

    /** 剥掉节点中文名中可能存在的 "R-AB-001 " 等内部编号前缀。 */
    private String displayName(Hk3ResearchNode node) {
        return Hk3ResearchNodes.stripIdPrefix(Component.translatable(node.nameKey()).getString());
    }

    /** 拼接前置研究的中文显示名，超长时截断为 "A, B…(+N)"。 */
    private String formatPrerequisiteNames(Hk3ResearchNode node, int maxWidth) {
        List<String> prereqIds = node.prerequisites();
        if (prereqIds.isEmpty()) return "";
        StringBuilder sb = new StringBuilder();
        int shown = 0;
        for (int i = 0; i < prereqIds.size(); i++) {
            Hk3ResearchNode prereq = Hk3ResearchNodes.get(prereqIds.get(i));
            String name = prereq != null ? displayName(prereq) : prereqIds.get(i);
            String candidate = (sb.length() == 0 ? name : sb + ", " + name);
            if (font.width(candidate) > maxWidth && shown > 0) {
                int remaining = prereqIds.size() - i;
                sb.append("…(+").append(remaining).append(")");
                return sb.toString();
            }
            if (sb.length() > 0) sb.append(", ");
            sb.append(name);
            shown++;
        }
        return sb.toString();
    }

    /** 当前是否正在研究"选中节点"。仅当矩阵忙且 research id 一致时为 true。 */
    private boolean isMatrixBusyForSelected() {
        if (selectedNode == null) return false;
        return isMatrixBusyForNode(selectedNode);
    }

    private boolean isMatrixBusyForOtherSelected() {
        if (selectedNode == null) return false;
        return isMatrixBusyForOtherNode(selectedNode);
    }

    private boolean isMatrixBusyForNode(Hk3ResearchNode node) {
        if (node == null) return false;
        CompoundTag tag = matrixTag();
        if (!tag.getBoolean("busy")) return false;
        return node.id().equals(tag.getString("research"));
    }

    private boolean isMatrixBusyForOtherNode(Hk3ResearchNode node) {
        if (node == null) return false;
        CompoundTag tag = matrixTag();
        if (!tag.getBoolean("busy")) return false;
        return !node.id().equals(tag.getString("research"));
    }

    private int computeRemainingSeconds() {
        CompoundTag tag = matrixTag();
        if (!tag.getBoolean("busy")) return 0;
        int progress = tag.getInt("progress");
        int total = Math.max(1, tag.getInt("total"));
        int projected = projectedProgress(tag, progress, total);
        return Math.max(0, (total - projected) / 20);
    }

    private void renderMatrixProgress(GuiGraphics gfx, int x, int y, int w, int h) {
        CompoundTag tag = matrixTag();
        gfx.fill(x, y, x + w, y + h, 0xFF090D10);
        drawBorder(gfx, x, y, w, h, 0xFF1C6C7A);
        if (!tag.getBoolean("busy")) {
            gfx.drawString(font, matrixHeaderText(), x + 5, y + 4, matrixOnline() ? TEXT_OK : TEXT_BAD, false);
            return;
        }
        int progress = tag.getInt("progress");
        int total = Math.max(1, tag.getInt("total"));
        int projected = projectedProgress(tag, progress, total);
        double speedFactor = Math.max(0.01D, tag.contains("speedFactor") ? tag.getDouble("speedFactor") : 1.0D);
        int fill = Math.max(0, Math.min(w - 2, (int) ((w - 2) * (projected / (double) total))));
        gfx.fill(x + 1, y + 1, x + 1 + fill, y + h - 1, 0xAA1FD8FF);
        int remain = Math.max(0, (total - projected) / 20);
        String label = Component.translatable("hk3gtl.gui.research_matrix.matrix.progress",
                remain, total / 20).getString() + String.format("  x%.2f", speedFactor);
        gfx.drawString(font, label, x + 5, y + 4, 0xFFFFFFFF, false);
    }

    private int projectedProgress(CompoundTag tag, int syncedProgress, int total) {
        Minecraft minecraft = Minecraft.getInstance();
        if (minecraft.level == null || !tag.contains("gameTime")) return syncedProgress;
        long elapsedTicks = Math.max(0L, minecraft.level.getGameTime() - tag.getLong("gameTime"));
        double speedFactor = Math.max(0.01D, tag.contains("speedFactor") ? tag.getDouble("speedFactor") : 1.0D);
        int elapsed = (int) Math.min(Integer.MAX_VALUE, Math.floor(elapsedTicks * speedFactor));
        return Math.min(total, syncedProgress + elapsed);
    }

    private boolean isCompleted(Hk3ResearchNode node) {
        Player player = getLocalPlayer();
        return player != null && Hk3ResearchManager.isCompleted(player, node.id());
    }

    private boolean prerequisitesMet(Hk3ResearchNode node) {
        Player player = getLocalPlayer();
        return player != null && Hk3ResearchManager.prerequisitesMetForDisplay(player, node);
    }

    private boolean hasRequirements(Hk3ResearchNode node) {
        Player player = getLocalPlayer();
        return player != null && Hk3ResearchManager.hasRequirementsForDisplay(player, node);
    }

    private NodeState getNodeState(Hk3ResearchNode node) {
        if (isCompleted(node)) return NodeState.COMPLETED;
        if (isMatrixBusyForNode(node)) return NodeState.IN_PROGRESS;
        if (node.isAutoComplete()) return NodeState.AUTO_PENDING;
        if (isMatrixBusyForOtherNode(node)) return NodeState.MATRIX_BUSY_OTHER;
        if (!prerequisitesMet(node)) return NodeState.LOCKED;
        if (!hasRequirements(node)) return NodeState.MISSING_ITEMS;
        return NodeState.READY;
    }

    private ItemStack getNodeIcon(Hk3ResearchNode node, NodeState state) {
        if (!node.requirements().isEmpty()) return node.requirements().get(0).createStack();
        return switch (state) {
            case COMPLETED -> new ItemStack(Items.KNOWLEDGE_BOOK);
            case IN_PROGRESS -> new ItemStack(Items.CLOCK);
            case READY -> new ItemStack(Items.EMERALD);
            case AUTO_PENDING -> new ItemStack(Items.COMPASS);
            case MISSING_ITEMS -> new ItemStack(Items.CHEST);
            case MATRIX_BUSY_OTHER -> new ItemStack(Items.GRAY_STAINED_GLASS_PANE);
            case LOCKED -> new ItemStack(Items.BARRIER);
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
        COMPLETED("研究已解锁", "已完成", TEXT_OK, 0xAA2FBF79),
        IN_PROGRESS("研究进行中", "研究中", ACCENT, 0xAA1F90AE),
        AUTO_PENDING("自动完成（等待事件）", "等待事件", 0xFF7BC8FF, 0xAA3A7DAD),
        MATRIX_BUSY_OTHER("目前正在研究其他研究", "矩阵占用", TEXT_WARN, 0xAA8A7644),
        LOCKED("研究不可用", "前置锁定", TEXT_BAD, 0xAAAF4E4E),
        MISSING_ITEMS("缺少材料", "材料不足", TEXT_WARN, 0xAAAD8841),
        READY("研究可用", "可以提交", ACCENT, 0xAA1F90AE);

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
