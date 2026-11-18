package com.sirin.hk3gtl.common.campus;

import com.gtl.enhancedcore.common.world.plot.PlannedCampus;

import java.util.ArrayList;
import java.util.Comparator;
import java.util.List;

/** 原园区保持完整，新街区分布在两道闭合环路之间。 */
public final class Hk3CampusIntegratedLayout {
    public record Road(int x1, int z1, int x2, int z2, int halfWidth) {}
    public record Layout(List<Hk3CampusExpansion.Plot> plots, int minX, int minZ, int maxX, int maxZ,
                         List<Road> roads, PlannedCampus.Bounds original) {}
    private record Rect(int x, int z, int width, int depth) {
        int right() { return x + width; }
        int bottom() { return z + depth; }
        boolean contains(Rect r) {
            return x <= r.x && z <= r.z && right() >= r.right() && bottom() >= r.bottom();
        }
    }
    private record Item(Hk3CampusCatalog.Entry entry, int margin, int width, int depth, int order) {}
    private record Part(Item item, int x, int z) {}
    private record Parcel(List<Part> parts, int width, int depth, int side) {}
    private record Placed(Parcel parcel, Rect rect) {}
    private record Candidate(List<Placed> placed, int extentX, int extentZ, double score) {}
    private record Choice(Rect rect, int side, double score) {}

    private Hk3CampusIntegratedLayout() {}

