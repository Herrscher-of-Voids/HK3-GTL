package com.sirin.hk3gtl.common.research;

import com.sirin.hk3gtl.common.constants.Hk3Values;

/** 2026-11-11：实体模块只加速获批正式课题；每次实际推进另付1A QSV，不改实验、槽位或研究点。 */
public final class Hk3ErosionResearch {
    private Hk3ErosionResearch() {}

    public static boolean allowed(int lab, boolean researched) {
        return researched && lab >= 2 && lab <= 5;
    }

    public static boolean boost(int lab, boolean researched, boolean installed, boolean enabled,
                                String topic, long baseEU, long availableEU) {
        if (!allowed(lab, researched) || !installed || !enabled || topic == null
                || Hk3LabExperimentRules.get(topic) != null || Hk3ResearchCatalog.bundled().get(topic) == null
                || baseEU < 1 || availableEU < 0) return false;
        try {
            return availableEU >= cost(baseEU, true);
        } catch (ArithmeticException overflow) {
            // long供电接口无法表达附加费时，保留普通研究，不钳制少收。
            return false;
        }
    }

    public static long cost(long baseEU, boolean boosted) {
        if (baseEU < 1) throw new IllegalArgumentException("研究基础用电无效");
        return boosted ? Math.addExact(baseEU, Hk3Values.VA_LONG[19]) : baseEU;
    }
}
