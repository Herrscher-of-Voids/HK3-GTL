package com.sirin.hk3gtl.mixin.client;

import com.sirin.hk3gtl.client.compat.Hk3JeiLifecyclePlugin;
import com.sirin.hk3gtl.common.config.Hk3ConfigPages;
import dev.toma.configuration.client.screen.AbstractConfigScreen;
import org.spongepowered.asm.mixin.Final;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Shadow;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

@Mixin(value = AbstractConfigScreen.class, remap = false)
public abstract class Hk3ConfigScreenSaveMixin {
    @Shadow @Final protected String configId;

    @Inject(method = "saveConfig(Z)V", at = @At(value = "INVOKE", target = "Ljava/util/Optional;ifPresent(Ljava/util/function/Consumer;)V", shift = At.Shift.AFTER))
    private void hk3gtl$applySavedPage(boolean force, CallbackInfo ci) {
        switch (configId) {
            case "hk3gtl-farview" -> Hk3ConfigPages.FAR_VIEW.apply();
            case "hk3gtl-phone" -> Hk3ConfigPages.PHONE.apply();
            case "hk3gtl-height" -> Hk3ConfigPages.HEIGHT.apply();
            case "hk3gtl-research" -> Hk3JeiLifecyclePlugin.refreshResearchVisibility();
        }
    }
}
