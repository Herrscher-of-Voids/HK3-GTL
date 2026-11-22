package com.sirin.hk3gtl.common.campus;

import com.sirin.hk3gtl.common.constants.Hk3ValuesImpl;
import com.gtl.enhancedcore.common.world.plot.PlannedCampus;

import java.util.ArrayList;
import java.util.Comparator;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;

/** 按真实结构装箱，庭院沿用所属预设的建筑风格。 */
public final class Hk3CampusExpansion {
    private static final int GAP = 8, BORDER = 8;
    private record Key(String identity, int minX, int minZ, int maxX, int maxZ, int surfaceY, Hk3CampusStyle style, int version, PlannedCampus.Bounds aeBounds) {}
    private interface Parcel { int width(); int depth(); int order(); }
    private record Item(Hk3CampusCatalog.Entry entry, int margin, int width, int depth, int order) implements Parcel {}
    private record Compound(List<Placed> placed, int width, int depth, int order) implements Parcel {}
    private record Rect(int x, int z, int width, int depth) {
        int right() { return x + width; }
        int bottom() { return z + depth; }
        boolean contains(Rect other) {
            return x <= other.x && z <= other.z && right() >= other.right() && bottom() >= other.bottom();
        }
        boolean intersects(Rect other) {
            return x < other.right() && right() > other.x && z < other.bottom() && bottom() > other.z;
        }
    }
    private record Placed(Parcel parcel, Rect rect) {}
    private record Packing(List<Placed> placed, int width, int depth) {
        double score() { return (double) width * depth * (1 + Math.abs(Math.log((double) width / depth)) * 0.24); }
    }
    private static final Map<Key, Plan> PLANS = com.google.common.cache.CacheBuilder.newBuilder().maximumSize(8).<Key, Plan>build().asMap();

    public record Plot(Hk3CampusCatalog.Entry entry, int minX, int minZ, int maxX, int maxZ,
                       int controllerX, int controllerY, int controllerZ, int arrivalX, int arrivalY, int arrivalZ) {
        public int surfaceY() { return arrivalY - 1; }
        public int structureMinX() { return controllerX - entry.controllerX(); }
        public int structureMaxX() { return structureMinX() + entry.sizeX() - 1; }
        public int structureMinZ() { return controllerZ - entry.controllerZ(); }
        public int structureMaxZ() { return structureMinZ() + entry.sizeZ() - 1; }
    }

    public static final class Plan {
        private final List<Plot> plots;
        private final int minX, minZ, maxX, maxZ, surfaceY, bridgeMinX, bridgeMaxX, bridgeZ;
        private final boolean legacy;
        private final Hk3CampusStyle style;
        private final Hk3CampusDecoration decoration;
        private final Hk3CampusArchitecture architecture;
        private final Hk3CampusIntegratedLayout.Layout urban;
        private final Hk3CampusRoadProfile roadProfile;
        private final Hk3CampusNativeRoad nativeRoad;
        private final Hk3CampusNativeDecoration nativeDecoration;
        private final int version;
        private final Map<Long, List<Plot>> cells = new HashMap<>();
        private final Map<Long, String[]> scenery = new HashMap<>();
        private final Map<Plot, String> accents = new HashMap<>();

        public Plan(List<Plot> plots, int minX, int minZ, int maxX, int maxZ, int surfaceY,
                     int bridgeMinX, int bridgeMaxX, int bridgeZ) {
            this(plots, minX, minZ, maxX, maxZ, surfaceY, bridgeMinX, bridgeMaxX, bridgeZ, true, null, 1);
        }

        private Plan(List<Plot> plots, int minX, int minZ, int maxX, int maxZ, int surfaceY,
                     int bridgeMinX, int bridgeMaxX, int bridgeZ, boolean legacy, Hk3CampusStyle style, int version) {
            this(plots, minX, minZ, maxX, maxZ, surfaceY, bridgeMinX, bridgeMaxX, bridgeZ, legacy, style, version, null);
        }

