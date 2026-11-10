package com.sirin.hk3gtl.client.narrative;


/**
 * 【文件职责】
 * - 管理 Hk3NarrativeCodexScreen 叙事节点与档案显示数据。
 * - 关键调用链：由上层系统入口调用 -> 本文件核心方法 -> 下游模块。
 *
 * 【变更记录】2026-05-19
 * - 删除：
 *   1) 左侧阵营 Button 列表（超出面板高度会截断末尾「彩蛋」项）。
 * - 新增：
 *   1) 「全部」下方固定「彩蛋/残篇」筛选；阵营列表可滚动。
 *   2) 节点/详情/阵营滚动条支持鼠标拖拽。
 * - 修改：
 *   1) 阵营筛选改为自绘列表 + factionScroll，确保 100 条彩蛋档案可进入。
 * - 用途：
 *   1) 帮助维护者快速理解文件职责、变更背景与风险点。
 *
 * 【段内说明】
 * - 复杂方法补充“干什么 / 边界 / 线程侧”精简中文注释。
 */
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
/** 中文说明：该处说明已按当前代码行为整理。*/
/** 【变更记录 #1】2026-10-01 00:44:40（修订123）：删除无；新增/修改：卷轴增加服务端正式经历分页，旧收藏保留独立切换；正式页不使用滚轮；用途：个人交流、团队决定及额外收藏分开，保留真实记录。 */
/** 【变更记录 #2】2026-10-01 01:54:14（修订127）：删除：被替代的旧分支；新增/修改：三栏目录保留，正文及完整触发条件改翻页；底部进度避让切换按钮，与手机同源分类说明；用途：个人收藏与正式资格分离，保留历史记录。 */
/** 【变更记录 #3】2026-10-01 01:59:30（修订127）：删除：被替代的旧分支；新增/修改：卷轴目录和数量读取此次打开的服务端本人快照，调试与复活后不显示过期进度；用途：个人收藏与正式资格分离，保留历史记录。 */
/** 【变更记录 #4】2026-10-01 22:47:35（第4次备注 · 内测5修订155）：删除玩家展示中的旧电压及开发说明；新增现行正文投影或对应回归；修改仅限呈现与检索，不改变进度、回执、触发条件或权限；用途：统一发布版玩家文案，历史备注保留。 */
/** 【变更记录 #5】2026-11-04 06:08:10（第5次备注 · 内测5修订196）：删除64正式收藏列表的旧标题投影；新增共享迁移标题入口；修改仅当前收藏列表，锁定项与终审正文不变；用途：列表与详情显示同一获准新版档案。 */
public class Hk3NarrativeCodexScreen extends com.sirin.hk3gtl.client.gui.Hk3FittedScreen {

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
    private int detailPage;
    private net.minecraft.client.gui.components.Button detailPrev,detailNext;
    private String progressBody="";
    private java.util.Set<String> unlockedSnapshot;
    private boolean formal=true;
    private int progressPage;
    private final List<net.minecraft.util.FormattedCharSequence> progressLines=new ArrayList<>();
    public static void openProgress(net.minecraft.nbt.CompoundTag view){
        var mc=Minecraft.getInstance();var screen=new Hk3NarrativeCodexScreen();
        screen.progressBody=view.getString("Body");
        if(view.contains("Unlocked",net.minecraft.nbt.Tag.TAG_LIST)){
            screen.unlockedSnapshot=new java.util.HashSet<>();
            for(var tag:view.getList("Unlocked",net.minecraft.nbt.Tag.TAG_STRING))screen.unlockedSnapshot.add(tag.getAsString());
        }
        mc.setScreen(screen);
    }
    private ScrollTarget draggingScroll = ScrollTarget.NONE;
    private int dragScrollAnchor;
    private double dragMouseAnchor;

    public Hk3NarrativeCodexScreen() {
        super(Component.literal("文明档案卷轴"), 444, 344);
        buildFactionFilters();
        applyFactionFilter(null);
    }

    public static void open(Player player) {
        Minecraft mc = Minecraft.getInstance();
        if (player == null) return;
        mc.execute(() -> mc.setScreen(new Hk3NarrativeCodexScreen()));
    }

