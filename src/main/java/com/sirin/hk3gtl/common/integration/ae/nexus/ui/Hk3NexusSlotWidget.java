package com.sirin.hk3gtl.common.integration.ae.nexus.ui;

import com.lowdragmc.lowdraglib.gui.widget.SlotWidget;
import com.lowdragmc.lowdraglib.gui.widget.Widget;
import com.lowdragmc.lowdraglib.side.item.IItemTransfer;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.inventory.ClickType;
import net.minecraft.world.item.ItemStack;

public final class Hk3NexusSlotWidget extends SlotWidget {
    public Hk3NexusSlotWidget(IItemTransfer inventory, int slot, int x, int y) {
        super(inventory, slot, x, y);
    }

    @Override public boolean isEnabled() {
        for (Widget widget = this; widget != null; widget = widget.getParent())
            if (!widget.isVisible() || !widget.isActive()) return false;
        return true;
    }

    @Override public ItemStack slotClick(int button, ClickType clickType, Player player) {
        return isEnabled() ? super.slotClick(button, clickType, player) : ItemStack.EMPTY;
    }
}
