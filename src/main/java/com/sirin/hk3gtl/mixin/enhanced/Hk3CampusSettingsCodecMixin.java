package com.sirin.hk3gtl.mixin.enhanced;

import com.gtl.enhancedcore.common.world.plot.PlotSettings;
import com.gtl.enhancedcore.common.world.plot.PlotSettingsCodec;
import com.mojang.serialization.Codec;
import com.sirin.hk3gtl.common.campus.Hk3CampusLayoutVersion;
import org.spongepowered.asm.mixin.Final;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Mutable;
import org.spongepowered.asm.mixin.Pseudo;
import org.spongepowered.asm.mixin.Shadow;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

@Pseudo
@Mixin(value = PlotSettingsCodec.class, remap = false)
public abstract class Hk3CampusSettingsCodecMixin {
    @Shadow @Final @Mutable public static Codec<PlotSettings> CODEC;

    @Inject(method = "<clinit>", at = @At("RETURN"))
    private static void hk3gtl$versionedCodec(CallbackInfo ci) {
        CODEC = Hk3CampusLayoutVersion.codec(CODEC);
    }
}