    @Override
    protected void initFitted() {
        guiWidth = Math.min(GUI_WIDTH, Math.max(240, width - 12));
        guiHeight = Math.min(GUI_HEIGHT, Math.max(160, height - 12));
        guiLeft = (width - guiWidth) / 2;
        guiTop = (height - guiHeight) / 2;
        contentTop = guiTop + PADDING;
        contentHeight = guiHeight - BOTTOM_HEIGHT - PADDING * 2;
        detailWidth = guiWidth - LEFT_WIDTH - MID_WIDTH - PADDING * 4;
        clearWidgets();
        addRenderableWidget(net.minecraft.client.gui.components.Button.builder(Component.literal(formal?"档案与收藏":"正式经历"),b->{formal=!formal;initFitted();}).bounds(guiLeft+guiWidth-102,guiTop+guiHeight-23,96,18).build());
        if(!formal){
            int dx=guiLeft+PADDING*3+LEFT_WIDTH+MID_WIDTH;
            detailPrev=addRenderableWidget(net.minecraft.client.gui.components.Button.builder(Component.literal("上一页"),b->{detailPage=Math.max(0,detailPage-1);}).bounds(dx+6,contentTop+contentHeight-24,60,18).build());
            detailNext=addRenderableWidget(net.minecraft.client.gui.components.Button.builder(Component.literal("下一页"),b->{detailPage=Math.min(detailPages()-1,detailPage+1);}).bounds(dx+detailWidth-66,contentTop+contentHeight-24,60,18).build());
        }
        if(formal){
            progressLines.clear();
            for(String line:progressBody.split("\n",-1))if(line.isEmpty())progressLines.add(net.minecraft.util.FormattedCharSequence.EMPTY);else progressLines.addAll(font.split(Component.literal(line),guiWidth-28));
            int count=Math.max(1,(progressLines.size()+19)/20);progressPage=Math.max(0,Math.min(progressPage,count-1));
            addRenderableWidget(net.minecraft.client.gui.components.Button.builder(Component.literal("上一页"),b->{progressPage--;initFitted();}).bounds(guiLeft+8,guiTop+guiHeight-23,60,18).build()).active=progressPage>0;
            addRenderableWidget(net.minecraft.client.gui.components.Button.builder(Component.literal("下一页"),b->{progressPage++;initFitted();}).bounds(guiLeft+72,guiTop+guiHeight-23,60,18).build()).active=progressPage+1<count;
        }
    }

    @Override
    public void renderFitted(GuiGraphics gui, int mouseX, int mouseY, float partialTick) {
        renderBackground(gui);
        gui.fill(0, 0, width, height, BG_ROOT);

        drawPanel(gui, guiLeft, guiTop, guiWidth, guiHeight, BG_PANEL, BORDER);
        if(formal){
            gui.drawString(font,"本人经历",guiLeft+12,guiTop+10,TEXT_TITLE,false);
            for(int i=0;i<20&&progressPage*20+i<progressLines.size();i++)gui.drawString(font,progressLines.get(progressPage*20+i),guiLeft+12,guiTop+32+i*12,TEXT_NORMAL,false);
            gui.drawString(font,"第 "+(progressPage+1)+" / "+Math.max(1,(progressLines.size()+19)/20)+" 页",guiLeft+145,guiTop+guiHeight-18,TEXT_DIM,false);
            super.renderFitted(gui,mouseX,mouseY,partialTick);return;
        }
        drawFactionPanel(gui, mouseX, mouseY);
        drawNodePanel(gui, mouseX, mouseY);
        drawDetailPanel(gui);
        drawBottomProgress(gui);

        super.renderFitted(gui, mouseX, mouseY, partialTick);
    }

