package com.sirin.hk3gtl.common.campus;

import com.gtl.enhancedcore.common.world.plot.CompactPlannedCampus;
import com.gtl.enhancedcore.common.world.plot.DensePlannedCampus;
import com.gtl.enhancedcore.common.world.plot.FileCampus;
import com.gtl.enhancedcore.common.world.plot.LegacyPlannedCampus;
import com.gtl.enhancedcore.common.world.plot.ParkPlannedCampus;
import com.gtl.enhancedcore.common.world.plot.PlannedCampus;

import java.util.Arrays;
import java.util.function.IntBinaryOperator;

final class Hk3CampusNativeRoad {
    private interface Surface { String at(int x, int z); }
    private interface Blocks { String at(int x, int y, int z); }
    private record Source(Surface surface, Blocks foundation, Blocks above, IntBinaryOperator top) {}
    private record Span(int minAlong, int maxAlong, int minAcross, int maxAcross) {}
    private record Strip(int anchor, String[][][] columns, Span[][] facilities) {
        String[] column(int along, int across) {
            return columns[Math.floorMod(along - anchor, columns.length)][across + columns[0].length / 2];
        }

        Span facility(int along, int across) {
            return facilities[Math.floorMod(along - anchor, columns.length)][across + columns[0].length / 2];
        }
    }

    private final Strip mainX, mainZ, sideX, sideZ;
    private final int shoulder;
    private final Hk3CampusStyle.Kind kind;
    private final String junctionSurface;
    private final int clearance;

    Hk3CampusNativeRoad(Hk3CampusStyle style) {
        kind = style.kind();
        junctionSurface = switch (kind) {
            case FACTORY -> "minecraft:gray_concrete";
            case PINK -> "minecraft:pink_concrete";
            case GRID -> style.road();
            default -> "minecraft:black_concrete";
        };
        var source = source(style);
        shoulder = switch (style.kind()) {
            case FACTORY -> 4;
            case WOODLAND, DENSE, PINK, GRID -> 0;
            default -> 2;
        };
        int half = style.kind() == Hk3CampusStyle.Kind.PINK ? 8 : 16;
        int anchor = switch (style.kind()) {
            case MODERN -> 192;
            case PARK, COMPACT -> 128;
            default -> 600;
        };
        int period = switch (style.kind()) {
            case MODERN, PARK, COMPACT -> 32;
            case FACTORY -> 48;
            case PINK, GRID -> 1;
            default -> 96;
        };
        mainX = capture(source, true, anchor, 0, period, half + shoulder);
        mainZ = capture(source, false, anchor, 0, period, half + shoulder);
        int sideAxis = switch (style.kind()) {
            case WOODLAND, DENSE -> 400;
            case COMPACT -> 88;
            case MODERN, PARK -> 96;
            default -> 0;
        };
        int sidePeriod = switch (style.kind()) {
            case MODERN -> 160;
            case PARK, COMPACT -> 96;
            default -> period;
        };
        if (style.kind() == Hk3CampusStyle.Kind.FACTORY || style.kind() == Hk3CampusStyle.Kind.PINK) {
            sideX = mainX;
            sideZ = mainZ;
        } else {
            int sideAnchorX = switch (style.kind()) {
                case MODERN, PARK -> 96;
                case COMPACT -> 600;
                default -> anchor;
            };
            int sideAnchorZ = switch (style.kind()) {
                case MODERN -> 632;
                case PARK -> 1186;
                case COMPACT -> 106;
                default -> anchor;
            };
            int sideAxisZ = switch (style.kind()) {
                case MODERN -> 804;
                case PARK -> 324;
                case COMPACT -> 232;
                default -> sideAxis;
            };
            sideX = capture(source, true, sideAnchorX, sideAxis, sidePeriod, 14);
            sideZ = capture(source, false, sideAnchorZ, sideAxisZ, sidePeriod, 14);
        }
        int height = 0;
        for (var strip : new Strip[]{mainX, mainZ, sideX, sideZ})
            for (var row : strip.columns())
                for (var column : row) height = Math.max(height, column.length - 4);
        clearance = height;
    }

    int shoulder(Hk3CampusIntegratedLayout.Road road) { return road.halfWidth() == 12 ? 2 : shoulder; }
    int clearance() { return clearance; }

