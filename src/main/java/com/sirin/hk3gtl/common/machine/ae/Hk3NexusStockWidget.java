package com.sirin.hk3gtl.common.machine.ae;

import appeng.api.stacks.AEFluidKey;
import appeng.api.stacks.AEKey;
import appeng.api.networking.security.IActionSource;
import com.lowdragmc.lowdraglib.gui.widget.ButtonWidget;
import com.lowdragmc.lowdraglib.gui.widget.TextFieldWidget;
import com.lowdragmc.lowdraglib.gui.widget.WidgetGroup;
import com.sirin.hk3gtl.common.integration.ae.Hk3InfiniteSources;
import com.sirin.hk3gtl.common.integration.ae.nexus.network.Hk3NexusStock;
import com.sirin.hk3gtl.common.integration.ae.nexus.ui.Hk3NexusTheme;
import net.minecraft.network.chat.Component;

import java.math.BigInteger;
import java.util.Comparator;
import java.util.List;
import java.util.Locale;
import java.util.Map;
import java.util.Set;

final class Hk3NexusStockWidget extends WidgetGroup {
    private final Hk3NexusMachine machine;
    private List<Map.Entry<AEKey, BigInteger>> stock = List.of();
    private Set<AEKey> infinite = Set.of();
    private String search = "";
    private int page;

    Hk3NexusStockWidget(Hk3NexusMachine machine) {
        super(0, 24, 314, 218);
        this.machine = machine;
        addWidget(Hk3NexusTheme.label(8, 5, "hk3gtl.nexus.stock_search"));
        addWidget(Hk3NexusTheme.field(new TextFieldWidget(54, 0, 252, 18, () -> search, value -> {
            search = value;
            page = 0;
        })).setMaxStringLength(128));
        for (int row = 0; row < 6; row++) {
            int index = row;
            addWidget(Hk3NexusTheme.label(8, 28 + row * 25, () -> name(index)));
            addWidget(Hk3NexusTheme.label(8, 39 + row * 25, () -> amount(index)));
        }
        addWidget(button(8, "hk3gtl.nexus.previous", () -> page = Math.max(0, page - 1)));
        addWidget(button(246, "hk3gtl.nexus.next", () -> page = Math.min(pages() - 1, page + 1)));
        addWidget(Hk3NexusTheme.label(79, 185, () -> Component.translatable(
                "hk3gtl.nexus.stock_page", page + 1, pages(), stock.size()).getString()));
    }

    @Override public void detectAndSendChanges() {
        String query = search.strip().toLowerCase(Locale.ROOT);
        boolean ready = machine.network().getMainNode().isReady();
        infinite = ready ? Hk3InfiniteSources.collect(machine.network().getGrid().getStorageService().getInventory(),
                IActionSource.ofMachine(machine.network())) : Set.of();
        stock = ready
                ? Hk3NexusStock.snapshot(machine.network().getGrid()).entrySet().stream()
                .filter(entry -> entry.getKey().getDisplayName().getString().toLowerCase(Locale.ROOT).contains(query)
                        || entry.getKey().getId().toString().contains(query))
                .sorted(Comparator.comparing(entry -> entry.getKey().getId().toString()))
                .toList() : List.of();
        page = Math.min(page, pages() - 1);
        super.detectAndSendChanges();
    }

    private int pages() { return Math.max(1, (stock.size() + 5) / 6); }

    private String name(int row) {
        int index = page * 6 + row;
        return index < stock.size() ? stock.get(index).getKey().getDisplayName().getString() : "";
    }

    private String amount(int row) {
        int index = page * 6 + row;
        if (index >= stock.size()) return "";
        var entry = stock.get(index);
        if (infinite.contains(entry.getKey())) return "∞";
        return entry.getValue().toString() + (entry.getKey() instanceof AEFluidKey ? " mB" : "");
    }

    private static ButtonWidget button(int x, String key, Runnable action) {
        return new ButtonWidget(x, 180, 60, 18,
                Hk3NexusTheme.button(key),
                click -> { if (!click.isRemote) action.run(); });
    }
}
