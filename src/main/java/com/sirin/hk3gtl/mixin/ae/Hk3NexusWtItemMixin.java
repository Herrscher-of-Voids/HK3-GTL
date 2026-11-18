package com.sirin.hk3gtl.mixin.ae;

import appeng.api.networking.IGrid;
import appeng.items.tools.powered.WirelessTerminalItem;
import com.sirin.hk3gtl.common.integration.ae.nexus.network.Hk3NexusGrid;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.Level;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Pseudo;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

@Pseudo
@Mixin(targets = "de.mari_023.ae2wtlib.terminal.ItemWT", remap = false)
public abstract class Hk3NexusWtItemMixin {
    @Inject(method = "getLinkedGrid(Lnet/minecraft/world/item/ItemStack;Lnet/minecraft/world/level/Level;Lnet/minecraft/world/entity/player/Player;)Lappeng/api/networking/IGrid;",
            at = @At("HEAD"), cancellable = true)
    private void hk3gtl$nexusLink(ItemStack stack, Level level, Player player, CallbackInfoReturnable<IGrid> cir) {
        if (!(level instanceof ServerLevel serverLevel)) return;
        var position = ((WirelessTerminalItem) (Object) this).getLinkedPosition(stack);
        if (position == null) return;
        var nexus = Hk3NexusGrid.at(serverLevel.getServer(), position);
        if (nexus != null && nexus.getGrid().getEnergyService().isNetworkPowered())
            cir.setReturnValue(nexus.getGrid());
    }
}
