package com.sirin.hk3gtl.common.research;













public final class Hk3ResearchMath {
    private Hk3ResearchMath() {}

    public static int slots(int lab) {
        if (lab < 1 || lab > 5) throw new IllegalArgumentException("Invalid lab level");
        return 1 << (lab - 1);
    }

    public static double pressure(int lab, double gaze, double suppression) {
        slots(lab);
        if (!Double.isFinite(gaze) || gaze < 0 || !Double.isFinite(suppression)
                || suppression < 0 || suppression > 1) throw new IllegalArgumentException("Invalid research pressure");
        return lab == 1 ? 0 : (0.65 * (gaze / (gaze + 100.0)) + 0.35 * (gaze / (gaze + 300.0))) * Math.pow(1 - suppression, 1.25);
    }

    public static double speed(int lab, double gaze, double suppression, boolean erosion, boolean wonder) {
        double q = pressure(lab, gaze, suppression), q2 = q * q;
        return Math.min(3, 1 + (erosion ? 0.5 : 0) + (wonder ? 1.5 : 0)) / (1 + 1.2 * q + 1.2 * q2 + 0.6 * q2 * q2);
    }

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
