package com.sirin.hk3gtl.mixin.ae;

import appeng.me.GridNode;
import com.sirin.hk3gtl.common.integration.ae.nexus.network.Hk3NexusGrid;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

@Mixin(value = GridNode.class, remap = false)
public abstract class Hk3NexusNodeReadyMixin {
    @Inject(method = "markReady", at = @At("TAIL"))
    private void hk3gtl$nexusDiscover(CallbackInfo ci) {
        Hk3NexusGrid.nodeReady((GridNode) (Object) this);
    }
}