    public static Layout create(List<Hk3CampusCatalog.Entry> entries, PlannedCampus.Bounds original,
                                int surfaceY, Hk3CampusStyle style, PlannedCampus.Bounds aeBounds) {
        int ringHalf = style.kind() == Hk3CampusStyle.Kind.PINK ? 8 : 16;
        int axisHalf = ringHalf;
        int innerMinX = original.minX() - 24, innerMaxX = original.maxX() + 24;
        int innerMinZ = original.minZ() - 24, innerMaxZ = original.maxZ() + 24;
        int clearance = ringHalf + 8;
        var core = new Rect(innerMinX - clearance, innerMinZ - clearance,
                innerMaxX - innerMinX + clearance * 2 + 1, innerMaxZ - innerMinZ + clearance * 2 + 1);
        var outdoor = new ArrayList<Parcel>();
        var indoor = new ArrayList<Item>();
        var aeMachines = new ArrayList<Hk3CampusCatalog.Entry>();
        for (int i = 0; i < entries.size(); i++) {
            var e = entries.get(i);
            if (aeBounds != null && e.machineId().getPath().equals("ae_nexus")) {
                aeMachines.add(e);
                continue;
            }
            boolean hall = Math.max(e.sizeX(), e.sizeZ()) <= 128 && e.sizeY() <= 96;
            int margin = hall ? 14 : 8;
            int width = hall ? Math.max(40, e.sizeX() + 28) + 8 : e.sizeX() + 24;
            int depth = hall ? Math.max(48, e.sizeZ() + 38) + 8 : e.sizeZ() + 28;
            var item = new Item(e, margin, width, depth, i);
            if (hall) indoor.add(item);
            else outdoor.add(new Parcel(List.of(new Part(item, 0, 0)), width, depth, -1));
        }
        indoor.sort(Comparator.<Item>comparingLong(i -> (long) i.width * i.depth).reversed());
        var groups = new ArrayList<List<Item>>();
        long[] groupArea = new long[4];
        for (int i = 0; i < 4; i++) groups.add(new ArrayList<>());
        for (var item : indoor) {
            int side = 0;
            for (int i = 1; i < 4; i++) if (groupArea[i] < groupArea[side]) side = i;
            groups.get(side).add(item);
            groupArea[side] += (long) item.width * item.depth;
        }
        var parcels = new ArrayList<Parcel>();
        for (int side = 0; side < 4; side++) if (!groups.get(side).isEmpty()) parcels.add(compound(groups.get(side), side));
        outdoor.sort(Comparator.<Parcel>comparingLong(p -> (long) p.width * p.depth).reversed()
                .thenComparing(Comparator.comparingInt((Parcel p) -> Math.max(p.width, p.depth)).reversed()));
        parcels.addAll(outdoor);
        long area = parcels.stream().mapToLong(p -> (long) p.width * p.depth).sum();
        int baseX = Math.max(Math.abs(original.minX()), Math.abs(original.maxX()));
        int baseZ = Math.max(Math.abs(original.minZ()), Math.abs(original.maxZ()));
        int base = (int) Math.ceil(Math.sqrt(area + (long) core.width * core.depth) / 2);
        Candidate best = null;
        for (int scale = 105; scale <= 180; scale += 5) {
            for (int aspect = 80; aspect <= 125; aspect += 5) {
                int extentX = Math.max(baseX + 128, align(base * scale * aspect / 10000));
                int extentZ = Math.max(baseZ + 128, align(base * scale / aspect));
                var candidate = place(parcels, core, extentX, extentZ, axisHalf, ringHalf);
                if (candidate != null && (best == null || candidate.score < best.score)) best = candidate;
            }
        }
        var parts = new ArrayList<Part>();
        for (var placed : best.placed) for (var part : placed.parcel.parts)
            parts.add(new Part(part.item, placed.rect.x + part.x, placed.rect.z + part.z));
        parts.sort(Comparator.comparingInt(p -> p.item.order));
        var plots = new ArrayList<Hk3CampusExpansion.Plot>();
        for (var part : parts) {
            var item = part.item;
            var entry = item.entry;
            int x = part.x + 4, z = part.z + 4, width = item.width - 8, depth = item.depth - 8;
            plots.add(new Hk3CampusExpansion.Plot(entry, x, z, x + width - 1, z + depth - 1,
                    x + item.margin + entry.controllerX(), surfaceY + 1 + entry.controllerY(),
                    z + item.margin + entry.controllerZ(), x + width / 2, surfaceY + 1, z + depth + 2));
        }
        var roads = new ArrayList<Road>();
        ring(roads, innerMinX, innerMinZ, innerMaxX, innerMaxZ, ringHalf);
        ring(roads, -best.extentX, -best.extentZ, best.extentX, best.extentZ, ringHalf);
        int north = switch (style.kind()) {
            case MODERN -> -1416;
            case PARK -> -5008;
            default -> original.minZ() + 1;
        };
        int south = switch (style.kind()) {
            case MODERN -> 1368;
            case PARK -> 5007;
            default -> original.maxZ() - 1;
        };
        int west = switch (style.kind()) {
            case MODERN -> innerMinX;
            case PARK -> -319;
            default -> original.minX() + 1;
        };
        int east = switch (style.kind()) {
            case MODERN -> innerMaxX;
            case PARK -> 318;
            default -> original.maxX() - 1;
        };
        roads.add(new Road(0, -best.extentZ, 0, north, axisHalf));
        roads.add(new Road(0, south, 0, best.extentZ, axisHalf));
        roads.add(new Road(-best.extentX, 0, west, 0, axisHalf));
        roads.add(new Road(east, 0, best.extentX, 0, axisHalf));
        switch (style.kind()) {
            case WOODLAND, DENSE -> {
                for (int axis : new int[]{-400, 400}) {
                    roads.add(new Road(axis, innerMinZ, axis, original.minZ() + 1, 12));
                    roads.add(new Road(axis, original.maxZ() - 1, axis, innerMaxZ, 12));
                    roads.add(new Road(innerMinX, axis, original.minX() + 1, axis, 12));
                    roads.add(new Road(original.maxX() - 1, axis, innerMaxX, axis, 12));
                }
            }
            case COMPACT -> {
                for (int axis : new int[]{-72, 88}) {
                    roads.add(new Road(innerMinX, axis, original.minX() + 1, axis, 12));
                    roads.add(new Road(original.maxX() - 1, axis, innerMaxX, axis, 12));
                }
            }
            case MODERN -> {
                for (int axis : new int[]{-1404, 1356}) {
                    roads.add(new Road(innerMinX, axis, -816, axis, 12));
                    roads.add(new Road(815, axis, innerMaxX, axis, 12));
                }
            }
        }
        roads.addAll(Hk3CampusRoadLinks.create(plots, roads, original));
        for (var entry : aeMachines) {
            int x = (aeBounds.minX() + aeBounds.maxX() + 1) / 2 - entry.sizeX() / 2;
            int z = aeBounds.minZ() + 17;
            plots.add(new Hk3CampusExpansion.Plot(entry, x - 4, z - 4, x + entry.sizeX() + 3, z + entry.sizeZ() + 3,
                    x + entry.controllerX(), surfaceY + 1 + entry.controllerY(), z + entry.controllerZ(),
                    x + entry.sizeX() / 2, surfaceY + 1, z - 4));
        }
        int border = ringHalf + 8;
        return new Layout(List.copyOf(plots), -best.extentX - border, -best.extentZ - border,
                best.extentX + border, best.extentZ + border, List.copyOf(roads), original);
    }

    private static Parcel compound(List<Item> items, int side) {
        long area = items.stream().mapToLong(i -> (long) i.width * i.depth).sum();
        int widest = items.stream().mapToInt(Item::width).max().orElseThrow();
        int totalDepth = items.stream().mapToInt(Item::depth).sum();
        Parcel best = null;
        double bestScore = Double.MAX_VALUE;
        for (int percent = 80; percent <= 145; percent += 5) {
            int width = Math.max(widest, (int) Math.ceil(Math.sqrt(area) * percent / 100));
            var free = new ArrayList<Rect>();
            free.add(new Rect(0, 0, width, totalDepth));
            var parts = new ArrayList<Part>();
            int endX = 0, endZ = 0;
            for (var item : items) {
                Rect selected = null;
                long score = Long.MAX_VALUE;
                for (var r : free) if (item.width <= r.width && item.depth <= r.depth) {
                    long next = (long) Math.min(r.width - item.width, r.depth - item.depth) << 40
                            | (long) Math.max(r.width - item.width, r.depth - item.depth) << 20 | r.z;
                    if (next < score) { score = next; selected = new Rect(r.x, r.z, item.width, item.depth); }
                }
                parts.add(new Part(item, selected.x, selected.z));
                free = subtract(free, selected);
                endX = Math.max(endX, selected.right()); endZ = Math.max(endZ, selected.bottom());
            }
            double score = (double) endX * endZ * (1 + Math.abs(Math.log((double) endX / endZ)) * .24);
            if (score < bestScore) { bestScore = score; best = new Parcel(List.copyOf(parts), endX, endZ, side); }
        }
        return best;
    }

