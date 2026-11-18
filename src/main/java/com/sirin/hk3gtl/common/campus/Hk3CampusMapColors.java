package com.sirin.hk3gtl.common.campus;

import com.gtl.enhancedcore.common.world.plot.CompactPlannedCampus;
import com.gtl.enhancedcore.common.world.plot.DensePlannedCampus;
import com.gtl.enhancedcore.common.world.plot.FactoryCampus;
import com.gtl.enhancedcore.common.world.plot.FileCampus;
import com.gtl.enhancedcore.common.world.plot.LegacyPlannedCampus;
import com.gtl.enhancedcore.common.world.plot.ParkPlannedCampus;
import com.gtl.enhancedcore.common.world.plot.PlannedCampus;
import com.gtl.enhancedcore.common.world.plot.PlotLayout;
import com.gtl.enhancedcore.common.world.plot.PlotSettings;
import com.sirin.hk3gtl.common.constants.Hk3ValuesImpl;
import it.unimi.dsi.fastutil.longs.Long2ObjectOpenHashMap;
import net.minecraft.core.BlockPos;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.level.EmptyBlockGetter;

import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.ConcurrentHashMap;
import java.util.function.IntBinaryOperator;

public final class Hk3CampusMapColors {
    private static final ConcurrentHashMap<String, Integer> MATERIAL_COLORS = new ConcurrentHashMap<>();

    public interface ScaledImage {
        void hk3gtl$sampleScale(int scale);
    }

    private Hk3CampusMapColors() {}

    public static IntBinaryOperator sampler(PlotSettings settings) {
        IntBinaryOperator original = switch (settings.roadStyle()) {
            case CAMPUS -> LegacyPlannedCampus::previewColorAt;
            case CAMPUS_PARK -> ParkPlannedCampus::previewColorAt;
            case CAMPUS_COMPACT -> CompactPlannedCampus::previewColorAt;
            case CAMPUS_DENSE -> DensePlannedCampus::previewColorAt;
            case CAMPUS_WOODLAND -> PlannedCampus::previewColorAt;
            case CAMPUS_FACTORY -> FactoryCampus::previewColorAt;
            case CAMPUS_FILE -> FileCampus.of(settings.campusPresetId())::previewColorAt;
            default -> grid(settings);
        };
        var expansion = Hk3EnhancedCampusBridge.expansion(settings);
        var cells = new Long2ObjectOpenHashMap<List<Hk3CampusExpansion.Plot>>();
        for (var plot : expansion.plots()) {
            for (int x = plot.minX() >> 7; x <= plot.maxX() >> 7; x++) {
                for (int z = plot.minZ() >> 7; z <= plot.maxZ() >> 7; z++) {
                    cells.computeIfAbsent(key(x, z), ignored -> new ArrayList<>()).add(plot);
                }
            }
        }
        return (x, z) -> {
            var plots = cells.get(key(x >> 7, z >> 7));
            if (plots != null) for (var plot : plots) {
                if (x < plot.structureMinX() || x > plot.structureMaxX()
                        || z < plot.structureMinZ() || z > plot.structureMaxZ()) continue;
                if (Math.abs(x - plot.controllerX()) <= 3 && Math.abs(z - plot.controllerZ()) <= 3)
                    return 0xFFFFFF;
                if (x == plot.structureMinX() || x == plot.structureMaxX()
                        || z == plot.structureMinZ() || z == plot.structureMaxZ())
                    return Hk3ValuesImpl.getVC(plot.entry().tier());
                break;
            }
            if (!expansion.terrainAt(x, z)) return original.applyAsInt(x, z);
            var block = expansion.blockAt(x, expansion.topAt(x, z), z);
            return MATERIAL_COLORS.computeIfAbsent(block, id -> Hk3EnhancedCampusBridge.material(id)
                    .getMapColor(EmptyBlockGetter.INSTANCE, BlockPos.ZERO).col);
        };
    }

    private static IntBinaryOperator grid(PlotSettings settings) {
        var blocks = List.of(settings.groundBlock(), settings.plotEdgeBlock(), settings.roadBlock(),
                settings.borderBlock(), settings.markerBlock(), settings.lineBlock());
        var colors = blocks.stream().mapToInt(id -> BuiltInRegistries.BLOCK.get(new ResourceLocation(id))
                .defaultBlockState().getMapColor(EmptyBlockGetter.INSTANCE, BlockPos.ZERO).col).toArray();
        return (x, z) -> colors[PlotLayout.surfaceAt(settings, x, z).ordinal()];
    }

    private static long key(int x, int z) {
        return (long) x << 32 | z & 0xFFFFFFFFL;
    }
}