        private Plan(List<Plot> plots, int minX, int minZ, int maxX, int maxZ, int surfaceY,
                     int bridgeMinX, int bridgeMaxX, int bridgeZ, boolean legacy, Hk3CampusStyle style, int version,
                     Hk3CampusIntegratedLayout.Layout urban) {
            this.plots = List.copyOf(plots);
            this.minX = minX; this.minZ = minZ; this.maxX = maxX; this.maxZ = maxZ;
            this.surfaceY = surfaceY; this.bridgeMinX = bridgeMinX; this.bridgeMaxX = bridgeMaxX; this.bridgeZ = bridgeZ;
            this.legacy = legacy;
            this.style = style;
            this.version = version;
            this.urban = urban;
            roadProfile = urban == null || version >= 7 ? null : new Hk3CampusRoadProfile(style);
            nativeRoad = urban != null && version >= 7 ? new Hk3CampusNativeRoad(style) : null;
            for (var plot : plots) {
                accents.put(plot, accent(plot.entry.tier()));
                int reach = version >= 4 ? 32 : 12;
                for (int x = (plot.minX - reach) >> 7; x <= (plot.maxX + reach) >> 7; x++)
                    for (int z = (plot.minZ - reach) >> 7; z <= (plot.maxZ + reach) >> 7; z++)
                        cells.computeIfAbsent(position(x, z), ignored -> new ArrayList<>()).add(plot);
            }
            decoration = style == null || version >= 7 ? null : new Hk3CampusDecoration(this, style);
            nativeDecoration = style != null && version >= 7 ? new Hk3CampusNativeDecoration(this, style) : null;
            architecture = version >= 4 && version < 6 && style != null ? new Hk3CampusArchitecture(this, style) : null;
            if (!legacy && style == null) garden();
        }

        public List<Plot> plots() { return plots; }
        public int minX() { return minX; }
        public int minZ() { return minZ; }
        public int maxX() { return maxX; }
        public int maxZ() { return maxZ; }
        public int surfaceY() { return surfaceY; }
        public int bridgeMinX() { return bridgeMinX; }
        public int bridgeMaxX() { return bridgeMaxX; }
        public int bridgeZ() { return bridgeZ; }
        public int version() { return version; }
        public Hk3CampusIntegratedLayout.Layout urban() { return urban; }

        public boolean terrainAt(int x, int z) {
            if (urban != null) return x >= minX && x <= maxX && z >= minZ && z <= maxZ
                    && (!urban.original().contains(x, z) || roadAt(x, z) != null);
            return x >= minX && x <= maxX && z >= minZ && z <= maxZ
                    || x >= bridgeMinX && x <= bridgeMaxX && Math.abs(z - bridgeZ) <= (legacy ? 16 : GAP / 2);
        }

        public int bottomAt(int x, int z) {
            return surfaceY + (nativeDecoration == null ? 1 : nativeDecoration.bottomAt(x, z));
        }

        public int topAt(int x, int z) {
            if (legacy) return surfaceY;
            if (urban != null) {
                var road = roadAt(x, z);
                if (road != null) return surfaceY + (nativeRoad == null ? 5
                        : road.halfWidth() == 2 || junction(road, x, z) ? 0 : nativeRoad.topAt(road, x, z));
            }
            if (nativeDecoration != null) return surfaceY + nativeDecoration.topAt(x, z);
            if (style != null) return surfaceY + Math.max(decoration.topAt(x, z), architecture == null ? 0 : architecture.topAt(x, z));
            var column = scenery.get(position(x, z));
            return surfaceY + (column != null ? column.length : flower(x, z) != null ? 1 : 0);
        }

        public int generationTopAt(int x, int z) {
            int top = topAt(x, z);
            if (nativeRoad == null) return top;
            var road = roadAt(x, z);
            return road != null && road.halfWidth() != 2 && junction(road, x, z)
                    ? Math.max(top, surfaceY + nativeRoad.clearance()) : top;
        }

