package com.sirin.hk3gtl.common.easter;

/** 2026-11-11：沿用091／095／096原条件，只接受对应真实成功事务。 */
public final class Hk3EggNativeMachineFacts {
    public static final String QUANTUM_MACHINE = "hk3gtl:i24_quantum_anomaly_observation_array";
    public static final String FLAGSHIP_MACHINE = "hk3gtl:hyperion_flagship";

    private Hk3EggNativeMachineFacts() {}

    public static boolean boat(boolean spawned, boolean boat, boolean water, String machine,
                               boolean formed, boolean error, Box bounds, int x, int y, int z) {
        return spawned && boat && water && QUANTUM_MACHINE.equals(machine) && formed && !error
                && bounds != null && bounds.nearOutside(x, y, z, 8);
    }

    public static boolean ice(boolean placedIce, boolean fusion, boolean formed, boolean error,
                              Box bounds, int x, int y, int z) {
        return placedIce && fusion && formed && !error && bounds != null && bounds.nearOutside(x, y, z, 4);
    }

    public static boolean flagship(boolean succeeded, boolean flagship, String machine, boolean soulium, int count) {
        return succeeded && flagship && FLAGSHIP_MACHINE.equals(machine) && soulium && count > 0;
    }

    public static boolean waterSurface(boolean water, double boatY, int blockY, float fluidHeight) {
        return water && Double.isFinite(boatY) && Float.isFinite(fluidHeight) && fluidHeight > 0 && fluidHeight <= 1
                && Math.abs(boatY - ((double) blockY + fluidHeight)) <= 0.00001;
    }

    public record Box(int minX, int minY, int minZ, int maxX, int maxY, int maxZ) {
        public Box {
            if (minX > maxX || minY > maxY || minZ > maxZ) throw new IllegalArgumentException("设备边界颠倒");
        }

        public boolean nearOutside(int x, int y, int z, int radius) {
            if (radius != 4 && radius != 8) return false;
            long dx = gap(x, minX, maxX), dy = gap(y, minY, maxY), dz = gap(z, minZ, maxZ);
            return dx <= radius && dy <= radius && dz <= radius && dx + dy + dz > 0
                    && dx * dx + dy * dy + dz * dz <= (long) radius * radius;
        }

        private static long gap(int value, int min, int max) {
            return value < min ? (long) min - value : value > max ? (long) value - max : 0;
        }
    }
}
