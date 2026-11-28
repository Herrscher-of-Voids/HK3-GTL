package com.sirin.hk3gtl.mixin.gtceu;

import com.gregtechceu.gtceu.api.gui.fancy.ConfiguratorPanel;
import com.gregtechceu.gtceu.api.gui.fancy.FancyMachineUIWidget;
import com.gregtechceu.gtceu.api.gui.fancy.IFancyUIProvider;
import com.gregtechceu.gtceu.api.machine.MetaMachine;
import com.sirin.hk3gtl.common.integration.ae.Hk3StockingCraftingCard;
import org.spongepowered.asm.mixin.Final;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Shadow;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

@Mixin(value = FancyMachineUIWidget.class, remap = false)
public abstract class Hk3StockingCardUIMixin {
    @Shadow @Final protected ConfiguratorPanel configuratorPanel;

    @Inject(method = "setupFancyUI(Lcom/gregtechceu/gtceu/api/gui/fancy/IFancyUIProvider;Z)V", at = @At(value = "INVOKE",
            target = "Lcom/gregtechceu/gtceu/api/gui/fancy/IFancyUIProvider;attachConfigurators(Lcom/gregtechceu/gtceu/api/gui/fancy/ConfiguratorPanel;)V",
            shift = At.Shift.AFTER))
    private void hk3gtl$showCraftingCard(IFancyUIProvider provider, boolean includeInventory, CallbackInfo ci) {
        if (provider instanceof MetaMachine machine)
            for (var trait : machine.getTraits())
                if (trait instanceof Hk3StockingCraftingCard card) configuratorPanel.attachConfigurators(card.configurator());
    }
}
