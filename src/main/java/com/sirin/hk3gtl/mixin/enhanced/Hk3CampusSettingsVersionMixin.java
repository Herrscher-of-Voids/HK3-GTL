package com.sirin.hk3gtl.mixin.enhanced;

import com.gtl.enhancedcore.common.world.plot.PlotSettings;
import com.sirin.hk3gtl.common.campus.Hk3CampusCatalog;
import com.sirin.hk3gtl.common.campus.Hk3CampusLayoutVersion;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Pseudo;
import org.spongepowered.asm.mixin.Unique;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

@Pseudo
@Mixin(value = PlotSettings.class, remap = false)
public abstract class Hk3CampusSettingsVersionMixin implements Hk3CampusLayoutVersion {
    @Unique private int hk3gtl$layoutVersion = 7;

    @Override
    public int hk3gtl$layoutVersion() { return hk3gtl$layoutVersion; }

    @Override
    public void hk3gtl$layoutVersion(int version) { hk3gtl$layoutVersion = version; }

    @Inject(method = {"copy", "roadTheme", "withMachineFrames"}, at = @At("RETURN"))
    private void hk3gtl$copyVersion(CallbackInfoReturnable<PlotSettings> cir) {
        Hk3CampusLayoutVersion.set(cir.getReturnValue(), hk3gtl$layoutVersion);
    }

    @Inject(method = "campusPlotCount", at = @At("RETURN"), cancellable = true)
    private void hk3gtl$plotCount(CallbackInfoReturnable<Integer> cir) {
        int added = Hk3CampusCatalog.entries(hk3gtl$layoutVersion).size();
        cir.setReturnValue(cir.getReturnValue() + added);
    }
}
