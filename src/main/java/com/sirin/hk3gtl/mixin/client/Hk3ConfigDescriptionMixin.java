package com.sirin.hk3gtl.mixin.client;

import dev.toma.configuration.client.widget.ConfigEntryWidget;
import dev.toma.configuration.config.value.ConfigValue;
import net.minecraft.network.chat.Component;
import org.spongepowered.asm.mixin.Final;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Shadow;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

import java.util.List;

@Mixin(value = ConfigEntryWidget.class, remap = false)
public abstract class Hk3ConfigDescriptionMixin {
    @Shadow @Final private List<Component> description;

    @Inject(method = "<init>", at = @At("RETURN"))
    private void hk3gtl$translateDescription(int x, int y, int width, int height, ConfigValue<?> value,
                                             String configId, CallbackInfo ci) {
        if (!configId.startsWith("hk3gtl-")) return;
        description.replaceAll(line -> {
            String key = line.getString();
            return key.startsWith("hk3gtl.config.") ? Component.translatable(key).setStyle(line.getStyle()) : line;
        });
    }
}
