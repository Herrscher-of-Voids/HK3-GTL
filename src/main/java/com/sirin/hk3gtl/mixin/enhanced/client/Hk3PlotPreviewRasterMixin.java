package com.sirin.hk3gtl.mixin.enhanced.client;

import com.gtl.enhancedcore.common.world.campus.CampusPlanAccess;
import com.gtl.enhancedcore.common.world.plot.CampusPresetRegistry;
import com.gtl.enhancedcore.common.world.plot.PlotPreviewRaster;
import com.gtl.enhancedcore.common.world.plot.PlotSettings;
import com.sirin.hk3gtl.common.campus.Hk3CampusMapColors;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Pseudo;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

import java.util.concurrent.CancellationException;
import java.util.function.BooleanSupplier;

@Pseudo
@Mixin(value = PlotPreviewRaster.class, remap = false)
public abstract class Hk3PlotPreviewRasterMixin {
    @Inject(method = "campus", at = @At("HEAD"), cancellable = true)
    private static void hk3gtl$bounds(PlotSettings settings, int size, boolean grid, BooleanSupplier cancelled,
                                     CallbackInfoReturnable<int[]> cir) {
        var bounds = CampusPlanAccess.of(settings).bounds();
        var viewport = new PlotPreviewRaster.CampusViewport(bounds.minX(), bounds.minZ(), bounds.width(), bounds.depth());
        boolean scene = settings.roadStyle() == PlotSettings.RoadStyle.CAMPUS
                || settings.roadStyle() == PlotSettings.RoadStyle.CAMPUS_FILE
                && CampusPresetRegistry.get(settings.campusPresetId()).engine().equals("file_scene");
        cir.setReturnValue(PlotPreviewRaster.renderCampus(settings, size, size, viewport, scene ? 1 : 4, cancelled));
    }

    @Inject(method = "renderCampus(Lcom/gtl/enhancedcore/common/world/plot/PlotSettings;IILcom/gtl/enhancedcore/common/world/plot/PlotPreviewRaster$CampusViewport;ILjava/util/function/BooleanSupplier;)[I",
            at = @At("HEAD"), cancellable = true)
    private static void hk3gtl$raster(PlotSettings settings, int width, int height,
                                     PlotPreviewRaster.CampusViewport viewport, int quality, BooleanSupplier cancelled,
                                     CallbackInfoReturnable<int[]> cir) {
        var sampler = Hk3CampusMapColors.sampler(settings);
        var pixels = new int[width * height];
        for (int row = 0; row < height; row++) {
            if (cancelled.getAsBoolean()) throw new CancellationException("园区预览请求已取消");
            for (int column = 0; column < width; column++) {
                int red = 0, green = 0, blue = 0;
                for (int z = 0; z < quality; z++) for (int x = 0; x < quality; x++) {
                    int worldX = (int) Math.floor(viewport.minX() + (column + (x + 0.5) / quality) * viewport.width() / width);
                    int worldZ = (int) Math.floor(viewport.minZ() + (row + (z + 0.5) / quality) * viewport.depth() / height);
                    int color = sampler.applyAsInt(worldX, worldZ);
                    red += color >> 16 & 255; green += color >> 8 & 255; blue += color & 255;
                }
                int samples = quality * quality;
                pixels[row * width + column] = 0xFF000000 | red / samples << 16 | green / samples << 8 | blue / samples;
            }
        }
        cir.setReturnValue(pixels);
    }
}
