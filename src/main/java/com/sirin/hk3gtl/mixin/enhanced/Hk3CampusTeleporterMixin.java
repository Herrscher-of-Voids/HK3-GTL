package com.sirin.hk3gtl.mixin.enhanced;

import com.gtl.enhancedcore.common.world.campus.CentralTeleporterBlockEntity;
import com.gtl.enhancedcore.common.world.plot.PlotSettings;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Pseudo;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Redirect;

@Pseudo
@Mixin(value = CentralTeleporterBlockEntity.class, remap = false)
public abstract class Hk3CampusTeleporterMixin {
    @Redirect(method = "bindToCurrentCampusIfUnbound", at = @At(value = "INVOKE",
            target = "Lcom/gtl/enhancedcore/common/world/plot/PlotSettings;isCampus()Z"))
    private boolean hk3gtl$gridBinding(PlotSettings settings) { return true; }
}
