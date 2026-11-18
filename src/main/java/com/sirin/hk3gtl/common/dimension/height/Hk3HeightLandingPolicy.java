package com.sirin.hk3gtl.common.dimension.height;



/** 扩高世界的降落入口至少留出八格净空，只抬高原入口，不改变目的地或降低高度。 */
public final class Hk3HeightLandingPolicy {
    private Hk3HeightLandingPolicy() {}

    public static double arrivalY(double requestedY, int firstFreeY) {
        if (!Double.isFinite(requestedY)) throw new IllegalArgumentException("降落入口高度必须有限");
        return Math.max(requestedY, (double) firstFreeY + 8);
    }
}
