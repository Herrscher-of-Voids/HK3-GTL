package com.sirin.hk3gtl.mixin.enhanced.client;

import com.gtl.enhancedcore.common.world.plot.CampusMapImage;
import com.gtl.enhancedcore.common.world.plot.PlannedCampus;
import com.gtl.enhancedcore.common.world.plot.PlotSettings;
import com.sirin.hk3gtl.common.campus.Hk3CampusMapColors;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Pseudo;
import org.spongepowered.asm.mixin.Unique;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.ModifyVariable;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

@Pseudo
@Mixin(value = CampusMapImage.class, remap = false)
public abstract class Hk3CampusMapImageMixin implements Hk3CampusMapColors.ScaledImage {
    @Unique private int hk3gtl$scale = 1;

    @Inject(method = "capture", at = @At("HEAD"), cancellable = true)
    private static void hk3gtl$map(PlotSettings settings, PlannedCampus.Bounds bounds,
                                  CallbackInfoReturnable<CampusMapImage> cir) {
        int scale = Math.max(1, (Math.max(bounds.width(), bounds.depth()) + 4095) / 4096);
        var sampler = Hk3CampusMapColors.sampler(settings);
        var image = CampusMapImage.sample(0, 0, (bounds.width() + scale - 1) / scale,
                (bounds.depth() + scale - 1) / scale,
                (x, z) -> sampler.applyAsInt(bounds.minX() + x * scale, bounds.minZ() + z * scale));
        ((Hk3CampusMapColors.ScaledImage) (Object) image).hk3gtl$sampleScale(scale);
        cir.setReturnValue(image);
    }

    @Override
    public void hk3gtl$sampleScale(int scale) {
        hk3gtl$scale = scale;
    }

    @ModifyVariable(method = "levelFor", at = @At("HEAD"), argsOnly = true)
    private double hk3gtl$level(double blocksPerPixel) {
        return blocksPerPixel / hk3gtl$scale;
    }
}
