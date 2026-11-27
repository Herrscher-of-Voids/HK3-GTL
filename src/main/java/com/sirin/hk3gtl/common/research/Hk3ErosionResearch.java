package com.sirin.hk3gtl.common.research;

import com.sirin.hk3gtl.common.constants.Hk3Values;

/** 实体模块只加速获批正式课题，不改实验、槽位或研究点。 */
public final class Hk3ErosionResearch {
    public static final int MAX_MODULES = 3;
    private Hk3ErosionResearch() {}

    public static boolean allowed(int lab, boolean researched) {
        return researched && lab >= 2 && lab <= 5;
    }

    public static int eligibleModules(int lab, boolean researched, int installed, boolean enabled,
                                      String topic, boolean wonder) {
        if (!allowed(lab, researched) || installed == 0 || !enabled || topic == null
                || Hk3LabExperimentRules.get(topic) != null || Hk3ResearchCatalog.bundled().get(topic) == null) return 0;
        return wonder ? 1 : installed;
    }

    public static int poweredModules(int eligible, long baseEU, long availableEU) {
        if (baseEU < 1 || availableEU <= baseEU) return 0;
        return (int) Math.min(eligible, (availableEU - baseEU) / Hk3Values.VA_LONG[19]);
    }

    public static boolean boost(int lab, boolean researched, boolean installed, boolean enabled,
                                String topic, long baseEU, long availableEU) {
        int eligible = eligibleModules(lab, researched, installed ? 1 : 0, enabled, topic, false);
        return poweredModules(eligible, baseEU, availableEU) > 0;
    }

    public static long cost(long baseEU, boolean boosted) {
        return cost(baseEU, boosted ? 1 : 0);
    }

    public static long cost(long baseEU, int modules) {
        if (baseEU < 1) throw new IllegalArgumentException("研究基础用电无效");
        return Math.addExact(baseEU, modules * Hk3Values.VA_LONG[19]);
    }
}
