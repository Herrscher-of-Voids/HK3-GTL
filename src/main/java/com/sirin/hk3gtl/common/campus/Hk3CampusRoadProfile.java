package com.sirin.hk3gtl.common.campus;

import com.gtl.enhancedcore.common.world.plot.CampusPresetRegistry;
import com.gtl.enhancedcore.common.world.plot.CompactPlannedCampus;
import com.gtl.enhancedcore.common.world.plot.DensePlannedCampus;
import com.gtl.enhancedcore.common.world.plot.FileCampus;
import com.gtl.enhancedcore.common.world.plot.LegacyPlannedCampus;
import com.gtl.enhancedcore.common.world.plot.ParkPlannedCampus;
import com.gtl.enhancedcore.common.world.plot.PlannedCampus;

/** 从原预设无路口路段采样，沿用道路横断面与24格标线相位。 */
final class Hk3CampusRoadProfile {
    @FunctionalInterface
    private interface Surface { String at(int x, int z); }

    private final String[][] main;
    private final String[][] secondary;

    Hk3CampusRoadProfile(Hk3CampusStyle style) {
        if (style.kind() == Hk3CampusStyle.Kind.FACTORY || style.kind() == Hk3CampusStyle.Kind.PINK) {
            var definition = CampusPresetRegistry.definitions().stream()
                    .filter(value -> value.architectureResource().equals(style.architectureResource())).findFirst().orElseThrow();
            var campus = FileCampus.of(definition.id());
            boolean pink = style.kind() == Hk3CampusStyle.Kind.PINK;
            main = capture((x, z) -> campus.surfaceBlock(null, x, z), 600, 0, pink ? -7 : -16, pink ? 15 : 32);
            secondary = main;
            return;
        }
        Surface surface = switch (style.kind()) {
            case MODERN -> (x, z) -> LegacyPlannedCampus.surfaceBlock(null, x, z);
            case PARK -> (x, z) -> ParkPlannedCampus.surfaceBlock(null, x, z);
            case COMPACT -> (x, z) -> CompactPlannedCampus.surfaceBlock(null, x, z);
            case DENSE -> (x, z) -> DensePlannedCampus.surfaceBlock(null, x, z);
            case WOODLAND -> (x, z) -> PlannedCampus.surfaceBlock(null, x, z);
            default -> (x, z) -> style.road();
        };
        int anchor = style.kind() == Hk3CampusStyle.Kind.MODERN || style.kind() == Hk3CampusStyle.Kind.PARK ? 192 : 600;
        int sideAxis = switch (style.kind()) {
            case WOODLAND, DENSE -> 400;
            case COMPACT -> 88;
            case MODERN, PARK -> 96;
            default -> 0;
        };
        main = capture(surface, anchor, 0, -16, 32);
        secondary = capture(surface, anchor, sideAxis, -12, 24);
    }

    String crossAt(int lateral, int longitudinal, int halfWidth) {
        var profile = halfWidth >= 16 ? main : secondary;
        int folded = longitudinal < 0 ? -longitudinal - 1 : longitudinal;
        var row = profile[Math.floorMod(folded, 24)];
        return row[(lateral + halfWidth) * row.length / (halfWidth * 2)];
    }

    private static String[][] capture(Surface surface, int anchor, int axis, int first, int width) {
        var profile = new String[24][width];
        for (int along = 0; along < 24; along++)
            for (int across = 0; across < width; across++)
                profile[along][across] = surface.at(anchor + along, axis + first + across);
        return profile;
    }
}
