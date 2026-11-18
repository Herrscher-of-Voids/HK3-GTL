package com.sirin.hk3gtl.common.campus;

import com.gtl.enhancedcore.common.world.plot.FactoryArchitecture;
import net.minecraft.core.Direction;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

/** 厂房依机器净空生成；巨构只保留外围框柱与低矮服务廊。 */
final class Hk3CampusArchitecture {
    private record Building(Hk3CampusExpansion.Plot plot, FactoryArchitecture.Hall hall,
                            boolean indoor, int clearHeight) {}
    private record Palette(String wall, String pillar, String glass, String roof, String trim, String accent) {}

    private final Hk3CampusStyle style;
    private final Palette palette;
    private final FactoryArchitecture.Renderer renderer;
    private final Map<Long, List<Building>> cells = new HashMap<>();

    Hk3CampusArchitecture(Hk3CampusExpansion.Plan plan, Hk3CampusStyle style) {
        this.style = style;
        palette = palette(style);
        renderer = style.kind() == Hk3CampusStyle.Kind.FACTORY
                ? FactoryArchitecture.forResource(style.architectureResource()) : null;
        int variant = 0;
        for (var plot : plan.plots()) {
            var entry = plot.entry();
            boolean indoor = Math.max(entry.sizeX(), entry.sizeZ()) <= 128 && entry.sizeY() <= 96;
            int clear = Math.max(20, entry.sizeY() + 4);
            var hall = renderer != null && indoor ? new FactoryArchitecture.Hall(entry.key(), "default", "HK3GTL",
                    plot.minX(), plot.minZ(), plot.maxX() - plot.minX() + 1, plot.maxZ() - plot.minZ() + 1,
                    clear, variant, false, "south") : null;
            var building = new Building(plot, hall, indoor, clear);
            variant++;
            for (int x = plot.minX() >> 7; x <= plot.maxX() >> 7; x++)
                for (int z = plot.minZ() >> 7; z <= plot.maxZ() >> 7; z++)
                    cells.computeIfAbsent(key(x, z), ignored -> new ArrayList<>()).add(building);
        }
    }

    String blockAt(int x, int y, int z) {
        var building = buildingAt(x, z);
        return building == null ? null : blockAt(building, x, y, z);
    }

    int topAt(int x, int z) {
        var building = buildingAt(x, z);
        if (building == null) return 0;
        var plot = building.plot();
        if (building.indoor()) {
            if (building.hall() != null) {
                int top = renderer.top(building.hall(), x, z);
                while (top > 0 && blockAt(building, x, top, z) == null) top--;
                return top;
            }
            return roofFootprint(plot, x, z) ? roofY(building, x, z) + (roofRim(plot, x, z) ? 1 : 0) : 0;
        }
        if (openAccess(plot, x, z)) return 0;
        if (frame(plot, x, z)) return plot.entry().sizeY() + 1;
        return gallery(plot, x, z) ? 8 : 0;
    }

    private String blockAt(Building building, int x, int y, int z) {
        var plot = building.plot();
        if (y < 0) return null;
        if (y == 0) {
            if (building.hall() != null) return renderer.surface(building.hall(), x, z);
            if (machine(plot, x, z)) return switch (style.kind()) {
                case WOODLAND, PARK, DENSE, MODERN -> "minecraft:light_gray_concrete";
                case COMPACT -> "minecraft:smooth_stone";
                case FACTORY -> Math.floorMod(x - plot.structureMinX(), 16) == 0
                        || Math.floorMod(z - plot.structureMinZ(), 16) == 0
                        ? "minecraft:smooth_stone" : "minecraft:polished_andesite";
                case PINK -> "minecraft:smooth_quartz";
                case GRID -> style.floor();
            };
            if (style.kind() == Hk3CampusStyle.Kind.PINK)
                return roofRim(plot, x, z) ? "minecraft:smooth_quartz" : "minecraft:pink_terracotta";
            if (building.indoor() || gallery(plot, x, z))
                return Math.floorMod(x - plot.minX(), 8) == 0 || Math.floorMod(z - plot.minZ(), 8) == 0
                        ? palette.trim() : style.floor();
            if (style.kind() == Hk3CampusStyle.Kind.FACTORY && !openAccess(plot, x, z)
                    && z == plot.minZ() + 6 && Math.floorMod(x - plot.minX(), 32) < 16)
                return "minecraft:water[level=0]";
            return null;
        }
        if (machine(plot, x, z) && y <= plot.entry().sizeY()) return null;
        if (openAccess(plot, x, z) && y <= Math.max(8, plot.controllerY() - plot.surfaceY() + 3)) return null;
        if (building.hall() != null) return renderer.above(building.hall(), x, y, z);
        if (!building.indoor()) return outdoor(plot, x, y, z);
        return workshop(building, x, y, z);
    }

