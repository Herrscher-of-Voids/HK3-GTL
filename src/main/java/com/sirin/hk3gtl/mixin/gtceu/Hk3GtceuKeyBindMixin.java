package com.sirin.hk3gtl.mixin.gtceu;

import com.gregtechceu.gtceu.utils.input.KeyBind;
import net.minecraftforge.client.event.InputEvent;
import net.minecraft.client.Minecraft;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

/**
 * GTCEu can receive one final key event while the client is leaving a world.
 * LowDragLib's sendToServer assumes a live connection and otherwise throws an
 * NPE. Dropping that event is safe because no gameplay input can be applied
 * after the client connection has already been torn down.
 */
@Mixin(KeyBind.class)
public abstract class Hk3GtceuKeyBindMixin {
    @Inject(method = "onInputEvent", at = @At("HEAD"), cancellable = true, remap = false)
    private static void hk3gtl$skipDisconnectedInput(InputEvent.Key event, CallbackInfo ci) {
        Minecraft mc = Minecraft.getInstance();
        if (mc.getConnection() == null || mc.level == null || mc.player == null) {
            ci.cancel();
        }
    }
}
