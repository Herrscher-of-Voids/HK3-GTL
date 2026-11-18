package com.sirin.hk3gtl.mixin.enhanced;

import com.gtl.enhancedcore.common.world.plot.PlotSettings;
import com.sirin.hk3gtl.common.campus.Hk3CampusLayoutVersion;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Pseudo;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Redirect;

@Pseudo
@Mixin(targets = "com.gtl.enhancedcore.common.world.campus.CampusTeleportNetwork$Open", remap = false)
public abstract class Hk3CampusOpenVersionMixin {
    @Redirect(method = "encode", at = @At(value = "INVOKE", target =
            "Lcom/gtl/enhancedcore/common/world/plot/PlotPresetShare;encode(Lcom/gtl/enhancedcore/common/world/plot/PlotSettings;)Ljava/lang/String;"))
    private static String hk3gtl$encode(PlotSettings settings) {
        return Hk3CampusLayoutVersion.encodeShare(settings);
    }

    @Redirect(method = "decode", at = @At(value = "INVOKE", target =
            "Lcom/gtl/enhancedcore/common/world/plot/PlotPresetShare;decode(Ljava/lang/String;)Lcom/gtl/enhancedcore/common/world/plot/PlotSettings;"))
    private static PlotSettings hk3gtl$decode(String source) {
        return Hk3CampusLayoutVersion.decodeShare(source);
    }
}
