package com.sirin.hk3gtl.common.recipe.main;

import java.util.List;

 







public final class Hk3MainMaterialAccess {
    private static final int FIRST = 15;
    private static final int LAST = 30;
    private static final int MAX = 14;
    private static final List<List<String>> REQUIREMENTS = List.of(
            List.of("RN-LES", "RN-NSP"), List.of("RN-HRC"), List.of("RN-NSP", "RN-SPM"),
            List.of("RN-SPM", "RN-HLC"), List.of("RN-MCE", "RN-SSQ"), List.of("RN-CPT", "RN-ICA"),
            List.of("RN-QOM", "RN-CQS"), List.of("RN-ERA", "RN-SSQ"), List.of("RN-SSQ"),
            List.of("RN-CQS", "RN-ICA"), List.of("RN-UPR", "RN-SPM"), List.of("RN-SWC", "RN-SPM"),
            List.of("RN-WMS", "RN-WCP"), List.of("RN-WME", "RN-WMS"),
            List.of("RN-CEE", "RN-CQS", "RN-IAA"), List.of("RN-CLE", "RN-WMS", "RN-UPR"));

    private Hk3MainMaterialAccess() {}

    public static int productionPowerTier(int materialTier) {
        validateMaterial(materialTier);
        return materialTier == FIRST ? FIRST : materialTier - 1;
    }

    public static void validateOperation(int materialTier, int powerTier) {
        validateMaterial(materialTier);
        if (powerTier == materialTier || powerTier == materialTier - 1 && materialTier > FIRST
                || materialTier == FIRST && powerTier == MAX) return;
        throw new IllegalArgumentException("主材加工电压越阶或不合法：产物=" + materialTier + "，工况=" + powerTier);
    }

    public static List<String> requirements(int materialTier, int powerTier) {
        validateOperation(materialTier, powerTier);
        return powerTier == MAX ? List.of() : REQUIREMENTS.get(materialTier - FIRST);
    }

    private static void validateMaterial(int materialTier) {
        if (materialTier < FIRST || materialTier > LAST) throw new IllegalArgumentException("未知主材阶级：" + materialTier);
    }
}