    String junctionAt(Hk3CampusIntegratedLayout.Road road, Hk3CampusIntegratedLayout.Road other, int x, int z) {
        if (road.halfWidth() == 2 || other.halfWidth() == 2) return null;
        boolean alongX = road.z1() == road.z2();
        if (alongX == (other.z1() == other.z2())) return null;
        var horizontal = alongX ? road : other;
        var vertical = alongX ? other : road;
        int centerX = vertical.x1(), centerZ = horizontal.z1();
        if (centerX < horizontal.x1() || centerX > horizontal.x2()
                || centerZ < vertical.z1() || centerZ > vertical.z2()) return null;
        int dx = x - centerX, dz = z - centerZ;
        int halfX = vertical.halfWidth() + shoulder(vertical), halfZ = horizontal.halfWidth() + shoulder(horizontal);
        if (dx < -halfX || dx >= halfX || dz < -halfZ || dz >= halfZ) return null;
        return z >= vertical.z1() && z <= vertical.z2() && lane(vertical, dx)
                || x >= horizontal.x1() && x <= horizontal.x2() && lane(horizontal, dz) ? junctionSurface : null;
    }

    private boolean lane(Hk3CampusIntegratedLayout.Road road, int offset) {
        return switch (kind) {
            case FACTORY -> offset >= -14 && offset < 14;
            case PINK -> offset >= -7 && offset <= 7;
            case GRID -> offset >= -road.halfWidth() && offset < road.halfWidth();
            default -> offset >= 7 - road.halfWidth() && offset < road.halfWidth() - 7;
        };
    }

    String blockAt(Hk3CampusIntegratedLayout.Road road, int x, int y, int z) {
        var column = column(road, x, z);
        return y + 3 < column.length ? column[y + 3] : "minecraft:air";
    }

    int topAt(Hk3CampusIntegratedLayout.Road road, int x, int z) {
        return column(road, x, z).length - 4;
    }

    boolean intersects(Hk3CampusIntegratedLayout.Road road, int x, int z,
                       Hk3CampusIntegratedLayout.Road otherRoad) {
        boolean alongX = road.z1() == road.z2();
        var span = strip(road).facility(alongX ? x : z, alongX ? z - road.z1() : x - road.x1());
        if (span == null) return false;
        int minX = alongX ? x + span.minAlong() : road.x1() + span.minAcross();
        int maxX = alongX ? x + span.maxAlong() : road.x1() + span.maxAcross();
        int minZ = alongX ? road.z1() + span.minAcross() : z + span.minAlong();
        int maxZ = alongX ? road.z1() + span.maxAcross() : z + span.maxAlong();
        int width = otherRoad.halfWidth();
        int margin = width == 2 ? 0 : shoulder(otherRoad);
        int high = width == 2 ? width : width - 1;
        if (otherRoad.z1() == otherRoad.z2()) {
            return minX <= otherRoad.x2() && maxX >= otherRoad.x1()
                    && minZ <= otherRoad.z1() + high + margin && maxZ >= otherRoad.z1() - width - margin;
        }
        return minZ <= otherRoad.z2() && maxZ >= otherRoad.z1()
                && minX <= otherRoad.x1() + high + margin && maxX >= otherRoad.x1() - width - margin;
    }

    private String[] column(Hk3CampusIntegratedLayout.Road road, int x, int z) {
        boolean alongX = road.z1() == road.z2();
        return strip(road).column(alongX ? x : z, alongX ? z - road.z1() : x - road.x1());
    }

    private Strip strip(Hk3CampusIntegratedLayout.Road road) {
        boolean alongX = road.z1() == road.z2();
        return road.halfWidth() >= 16 || road.halfWidth() == 8
                ? alongX ? mainX : mainZ : alongX ? sideX : sideZ;
    }

    private static Strip capture(Source source, boolean alongX, int anchor, int axis, int period, int half) {
        var columns = new String[period][half * 2][];
        for (int along = 0; along < period; along++) {
            for (int across = -half; across < half; across++) {
                int x = alongX ? anchor + along : axis + across;
                int z = alongX ? axis + across : anchor + along;
                var column = new String[source.top().applyAsInt(x, z) + 4];
                for (int y = -3; y < column.length - 3; y++) {
                    var block = y < 0 ? source.foundation().at(x, y, z)
                            : y == 0 ? source.surface().at(x, z) : source.above().at(x, y, z);
                    column[y + 3] = block == null ? "minecraft:air" : block;
                }
                int length = column.length;
                while (length > 4 && column[length - 1].equals("minecraft:air")) length--;
                columns[along][across + half] = Arrays.copyOf(column, length);
            }
        }
        return new Strip(anchor, columns, facilities(columns, half));
    }

