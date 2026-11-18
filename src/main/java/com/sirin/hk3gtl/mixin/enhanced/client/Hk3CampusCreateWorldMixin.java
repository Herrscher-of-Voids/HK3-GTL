package com.sirin.hk3gtl.mixin.enhanced.client;

import com.gtl.enhancedcore.client.plot.CreateWorldPlotScreen;
import com.gtl.enhancedcore.common.world.plot.PlotSettings;
import com.sirin.hk3gtl.common.campus.Hk3CampusLayoutVersion;
import net.minecraft.client.gui.screens.worldselection.WorldCreationUiState;
import org.spongepowered.asm.mixin.Final;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Pseudo;
import org.spongepowered.asm.mixin.Shadow;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

@Pseudo
@Mixin(value = CreateWorldPlotScreen.class, remap = false)
public abstract class Hk3CampusCreateWorldMixin {
    @Shadow @Final private WorldCreationUiState state;
    @Shadow private PlotSettings draft;

    @Inject(method = "resetInputs", at = @At("HEAD"))
    private void hk3gtl$currentLayout(CallbackInfo ci) {
        if (state != null) Hk3CampusLayoutVersion.set(draft, Hk3CampusLayoutVersion.CURRENT);
    }
}