        public String blockAt(int x, int y, int z) {
            if (!terrainAt(x, z) || y < surfaceY - 3 && y < bottomAt(x, z)) return null;
            if (urban != null) {
                var road = roadAt(x, z);
                if (road != null) {
                    if (nativeRoad != null && road.halfWidth() != 2) {
                        if (y > surfaceY && junction(road, x, z)) return "minecraft:air";
                        if (y == surfaceY) {
                            var crossing = junctionSurface(road, x, z);
                            if (crossing != null) return crossing;
                        }
                        return nativeRoad.blockAt(road, x, y - surfaceY, z);
                    }
                    if (y < surfaceY) return style.foundation();
                    if (y == surfaceY) {
                        if (road.halfWidth() == 2) return version >= 6 ? style.originalFloor() : style.paving(x, z, true);
                        boolean alongX = road.z1() == road.z2();
                        return roadProfile.crossAt(alongX ? z - road.z1() : x - road.x1(),
                                alongX ? x : z, road.halfWidth());
                    }
                    return y <= surfaceY + 5 ? "minecraft:air" : null;
                }
            }
            if (legacy) {
                if (y > surfaceY) return null;
                if (y < surfaceY) return "minecraft:polished_andesite";
                var plot = reserved(x, z);
                if (plot == null) return "minecraft:gray_concrete";
                return x == plot.minX || x == plot.maxX || z == plot.minZ || z == plot.maxZ
                        ? "minecraft:cyan_concrete" : "minecraft:light_gray_concrete";
            }
            if (style != null) {
                if (version >= 4 && version < 6 && y == surfaceY) {
                    var border = structureBorder(x, z);
                    if (border != null) return border;
                }
                var block = nativeDecoration == null ? decoration.blockAt(x, y - surfaceY, z)
                        : nativeDecoration.blockAt(x, y - surfaceY, z);
                if (block != null) return block;
                if (architecture != null) {
                    block = architecture.blockAt(x, y - surfaceY, z);
                    if (block != null) return block;
                }
                if (y < surfaceY) return style.foundation();
                return y == surfaceY ? themedGround(x, z) : null;
            }
            if (y < surfaceY) return y == surfaceY - 3 ? "minecraft:polished_andesite" : "minecraft:dirt";
            if (y == surfaceY) return ground(x, z);
            var column = scenery.get(position(x, z));
            if (column != null) return y - surfaceY <= column.length ? column[y - surfaceY - 1] : null;
            return y == surfaceY + 1 ? flower(x, z) : null;
        }

        private List<Plot> nearby(int x, int z) { return cells.getOrDefault(position(x >> 7, z >> 7), List.of()); }
        List<Plot> nearbyPlots(int x, int z) { return nearby(x, z); }

        private Plot reserved(int x, int z) {
            for (var plot : nearby(x, z))
                if (x >= plot.minX && x <= plot.maxX && z >= plot.minZ && z <= plot.maxZ) return plot;
            return null;
        }

        private boolean path(int x, int z) {
            if (urban != null) {
                if (roadAt(x, z) != null) return true;
            } else {
                if (x <= bridgeMaxX && x >= bridgeMinX && Math.abs(z - bridgeZ) <= (version >= 4 ? 4 : 2)) return true;
                int perimeter = version >= 4 ? 4 : 1;
                if (Math.abs(x - minX - BORDER) <= perimeter || Math.abs(x - maxX + BORDER) <= perimeter
                        || Math.abs(z - minZ - BORDER) <= perimeter || Math.abs(z - maxZ + BORDER) <= perimeter) return true;
            }
            for (var plot : nearby(x, z)) {
                if (Math.abs(x - plot.arrivalX) <= 2 && Math.abs(z - plot.arrivalZ) <= 2) return true;
                int left = plot.minX - 4, right = plot.maxX + 5, top = plot.minZ - 4, bottom = plot.maxZ + 5;
                boolean curved = version < 5 && (style == null || style.kind() == Hk3CampusStyle.Kind.WOODLAND);
                int bendX = curved ? (int) Math.round(Math.sin(z / 23.0)) : 0;
                int bendZ = curved ? (int) Math.round(Math.sin(x / 23.0)) : 0;
                int halfWidth = version >= 4 ? 2 : 1;
                if (z >= top - 1 && z <= bottom + 1
                        && (Math.abs(x - left - bendX) <= halfWidth || Math.abs(x - right -bendX) <= halfWidth)) return true;
                if (x >= left - 1 && x <= right + 1
                        && (Math.abs(z - top - bendZ) <= halfWidth || Math.abs(z - bottom - bendZ) <= halfWidth)) return true;
            }
            return false;
        }