    private static Candidate place(List<Parcel> parcels, Rect core, int extentX, int extentZ, int axisHalf, int ringHalf) {
        int edgeX = extentX - ringHalf - 24, edgeZ = extentZ - ringHalf - 24;
        var free = new ArrayList<Rect>();
        free.add(new Rect(-edgeX, -edgeZ, edgeX * 2 + 1, edgeZ * 2 + 1));
        free = subtract(free, core);
        free = subtract(free, new Rect(-axisHalf, -edgeZ, axisHalf * 2 + 1, edgeZ * 2 + 1));
        free = subtract(free, new Rect(-edgeX, -axisHalf, edgeX * 2 + 1, axisHalf * 2 + 1));
        long[] sideArea = new long[4];
        var placed = new ArrayList<Placed>();
        double distance = 0;
        for (var parcel : parcels) {
            Choice best = null;
            for (var r : free) {
                if (parcel.width > r.width || parcel.depth > r.depth) continue;
                for (int x : new int[]{r.x, r.right() - parcel.width}) for (int z : new int[]{r.z, r.bottom() - parcel.depth}) {
                    var at = new Rect(x, z, parcel.width, parcel.depth);
                    for (int side = 0; side < 4; side++) {
                        if (parcel.side >= 0 && parcel.side != side || !onSide(at, core, side)) continue;
                        double cx = x + parcel.width / 2.0, cz = z + parcel.depth / 2.0;
                        double score = cx * cx + cz * cz + sideArea[side] * .7
                                + Math.min(r.width - parcel.width, r.depth - parcel.depth) * 4.0;
                        if (best == null || score < best.score) best = new Choice(at, side, score);
                    }
                }
            }
            if (best == null) return null;
            placed.add(new Placed(parcel, best.rect));
            sideArea[best.side] += (long) parcel.width * parcel.depth;
            double cx = best.rect.x + parcel.width / 2.0, cz = best.rect.z + parcel.depth / 2.0;
            distance += Math.sqrt(cx * cx + cz * cz) * parcel.width * parcel.depth;
            free = subtract(free, best.rect);
        }
        double area = parcels.stream().mapToDouble(p -> (double) p.width * p.depth).sum();
        double score = (double) extentX * extentZ * 4 + distance / area * 500
                + Math.abs(extentX - extentZ) * 200;
        return new Candidate(List.copyOf(placed), extentX, extentZ, score);
    }

    private static boolean onSide(Rect r, Rect core, int side) {
        return switch (side) {
            case 0 -> r.bottom() <= core.z;
            case 1 -> r.x >= core.right();
            case 2 -> r.z >= core.bottom();
            default -> r.right() <= core.x;
        };
    }

    private static ArrayList<Rect> subtract(List<Rect> free, Rect used) {
        var remaining = new ArrayList<Rect>();
        for (var r : free) {
            if (used.x >= r.right() || used.right() <= r.x || used.z >= r.bottom() || used.bottom() <= r.z) {
                remaining.add(r); continue;
            }
            if (used.x > r.x) remaining.add(new Rect(r.x, r.z, used.x - r.x, r.depth));
            if (used.right() < r.right()) remaining.add(new Rect(used.right(), r.z, r.right() - used.right(), r.depth));
            if (used.z > r.z) remaining.add(new Rect(r.x, r.z, r.width, used.z - r.z));
            if (used.bottom() < r.bottom()) remaining.add(new Rect(r.x, used.bottom(), r.width, r.bottom() - used.bottom()));
        }
        for (int i = remaining.size() - 1; i >= 0; i--) for (int j = 0; j < remaining.size(); j++)
            if (i != j && remaining.get(j).contains(remaining.get(i))) { remaining.remove(i); break; }
        return remaining;
    }

    private static void ring(List<Road> roads, int left, int top, int right, int bottom, int half) {
        roads.add(new Road(left, top, right, top, half));
        roads.add(new Road(right, top, right, bottom, half));
        roads.add(new Road(left, bottom, right, bottom, half));
        roads.add(new Road(left, top, left, bottom, half));
    }

    private static int align(int value) { return Math.floorDiv(value + 15, 16) * 16; }
}
