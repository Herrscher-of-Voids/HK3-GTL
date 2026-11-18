package com.sirin.hk3gtl.common.campus;

import java.util.Arrays;
import java.util.HashMap;
import java.util.Map;

/** 复用原预设庭院，只在机器和检修通道之外布置低矮设施。 */
final class Hk3CampusDecoration {
    private final Hk3CampusExpansion.Plan plan;
    private final Hk3CampusStyle style;
    private final Map<Long, String[]> columns = new HashMap<>();

    Hk3CampusDecoration(Hk3CampusExpansion.Plan plan, Hk3CampusStyle style) {
        this.plan = plan;
        this.style = style;
        int radius = style.landscapeRadius();
        int spacing = plan.version() >= 4 ? 96 : 48;
        for (int x = plan.minX() + 16; x < plan.maxX() - 15; x += spacing) {
            for (int z = plan.minZ() + 16; z < plan.maxZ() - 15; z += spacing) {
                int theme = Math.floorMod(x / 48 + z / 48, 4);
                if (style.kind() == Hk3CampusStyle.Kind.PARK) theme = theme % 2 == 0 ? 0 : 3;
                if (plan.version() >= 4 && style.kind() != Hk3CampusStyle.Kind.GRID
                        && style.kind() != Hk3CampusStyle.Kind.PINK && space(x, z, 26)) basin(x, z);
                else if (radius > 0 && space(x, z, radius)) landscape(x, z, theme);
                else if (style.kind() == Hk3CampusStyle.Kind.FACTORY && space(x, z, 4)) serviceBay(x, z);
                else if (style.kind() == Hk3CampusStyle.Kind.PINK && space(x, z, 3)) cherryCourt(x, z);
            }
        }
        for (var plot : plan.plots()) {
            for (int z = plot.minZ() + 12; z < plot.maxZ() - 6; z += 64) {
                lamp(plot.minX() - 2, z, false);
                lamp(plot.maxX() + 2, z + 8, false);
                if (style.kind() == Hk3CampusStyle.Kind.FACTORY) pipeRack(plot.maxX() + 2, z + 24);
            }
            for (int x = plot.minX() + 12; x < plot.maxX() - 6; x += 64) {
                lamp(x, plot.minZ() - 2, true);
                lamp(x + 8, plot.maxZ() + 2, true);
            }
            int x = plot.arrivalX() + 3, z = plot.arrivalZ() - 2;
            if (space(x, z, 0)) {
                put(x, 1, z, style.foundation());
                put(x, 2, z, style.accent());
                put(x, 3, z, style.light());
            }
            x = plot.maxX() + 2;
            z = plot.maxZ() + 2;
            if (style.kind() != Hk3CampusStyle.Kind.GRID && space(x, z, 1)) planter(x, z);
        }
        columns.replaceAll((key, blocks) -> {
            int length = blocks.length;
            while (length > 4 && blocks[length - 1] == null) length--;
            return Arrays.copyOf(blocks, length);
        });
    }

    String blockAt(int x, int y, int z) {
        var column = columns.get(key(x, z));
        return column != null && y + 3 < column.length ? column[y + 3] : null;
    }

    int topAt(int x, int z) {
        var column = columns.get(key(x, z));
        return column == null ? 0 : column.length - 4;
    }

    private boolean space(int x, int z, int radius) {
        if (!plan.decorationSpace(x, z, radius)) return false;
        for (int dx = -radius; dx <= radius; dx++) for (int dz = -radius; dz <= radius; dz++)
            if (columns.containsKey(key(x + dx, z + dz))) return false;
        return true;
    }

    private void landscape(int x, int z, int theme) {
        int radius = style.landscapeRadius();
        for (int dx = -radius; dx <= radius; dx++) for (int dz = -radius; dz <= radius; dz++) {
            for (int y = -3; y < 0; y++) put(x + dx, y, z + dz, style.landscapeFoundation(dx, y, dz, theme));
            put(x + dx, 0, z + dz, style.landscapeSurface(dx, dz, theme));
            for (int y = 1; y <= style.landscapeHeight(); y++)
                put(x + dx, y, z + dz, style.landscapeAbove(dx, y, dz, theme));
        }
    }

