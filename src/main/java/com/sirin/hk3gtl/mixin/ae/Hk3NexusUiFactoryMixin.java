package com.sirin.hk3gtl.mixin.ae;

import com.lowdragmc.lowdraglib.gui.factory.UIFactory;
import com.lowdragmc.lowdraglib.gui.modular.ModularUIGuiContainer;
import com.sirin.hk3gtl.client.gui.Hk3NexusScreen;
import com.sirin.hk3gtl.common.machine.ae.Hk3NexusMachine;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.ModifyVariable;

@Mixin(value = UIFactory.class, remap = false)
public abstract class Hk3NexusUiFactoryMixin {
    @ModifyVariable(method = "initClientUI", at = @At("STORE"), ordinal = 0)
    private ModularUIGuiContainer hk3gtl$fitNexus(ModularUIGuiContainer screen) {
        return screen.modularUI.holder instanceof Hk3NexusMachine
                ? new Hk3NexusScreen(screen.modularUI, screen.getMenu().containerId) : screen;
    }
}
