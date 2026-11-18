package com.sirin.hk3gtl.mixin.enhanced;

import com.gtl.enhancedcore.common.world.campus.CampusPlanAccess;
import com.gtl.enhancedcore.common.world.plot.PlotSettings;
import com.sirin.hk3gtl.common.campus.Hk3CampusLayoutVersion;
import com.sirin.hk3gtl.common.campus.Hk3EnhancedCampusBridge;
import com.sirin.hk3gtl.common.constants.Hk3ValuesImpl;
import org.spongepowered.asm.mixin.Final;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Mutable;
import org.spongepowered.asm.mixin.Pseudo;
import org.spongepowered.asm.mixin.Shadow;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.Redirect;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

import java.util.ArrayList;
import java.util.List;

@Pseudo
@Mixin(value = CampusPlanAccess.class, remap = false)
public abstract class Hk3CampusPlanMixin {
    @Shadow @Final @Mutable public static List<String> PLANNING_TIERS;

    @Inject(method = "<clinit>", at = @At("RETURN"))
    private static void hk3gtl$tiers(CallbackInfo ci) {
        var tiers = new ArrayList<>(PLANNING_TIERS);
        for (int tier = 15; tier <= 30; tier++) tiers.add(Hk3ValuesImpl.getVN(tier));
        PLANNING_TIERS = List.copyOf(tiers);
    }

    @Redirect(method = {"of", "layoutIdentity"}, at = @At(value = "INVOKE",
            target = "Lcom/gtl/enhancedcore/common/world/plot/PlotSettings;campusKey()Ljava/lang/String;"))
    private static String hk3gtl$versionedKey(PlotSettings settings) {
        return settings.campusKey() + ":hk3gtl-layout-v" + Hk3CampusLayoutVersion.get(settings);
    }

    @Inject(method = "of", at = @At("HEAD"), cancellable = true)
    private static void hk3gtl$grid(PlotSettings settings, CallbackInfoReturnable<CampusPlanAccess.Plan> cir) {
        if (!settings.isCampus()) cir.setReturnValue(Hk3EnhancedCampusBridge.extend(settings, null));
    }

    @Inject(method = "of", at = @At("RETURN"), cancellable = true)
    private static void hk3gtl$annex(PlotSettings settings, CallbackInfoReturnable<CampusPlanAccess.Plan> cir) {
        if (settings.isCampus()) cir.setReturnValue(Hk3EnhancedCampusBridge.extend(settings, cir.getReturnValue()));
    }
}
