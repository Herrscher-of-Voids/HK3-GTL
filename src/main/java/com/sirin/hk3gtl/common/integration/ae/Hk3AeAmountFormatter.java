package com.sirin.hk3gtl.common.integration.ae;

import java.math.BigDecimal;
import java.math.BigInteger;
import java.math.MathContext;
import java.math.RoundingMode;

public final class Hk3AeAmountFormatter {
    private static final String[] SUFFIXES = {"", "k", "M", "B", "T", "P", "E", "Z", "Y", "R", "Q"};
    private static final BigDecimal THOUSAND = BigDecimal.valueOf(1000);
    private static final BigDecimal SCIENTIFIC_THRESHOLD = BigDecimal.TEN.pow(30);

    private Hk3AeAmountFormatter() {}

    public static String compact(BigInteger value) {
        return compact(new BigDecimal(value));
    }

    public static String compact(BigDecimal value) {
        if (value.abs().compareTo(BigDecimal.ONE) < 0) return value.stripTrailingZeros().toPlainString();
        if (value.abs().compareTo(SCIENTIFIC_THRESHOLD) > 0) {
            var rounded = value.round(new MathContext(2, RoundingMode.HALF_UP));
            int exponent = rounded.precision() - rounded.scale() - 1;
            return rounded.movePointLeft(exponent).stripTrailingZeros().toPlainString() + "e" + exponent;
        }
        int group = (value.precision() - value.scale() - 1) / 3;
        var scaled = value.movePointLeft(group * 3).setScale(1, RoundingMode.HALF_UP);
        if (scaled.abs().compareTo(THOUSAND) >= 0) {
            group++;
            scaled = scaled.movePointLeft(3).setScale(1, RoundingMode.HALF_UP);
        }
        return scaled.stripTrailingZeros().toPlainString() + SUFFIXES[group];
    }
}