        private Hk3CampusIntegratedLayout.Road roadAt(int x, int z) {
            for (var road : urban.roads()) if (onRoad(road, x, z, 0)) return road;
            if (nativeRoad != null && reserved(x, z) == null)
                for (var road : urban.roads()) if (road.halfWidth() != 2
                        && onRoad(road, x, z, nativeRoad.shoulder(road))) return road;
            return null;
        }

        private static boolean onRoad(Hk3CampusIntegratedLayout.Road road, int x, int z, int shoulder) {
            int half = road.halfWidth() + shoulder;
            int end = half + (road.halfWidth() == 2 ? 1 : 0);
            return road.z1() == road.z2() && x >= road.x1() && x <= road.x2()
                    && z >= road.z1() - half && z < road.z1() + end
                    || road.x1() == road.x2() && z >= road.z1() && z <= road.z2()
                    && x >= road.x1() - half && x < road.x1() + end;
        }

        private boolean junction(Hk3CampusIntegratedLayout.Road selected, int x, int z) {
            for (var road : urban.roads())
                if (road != selected && (road.x1() == road.x2()) != (selected.x1() == selected.x2())
                        && (nativeRoad.junctionAt(selected, road, x, z) != null
                        || nativeRoad.intersects(selected, x, z, road))) return true;
            return false;
        }

        private String junctionSurface(Hk3CampusIntegratedLayout.Road selected, int x, int z) {
            for (var road : urban.roads()) {
                var block = nativeRoad.junctionAt(selected, road, x, z);
                if (block != null) return block;
            }
            return null;
        }

        private String ground(int x, int z) {
            var plot = reserved(x, z);
            if (plot != null) {
                int left = plot.structureMinX(), right = plot.structureMaxX(), top = plot.structureMinZ(), bottom = plot.structureMaxZ();
                if (x >= left && x <= right && z >= top && z <= bottom
                        && (x == left || x == right || z == top || z == bottom)) return accents.get(plot);
                if (Math.abs(x - plot.controllerX) <= 1 && z >= plot.controllerZ && z <= plot.maxZ)
                    return Math.floorMod(z, 9) == 0 ? "minecraft:polished_andesite" : "minecraft:stone_bricks";
                if (plot.entry.sizeX() <= 48 && plot.entry.sizeZ() <= 48
                        && x >= left && x <= right && z >= top && z <= bottom)
                    return Math.floorMod(x + z, 7) == 0 ? "minecraft:andesite" : "minecraft:smooth_stone";
                return "minecraft:grass_block";
            }
            if (path(x, z)) return Math.floorMod(x * 3 + z, 13) < 3 ? "minecraft:mossy_stone_bricks" : "minecraft:stone_bricks";
            return "minecraft:grass_block";
        }

