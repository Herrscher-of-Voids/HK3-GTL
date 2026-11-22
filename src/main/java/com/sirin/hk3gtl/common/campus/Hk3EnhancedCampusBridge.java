package com.sirin.hk3gtl.common.campus;

import com.gtl.enhancedcore.common.world.campus.CampusDeviceBlocks;
import com.gtl.enhancedcore.common.world.campus.CampusPlanAccess;
import com.gtl.enhancedcore.common.world.campus.VirtualMarkerBlockEntity;
import com.gtl.enhancedcore.common.world.plot.PlannedCampus;
import com.gtl.enhancedcore.common.world.plot.PlotSettings;
import com.sirin.hk3gtl.common.constants.Hk3ValuesImpl;
import com.sirin.hk3gtl.mixin.enhanced.Hk3CampusMaterialAccess;
import net.minecraft.core.BlockPos;
import net.minecraft.world.level.block.EntityBlock;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.chunk.ChunkAccess;

import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.ConcurrentHashMap;

/** 保留原园区与传送索引，附区仅生成主控占位标记。 */
public final class Hk3EnhancedCampusBridge {
    private record Campus(Hk3CampusExpansion.Plan annex, CampusPlanAccess.Plan plan) {}
    private static final java.util.concurrent.ConcurrentMap<Hk3CampusLayoutVersion.Key, Campus> PLANS =
            com.google.common.cache.CacheBuilder.newBuilder().maximumSize(8).<Hk3CampusLayoutVersion.Key, Campus>build().asMap();
    private static final ConcurrentHashMap<String, BlockState> MATERIALS = new ConcurrentHashMap<>();

    private Hk3EnhancedCampusBridge() {}


    public static BlockState blockState(PlotSettings settings, int x, int y, int z) {
        var block = expansion(settings).blockAt(x, y, z);
        return block == null ? null : material(block);
    }

    public static BlockState material(String block) {
        return MATERIALS.computeIfAbsent(block, Hk3CampusMaterialAccess::hk3gtl$resolve);
    }

    public static Hk3CampusExpansion.Plan expansion(PlotSettings settings) {
        return campus(settings).annex();
    }

    private static Campus campus(PlotSettings settings) {
        var key = Hk3CampusLayoutVersion.key(settings);
        var found = PLANS.get(key);
        if (found != null) return found;
        synchronized (PLANS) {
            CampusPlanAccess.of(settings);
            return PLANS.get(key);
        }
    }

    public static CampusPlanAccess.Plan extend(PlotSettings settings, CampusPlanAccess.Plan original) {
        synchronized (PLANS) {
        return PLANS.computeIfAbsent(Hk3CampusLayoutVersion.key(settings), key -> {
            var bounds = original == null ? new PlannedCampus.Bounds(-128, -128, 127, 127) : original.bounds();
            var annex = key.version() == 1
                    ? Hk3CampusLegacyLayout.plan(bounds.minX(), bounds.minZ(), bounds.maxX(), bounds.maxZ(), settings.surfaceY())
                    : Hk3CampusExpansion.plan(settings.campusKey() + ":" + key.version(), bounds.minX(), bounds.minZ(),
                            bounds.maxX(), bounds.maxZ(), settings.surfaceY(), key.version() >= 3 ? Hk3CampusStyle.of(settings) : null,
                            key.version(), original == null ? null : original.aeBounds());
            var plots = new ArrayList<PlannedCampus.Plot>(original == null ? List.of() : original.plots());
            var tiers = new ArrayList<Integer>(original == null ? List.of() : original.tiers());
            var targets = new ArrayList<CampusPlanAccess.Target>(original == null ? List.of() : original.targets());
            for (var added : annex.plots()) {
                var plot = external(added, plots.size());
                plots.add(plot);
                tiers.add(added.entry().tier());
                targets.add(new CampusPlanAccess.Target(targets.size(), CampusPlanAccess.Kind.MACHINE,
                        plot.bounds(), plot, plot.stage(), plot.slotIndex(), added.arrivalX(), added.arrivalZ()));
            }
            var overall = new PlannedCampus.Bounds(Math.min(bounds.minX(), annex.minX()), Math.min(bounds.minZ(), annex.minZ()),
                    Math.max(bounds.maxX(), annex.maxX()), Math.max(bounds.maxZ(), annex.maxZ()));
            com.mojang.logging.LogUtils.getLogger().info("HK3GTL园区扩展 {}：追加{}台，目录{}项，用地{}", settings.campusKey(), annex.plots().size(), targets.size(), overall);
            return new Campus(annex, new CampusPlanAccess.Plan(List.copyOf(plots), original == null ? List.of() : original.workshops(),
                    overall, original == null ? new PlannedCampus.Bounds(0, 0, 0, 0) : original.aeBounds(),
                    List.copyOf(tiers), List.copyOf(targets)));
        }).plan();
        }
    }

    private static PlannedCampus.Plot external(Hk3CampusExpansion.Plot plot, int index) {
        var entry = plot.entry();
        return new PlannedCampus.Plot(entry.machineId().toString(), Hk3ValuesImpl.getVN(entry.tier()), plot.structureMinX(), plot.structureMinZ(),
                entry.sizeX(), entry.sizeY(), entry.sizeZ(),
                plot.controllerX(), plot.controllerY() - plot.surfaceY(),
                plot.controllerZ(), "hk3gtl:campus/" + entry.key(), index, "precision",
                entry.definition().getBlock().getDescriptionId());
    }

    public static void populate(PlotSettings settings, ChunkAccess chunk) {
        var campus = campus(settings);
        var annex = campus.annex();
        var plan = campus.plan();
        var position = new BlockPos.MutableBlockPos();
        for (int x = chunk.getPos().getMinBlockX(); x <= chunk.getPos().getMaxBlockX(); x++) {
            for (int z = chunk.getPos().getMinBlockZ(); z <= chunk.getPos().getMaxBlockZ(); z++) {
                int top = annex.generationTopAt(x, z);
                for (int y = annex.bottomAt(x, z); y <= top; y++) {
                    var block = annex.blockAt(x, y, z);
                    if (block != null) chunk.setBlockState(position.set(x, y, z), material(block), false);
                }
            }
        }
        int start = plan.plots().size() - annex.plots().size();
        for (int i = 0; i < annex.plots().size(); i++) {
            var plot = annex.plots().get(i);
            var marker = new BlockPos(plot.controllerX(), plot.controllerY(), plot.controllerZ());
            if (inside(chunk, marker)) {
                chunk.setBlockState(marker, CampusDeviceBlocks.VIRTUAL_MARKER.get().defaultBlockState(), false);
                chunk.setBlockEntityNbt(VirtualMarkerBlockEntity.initialTag(marker, plan.plots().get(start + i)));
            }
        }
        if (!settings.isCampus()) {
            var teleporter = new BlockPos(0, settings.surfaceY() + 1, 0);
            if (inside(chunk, teleporter)) place(chunk, teleporter, CampusDeviceBlocks.CENTRAL_TELEPORTER.get().defaultBlockState());
        }
    }

    private static boolean inside(ChunkAccess chunk, BlockPos position) {
        return position.getX() >> 4 == chunk.getPos().x && position.getZ() >> 4 == chunk.getPos().z;
    }

    private static void place(ChunkAccess chunk, BlockPos position, BlockState state) {
        chunk.setBlockState(position, state, false);
        var entity = ((EntityBlock) state.getBlock()).newBlockEntity(position, state);
        chunk.setBlockEntityNbt(entity.saveWithFullMetadata());
    }
}