    private void basin(int x, int z) {
        for (int dx = -24; dx <= 24; dx++) for (int dz = -7; dz <= 7; dz++) {
            boolean rim = Math.abs(dx) == 24 || Math.abs(dz) == 7;
            put(x + dx, -1, z + dz, style.border());
            put(x + dx, 0, z + dz, rim ? style.border() : "minecraft:water[level=0]");
        }
    }

    private void lamp(int x, int z, boolean alongX) {
        if (!space(x, z, 0)) return;
        int dx = alongX ? 1 : 0, dz = alongX ? 0 : 1;
        if (style.kind() == Hk3CampusStyle.Kind.PINK && (!space(x - dx, z - dz, 0) || !space(x + dx, z + dz, 0))) return;
        var blocks = style.lamp();
        for (int y = 0; y < blocks.length; y++) put(x, y + 1, z, blocks[y]);
        if (style.kind() == Hk3CampusStyle.Kind.PINK) {
            put(x - dx, 5, z - dz, "minecraft:pink_concrete");
            put(x + dx, 5, z + dz, "minecraft:pink_concrete");
        }
    }

    private void planter(int x, int z) {
        for (int dx = -1; dx <= 1; dx++) for (int dz = -1; dz <= 1; dz++) {
            put(x + dx, 1, z + dz, dx == 0 && dz == 0 ? "minecraft:dirt" : style.border());
            if (dx == 0 && dz == 0) put(x, 2, z, style.planterFlower());
        }
    }

    private void serviceBay(int x, int z) {
        for (int dx = -4; dx <= 4; dx++) for (int dz = -3; dz <= 3; dz++) {
            put(x + dx, 0, z + dz, Math.abs(dx) == 4 || Math.abs(dz) == 3 ? style.border() : style.foundation());
            if (Math.abs(dx) == 3 && Math.abs(dz) == 2) {
                put(x + dx, 1, z + dz, style.foundation());
                for (int y = 2; y <= 4; y++) put(x + dx, y, z + dz, style.column());
                put(x + dx, 5, z + dz, style.accent());
                put(x + dx, 6, z + dz, style.light());
            }
        }
        for (int dx = -2; dx <= 2; dx++) {
            put(x + dx, 1, z - 2, style.foundation());
            put(x + dx, 2, z - 2, style.accent());
            put(x + dx, 3, z - 2, "minecraft:iron_trapdoor[facing=north,half=top,open=false,powered=false,waterlogged=false]");
            put(x + dx, 4, z - 2, style.border());
        }
    }

    private void pipeRack(int x, int z) {
        for (int dz = -3; dz <= 3; dz++) if (!space(x, z + dz, 0)) return;
        for (int dz = -3; dz <= 3; dz++) {
            put(x, 0, z + dz, Math.floorMod(dz, 2) == 0 ? "minecraft:yellow_concrete" : style.foundation());
            put(x, 3, z + dz, style.accent());
            put(x, 4, z + dz, style.border());
            if (Math.abs(dz) == 3) {
                put(x, 1, z + dz, style.foundation());
                put(x, 2, z + dz, style.column());
            }
        }
    }

    private void cherryCourt(int x, int z) {
        for (int dx = -3; dx <= 3; dx++) for (int dz = -3; dz <= 3; dz++) {
            int distance = dx * dx + dz * dz;
            if (distance > 10) continue;
            put(x + dx, 0, z + dz, distance >= 5 ? style.border() : "minecraft:grass_block");
            if (distance >= 5) put(x + dx, 1, z + dz, "minecraft:smooth_quartz_slab[type=bottom]");
            else if (distance > 0) put(x + dx, 1, z + dz, style.planterFlower());
            if (distance <= 5) put(x + dx, 4, z + dz, style.leaves());
            if (distance <= 2) put(x + dx, 5, z + dz, style.leaves());
        }
        for (int y = 1; y <= 4; y++) put(x, y, z, style.column());
    }

    private void put(int x, int y, int z, String block) {
        if (block != null) columns.computeIfAbsent(key(x, z), ignored -> new String[24])[y + 3] = block;
    }

    private static long key(int x, int z) { return (long) x << 32 | z & 0xFFFFFFFFL; }
}