        private String themedGround(int x, int z) {
            var plot = reserved(x, z);
            if (version >= 6) {
                if (plot != null && (x >= plot.structureMinX() && x <= plot.structureMaxX()
                        && z >= plot.structureMinZ() && z <= plot.structureMaxZ()
                        || Math.abs(x - plot.controllerX) <= 1 && z >= plot.controllerZ && z <= plot.maxZ))
                    return style.originalFloor();
                return path(x, z) ? style.originalFloor() : style.green();
            }
            if (plot != null) {
                int left = plot.structureMinX(), right = plot.structureMaxX(), top = plot.structureMinZ(), bottom = plot.structureMaxZ();
                if (x >= left && x <= right && z >= top && z <= bottom
                        && (x == left || x == right || z == top || z == bottom)) return accents.get(plot);
                if (Math.abs(x - plot.controllerX) <= 1 && z >= plot.controllerZ && z <= plot.maxZ)
                    return style.paving(x, z, true);
            }
            if (version >= 4 && !path(x, z)) return switch (style.kind()) {
                case GRID -> style.floor();
                case PINK -> Math.floorMod(x + z, 24) < 3 ? "minecraft:white_concrete" : "minecraft:pink_terracotta";
                default -> "minecraft:grass_block";
            };
            return style.paving(x, z, plot == null && path(x, z));
        }

        private String structureBorder(int x, int z) {
            var plot = reserved(x, z);
            if (plot != null && x >= plot.structureMinX() && x <= plot.structureMaxX()
                    && z >= plot.structureMinZ() && z <= plot.structureMaxZ()
                    && (x == plot.structureMinX() || x == plot.structureMaxX()
                    || z == plot.structureMinZ() || z == plot.structureMaxZ())) return accents.get(plot);
            return null;
        }

        private boolean clear(int x, int z, int radius) {
            if (x - radius < minX || x + radius > maxX || z - radius < minZ || z + radius > maxZ) return false;
            for (var plot : nearby(x, z)) {
                if (x + radius >= plot.minX && x - radius <= plot.maxX
                        && z + radius >= plot.minZ && z - radius <= plot.maxZ) return false;
                if (Math.abs(x - plot.arrivalX) <= radius + 2 && Math.abs(z - plot.arrivalZ) <= radius + 2) return false;
            }
            for (int dx = -radius; dx <= radius; dx++) for (int dz = -radius; dz <= radius; dz++)
                if (urban != null && !terrainAt(x + dx, z + dz)
                        || path(x + dx, z + dz) || scenery.containsKey(position(x + dx, z + dz))) return false;
            return true;
        }

        boolean decorationSpace(int x, int z, int radius) {
            return clear(x, z, radius);
        }

        boolean decorationSpace(int x, int z, int width, int depth) {
            var area = new Rect(x, z, width, depth);
            if (x < minX || area.right() > maxX + 1 || z < minZ || area.bottom() > maxZ + 1) return false;
            var original = urban.original();
            if (area.intersects(new Rect(original.minX(), original.minZ(),
                    original.maxX() - original.minX() + 1, original.maxZ() - original.minZ() + 1))) return false;
            for (var plot : plots) {
                if (area.intersects(new Rect(plot.minX - 8, plot.minZ - 8,
                        plot.maxX - plot.minX + 17, plot.maxZ - plot.minZ + 17))) return false;
                if (area.intersects(new Rect(plot.arrivalX - 3, plot.arrivalZ - 3, 7, 7))) return false;
            }
            for (var road : urban.roads()) {
                int half = road.halfWidth() + (road.halfWidth() == 2 ? 1 : nativeRoad.shoulder(road));
                if (area.intersects(new Rect(road.x1() - half, road.z1() - half,
                        road.x2() - road.x1() + half * 2 + 1, road.z2() - road.z1() + half * 2 + 1))) return false;
            }
            return true;
        }

        private String flower(int x, int z) {
            if (!terrainAt(x, z) || x < minX || reserved(x, z) != null || path(x, z)) return null;
            int hash = hash(x, z);
            if ((hash & 31) != 0) return null;
            return switch ((hash >>> 5) % 5) {
                case 0 -> "minecraft:cornflower";
                case 1 -> "minecraft:azure_bluet";
                case 2 -> "minecraft:oxeye_daisy";
                case 3 -> "minecraft:allium";
                default -> "minecraft:fern";
            };
        }

