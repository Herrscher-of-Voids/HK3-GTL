package com.sirin.hk3gtl.mixin.ae;

import appeng.api.implementations.blockentities.IWirelessAccessPoint;
import appeng.api.networking.IGrid;
import appeng.api.networking.storage.IStorageService;
import appeng.helpers.WirelessTerminalMenuHost;
import appeng.items.tools.powered.WirelessTerminalItem;
import com.sirin.hk3gtl.common.integration.ae.nexus.network.Hk3NexusGrid;
import org.spongepowered.asm.mixin.Final;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Mutable;
import org.spongepowered.asm.mixin.Shadow;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

@Mixin(value = WirelessTerminalMenuHost.class, remap = false)
public abstract class Hk3NexusWirelessHostMixin {
    @Shadow @Final private WirelessTerminalItem terminal;
    @Shadow @Final @Mutable private IGrid targetGrid;
    @Shadow private IStorageService sg;
    @Shadow private IWirelessAccessPoint myWap;
    @Shadow private double currentDistanceFromGrid;

    @Inject(method = "rangeCheck", at = @At("HEAD"), cancellable = true)
    private void hk3gtl$nexusAccess(CallbackInfoReturnable<Boolean> cir) {
        var host = (WirelessTerminalMenuHost) (Object) this;
        if (host.isClientSide()) return;
        var position = terminal.getLinkedPosition(host.getItemStack());
        if (position != null) {
            var nexus = Hk3NexusGrid.at(host.getPlayer().getServer(), position);
            if (nexus != null && nexus.getGrid() != targetGrid) {
                targetGrid = nexus.getGrid();
                sg = targetGrid.getStorageService();
                myWap = null;
            }
        }
        if (targetGrid == null) return;
        for (var nexus : targetGrid.getMachines(Hk3NexusGrid.class)) {
            if (!nexus.isActive()) continue;
            myWap = nexus;
            currentDistanceFromGrid = 0;
            cir.setReturnValue(true);
            return;
        }
    }
}
