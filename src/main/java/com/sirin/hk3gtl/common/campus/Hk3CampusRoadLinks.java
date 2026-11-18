package com.sirin.hk3gtl.common.campus;

import com.gtl.enhancedcore.common.world.plot.PlannedCampus;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.Comparator;
import java.util.List;
import java.util.PriorityQueue;
import java.util.TreeSet;

final class Hk3CampusRoadLinks {
    private record Area(int left, int top, int right, int bottom) {}
    private record Step(int node, int distance) {}

    private Hk3CampusRoadLinks() {}

    static List<Hk3CampusIntegratedLayout.Road> create(List<Hk3CampusExpansion.Plot> plots,
            List<Hk3CampusIntegratedLayout.Road> roads, PlannedCampus.Bounds original) {
        var xCoordinates = new TreeSet<Integer>();
        var zCoordinates = new TreeSet<Integer>();
        var obstacles = new ArrayList<Area>();
        obstacles.add(new Area(original.minX() - 2, original.minZ() - 2,
                original.maxX() + 2, original.maxZ() + 2));
        for (var plot : plots) {
            xCoordinates.add(plot.minX() - 4); xCoordinates.add(plot.maxX() + 5);
            zCoordinates.add(plot.minZ() - 4); zCoordinates.add(plot.maxZ() + 5);
            obstacles.add(new Area(plot.minX() - 2, plot.minZ() - 2, plot.maxX() + 2, plot.maxZ() + 2));
        }
        for (var road : roads) {
            xCoordinates.add(road.x1()); xCoordinates.add(road.x2());
            zCoordinates.add(road.z1()); zCoordinates.add(road.z2());
        }
        int[] xs = xCoordinates.stream().mapToInt(Integer::intValue).toArray();
        int[] zs = zCoordinates.stream().mapToInt(Integer::intValue).toArray();
        int height = zs.length, count = xs.length * height;
        var edges = new byte[count];
        var distance = new int[count];
        var previous = new int[count];
        Arrays.fill(distance, Integer.MAX_VALUE);
        Arrays.fill(previous, -1);
        var queue = new PriorityQueue<Step>(Comparator.comparingInt(Step::distance));
        for (int ix = 0; ix < xs.length; ix++) for (int iz = 0; iz < height; iz++) {
            int node = ix * height + iz, x = xs[ix], z = zs[iz];
            if (!clear(x, z, x, z, obstacles)) continue;
            if (ix + 1 < xs.length && clear(x, z, xs[ix + 1], z, obstacles)) {
                edges[node] |= 1; edges[node + height] |= 2;
            }
            if (iz + 1 < height && clear(x, z, x, zs[iz + 1], obstacles)) {
                edges[node] |= 4; edges[node + 1] |= 8;
            }
            for (var road : roads) {
                if (road.z1() == road.z2() && z == road.z1() && x >= road.x1() && x <= road.x2()
                        || road.x1() == road.x2() && x == road.x1() && z >= road.z1() && z <= road.z2()) {
                    source(node, distance, previous, queue);
                    break;
                }
            }
        }
        var links = new ArrayList<Hk3CampusIntegratedLayout.Road>();
        var connected = new boolean[plots.size()];
        int remaining = plots.size();
        while (remaining > 0) {
            var step = queue.remove();
            int node = step.node();
            if (step.distance() != distance[node]) continue;
            int ix = node / height, iz = node % height, x = xs[ix], z = zs[iz];
            for (int i = 0; i < plots.size(); i++) {
                if (connected[i] || !perimeter(plots.get(i), x, z)) continue;
                trace(node, previous, xs, zs, height, links);
                for (int at = node; at >= 0;) {
                    int parent = previous[at];
                    source(at, distance, previous, queue);
                    at = parent;
                }
                connected[i] = true;
                remaining--;
                var plot = plots.get(i);
                for (int px = 0; px < xs.length; px++) for (int pz = 0; pz < height; pz++)
                    if (perimeter(plot, xs[px], zs[pz]) && clear(xs[px], zs[pz], xs[px], zs[pz], obstacles))
                        source(px * height + pz, distance, previous, queue);
            }
            if ((edges[node] & 1) != 0) relax(node, node + height, xs[ix + 1] - x, distance, previous, queue);
            if ((edges[node] & 2) != 0) relax(node, node - height, x - xs[ix - 1], distance, previous, queue);
            if ((edges[node] & 4) != 0) relax(node, node + 1, zs[iz + 1] - z, distance, previous, queue);
            if ((edges[node] & 8) != 0) relax(node, node - 1, z - zs[iz - 1], distance, previous, queue);
        }
        return links;
    }

    private static boolean clear(int x1, int z1, int x2, int z2, List<Area> obstacles) {
        for (var area : obstacles)
            if (x1 <= area.right() && x2 >= area.left() && z1 <= area.bottom() && z2 >= area.top()) return false;
        return true;
    }

    private static boolean perimeter(Hk3CampusExpansion.Plot plot, int x, int z) {
        int left = plot.minX() - 4, right = plot.maxX() + 5, top = plot.minZ() - 4, bottom = plot.maxZ() + 5;
        return x >= left && x <= right && z >= top && z <= bottom
                && (x == left || x == right || z == top || z == bottom);
    }

    private static void source(int node, int[] distance, int[] previous, PriorityQueue<Step> queue) {
        if (distance[node] == 0) return;
        distance[node] = 0;
        previous[node] = -1;
        queue.add(new Step(node, 0));
    }

    private static void relax(int from, int to, int length, int[] distance, int[] previous, PriorityQueue<Step> queue) {
        int next = distance[from] + length;
        if (next >= distance[to]) return;
        distance[to] = next;
        previous[to] = from;
        queue.add(new Step(to, next));
    }

    private static void trace(int node, int[] previous, int[] xs, int[] zs, int height,
                              List<Hk3CampusIntegratedLayout.Road> links) {
        int start = node, at = node, direction = 0;
        while (previous[at] >= 0) {
            int parent = previous[at], nextDirection = parent - at;
            if (direction != 0 && direction != nextDirection) {
                link(start, at, xs, zs, height, links);
                start = at;
            }
            direction = nextDirection;
            at = parent;
        }
        if (at != start) link(start, at, xs, zs, height, links);
    }

    private static void link(int from, int to, int[] xs, int[] zs, int height,
                             List<Hk3CampusIntegratedLayout.Road> links) {
        int x1 = xs[from / height], z1 = zs[from % height], x2 = xs[to / height], z2 = zs[to % height];
        links.add(new Hk3CampusIntegratedLayout.Road(Math.min(x1, x2), Math.min(z1, z2),
                Math.max(x1, x2), Math.max(z1, z2), 2));
    }
}