        private void garden() {
            for (int x = minX + 4; x < maxX - 3; x += 20) for (int z = minZ + 4; z < maxZ - 3; z += 20) {
                int hash = hash(x, z), px = x + (hash & 7) - 3, pz = z + (hash >>> 3 & 7) - 3;
                if (clear(px, pz, 3)) tree(px, pz, hash);
            }
            for (var plot : plots) {
                for (int z = plot.minZ + 12; z < plot.maxZ - 6; z += 64) {
                    lamp(plot.minX - 2, z); lamp(plot.maxX + 2, z + 8);
                }
                for (int x = plot.minX + 12; x < plot.maxX - 6; x += 64) {
                    lamp(x, plot.minZ - 2); lamp(x + 8, plot.maxZ + 2);
                }
                int x = plot.arrivalX + 3, z = plot.arrivalZ - 2;
                if (clear(x, z, 0)) scenery.put(position(x, z), new String[]{"minecraft:polished_deepslate", accents.get(plot), "minecraft:lantern"});
            }
        }

        private void lamp(int x, int z) {
            if (clear(x, z, 0)) scenery.put(position(x, z), new String[]{"minecraft:stone_brick_wall", "minecraft:dark_oak_fence", "minecraft:lantern"});
        }

        private void tree(int x, int z, int hash) {
            int height = 4 + (hash >>> 8 & 1);
            boolean birch = (hash & 256) == 0;
            String leaves = birch ? "minecraft:birch_leaves[persistent=true]" : "minecraft:oak_leaves[persistent=true]";
            String log = birch ? "minecraft:birch_log" : "minecraft:oak_log";
            for (int dx = -2; dx <= 2; dx++) for (int dz = -2; dz <= 2; dz++) {
                if (Math.abs(dx) == 2 && Math.abs(dz) == 2) continue;
                int top = height + (Math.abs(dx) + Math.abs(dz) <= 1 ? 1 : 0);
                var column = new String[top];
                for (int y = height - 2; y <= top; y++) column[y - 1] = leaves;
                if (dx == 0 && dz == 0) for (int y = 0; y < height; y++) column[y] = log;
                scenery.put(position(x + dx, z + dz), column);
            }
        }
    }

    private Hk3CampusExpansion() {}

    public static Plan plan(String identity, int minX, int minZ, int maxX, int maxZ, int surfaceY) {
        return plan(identity, minX, minZ, maxX, maxZ, surfaceY, null);
    }

    public static Plan plan(String identity, int minX, int minZ, int maxX, int maxZ, int surfaceY, Hk3CampusStyle style) {
        return plan(identity, minX, minZ, maxX, maxZ, surfaceY, style, 3);
    }

    public static Plan plan(String identity, int minX, int minZ, int maxX, int maxZ, int surfaceY, Hk3CampusStyle style, int version) {
        return plan(identity, minX, minZ, maxX, maxZ, surfaceY, style, version, null);
    }

    public static Plan plan(String identity, int minX, int minZ, int maxX, int maxZ, int surfaceY,
                            Hk3CampusStyle style, int version, PlannedCampus.Bounds aeBounds) {
        var key = new Key(identity, minX, minZ, maxX, maxZ, surfaceY, style, version, aeBounds);
        return PLANS.computeIfAbsent(key, value -> create(value, Hk3CampusCatalog.entries(version)));
    }

    public static Plan layout(List<Hk3CampusCatalog.Entry> entries, String identity, int minX, int minZ,
                              int maxX, int maxZ, int surfaceY, Hk3CampusStyle style, int version) {
        return create(new Key(identity, minX, minZ, maxX, maxZ, surfaceY, style, version, null), entries);
    }

