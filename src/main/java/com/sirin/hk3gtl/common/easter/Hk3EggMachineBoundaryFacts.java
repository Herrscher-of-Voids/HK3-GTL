package com.sirin.hk3gtl.common.easter;

import java.util.Map;

/** 2026-11-11：只识别正式设备及成型包络外四格内的真实放置，不授生产或工程资格。 */
public final class Hk3EggMachineBoundaryFacts {
    private static final Map<String, String> MACHINES = Map.of(
            "hk3gtl:soulium_polymerization_die_caster", "i14",
            "hk3gtl:soulium_reconstruction_annealing_furnace", "i15",
            "hk3gtl:soulium_precision_processing_center", "i16",
            "hk3gtl:i19_small_honkai_reactor", "i19",
            "hk3gtl:i20_medium_honkai_reactor", "i20",
            "hk3gtl:i21_large_honkai_reactor", "i21",
            "hk3gtl:i22_ultimate_honkai_reactor", "i22");

    private Hk3EggMachineBoundaryFacts() {}

    public static String layout(String block, String machine) {
        String key = MACHINES.get(machine);
        if (key == null) return null;
        boolean soulium = key.equals("i14") || key.equals("i15") || key.equals("i16");
        return (soulium ? block.equals("minecraft:crafting_table") : block.equals("minecraft:tnt")) ? key : null;
    }

    public static int caseFor(String block, String machine, boolean formed, boolean error, Box bounds,
                              int x, int y, int z) {
        if (!formed || error || layout(block, machine) == null || bounds == null || !bounds.nearOutside(x, y, z)) return 0;
        return block.equals("minecraft:crafting_table") ? 78 : 80;
    }

    public record Box(int minX, int minY, int minZ, int maxX, int maxY, int maxZ) {
        public Box {
            if (minX > maxX || minY > maxY || minZ > maxZ) throw new IllegalArgumentException("设备边界颠倒");
        }

        public boolean nearOutside(int x, int y, int z) {
            long dx = gap(x, minX, maxX), dy = gap(y, minY, maxY), dz = gap(z, minZ, maxZ);
            return dx <= 4 && dy <= 4 && dz <= 4 && dx + dy + dz > 0 && dx * dx + dy * dy + dz * dz <= 16;
        }

        private static long gap(int value, int min, int max) {
            return value < min ? (long) min - value : value > max ? (long) value - max : 0;
        }

    }
}
