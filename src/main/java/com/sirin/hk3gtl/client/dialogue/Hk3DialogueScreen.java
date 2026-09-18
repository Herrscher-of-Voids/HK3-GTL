package com.sirin.hk3gtl.client.dialogue;



import com.sirin.hk3gtl.common.dialogue.*;
import com.sirin.hk3gtl.common.dialogue.definition.SirinDialogueDefinitions;
import com.sirin.hk3gtl.common.network.DialogueCloseC2SPacket;
import com.sirin.hk3gtl.common.network.DialoguePlayerChoiceC2SPacket;
import com.sirin.hk3gtl.common.network.Hk3Network;
import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.client.gui.components.Button;
import net.minecraft.client.gui.screens.Screen;
import net.minecraft.client.resources.language.I18n;
import net.minecraft.network.chat.Component;
import net.minecraft.util.FormattedCharSequence;
import net.minecraft.util.Mth;
import org.lwjgl.glfw.GLFW;

import javax.annotation.Nullable;
import java.util.ArrayList;
import java.util.List;

/**
 * 通用崩坏三风格对话界面。
 * <p>
 * 布局：全屏暗幕 + 底部面板(文本) + 角色名牌 + 选项按钮。
 * 支持逐字显示、多 segment 跳转、动态选项过滤。
 */
public class Hk3DialogueScreen extends Screen {

    private static final int CHARS_PER_TICK = 2;
    private static final int PANEL_HEIGHT = 240;
    private static final int PANEL_BOTTOM_MARGIN = 22;
    private static final int OVERLAY_COLOR = 0xCC000000;
    private static final int PANEL_BG = 0xBB101020;
    private static final int NAME_TAG_OFFSET_Y = 24;

    private final String dialogueId;
    private final int extraData;
    private final DialogueDefinition definition;
    private final boolean closableByEsc;

    private String currentSegmentId;
    private List<DialogueLine> currentLines = List.of();
    private int lineIndex = 0;
    private int charsRevealed = 0;
    private boolean textFullyRevealed = false;
    private boolean showingChoices = false;
    /** 已发送选项包、等待 S2C 推进，防止重复打开选项或误点推进 */
    boolean awaitingChoiceAck = false;
    /** 西琳终局：仅 IF 分支播完后允许关屏并发关闭包 */
    private boolean finaleNaturalEnd;

    // 面板滑入动画
    private int animTick = 0;
    private static final int ANIM_DURATION = 4;

    public Hk3DialogueScreen(String dialogueId, String startSegmentId, int extraData) {
        super(Component.empty());
        this.dialogueId = dialogueId;
        this.extraData = extraData;
        this.definition = DialogueRegistry.getDialogue(dialogueId);
        this.closableByEsc = definition != null && definition.closableByEsc();
        this.currentSegmentId = startSegmentId;
    }

    // ═══════════════ 静态入口（网络包调用） ═══════════════

    public static void openFromPacket(String dialogueId, String startSegmentId, int extraData) {
        Minecraft mc = Minecraft.getInstance();
        mc.execute(() -> mc.setScreen(new Hk3DialogueScreen(dialogueId, startSegmentId, extraData)));
    }

    public static void advanceFromPacket(String dialogueId, String nextSegmentId, int extraData) {
        Minecraft mc = Minecraft.getInstance();
        if (mc.screen instanceof Hk3DialogueScreen screen && screen.dialogueId.equals(dialogueId)) {
            mc.execute(() -> {
                screen.awaitingChoiceAck = false;
                screen.advanceToSegment(nextSegmentId);
            });
        }
    }

    /** 服务端校验失败：关界面且不向服务端再发关闭包（会话已由服务端清理） */
    public static void abortFromPacket(String dialogueId, String messageKey) {
        Minecraft mc = Minecraft.getInstance();
        mc.execute(() -> {
            if (mc.screen instanceof Hk3DialogueScreen screen && screen.dialogueId.equals(dialogueId)) {
                screen.awaitingChoiceAck = false;
                mc.setScreen(null);
            }
            if (!messageKey.isEmpty() && mc.player != null) {
                mc.player.displayClientMessage(Component.translatable(messageKey), false);
            }
        });
    }

