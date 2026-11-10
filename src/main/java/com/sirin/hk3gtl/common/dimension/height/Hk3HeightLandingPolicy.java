package com.sirin.hk3gtl.common.dimension.height;

/** 【变更记录 #1】2026-10-31 00:46:39（第1次备注 · 修订187）：删除无；新增有限高度与八格净空策略；修改原入口只上移不下移；用途：供Ad Astra入口兼容和生产回归共用。 */

/** 扩高世界的降落入口至少留出八格净空，只抬高原入口，不改变目的地或降低高度。 */
public final class Hk3HeightLandingPolicy {
    private Hk3HeightLandingPolicy() {}

    public static double arrivalY(double requestedY, int firstFreeY) {
        if (!Double.isFinite(requestedY)) throw new IllegalArgumentException("降落入口高度必须有限");
        return Math.max(requestedY, (double) firstFreeY + 8);
    }
}
