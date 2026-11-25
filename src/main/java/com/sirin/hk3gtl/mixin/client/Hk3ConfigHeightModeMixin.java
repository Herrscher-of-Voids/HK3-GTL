package com.sirin.hk3gtl.mixin.client;

import com.sirin.hk3gtl.common.dimension.height.Hk3HeightConfig.NewWorldMode;
import dev.toma.configuration.client.widget.EnumWidget;
import dev.toma.configuration.config.value.EnumValue;
import net.minecraft.client.gui.components.AbstractWidget;
import net.minecraft.network.chat.Component;
import org.spongepowered.asm.mixin.Final;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Shadow;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

import java.util.Locale;

@Mixin(value = EnumWidget.class, remap = false)
public abstract class Hk3ConfigHeightModeMixin extends AbstractWidget {
    @Shadow @Final private EnumValue<?> value;

    protected Hk3ConfigHeightModeMixin(int x, int y, int width, int height, Component message) {
        super(x, y, width, height, message);
    }

    @Inject(method = "updateText", at = @At("RETURN"))
    private void hk3gtl$translateHeightMode(CallbackInfo ci) {
        if (value.get() instanceof NewWorldMode mode) {
            setMessage(Component.translatable("hk3gtl.height.config.mode." + mode.name().toLowerCase(Locale.ROOT)));
        }
    }
}