    // ═══════════════ 生命周期 ═══════════════

    @Override
    protected void init() {
        super.init();
        if (definition == null) {
            closeDialogue();
            return;
        }
        loadSegment(currentSegmentId);
    }

    @Override
    public boolean shouldCloseOnEsc() {
        return closableByEsc;
    }

    @Override
    public boolean isPauseScreen() {
        return false;
    }

    @Override
    public void onClose() {
        if (isSirinFinale() && !finaleNaturalEnd) {
            Minecraft.getInstance().setScreen(this);
            return;
        }
        closeDialogue();
    }

    @Override
    public void tick() {
        super.tick();
        if (animTick < ANIM_DURATION) animTick++;
        if (showingChoices) return;

        if (lineIndex >= currentLines.size()) {
            onSegmentFinished();
            return;
        }

        if (!textFullyRevealed) {
            DialogueLine line = currentLines.get(lineIndex);
            String text = I18n.get(resolveDisplayedTextKey(line));
            int totalVisible = DialogueRenderHelper.countVisibleChars(text);
            charsRevealed = Math.min(charsRevealed + CHARS_PER_TICK, totalVisible);
            if (charsRevealed >= totalVisible) {
                textFullyRevealed = true;
            }
        }
    }

    // ═══════════════ 渲染 ═══════════════

    @Override
    public void render(GuiGraphics gui, int mouseX, int mouseY, float partialTick) {
        // 全屏暗幕
        gui.fill(0, 0, width, height, OVERLAY_COLOR);

        if (definition == null) {
            super.render(gui, mouseX, mouseY, partialTick);
            return;
        }

        int panelW = Mth.clamp((int) (width * 0.86), 520, 820);
        int panelX = (width - panelW) / 2;

        // 面板滑入动画
        float animProgress = Math.min(1.0F, (float) animTick / ANIM_DURATION);
        int targetPanelY = height - PANEL_HEIGHT - PANEL_BOTTOM_MARGIN;
        int panelY = (int) (height + (targetPanelY - height) * animProgress);

        // 获取当前说话者主题
        DialogueSpeakerTheme theme = getCurrentSpeakerTheme();
        int accentColor = theme != null ? theme.accentColor() : 0xFF888888;

        // 面板背景 + 边框
        gui.fill(panelX, panelY, panelX + panelW, panelY + PANEL_HEIGHT, PANEL_BG);
        drawBorder(gui, panelX, panelY, panelW, PANEL_HEIGHT, accentColor);

        // 角色名牌
        if (theme != null) {
            String name = "「" + I18n.get(theme.nameKey()) + "」";
            gui.drawString(font, name, panelX + 12, panelY - NAME_TAG_OFFSET_Y, theme.nameColor());
        }

        // 文本区（纯文本模式：不渲染头像）
        int textX = panelX + 16;
        int textY = panelY + 20;
        int textWrapWidth = Math.max(120, panelW - 32);

        if (!showingChoices && lineIndex < currentLines.size()) {
            DialogueLine line = currentLines.get(lineIndex);
            String fullText = I18n.get(resolveDisplayedTextKey(line));
            String revealed = DialogueRenderHelper.truncateToVisibleChars(fullText, charsRevealed);
            Component textComp = Component.literal("§f" + revealed);
            List<FormattedCharSequence> wrapped = font.split(textComp, textWrapWidth);

            int lineH = font.lineHeight + 2;
            for (int i = 0; i < wrapped.size(); i++) {
                gui.drawString(font, wrapped.get(i), textX, textY + i * lineH, 0xFFFFFF);
            }
        }

        // 底部提示
        if (!showingChoices) {
            String hint = I18n.get("hk3gtl.dialogue.hint.continue");
            gui.drawCenteredString(font, "§8" + hint, width / 2, height - 16, 0x888888);
        }

        super.render(gui, mouseX, mouseY, partialTick);
    }

    // ═══════════════ 输入处理 ═══════════════

