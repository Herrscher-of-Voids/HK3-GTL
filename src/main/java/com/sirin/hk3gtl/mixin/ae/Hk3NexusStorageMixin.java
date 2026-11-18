package com.sirin.hk3gtl.mixin.ae;

import appeng.api.stacks.KeyCounter;
import appeng.api.storage.MEStorage;
import appeng.me.storage.NetworkStorage;
import com.llamalad7.mixinextras.injector.wrapoperation.Operation;
import com.llamalad7.mixinextras.injector.wrapoperation.WrapOperation;
import com.sirin.hk3gtl.common.integration.ae.nexus.network.Hk3NexusGrid;
import org.gtlcore.gtlcore.integration.ae2.storage.TerminalDisplayRead;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;

@Mixin(value = NetworkStorage.class, remap = false)
public abstract class Hk3NexusStorageMixin {
    @WrapOperation(method = "getAvailableStacks", at = @At(value = "INVOKE",
            target = "Lappeng/api/storage/MEStorage;getAvailableStacks(Lappeng/api/stacks/KeyCounter;)V"))
    private void hk3gtl$saturateNetworkStock(MEStorage inventory, KeyCounter output, Operation<Void> original) {
        if (TerminalDisplayRead.tracks(output) || !Hk3NexusGrid.contains((MEStorage) (Object) this)) {
            original.call(inventory, output);
            return;
        }
        var stacks = new KeyCounter();
        original.call(inventory, stacks);
        for (var entry : stacks) {
            var key = entry.getKey();
            long amount = entry.getLongValue(), current = output.get(key);
            output.set(key, current > Long.MAX_VALUE - amount ? Long.MAX_VALUE : current + amount);
        }
    }
}