    private static Span[][] facilities(String[][][] columns, int half) {
        int period = columns.length, width = half * 2;
        var spans = new Span[period][width];
        var visited = new boolean[period][width];
        var unwrapped = new int[period][width];
        var queue = new int[period * width];
        int[] alongSteps = {-1, 1, 0, 0}, acrossSteps = {0, 0, -1, 1};
        for (int along = 0; along < period; along++) {
            for (int across = 0; across < width; across++) {
                if (visited[along][across] || columns[along][across].length == 4) continue;
                int head = 0, size = 1;
                int minAlong = along, maxAlong = along, minAcross = across, maxAcross = across;
                queue[0] = along * width + across;
                visited[along][across] = true;
                unwrapped[along][across] = along;
                while (head < size) {
                    int node = queue[head++], a = node / width, c = node % width;
                    for (int direction = 0; direction < 4; direction++) {
                        int nextA = Math.floorMod(a + alongSteps[direction], period);
                        int nextC = c + acrossSteps[direction];
                        if (nextC < 0 || nextC >= width || visited[nextA][nextC]
                                || columns[nextA][nextC].length == 4) continue;
                        int position = unwrapped[a][c] + alongSteps[direction];
                        visited[nextA][nextC] = true;
                        unwrapped[nextA][nextC] = position;
                        minAlong = Math.min(minAlong, position);
                        maxAlong = Math.max(maxAlong, position);
                        minAcross = Math.min(minAcross, nextC);
                        maxAcross = Math.max(maxAcross, nextC);
                        queue[size++] = nextA * width + nextC;
                    }
                }
                for (int i = 0; i < size; i++) {
                    int node = queue[i], a = node / width, c = node % width;
                    spans[a][c] = new Span(minAlong - unwrapped[a][c], maxAlong - unwrapped[a][c],
                            minAcross - half, maxAcross - half);
                }
            }
        }
        return spans;
    }

    private static Source source(Hk3CampusStyle style) {
        return switch (style.kind()) {
            case MODERN -> new Source((x, z) -> LegacyPlannedCampus.surfaceBlock(null, x, z),
                    LegacyPlannedCampus::foundationBlockAt, (x, y, z) -> LegacyPlannedCampus.blockAboveAt(null, x, y, z),
                    LegacyPlannedCampus::maxDecorationYAt);
            case PARK -> new Source((x, z) -> ParkPlannedCampus.surfaceBlock(null, x, z),
                    ParkPlannedCampus::foundationBlockAt, (x, y, z) -> ParkPlannedCampus.blockAboveAt(null, x, y, z),
                    (x, z) -> ParkPlannedCampus.maxDecorationYAt(null, x, z));
            case COMPACT -> new Source((x, z) -> CompactPlannedCampus.surfaceBlock(null, x, z),
                    CompactPlannedCampus::foundationBlockAt, (x, y, z) -> CompactPlannedCampus.blockAboveAt(null, x, y, z),
                    (x, z) -> CompactPlannedCampus.maxDecorationYAt(null, x, z));
            case DENSE -> new Source((x, z) -> DensePlannedCampus.surfaceBlock(null, x, z),
                    DensePlannedCampus::foundationBlockAt, (x, y, z) -> DensePlannedCampus.blockAboveAt(null, x, y, z),
                    (x, z) -> DensePlannedCampus.maxDecorationYAt(null, x, z));
            case WOODLAND -> new Source((x, z) -> PlannedCampus.surfaceBlock(null, x, z),
                    PlannedCampus::foundationBlockAt, (x, y, z) -> PlannedCampus.blockAboveAt(null, x, y, z),
                    (x, z) -> PlannedCampus.maxDecorationYAt(null, x, z));
            case FACTORY, PINK -> {
                var campus = FileCampus.of(style.kind() == Hk3CampusStyle.Kind.PINK ? "pink_dream_home_v1" : "quartz_works");
                yield new Source((x, z) -> campus.surfaceBlock(null, x, z), campus::foundationBlockAt,
                        (x, y, z) -> campus.blockAboveAt(null, x, y, z), (x, z) -> campus.maxDecorationYAt(null, x, z));
            }
            case GRID -> new Source((x, z) -> style.road(), (x, y, z) -> style.foundation(),
                    (x, y, z) -> null, (x, z) -> 0);
        };
    }
}
