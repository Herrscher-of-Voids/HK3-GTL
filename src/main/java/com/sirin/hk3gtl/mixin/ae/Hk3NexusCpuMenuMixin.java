package com.sirin.hk3gtl.mixin.ae;

import appeng.api.networking.crafting.ICraftingCPU;
import appeng.core.sync.packets.CraftingStatusPacket;
import appeng.api.config.CpuSelectionMode;
import appeng.menu.AEBaseMenu;
import appeng.menu.me.crafting.CraftingCPUMenu;
import com.sirin.hk3gtl.common.integration.ae.nexus.crafting.Hk3NexusCrafting;
import net.minecraft.world.entity.player.Inventory;
import net.minecraft.world.inventory.MenuType;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Shadow;
import org.spongepowered.asm.mixin.Unique;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

@Mixin(value = CraftingCPUMenu.class, remap = false, priority = 1200)
public abstract class Hk3NexusCpuMenuMixin extends AEBaseMenu {
    @Shadow protected abstract void setCPU(ICraftingCPU cpu);
    @Shadow public CpuSelectionMode schedulingMode;
    @Shadow public boolean cantStoreItems;
    @Unique private Hk3NexusCrafting.NexusCpu hk3gtl$nexus;
    @Unique private int hk3gtl$nexusStatusTicks;

    protected Hk3NexusCpuMenuMixin(MenuType<?> type, int id, Inventory inventory, Object host) {
        super(type, id, inventory, host);
    }

    @Inject(method = "setCPU", at = @At("HEAD"), cancellable = true)
    private void hk3gtl$selectNexus(ICraftingCPU cpu, CallbackInfo ci) {
        hk3gtl$nexusStatusTicks = 0;
        if (!(cpu instanceof Hk3NexusCrafting.NexusCpu nexus)) {
            hk3gtl$nexus = null;
            return;
        }
        setCPU(null);
        hk3gtl$nexus = nexus;
        schedulingMode = CpuSelectionMode.ANY;
        cantStoreItems = false;
        if (isServerSide()) sendPacketToClient(new CraftingStatusPacket(containerId, hk3gtl$nexus.nativeStatus()));
        ci.cancel();
    }

    @Inject(method = "broadcastChanges", at = @At("TAIL"), remap = true)
    private void hk3gtl$syncNexusStatus(CallbackInfo ci) {
        if (isServerSide() && hk3gtl$nexus != null && hk3gtl$nexusStatusTicks++ % 5 == 0)
            sendPacketToClient(new CraftingStatusPacket(containerId, hk3gtl$nexus.nativeStatus()));
    }

    @Inject(method = "cancelCrafting", at = @At("HEAD"), cancellable = true)
    private void hk3gtl$cancelNexus(CallbackInfo ci) {
        if (isServerSide() && hk3gtl$nexus != null) { hk3gtl$nexus.cancelJob(); ci.cancel(); }
    }
}
