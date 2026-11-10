package com.sirin.hk3gtl.common.machine.research;

/** 2026-10-15：仅采集塔四个批准阶段可继承前阶工艺；与研究权限、付费或成果授予无关。 */
public final class Hk3IndustrialProcessRoles {
    private Hk3IndustrialProcessRoles() {}

    public static boolean acceptsCollectionRole(String role, int declaredStages) {
        if (declaredStages < 1 || declaredStages > 4 || role == null || !role.matches("I01-[1-4]")) return false;
        return role.charAt(4) - '0' <= declaredStages;
    }
}
