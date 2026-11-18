package com.sirin.hk3gtl.common.integration.ae.nexus.management;

import com.lowdragmc.lowdraglib.gui.util.ClickData;
import com.lowdragmc.lowdraglib.gui.widget.ButtonWidget;
import com.lowdragmc.lowdraglib.gui.widget.TextFieldWidget;
import com.lowdragmc.lowdraglib.gui.widget.WidgetGroup;
import com.sirin.hk3gtl.common.integration.ae.nexus.ui.Hk3NexusSlotWidget;
import com.sirin.hk3gtl.common.integration.ae.nexus.ui.Hk3NexusTheme;
import net.minecraft.network.FriendlyByteBuf;
import net.minecraft.world.entity.player.Player;

import java.util.ArrayList;
import java.util.List;
import java.util.function.Consumer;
import java.util.function.Supplier;

final class Hk3NexusManagementWidget extends WidgetGroup {
    private final Hk3NexusManagement management;
    private final List<WidgetGroup> panels = new ArrayList<>();
    private final Hk3NexusPatternInventory.PatternPage patternInventoryPage;
    private int patternPage;
    private long patternRevision = -1;
    private String inputSearch = "";
    private String outputSearch = "";

    Hk3NexusManagementWidget(Hk3NexusManagement management, Player player) {
        super(0, 0, 300, 218);
        this.management = management;
        patternInventoryPage = management.patterns().page(() -> patternPage, 54, () -> inputSearch, () -> outputSearch);
        addPanel("样板", this::patternPanel);
        addPanel("补货", panel -> panel.addWidget(new Hk3NexusRequestWidget(management, player)));
        showPanel(0);
    }

    @Override public void detectAndSendChanges() {
        long revision = management.patterns().revision();
        if (patternRevision != revision) {
            patternRevision = revision;
            writeUpdateInfo(100, patternInventoryPage::writeSearchData);
        }
        patternInventoryPage.refresh();
        super.detectAndSendChanges();
    }

    @Override public void readUpdateInfo(int id, FriendlyByteBuf buffer) {
        if (id == 100) {
            patternInventoryPage.readSearchData(buffer);
            writeClientAction(100, patternInventoryPage::writeFilter);
        } else super.readUpdateInfo(id, buffer);
    }

    @Override public void handleClientAction(int id, FriendlyByteBuf buffer) {
        if (id == 100 || id == 101) {
            if (id == 101) patternPage = 0;
            patternInventoryPage.readFilter(buffer);
        }
        else super.handleClientAction(id, buffer);
    }

    private void addPanel(String title, Consumer<WidgetGroup> build) {
        int index = panels.size();
        var panel = new WidgetGroup(0, 27, 300, 191);
        panels.add(panel);
        build.accept(panel);
        addWidget(panel);
        addWidget(button(index * 150, 0, 148, title, click -> showPanel(index)));
    }

    private void showPanel(int selected) {
        for (int index = 0; index < panels.size(); index++)
            panels.get(index).setVisible(index == selected).setActive(index == selected);
    }

    private void patternPanel(WidgetGroup panel) {
        panel.addWidget(Hk3NexusTheme.label(8, 0, () -> "样板：" + management.patterns().count()));
        panel.addWidget(Hk3NexusTheme.label(8, 22, "输入"));
        panel.addWidget(searchField(17, () -> inputSearch, value -> inputSearch = value));
        panel.addWidget(Hk3NexusTheme.label(8, 43, "输出"));
        panel.addWidget(searchField(38, () -> outputSearch, value -> outputSearch = value));
        for (int slot = 0; slot < 54; slot++)
            panel.addWidget(new Hk3NexusSlotWidget(patternInventoryPage, slot, 69 + slot % 9 * 18, 60 + slot / 9 * 18)
                    .setBackgroundTexture(Hk3NexusTheme.SLOT));
        panel.addWidget(button(8, 172, 56, "上一页", click -> {
            if (!click.isRemote) patternPage = Math.max(0, patternPage - 1);
        }));
        panel.addWidget(button(236, 172, 56, "下一页", click -> {
            if (!click.isRemote) patternPage++;
        }));
        panel.addWidget(Hk3NexusTheme.label(143, 177, () -> Integer.toString(patternPage + 1)));
    }

    private TextFieldWidget searchField(int y, Supplier<String> text, Consumer<String> changed) {
        var field = new TextFieldWidget(40, y, 252, 18, text, value -> {
            changed.accept(value);
            searchChanged();
        }) {
            @Override public boolean mouseClicked(double mouseX, double mouseY, int button) {
                if (button == 1 && isMouseOverElement(mouseX, mouseY)) {
                    super.mouseClicked(mouseX, mouseY, 0);
                    onTextChanged("");
                    return true;
                }
                return super.mouseClicked(mouseX, mouseY, button);
            }

            @Override public boolean keyPressed(int key, int scan, int modifiers) {
                if ((key == 257 || key == 335) && isFocus()) {
                    searchChanged();
                    return true;
                }
                return super.keyPressed(key, scan, modifiers);
            }
        };
        field.setClientSideWidget();
        field.setHoverTooltips("按名称搜索；右键清空");
        return Hk3NexusTheme.field(field).setMaxStringLength(128);
    }

    private void searchChanged() {
        patternPage = 0;
        if (isRemote()) writeClientAction(101, patternInventoryPage::writeFilter);
    }

    private static ButtonWidget button(int x, int y, int width, String label, Consumer<ClickData> action) {
        return new ButtonWidget(x, y, width, 18, Hk3NexusTheme.button(label), action);
    }

}
