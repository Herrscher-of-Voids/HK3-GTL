package com.sirin.hk3gtl.common.campus;

import com.gtl.enhancedcore.common.world.plot.FileCampus;
import com.gtl.enhancedcore.common.world.plot.LegacyPlannedCampus;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;
import java.util.function.IntBinaryOperator;

final class Hk3CampusNativeDecoration {
    static final int BOTTOM = -5;
    private interface Blocks { String at(int x, int y, int z); }
    private record Template(int width, int depth, String[][] columns) {}
    private record Placement(Template template, int minX, int minZ) {}
    private static final Map<Hk3CampusStyle, List<Template>> TEMPLATES = new ConcurrentHashMap<>();
    private final Map<Long, List<Placement>> cells = new HashMap<>();

    Hk3CampusNativeDecoration(Hk3CampusExpansion.Plan plan, Hk3CampusStyle style) {
        if (style.kind() == Hk3CampusStyle.Kind.GRID) return;
        var templates = TEMPLATES.computeIfAbsent(style, Hk3CampusNativeDecoration::templates);
        var first = templates.get(0);
        int radius = Math.max(first.width(), first.depth()) / 2;
        int spacing = Math.max(96, first.width() + 16);
        for (int x = plan.minX() + radius + 8; x <= plan.maxX() - radius - 8; x += spacing) {
            for (int z = plan.minZ() + radius + 8; z <= plan.maxZ() - radius - 8; z += spacing) {
                var template = templates.get(Math.floorMod(x / spacing + z / spacing, templates.size()));
                int minX = x - template.width() / 2, minZ = z - template.depth() / 2;
                if (!plan.decorationSpace(minX, minZ, template.width(), template.depth())) continue;
                var placement = new Placement(template, minX, minZ);
                for (int cellX = minX >> 7; cellX <= (minX + template.width() - 1) >> 7; cellX++)
                    for (int cellZ = minZ >> 7; cellZ <= (minZ + template.depth() - 1) >> 7; cellZ++)
                        cells.computeIfAbsent(key(cellX, cellZ), ignored -> new ArrayList<>()).add(placement);
            }
        }
    }

    String blockAt(int x, int relativeY, int z) {
        var column = columnAt(x, z);
        return column != null && relativeY >= BOTTOM && relativeY - BOTTOM < column.length ? column[relativeY - BOTTOM] : null;
    }

    int topAt(int x, int z) {
        var column = columnAt(x, z);
        return column == null ? 0 : column.length + BOTTOM - 1;
    }

    int bottomAt(int x, int z) { return columnAt(x, z) != null ? BOTTOM : 1; }

    private String[] columnAt(int x, int z) {
        for (var placement : cells.getOrDefault(key(x >> 7, z >> 7), List.of())) {
            int dx = x - placement.minX(), dz = z - placement.minZ();
            var template = placement.template();
            if (dx >= 0 && dx < template.width() && dz >= 0 && dz < template.depth())
                return template.columns()[dx * template.depth() + dz];
        }
        return null;
    }

    private static List<Template> templates(Hk3CampusStyle style) {
        if (style.kind() == Hk3CampusStyle.Kind.MODERN) {
            return List.of(capture(112, 56, (x, z) -> LegacyPlannedCampus.maxDecorationYAt(x - 232, z - 92),
                    (x, y, z) -> y < 0 ? LegacyPlannedCampus.foundationBlockAt(x - 232, y, z - 92)
                            : y == 0 ? LegacyPlannedCampus.surfaceBlock(null, x - 232, z - 92)
                            : LegacyPlannedCampus.blockAboveAt(null, x - 232, y, z - 92)));
        }
        if (style.kind() == Hk3CampusStyle.Kind.PINK || style.kind() == Hk3CampusStyle.Kind.FACTORY) {
            boolean pink = style.kind() == Hk3CampusStyle.Kind.PINK;
            var source = FileCampus.of(pink ? "pink_dream_home_v1" : "quartz_works");
            int minX = pink ? -469 : 589, minZ = pink ? 583 : 589;
            int width = pink ? 80 : 23;
            return List.of(capture(width, width, (x, z) -> source.maxDecorationYAt(null, minX + x, minZ + z),
                    (x, y, z) -> y < 0 ? source.foundationBlockAt(minX + x, y, minZ + z)
                            : y == 0 ? source.surfaceBlock(null, minX + x, minZ + z)
                            : source.blockAboveAt(null, minX + x, y, minZ + z)));
        }
        var templates = new ArrayList<Template>();
        int radius = style.landscapeRadius();
        for (int theme = 0; theme < 4; theme++) {
            int variant = theme;
            templates.add(capture(radius * 2 + 1, radius * 2 + 1, (x, z) -> style.landscapeHeight(),
                    (x, y, z) -> y < 0 ? style.landscapeFoundation(x - radius, y, z - radius, variant)
                            : y == 0 ? style.landscapeSurface(x - radius, z - radius, variant)
                            : style.landscapeAbove(x - radius, y, z - radius, variant)));
        }
        return List.copyOf(templates);
    }

    private static Template capture(int width, int depth, IntBinaryOperator top, Blocks blocks) {
        var columns = new String[width * depth][];
        for (int x = 0; x < width; x++) {
            for (int z = 0; z < depth; z++) {
                var column = new String[Math.max(0, top.applyAsInt(x, z)) - BOTTOM + 1];
                for (int y = BOTTOM; y < column.length + BOTTOM; y++) column[y - BOTTOM] = blocks.at(x, y, z);
                int length = column.length;
                while (length > 1 - BOTTOM && (column[length - 1] == null || column[length - 1].equals("minecraft:air"))) length--;
                columns[x * depth + z] = Arrays.copyOf(column, length);
            }
        }
        return new Template(width, depth, columns);
    }

    private static long key(int x, int z) { return (long) x << 32 | z & 0xFFFFFFFFL; }
}
