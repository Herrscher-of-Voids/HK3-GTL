package com.sirin.hk3gtl.mixin.enhanced;

import com.gtl.enhancedcore.common.world.plot.PlotLayout;
import com.gtl.enhancedcore.common.world.plot.PlotSettings;
import com.sirin.hk3gtl.common.campus.Hk3EnhancedCampusBridge;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Pseudo;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

@Pseudo
@Mixin(value = PlotLayout.class, remap = false)
public abstract class Hk3CampusTerrainMixin {
    @Inject(method = "blockIdAt", at = @At("HEAD"), cancellable = true)
    private static void hk3gtl$foundation(PlotSettings settings, int x, int y, int z, CallbackInfoReturnable<String> cir) {
        var block = Hk3EnhancedCampusBridge.expansion(settings).blockAt(x, y, z);
        if (block != null) cir.setReturnValue(block);
    }
}