    @Override
    public boolean mouseClicked(double mouseX, double mouseY, int button) {
        if (awaitingChoiceAck) return true;
        if (showingChoices) return super.mouseClicked(mouseX, mouseY, button);
        if (button == 0 && textFullyRevealed) {
            advanceText();
            return true;
        }
        return isSirinFinale() || super.mouseClicked(mouseX, mouseY, button);
    }

    @Override
    public boolean keyPressed(int keyCode, int scanCode, int modifiers) {
        if (awaitingChoiceAck) return true;
        if (showingChoices) return super.keyPressed(keyCode, scanCode, modifiers);
        if (isSirinFinale() && !textFullyRevealed) {
            return true;
        }
        if (keyCode == GLFW.GLFW_KEY_ENTER || keyCode == GLFW.GLFW_KEY_KP_ENTER || keyCode == GLFW.GLFW_KEY_SPACE) {
            if (textFullyRevealed) {
                advanceText();
            }
            return true;
        }
        if (closableByEsc && keyCode == GLFW.GLFW_KEY_ESCAPE) {
            closeDialogue();
            return true;
        }
        return isSirinFinale() || super.keyPressed(keyCode, scanCode, modifiers);
    }

    // ═══════════════ 内部逻辑 ═══════════════

    private void advanceText() {
        if (awaitingChoiceAck) return;
        if (lineIndex >= currentLines.size()) return;
        if (isSirinFinale() && !textFullyRevealed) return;

        DialogueLine line = currentLines.get(lineIndex);
        String fullText = I18n.get(resolveDisplayedTextKey(line));
        int totalVisible = DialogueRenderHelper.countVisibleChars(fullText);
        if (charsRevealed < totalVisible) {
            return;
        }

        // 若当前行有选项，显示选项
        if (line.choices() != null && !line.choices().isEmpty()) {
            showChoices(line.choices());
            return;
        }

        // 推进到下一行
        lineIndex++;
        charsRevealed = 0;
        textFullyRevealed = false;
    }

    private void showChoices(List<DialogueChoice> choices) {
        showingChoices = true;
        clearWidgets();

        int panelW = Mth.clamp((int) (width * 0.86), 520, 820);
        int panelX = (width - panelW) / 2;
        int panelY = height - PANEL_HEIGHT - PANEL_BOTTOM_MARGIN;

        int btnH = 22;
        int gap = 4;
        int startX = panelX + 16;
        int startY = panelY + 20;

        List<FilteredChoice> filtered = buildFilteredChoiceRows(choices);

        // 选项过多时(如内测三 10 条 IF)单列会溢出面板，按每列最多 MAX_ROWS_PER_COL 行分多列布局
        int maxRowsPerCol = 5;
        int cols = Math.max(1, (filtered.size() + maxRowsPerCol - 1) / maxRowsPerCol);
        int colGap = 8;
        int colW = (panelW - 32 - (cols - 1) * colGap) / cols;

        for (int i = 0; i < filtered.size(); i++) {
            FilteredChoice row = filtered.get(i);
            String label = I18n.get(row.choice().labelKey());
            int col = i / maxRowsPerCol;
            int rowInCol = i % maxRowsPerCol;
            int x = startX + col * (colW + colGap);
            int y = startY + rowInCol * (btnH + gap);
            addRenderableWidget(Button.builder(Component.literal(label), b -> onChoiceSelected(row.originalIndex(), row.choice()))
                    .bounds(x, y, colW, btnH)
                    .build());
        }
    }

    /** 与 {@link #filterChoices} 一致，但保留原始选项下标供 C2S 包与服务端会话对齐 */
    private List<FilteredChoice> buildFilteredChoiceRows(List<DialogueChoice> choices) {
        List<FilteredChoice> rows = new ArrayList<>();
        if ("sirin_finale".equals(dialogueId)) {
            int mask = extraData != 0 ? extraData : (1 << SirinDialogueDefinitions.IF_BRANCH_COUNT) - 1;
            for (int i = 0; i < choices.size(); i++) {
                if (((mask >> i) & 1) != 0) {
                    rows.add(new FilteredChoice(i, choices.get(i)));
                }
            }
            return rows;
        }
        for (int i = 0; i < choices.size(); i++) {
            rows.add(new FilteredChoice(i, choices.get(i)));
        }
        return rows;
    }

