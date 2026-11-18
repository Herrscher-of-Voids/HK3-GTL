package com.sirin.hk3gtl.common.multiblock.build;

 






final class Hk3W01BuildBudget {
    static final int BUILD_STEPS = 32768;
    static final int PREPARATION_STEPS = 65536;
    private Hk3W01BuildBudget() {}

    static long nanos(float averageTickMillis) {
        if (!Float.isFinite(averageTickMillis) || averageTickMillis < 0) return 4_000_000L;
        double availableMillis = Math.max(2.0, Math.min(12.0, 40.0 - averageTickMillis));
        return (long) (availableMillis * 1_000_000L);
    }

    static long nanos(float serverMillis,float frameMillis) {
        long clientLimit=frameMillis>40?1_000_000L:frameMillis>25?3_000_000L:frameMillis>16.7?6_000_000L:12_000_000L;
        return Math.min(nanos(serverMillis),clientLimit);
    }

    static int placementLimit(float frameMillis) {
        return frameMillis>40?256:frameMillis>25?1024:frameMillis>16.7?4096:16384;
    }
}
