package com.sirin.hk3gtl.common.machine.wonder;

import com.gregtechceu.gtceu.api.gui.fancy.FancyMachineUIWidget;
import com.gregtechceu.gtceu.api.gui.fancy.IFancyUIProvider;
import com.gregtechceu.gtceu.api.machine.feature.IFancyUIMachine;
import com.lowdragmc.lowdraglib.gui.texture.IGuiTexture;
import com.lowdragmc.lowdraglib.gui.widget.Widget;
import net.minecraft.network.chat.Component;
import net.minecraft.world.entity.player.Player;

import java.util.function.Function;

public record Hk3WonderManagementPage(IFancyUIMachine machine, Function<Player, Widget> contents, String title)
        implements IFancyUIProvider {
    public Hk3WonderManagementPage(IFancyUIMachine machine, Function<Player, Widget> contents) {
        this(machine, contents, "hk3gtl.wonder.management");
    }
    @Override public Widget createMainPage(FancyMachineUIWidget widget) {
        return contents.apply(widget.getGui().entityPlayer);
    }

    @Override public IGuiTexture getTabIcon() {
        return machine.getTabIcon();
    }

    @Override public Component getTitle() {
        return Component.translatable(title);
    }
}