    private record FilteredChoice(int originalIndex, DialogueChoice choice) {}

    private void onChoiceSelected(int originalChoiceIndex, DialogueChoice choice) {
        showingChoices = false;
        clearWidgets();
        awaitingChoiceAck = true;

        // 仅发 C2S；segment 由服务端校验后通过 DialogueAdvanceS2CPacket 推进，避免过滤下标漂移
        Hk3Network.CHANNEL.sendToServer(new DialoguePlayerChoiceC2SPacket(dialogueId, originalChoiceIndex));
    }

    private void advanceToSegment(String segmentId) {
        currentSegmentId = segmentId;
        loadSegment(segmentId);
    }

    private void loadSegment(String segmentId) {
        if (definition == null) return;
        awaitingChoiceAck = false;
        var rawLines = definition.segments().get(segmentId);
        if (rawLines == null) {
            currentLines = List.of();
        } else {
            // 过滤掉翻译键不存在的行（保留带 choices 的行）
            List<DialogueLine> valid = new ArrayList<>();
            for (DialogueLine line : rawLines) {
                boolean hasText = I18n.exists(line.textKey())
                        || (line.fallbackTextKey() != null && I18n.exists(line.fallbackTextKey()));
                if (line.choices() != null || hasText) {
                    valid.add(line);
                }
            }
            currentLines = valid;
        }
        lineIndex = 0;
        charsRevealed = 0;
        textFullyRevealed = false;
        showingChoices = false;
        clearWidgets();
    }

    private void onSegmentFinished() {
        if (!currentLines.isEmpty()) {
            DialogueLine lastLine = currentLines.get(currentLines.size() - 1);
            if (lastLine.choices() != null && !lastLine.choices().isEmpty()) {
                showChoices(lastLine.choices());
                return;
            }
        }
        if (isSirinFinale() && (currentSegmentId == null || !currentSegmentId.startsWith("if_"))) {
            return;
        }
        finaleNaturalEnd = true;
        closeDialogue();
    }

    private void closeDialogue() {
        if (isSirinFinale() && !finaleNaturalEnd) {
            return;
        }
        awaitingChoiceAck = false;
        Hk3Network.CHANNEL.sendToServer(new DialogueCloseC2SPacket(dialogueId));
        Minecraft mc = Minecraft.getInstance();
        mc.execute(() -> mc.setScreen(null));
    }

    private boolean isSirinFinale() {
        return SirinDialogueDefinitions.DIALOGUE_ID.equals(dialogueId);
    }

    // ═══════════════ 渲染辅助 ═══════════════

    @Nullable
    private DialogueSpeakerTheme getCurrentSpeakerTheme() {
        if (lineIndex < currentLines.size()) {
            return DialogueRegistry.getSpeaker(currentLines.get(lineIndex).speakerId());
        }
        if (!currentLines.isEmpty()) {
            return DialogueRegistry.getSpeaker(currentLines.get(0).speakerId());
        }
        return null;
    }

    /** 首选键无翻译时使用回退键（版本化开场等） */
    private static String resolveDisplayedTextKey(DialogueLine line) {
        if (I18n.exists(line.textKey())) {
            return line.textKey();
        }
        if (line.fallbackTextKey() != null && I18n.exists(line.fallbackTextKey())) {
            return line.fallbackTextKey();
        }
        return line.textKey();
    }

    private void drawBorder(GuiGraphics gui, int x, int y, int w, int h, int color) {
        int borderColor = (color & 0x00FFFFFF) | 0xAA000000;
        gui.fill(x, y, x + w, y + 1, borderColor);          // 上
        gui.fill(x, y + h - 1, x + w, y + h, borderColor);  // 下
        gui.fill(x, y, x + 1, y + h, borderColor);          // 左
        gui.fill(x + w - 1, y, x + w, y + h, borderColor);  // 右
    }
}
