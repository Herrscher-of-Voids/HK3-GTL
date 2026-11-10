package com.sirin.hk3gtl.common.research;

/**
 * 【文件职责／本轮边界】落实获批复合压力、三倍加速上限及逐材料敏感度；S01免压，额外材料向上取整。
 * 【变更记录 #1】2026-09-29 21:06:40（第 1 次编号备注 · 内测5修订100）
 * 删除：取消已被批准规则替代的研究个人独占、旧数值或在线限定分支；历史备注与其他系统保留。
 * 新增／修改：落实获批复合压力、三倍加速上限及逐材料敏感度；S01免压，额外材料向上取整。
 * 用途：接通实际证据→付款→研究完成与权限检查；不授予缺真实证据的课题。
 * 边界：编译和账本测试不代表游戏验收；S02至S05正式结构及未接线课题仍未完成。
 * 追溯：logs/research-mainline-r100；R100_FINAL_RECORD。
 */

/** 【变更记录 · 内测5修订100】2026-09-29：落实已批准研究费用、三公式及离线账户规则。 */

/** 中文说明：该处说明已按当前代码行为整理。*/
public final class Hk3ResearchMath {
    private Hk3ResearchMath() {}

    /** 中文说明：该处说明已按当前代码行为整理。*/
    public static int slots(int lab) {
        if (lab < 1 || lab > 5) throw new IllegalArgumentException("Invalid lab level");
        return 1 << (lab - 1);
    }

    /** 中文说明：该处备注已按当前代码行为整理，不使用问号占位。*/
    public static double pressure(int lab, double gaze, double suppression) {
        slots(lab);
        if (!Double.isFinite(gaze) || gaze < 0 || !Double.isFinite(suppression)
                || suppression < 0 || suppression > 1) throw new IllegalArgumentException("Invalid research pressure");
        return lab == 1 ? 0 : (0.65 * (gaze / (gaze + 100.0)) + 0.35 * (gaze / (gaze + 300.0))) * Math.pow(1 - suppression, 1.25);
    }

    /** 中文说明：该处备注已按当前代码行为整理，不使用问号占位。*/
    public static double speed(int lab, double gaze, double suppression, boolean erosion, boolean wonder) {
        double q = pressure(lab, gaze, suppression), q2 = q * q;
        return Math.min(3, 1 + (erosion ? 0.5 : 0) + (wonder ? 1.5 : 0)) / (1 + 1.2 * q + 1.2 * q2 + 0.6 * q2 * q2);
    }

    /** 中文说明：该处说明已按当前代码行为整理。*/
    public static long materialCount(long base, int lab, double gaze, double suppression) {
        return materialCount(base, lab, gaze, suppression, 1.0);
    }

    /** 仅额外消耗逐项向上取整；基础数保留整数精度，关键材料可明确免压。 */
    public static long materialCount(long base, int lab, double gaze, double suppression, double sensitivity) {
        if (base < 1 || !Double.isFinite(sensitivity) || sensitivity < 0 || sensitivity > 1) throw new IllegalArgumentException("Invalid material sensitivity");
        double q = pressure(lab, gaze, suppression);
        if (q == 0 || sensitivity == 0) return base;
        var extra = java.math.BigDecimal.valueOf(base).multiply(java.math.BigDecimal.valueOf(sensitivity))
                .multiply(java.math.BigDecimal.valueOf(0.4 * q + 0.6 * q * q))
                .setScale(0, java.math.RoundingMode.CEILING).longValueExact();
        return Math.addExact(base, extra);
    }
}