    private static Plan create(Key key, List<Hk3CampusCatalog.Entry> entries) {
        if (key.version >= 5) {
            var urban = Hk3CampusIntegratedLayout.create(entries,
                    new PlannedCampus.Bounds(key.minX, key.minZ, key.maxX, key.maxZ),
                    key.surfaceY, key.style, key.version >= 6 ? key.aeBounds : null);
            return new Plan(urban.plots(), urban.minX(), urban.minZ(), urban.maxX(), urban.maxZ(),
                    key.surfaceY, 0, -1, 0, false, key.style, key.version, urban);
        }
        var items = new ArrayList<Item>();
        for (int i = 0; i < entries.size(); i++) {
            var entry = entries.get(i);
            boolean hall = Math.max(entry.sizeX(), entry.sizeZ()) <= 128 && entry.sizeY() <= 96;
            int margin = key.version >= 4 ? hall ? 14 : 8 : Math.max(entry.sizeX(), entry.sizeZ()) > 128 ? 4 : 2;
            int width = entry.sizeX() + margin * 2, depth = entry.sizeZ() + margin * 2;
            if (key.version >= 4) {
                depth += hall ? 10 : 4;
                if (hall) { width = Math.max(40, width); depth = Math.max(48, depth); }
            }
            var item = new Item(entry, margin, width + GAP, depth + GAP, i);
            items.add(item);
        }
        var parcels = new ArrayList<Parcel>(items);
        if (key.version >= 4) {
            var halls = items.stream().filter(item -> Math.max(item.entry.sizeX(), item.entry.sizeZ()) <= 128
                    && item.entry.sizeY() <= 96).toList();
            if (!halls.isEmpty()) {
                var workshop = pack(halls);
                parcels.removeAll(halls);
                parcels.add(new Compound(workshop.placed, workshop.width, workshop.depth, halls.get(0).order));
            }
        }
        var best = pack(parcels);
        var placedItems = new ArrayList<Placed>();
        for (var placed : best.placed) {
            if (placed.parcel instanceof Compound compound) {
                for (var local : compound.placed) placedItems.add(new Placed(local.parcel,
                        new Rect(placed.rect.x + local.rect.x, placed.rect.z + local.rect.z,
                                local.rect.width, local.rect.depth)));
            } else placedItems.add(placed);
        }
        int bridgeZ = Math.max(key.minZ + GAP, Math.min(0, key.maxZ - GAP));
        int startX = Math.floorDiv(key.maxX + 32, 16) * 16;
        int startZ = Math.floorDiv(bridgeZ - (best.depth + BORDER * 2) / 2, 16) * 16;
        var plots = new ArrayList<Plot>();
        placedItems.stream().sorted(Comparator.comparingInt(placed -> placed.parcel.order())).forEach(placed -> {
            var item = (Item) placed.parcel; var entry = item.entry;
            int x = startX + BORDER + placed.rect.x + GAP / 2, z = startZ + BORDER + placed.rect.z + GAP / 2;
            int width = item.width - GAP, depth = item.depth - GAP;
            plots.add(new Plot(entry, x, z, x + width - 1, z + depth - 1,
                    x + item.margin + entry.controllerX(), key.surfaceY + 1 + entry.controllerY(), z + item.margin + entry.controllerZ(),
                    x + width / 2, key.surfaceY + 1, z + depth + 2));
        });
        return new Plan(plots, startX, startZ, startX + best.width + BORDER * 2, startZ + best.depth + BORDER * 2,
                key.surfaceY, key.maxX + 1, startX + BORDER, bridgeZ, false, key.style, key.version);
    }

    private static Packing pack(List<? extends Parcel> source) {
        var items = new ArrayList<Parcel>(source);
        items.sort(Comparator.<Parcel>comparingLong(item -> (long) item.width() * item.depth()).reversed()
                .thenComparing(Comparator.comparingInt((Parcel item) -> Math.max(item.width(), item.depth())).reversed()));
        long area = items.stream().mapToLong(item -> (long) item.width() * item.depth()).sum();
        int widest = items.stream().mapToInt(Parcel::width).max().orElseThrow();
        var best = pack(items, widest, items.stream().mapToInt(Parcel::depth).sum());
        for (int percent = 80; percent <= 145; percent += 5) {
            int width = Math.max(widest, (int) Math.ceil(Math.sqrt(area) * percent / 100.0));
            int height = Math.max(items.stream().mapToInt(Parcel::depth).max().orElseThrow(), (int) ((area + width - 1) / width));
            for (int attempt = 0; attempt < 10; attempt++) {
                var candidate = pack(items, width, height);
                if (candidate != null) {
                    if (candidate.score() < best.score()) best = candidate;
                    break;
                }
                height = (int) Math.ceil(height * 1.12);
            }
        }
        return best;
    }