    private String workshop(Building building, int x, int y, int z) {
        var plot = building.plot();
        int roof = roofY(building, x, z);
        if (roofFootprint(plot, x, z)) {
            if (y == roof) return roofMaterial(building, x, z);
            if (roofRim(plot, x, z) && y == roof + 1) return palette.trim();
        }
        int left = plot.minX() + 4, right = plot.maxX() - 4;
        int back = plot.minZ() + 4, front = plot.maxZ() - 4;
        if (x < left || x > right || z < back || z > front || y > roof) return null;
        boolean wallX = x == left || x == right, wallZ = z == back || z == front;
        if (!wallX && !wallZ) return null;
        int along = wallX ? z - back : x - left;
        if (y <= 2 || y >= building.clearHeight()) return palette.wall();
        if (Math.floorMod(along, 8) == 0 || wallX && wallZ) return palette.pillar();
        if (y == building.clearHeight() - 2) return palette.accent();
        return Math.floorMod(y, 5) == 0 ? palette.trim() : palette.glass();
    }

    private String outdoor(Hk3CampusExpansion.Plot plot, int x, int y, int z) {
        if (openAccess(plot, x, z)) return null;
        int top = plot.entry().sizeY() + 1;
        if (frame(plot, x, z)) {
            boolean corner = (x == plot.structureMinX() - 1 || x == plot.structureMaxX() + 1)
                    && (z == plot.structureMinZ() - 1 || z == plot.structureMaxZ() + 1);
            if (y == top || corner && y < top) return y == top ? palette.trim() : palette.pillar();
        }
        if (!gallery(plot, x, z) || y > 8) return null;
        if (y == 8) return palette.roof();
        int dx = Math.min(x - plot.minX(), plot.maxX() - x);
        int dz = Math.min(z - plot.minZ(), plot.maxZ() - z);
        boolean wall = dx == 1 || dx == 5 || dz == 1 || dz == 5;
        if (!wall) return null;
        if (y <= 2 || y == 7) return palette.wall();
        if (Math.floorMod(x - plot.minX() + z - plot.minZ(), 8) == 0) return palette.pillar();
        return y == 6 ? palette.accent() : palette.glass();
    }

    private boolean gallery(Hk3CampusExpansion.Plot plot, int x, int z) {
        if (machine(plot, x, z)) return false;
        int dx = Math.min(x - plot.minX(), plot.maxX() - x);
        int dz = Math.min(z - plot.minZ(), plot.maxZ() - z);
        return dx >= 1 && dz >= 1 && (dx <= 5 || dz <= 5);
    }

    private boolean openAccess(Hk3CampusExpansion.Plot plot, int x, int z) {
        if (Math.abs(x - plot.arrivalX()) <= 4 && z >= plot.structureMaxZ()) return true;
        if (Math.abs(x - plot.controllerX()) <= 4 && Math.abs(z - plot.controllerZ()) <= 4) return true;
        Direction front = plot.entry().front();
        if (front == Direction.WEST && x <= plot.controllerX() && Math.abs(z - plot.controllerZ()) <= 4) return true;
        if (front == Direction.EAST && x >= plot.controllerX() && Math.abs(z - plot.controllerZ()) <= 4) return true;
        if (front == Direction.NORTH && z <= plot.controllerZ() && Math.abs(x - plot.controllerX()) <= 4) return true;
        if (front == Direction.SOUTH && z >= plot.controllerZ() && Math.abs(x - plot.controllerX()) <= 4) return true;
        if (Math.max(plot.entry().sizeX(), plot.entry().sizeZ()) <= 128 && plot.entry().sizeY() <= 96) return false;
        return Math.abs(x - (plot.minX() + plot.maxX()) / 2) <= 4
                || Math.abs(z - (plot.minZ() + plot.maxZ()) / 2) <= 4;
    }

    private boolean frame(Hk3CampusExpansion.Plot plot, int x, int z) {
        int left = plot.structureMinX() - 1, right = plot.structureMaxX() + 1;
        int back = plot.structureMinZ() - 1, front = plot.structureMaxZ() + 1;
        return x >= left && x <= right && z >= back && z <= front
                && (x == left || x == right || z == back || z == front);
    }