    @Override
    public boolean clickFitted(double mouseX, double mouseY, int button) {
        if (formal) return super.clickFitted(mouseX,mouseY,button);
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
                    detailPage = 0;
                    return true;
                }
            }
        }
        return super.clickFitted(mouseX, mouseY, button);
    }

    @Override
    public boolean releaseFitted(double mouseX, double mouseY, int button) {
        if (button == 0 && draggingScroll != ScrollTarget.NONE) {
            draggingScroll = ScrollTarget.NONE;
            return true;
        }
        return super.releaseFitted(mouseX, mouseY, button);
    }

    @Override
    public boolean dragFitted(double mouseX, double mouseY, int button, double dragX, double dragY) {
        if (button == 0 && draggingScroll != ScrollTarget.NONE) {
            applyScrollDrag(mouseY);
            return true;
        }
        return super.dragFitted(mouseX, mouseY, button, dragX, dragY);
    }

    @Override
    public boolean scrollFitted(double mouseX, double mouseY, double delta) {
        if (formal) return true;
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
        if (isInsideDetailPanel(mouseX, mouseY)) return true;
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
        detailPage = 0;
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
            String title = unlocked ? com.sirin.hk3gtl.common.narrative.Hk3CollectionRecords.title(node,key->I18n.get(key)) : LOCKED_PLACEHOLDER;
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

        detailPrev.active=false;detailNext.active=false;
        if (!isNodeUnlocked(selectedNode)) {
            gui.drawString(font, "该节点尚未解锁", x + 6, y + 8, TEXT_LOCKED, false);
            return;
        }

        int textX=x+6,textWidth=detailWidth-12;
        gui.drawString(font,trimToWidth(com.sirin.hk3gtl.common.narrative.Hk3CollectionRecords.title(selectedNode,key->I18n.get(key)),textWidth),textX,y+8,TEXT_TITLE,false);
        List<String> lines=detailLines(selectedNode,textWidth);
        int visible=detailVisibleLines(),pages=detailPages();detailPage=Mth.clamp(detailPage,0,pages-1);
        detailPrev.active=detailPage>0;detailNext.active=detailPage+1<pages;
        for(int i=0;i<visible&&detailPage*visible+i<lines.size();i++)
            gui.drawString(font,lines.get(detailPage*visible+i),textX,y+26+i*DETAIL_LINE_HEIGHT,TEXT_NORMAL,false);
        gui.drawString(font,"第 "+(detailPage+1)+" / "+pages+" 页",textX,y+contentHeight-38,TEXT_DIM,false);
    }
    private int detailVisibleLines(){return Math.max(1,(contentHeight-70)/DETAIL_LINE_HEIGHT);}
    private int detailPages(){
        if(selectedNode==null||!isNodeUnlocked(selectedNode))return 1;
        return Math.max(1,(detailLines(selectedNode,detailWidth-12).size()+detailVisibleLines()-1)/detailVisibleLines());
    }

    private void drawBottomProgress(GuiGraphics gui) {
        int x = guiLeft + PADDING;
        int y = guiTop + guiHeight - BOTTOM_HEIGHT - PADDING + 2;
        int w = guiWidth - PADDING * 2 - 102;
        int h = BOTTOM_HEIGHT - 4;

        drawPanel(gui, x, y, w, h, 0xD010141B, BORDER);

        Player player = Minecraft.getInstance().player;
        int total = Hk3NarrativeNodes.totalCount();
        int unlocked = (int)Hk3NarrativeNodes.all().stream().filter(this::isNodeUnlocked).count();
        int fillWidth = total <= 0 ? 0 : (int) ((w - 2) * (unlocked / (double) total));
        gui.fill(x + 1, y + 1, x + 1 + fillWidth, y + h - 1, 0xA036B7D9);

        String progress = "已收录 " + unlocked + "/" + total + " · 非终审资格";
        gui.drawString(font, progress, x + 4, y + 4, 0xFFFFFFFF, false);
    }

    private boolean isNodeUnlocked(Hk3NarrativeNode node) {
        Player player = Minecraft.getInstance().player;
        return unlockedSnapshot!=null?unlockedSnapshot.contains(node.id()):player != null && Hk3NarrativeLog.isUnlocked(player, node.id());
    }

    private List<String> detailLines(Hk3NarrativeNode node, int width) {
        List<String> out = new ArrayList<>();
        String body=com.sirin.hk3gtl.common.narrative.Hk3CollectionRecords.body(node,key->I18n.get(key));
        if(com.sirin.hk3gtl.common.narrative.Hk3LegacyArchiveMigration.all().containsKey(node.unlockEventId()))body="仅回看；本次阅读不取得正式资格。正式全文请从手机通知进入。\n\n"+body;
        for(String paragraph:body.split("\\n",-1))out.addAll(wrapParagraph(paragraph,width));
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
        NONE, FACTION, NODE
    }

    private ScrollTarget scrollTargetAt(double mouseX, double mouseY) {
        if (isOnScrollbar(mouseX, mouseY, ScrollTarget.FACTION)) {
            return ScrollTarget.FACTION;
        }
        if (isOnScrollbar(mouseX, mouseY, ScrollTarget.NODE)) {
            return ScrollTarget.NODE;
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
            default -> null;
        };
    }

    private record ScrollMetrics(int trackX, int trackY, int trackH, int totalRows, int visibleRows, int scroll) {}

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
