package com.sirin.hk3gtl.common.campus;

import com.gtl.enhancedcore.common.world.plot.CampusLandscape;
import com.gtl.enhancedcore.common.world.plot.CampusPresetRegistry;
import com.gtl.enhancedcore.common.world.plot.CompactCampusLandscape;
import com.gtl.enhancedcore.common.world.plot.DenseCampusLandscape;
import com.gtl.enhancedcore.common.world.plot.PlotSettings;

import java.util.TreeMap;

public record Hk3CampusStyle(String identity, String floor, String road, String border, String foundation,
                             String accent, String column, String leaves, String light, String green,
                             Kind kind, String architectureResource) {
    public enum Kind { GRID, MODERN, PARK, COMPACT, DENSE, WOODLAND, FACTORY, PINK }

    public static Hk3CampusStyle of(PlotSettings settings) {
        return switch (settings.roadStyle()) {
            case CAMPUS_FACTORY -> file(settings, "quartz_works");
            case CAMPUS_FILE -> file(settings, settings.campusPresetId());
            case CAMPUS -> campus(settings, Kind.MODERN);
            case CAMPUS_PARK -> campus(settings, Kind.PARK);
            case CAMPUS_COMPACT -> campus(settings, Kind.COMPACT);
            case CAMPUS_DENSE -> campus(settings, Kind.DENSE);
            case CAMPUS_WOODLAND -> campus(settings, Kind.WOODLAND);
            default -> new Hk3CampusStyle(settings.toString(), settings.groundBlock(), settings.roadBlock(),
                    settings.borderBlock(), "minecraft:polished_andesite", settings.plotEdgeBlock(),
                    "minecraft:quartz_pillar[axis=y]", "minecraft:azalea_leaves[persistent=true]",
                    "minecraft:sea_lantern", settings.groundBlock(), Kind.GRID, null);
        };
    }

    private static Hk3CampusStyle file(PlotSettings settings, String id) {
        var definition = CampusPresetRegistry.get(id);
        var materials = definition.materials();
        return new Hk3CampusStyle(settings + ":" + new TreeMap<>(materials), materials.get("floor"),
                materials.get("road"), materials.get("quartz"), materials.get("dark"), materials.get("accent"),
                materials.get("column"), materials.get("leaves"), materials.get("light"), materials.get("green"),
                definition.id().equals("pink_dream_home_v1") ? Kind.PINK : Kind.FACTORY, definition.architectureResource());
    }

    private static Hk3CampusStyle campus(PlotSettings settings, Kind kind) {
        String leaves = switch (kind) {
            case MODERN, WOODLAND -> "minecraft:oak_leaves[persistent=true]";
            case DENSE -> "minecraft:birch_leaves[persistent=true]";
            default -> "minecraft:azalea_leaves[persistent=true]";
        };
        String floor = switch (kind) {
            case PARK, WOODLAND -> "minecraft:polished_andesite";
            case COMPACT -> "minecraft:smooth_stone";
            default -> "minecraft:light_gray_concrete";
        };
        String road = switch (kind) {
            case PARK, DENSE -> "minecraft:smooth_quartz";
            case COMPACT -> "minecraft:polished_andesite";
            case WOODLAND -> "minecraft:stone_bricks";
            default -> "minecraft:black_concrete";
        };
        return new Hk3CampusStyle(settings.toString(), floor, road,
                "minecraft:smooth_quartz", "minecraft:polished_andesite", "minecraft:cyan_concrete",
                "minecraft:quartz_pillar[axis=y]", leaves, "minecraft:sea_lantern",
                kind == Kind.MODERN ? "minecraft:green_concrete" : "minecraft:grass_block", kind, null);
    }

    public String originalFloor() {
        return switch (kind) {
            case GRID, FACTORY, PINK -> floor;
            default -> "minecraft:light_gray_concrete";
        };
    }

    public String paving(int x, int z, boolean road) {
        if (road) {
            if ((kind == Kind.MODERN || kind == Kind.FACTORY) && Math.floorMod(x + z, 12) < 2)
                return "minecraft:yellow_concrete";
            return this.road;
        }
        if (kind == Kind.GRID) return floor;
        return Math.floorMod(x, 16) == 0 || Math.floorMod(z, 16) == 0 ? foundation : floor;
    }

    public String[] lamp() {
        return switch (kind) {
            case DENSE, WOODLAND -> new String[]{border, "minecraft:polished_blackstone_brick_wall",
                    "minecraft:polished_blackstone_brick_wall", light, "minecraft:polished_andesite_slab[type=bottom]"};
            case PARK -> new String[]{border, "minecraft:stone_brick_wall[up=true]",
                    "minecraft:stone_brick_wall[up=true]", light, "minecraft:smooth_quartz_slab[type=bottom]"};
            case PINK -> new String[]{border, "minecraft:cherry_fence", "minecraft:cherry_fence",
                    "minecraft:cherry_fence", accent, light, "minecraft:smooth_quartz_slab[type=bottom]"};
            default -> new String[]{foundation, column, column, light, "minecraft:smooth_quartz_slab[type=bottom]"};
        };
    }

    public String planterFlower() {
        return switch (kind) {
            case PINK -> "minecraft:pink_tulip";
            case DENSE -> "minecraft:allium";
            case WOODLAND -> "minecraft:fern";
            default -> "minecraft:oxeye_daisy";
        };
    }

    public int landscapeRadius() {
        return switch (kind) {
            case COMPACT -> CompactCampusLandscape.radius();
            case DENSE -> DenseCampusLandscape.radius();
            case PARK, WOODLAND -> CampusLandscape.radius();
            default -> 0;
        };
    }

    public int landscapeHeight() {
        return switch (kind) {
            case COMPACT -> CompactCampusLandscape.height();
            case DENSE -> DenseCampusLandscape.height();
            case PARK, WOODLAND -> CampusLandscape.height();
            default -> 0;
        };
    }

    public String landscapeSurface(int x, int z, int theme) {
        return switch (kind) {
            case COMPACT -> CompactCampusLandscape.surface(x, z, theme);
            case DENSE -> DenseCampusLandscape.surface(x, z, theme);
            case PARK, WOODLAND -> CampusLandscape.surface(x, z, theme);
            default -> null;
        };
    }

    public String landscapeFoundation(int x, int y, int z, int theme) {
        return switch (kind) {
            case COMPACT -> CompactCampusLandscape.foundation(x, y, z, theme);
            case DENSE -> DenseCampusLandscape.foundation(x, y, z, theme);
            case PARK, WOODLAND -> CampusLandscape.foundation(x, y, z, theme);
            default -> null;
        };
    }

    public String landscapeAbove(int x, int y, int z, int theme) {
        return switch (kind) {
            case COMPACT -> CompactCampusLandscape.above(x, y, z, theme);
            case DENSE -> DenseCampusLandscape.above(x, y, z, theme);
            case PARK, WOODLAND -> CampusLandscape.above(x, y, z, theme);
            default -> null;
        };
    }
}
