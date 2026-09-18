package com.sirin.hk3gtl.common.util;

import java.math.BigDecimal;
import java.math.BigInteger;
import java.math.MathContext;
import java.math.RoundingMode;


public final class Hk3HonkaiEnergyFormatter {

    private static final BigInteger THOUSAND = BigInteger.valueOf(1_000L);
    private static final String[] COMPACT_SUFFIXES = {"", "K", "M", "G", "T", "P", "E", "Z", "Y"};

    private Hk3HonkaiEnergyFormatter() {}

    public static String formatCompact(BigInteger value) {
        BigInteger normalized = normalize(value);
        if (normalized.compareTo(THOUSAND) < 0) return normalized.toString();

        int unitIndex = (normalized.toString().length() - 1) / 3;
        if (unitIndex >= COMPACT_SUFFIXES.length) return formatScientific(normalized);

        BigDecimal divisor = BigDecimal.valueOf(1_000L).pow(unitIndex);
        BigDecimal compact = new BigDecimal(normalized).divide(divisor, 2, RoundingMode.DOWN);
        return compact.stripTrailingZeros().toPlainString() + COMPACT_SUFFIXES[unitIndex];
    }

    public static String formatScientific(BigInteger value) {
        BigInteger normalized = normalize(value);
        String digits = normalized.toString();
        if (digits.length() <= 6) return digits;

        int exponent = digits.length() - 1;
        BigDecimal mantissa = new BigDecimal(normalized)
                .movePointLeft(exponent)
                .round(new MathContext(3, RoundingMode.HALF_UP));
        if (mantissa.compareTo(BigDecimal.TEN) >= 0) {
            mantissa = mantissa.movePointLeft(1);
            exponent++;
        }
        return mantissa.stripTrailingZeros().toPlainString() + "×10^" + exponent;
    }

    public static String formatFullGrouped(BigInteger value) {
        StringBuilder grouped = new StringBuilder(normalize(value).toString());
        for (int index = grouped.length() - 3; index > 0; index -= 3) {
            grouped.insert(index, ',');
        }
        return grouped.toString();
    }

    public static String formatEngineering(BigInteger value, int significantDigits) {
        BigInteger normalized = normalize(value);
        int precision = Math.max(1, significantDigits);
        return new BigDecimal(normalized)
                .round(new MathContext(precision, RoundingMode.HALF_UP))
                .toEngineeringString();
    }

    private static BigInteger normalize(BigInteger value) {
        return value == null || value.signum() <= 0 ? BigInteger.ZERO : value;
    }
}