    private static Packing pack(List<? extends Parcel> items, int width, int depth) {
        var free = new ArrayList<Rect>();
        free.add(new Rect(0, 0, width, depth));
        var placed = new ArrayList<Placed>();
        int endX = 0, endZ = 0;
        for (var item : items) {
            Rect selected = null;
            long best = Long.MAX_VALUE;
            for (var rect : free) {
                if (item.width() > rect.width || item.depth() > rect.depth) continue;
                int shortSide = Math.min(rect.width - item.width(), rect.depth - item.depth());
                int longSide = Math.max(rect.width - item.width(), rect.depth - item.depth());
                long score = (long) shortSide << 40 | (long) longSide << 20 | rect.z;
                if (score < best) { selected = new Rect(rect.x, rect.z, item.width(), item.depth()); best = score; }
            }
            if (selected == null) return null;
            var remaining = new ArrayList<Rect>();
            for (var rect : free) {
                if (selected.x >= rect.right() || selected.right() <= rect.x || selected.z >= rect.bottom() || selected.bottom() <= rect.z) {
                    remaining.add(rect); continue;
                }
                if (selected.x > rect.x) remaining.add(new Rect(rect.x, rect.z, selected.x - rect.x, rect.depth));
                if (selected.right() < rect.right()) remaining.add(new Rect(selected.right(), rect.z, rect.right() - selected.right(), rect.depth));
                if (selected.z > rect.z) remaining.add(new Rect(rect.x, rect.z, rect.width, selected.z - rect.z));
                if (selected.bottom() < rect.bottom()) remaining.add(new Rect(rect.x, selected.bottom(), rect.width, rect.bottom() - selected.bottom()));
            }
            for (int i = remaining.size() - 1; i >= 0; i--)
                for (int j = 0; j < remaining.size(); j++)
                    if (i != j && remaining.get(j).contains(remaining.get(i))) { remaining.remove(i); break; }
            free = remaining;
            placed.add(new Placed(item, selected));
            endX = Math.max(endX, selected.right()); endZ = Math.max(endZ, selected.bottom());
        }
        return new Packing(List.copyOf(placed), endX, endZ);
    }

    private static String accent(int tier) {
        String[] dyes = {"white", "orange", "magenta", "light_blue", "yellow", "lime", "pink", "gray", "light_gray", "cyan", "purple", "blue", "brown", "green", "red", "black"};
        int[] colors = {0xCFD5D6, 0xE06100, 0xA9309F, 0x2389C6, 0xF1AF15, 0x5EA818, 0xD5658E, 0x36393D, 0x7D7D73, 0x157788, 0x64209C, 0x2D2F8F, 0x603B1F, 0x495B24, 0x8E2020, 0x080A0F};
        int target = Hk3ValuesImpl.getVC(tier), nearest = 0, distance = Integer.MAX_VALUE;
        for (int i = 0; i < colors.length; i++) {
            int red = (target >> 16 & 255) - (colors[i] >> 16 & 255), green = (target >> 8 & 255) - (colors[i] >> 8 & 255), blue = (target & 255) - (colors[i] & 255);
            int value = red * red + green * green + blue * blue;
            if (value < distance) { nearest = i; distance = value; }
        }
        return "minecraft:" + dyes[nearest] + "_concrete";
    }

    private static long position(int x, int z) { return (long) x << 32 | z & 0xFFFFFFFFL; }
    private static int hash(int x, int z) { return (x * 73428767 ^ z * 912931) & Integer.MAX_VALUE; }
}