    private boolean machine(Hk3CampusExpansion.Plot plot, int x, int z) {
        return x >= plot.structureMinX() && x <= plot.structureMaxX()
                && z >= plot.structureMinZ() && z <= plot.structureMaxZ();
    }

    private boolean roofFootprint(Hk3CampusExpansion.Plot plot, int x, int z) {
        return x >= plot.minX() + 2 && x <= plot.maxX() - 2
                && z >= plot.minZ() + 2 && z <= plot.maxZ() - 2;
    }

    private boolean roofRim(Hk3CampusExpansion.Plot plot, int x, int z) {
        return x == plot.minX() + 2 || x == plot.maxX() - 2
                || z == plot.minZ() + 2 || z == plot.maxZ() - 2;
    }

    private int roofY(Building building, int x, int z) {
        var plot = building.plot();
        int dx = Math.min(x - plot.minX() - 2, plot.maxX() - 2 - x);
        int dz = Math.min(z - plot.minZ() - 2, plot.maxZ() - 2 - z);
        int rise = switch (style.kind()) {
            case WOODLAND -> Math.min(7, Math.max(0, dx) / 3);
            case PARK -> Math.min(4, Math.max(0, Math.min(dx, dz)) / 3);
            case PINK -> Math.min(6, Math.max(0, dx) / 3);
            case DENSE -> Math.floorMod(x - plot.minX() - 2, 16) / 4;
            case COMPACT -> Math.floorMod(z - plot.minZ() - 2, 20) < 3 ? 2 : 0;
            default -> 0;
        };
        return building.clearHeight() + 2 + rise;
    }

    private String roofMaterial(Building building, int x, int z) {
        var plot = building.plot();
        if (roofRim(plot, x, z)) return palette.trim();
        if (style.kind() == Hk3CampusStyle.Kind.PINK)
            return Math.floorMod(x - plot.minX(), 12) < 3 ? "minecraft:white_concrete" : palette.roof();
        if (style.kind() == Hk3CampusStyle.Kind.DENSE && Math.floorMod(x - plot.minX() - 2, 16) >= 12)
            return "minecraft:light_blue_stained_glass";
        if ((style.kind() == Hk3CampusStyle.Kind.MODERN || style.kind() == Hk3CampusStyle.Kind.COMPACT)
                && Math.floorMod(x - plot.minX(), 16) >= 6 && Math.floorMod(x - plot.minX(), 16) <= 8)
            return palette.glass();
        return palette.roof();
    }

    private Building buildingAt(int x, int z) {
        for (var building : cells.getOrDefault(key(x >> 7, z >> 7), List.of())) {
            var plot = building.plot();
            if (x >= plot.minX() && x <= plot.maxX() && z >= plot.minZ() && z <= plot.maxZ()) return building;
        }
        return null;
    }

    private static Palette palette(Hk3CampusStyle style) {
        return switch (style.kind()) {
            case WOODLAND -> new Palette("minecraft:smooth_quartz", "minecraft:stripped_oak_log[axis=y]",
                    "minecraft:light_blue_stained_glass", "minecraft:white_concrete", "minecraft:smooth_quartz", "minecraft:cyan_concrete");
            case PARK -> new Palette("minecraft:smooth_quartz", "minecraft:quartz_pillar[axis=y]",
                    "minecraft:glass", "minecraft:smooth_quartz", "minecraft:mossy_stone_bricks", "minecraft:green_concrete");
            case PINK -> new Palette("minecraft:smooth_quartz", "minecraft:stripped_cherry_log[axis=y]",
                    "minecraft:pink_stained_glass", "minecraft:pink_concrete", "minecraft:cherry_planks", "minecraft:magenta_concrete");
            case DENSE -> new Palette("minecraft:white_concrete", "minecraft:polished_andesite",
                    "minecraft:light_blue_stained_glass", "minecraft:smooth_quartz", "minecraft:smooth_quartz", "minecraft:cyan_concrete");
            case COMPACT -> new Palette("minecraft:light_gray_concrete", "minecraft:quartz_pillar[axis=y]",
                    "minecraft:glass", "minecraft:white_concrete", "minecraft:smooth_stone", "minecraft:cyan_concrete");
            default -> new Palette(style.border(), style.column(), "minecraft:light_blue_stained_glass",
                    "minecraft:white_concrete", style.border(), style.accent());
        };
    }

    private static long key(int x, int z) { return ((long) x << 32) | (z & 0xffffffffL); }
}
