package com.sirin.hk3gtl.mixin.enhanced.client;

import com.gtl.enhancedcore.client.plot.CampusPlanScreen;
import com.gtl.enhancedcore.client.plot.CampusPlotSearch;
import com.gtl.enhancedcore.common.world.campus.CampusPlanAccess;
import com.gtl.enhancedcore.common.world.plot.PlotSettings;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.resources.ResourceLocation;
import org.spongepowered.asm.mixin.Final;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Pseudo;
import org.spongepowered.asm.mixin.Shadow;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

import java.util.List;
import java.util.Map;

@Pseudo
@Mixin(value = CampusPlanScreen.class, remap = false)
public abstract class Hk3CampusPlanScreenMixin {
    @Shadow @Final private PlotSettings settings;
    @Shadow @Final private CampusPlanAccess.Plan plan;
    @Shadow @Final private Map<Integer, CampusPlotSearch.Aliases> searchAliases;

    @Inject(method = "rebuildSearchAliases", at = @At("HEAD"), cancellable = true)
    private void hk3gtl$gridSearch(CallbackInfo ci) {
        if (settings.isCampus()) return;
        searchAliases.clear();
        for (var target : plan.targets()) {
            var plot = target.plot();
            var block = BuiltInRegistries.BLOCK.get(new ResourceLocation(plot.id()));
            searchAliases.put(target.index(), CampusPlotSearch.prepare(List.of(
                    plot.id(), block.getName().getString(), target.stage())));
        }
        ci.cancel();
    }
}
