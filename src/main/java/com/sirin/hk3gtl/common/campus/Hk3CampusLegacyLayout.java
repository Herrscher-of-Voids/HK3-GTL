package com.sirin.hk3gtl.common.campus;

import java.util.ArrayList;
import java.util.List;

/** r254测试园区保留原位置及传送顺序。 */
final class Hk3CampusLegacyLayout {
    private static final int MARGIN = 16, ROAD = 32, ROW_WIDTH = 4096;

    private Hk3CampusLegacyLayout() {}

    static Hk3CampusExpansion.Plan plan(int minX, int minZ, int maxX, int maxZ, int surfaceY) {
        int startX = Math.floorDiv(maxX + 97 + 15, 16) * 16;
        int startZ = Math.floorDiv(minZ, 16) * 16;
        int x = startX + ROAD, z = startZ + ROAD, rowDepth = 0, endX = x;
        var plots = new ArrayList<Hk3CampusExpansion.Plot>();
        for (var entry : Hk3CampusCatalog.entries(1)) {
            int width = entry.sizeX() + MARGIN * 2, depth = entry.sizeZ() + MARGIN * 2;
            if (x > startX + ROAD && x + width > startX + ROW_WIDTH) {
                x = startX + ROAD; z += rowDepth + ROAD; rowDepth = 0;
            }
            plots.add(new Hk3CampusExpansion.Plot(entry, x, z, x + width - 1, z + depth - 1,
                    x + MARGIN + entry.controllerX(), surfaceY + 1 + entry.controllerY(), z + MARGIN + entry.controllerZ(),
                    x + MARGIN + entry.sizeX() / 2, surfaceY + 1, z + depth + 8));
            x += width + ROAD; endX = Math.max(endX, x); rowDepth = Math.max(rowDepth, depth);
        }
        int endZ = z + rowDepth + ROAD;
        int bridgeZ = Math.max(minZ + ROAD, Math.min(0, maxZ - ROAD));
        return new Hk3CampusExpansion.Plan(List.copyOf(plots), startX, Math.min(startZ, bridgeZ - ROAD), endX,
                Math.max(endZ, bridgeZ + ROAD), surfaceY, maxX + 1, startX, bridgeZ);
    }
}
