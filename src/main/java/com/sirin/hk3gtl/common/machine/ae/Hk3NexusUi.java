package com.sirin.hk3gtl.common.machine.ae;

import com.gregtechceu.gtceu.api.gui.UITemplate;
import com.lowdragmc.lowdraglib.gui.modular.ModularUI;
import com.lowdragmc.lowdraglib.gui.widget.*;
import com.sirin.hk3gtl.common.integration.ae.nexus.ui.Hk3NexusSlotWidget;
import com.sirin.hk3gtl.common.integration.ae.nexus.ui.Hk3NexusTheme;
import net.minecraft.network.chat.Component;
import net.minecraft.world.entity.player.Player;

final class Hk3NexusUi {
    private Hk3NexusUi() {}

    static ModularUI create(Hk3NexusMachine machine, Player player) {
        var tabs = new TabContainer(18, 36, 314, 242);
        var cells = new Cells(machine, player);
        var management = new WidgetGroup(0, 24, 314, 218);
        var console = machine.management().widget(player);
        console.setSelfPosition(7, 0);
        management.addWidget(console);
        tabs.addTab(tab(0, "hk3gtl.nexus.cells", 0xff43dce2), cells);
        tabs.addTab(tab(107, "hk3gtl.nexus.management", 0xffb58af0), management);
        tabs.addTab(tab(214, "hk3gtl.nexus.stock_readings", 0xffe8b65a), new Hk3NexusStockWidget(machine));
        return new ModularUI(350, 360, machine, player).background(Hk3NexusTheme.BACKGROUND)
                .widget(Hk3NexusTheme.label(70, 10, "block.hk3gtl.ae_nexus").setTextColor(Hk3NexusTheme.ACCENT))
                .widget(Hk3NexusTheme.label(70, 24, () -> Component.translatable(!machine.isFormed()
                        ? "hk3gtl.nexus.unformed" : machine.isOnline()
                        ? "hk3gtl.nexus.online" : "hk3gtl.nexus.unpowered").getString()))
                .widget(tabs)
                .widget(UITemplate.bindPlayerInventory(player.getInventory(), Hk3NexusTheme.SLOT, 94, 278, true));
    }

    private static TabButton tab(int x, String key, int accent) {
        return new TabButton(x, 0, 100, 20).setTexture(
                Hk3NexusTheme.tab(key, accent, false), Hk3NexusTheme.tab(key, accent, true));
    }

    private static final class Cells extends WidgetGroup {
        private int page;
        private String message = "";

        Cells(Hk3NexusMachine machine, Player player) {
            super(0, 24, 314, 210);
            var network = machine.network();
            var inventory = network.pager(() -> page, 54);
            addWidget(Hk3NexusTheme.label(8, 5, () -> Component.translatable("hk3gtl.nexus.cell_count",
                    network.cellCount(), page + 1).getString()));
            addWidget(button(8, 20, 60, "hk3gtl.nexus.previous", () -> page = Math.max(0, page - 1)));
            addWidget(button(246, 20, 60, "hk3gtl.nexus.next", () -> page++));
            for (int slot = 0; slot < 54; slot++)
                addWidget(new Hk3NexusSlotWidget(inventory, slot, 76 + slot % 9 * 18, 45 + slot / 9 * 18)
                        .setBackgroundTexture(Hk3NexusTheme.SLOT));
            addWidget(Hk3NexusTheme.label(8, 161, "hk3gtl.nexus.radius"));
            addWidget(button(162, 157, 144, "hk3gtl.nexus.bind", () -> {
                message = Component.translatable(network.getMainNode().isReady()
                        && network.bind(player.containerMenu.getCarried())
                        ? "hk3gtl.nexus.bound" : "hk3gtl.nexus.bind_failed").getString();
                player.containerMenu.broadcastChanges();
            }));
            addWidget(Hk3NexusTheme.label(8, 183, () -> message));
            addWidget(Hk3NexusTheme.label(8, 198, () -> Component.translatable("hk3gtl.nexus.connections",
                    network.wirelessConnections()).getString()));
        }
    }

    private static ButtonWidget button(int x, int y, int width, String key, Runnable action) {
        return new ButtonWidget(x, y, width, 18,
                Hk3NexusTheme.button(key),
                click -> { if (!click.isRemote) action.run(); });
    }
}
