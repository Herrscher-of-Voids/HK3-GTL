package com.sirin.hk3gtl.client.gui;

import com.lowdragmc.lowdraglib.gui.modular.ModularUI;
import com.lowdragmc.lowdraglib.gui.modular.ModularUIGuiContainer;

public final class Hk3NexusScreen extends ModularUIGuiContainer {
    public Hk3NexusScreen(ModularUI ui, int windowId) {
        super(ui, windowId);
    }

    @Override public void init() {
        var window = minecraft.getWindow();
        double preferred = window.calculateScale(minecraft.options.guiScale().get(), minecraft.isEnforceUnicode());
        double fit = Math.min((double) window.getWidth() / (modularUI.getWidth() + 16),
                (double) window.getHeight() / (modularUI.getHeight() + 16));
        window.setGuiScale(Math.min(preferred, fit));
        width = window.getGuiScaledWidth();
        height = window.getGuiScaledHeight();
        super.init();
    }

    @Override public void removed() {
        super.removed();
        var window = minecraft.getWindow();
        window.setGuiScale(window.calculateScale(minecraft.options.guiScale().get(), minecraft.isEnforceUnicode()));
    }
}
