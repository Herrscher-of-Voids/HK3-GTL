package com.sirin.hk3gtl.common.util;

import java.math.BigDecimal;
import java.math.BigInteger;
import java.math.MathContext;
import java.math.RoundingMode;

/**
 * 【文件职责】
 * - 统一格式化任意精度崩坏能数值，避免 GUI、日志和明细页面各自截断 BigInteger。
 * - 关键调用链：机器 GUI/诊断日志 -> 本工具 -> 紧凑、科学、完整分组或工程计数文本。
 *
 * 【变更记录 #1】2026-07-19 19:16:14（第 1 次备注 · 内测四第 31 次更新）
 * - 删除：
 *   1) 无；本文件为 BigInteger 崩坏能网络新增的格式化边界。
 * - 新增：
 *   1) formatCompact 用于空间有限的机器 GUI，常用 SI 后缀保留最多两位小数，超过 Y 后转科学计数法。
 *   2) formatScientific 用于日志和超大值诊断，输出三位有效数字及十进制指数。
 *   3) formatFullGrouped 用于 tooltip/明细，完整保留所有十进制位并按三位分组。
 *   4) formatEngineering 用于每 tick 速率等技术信息，指数固定为三的倍数。
 * - 修改：
 *   1) 无历史逻辑；所有入口统一把 null 和非正值显示为 0。
 * - 用途：
 *   1) 保证任意精度余额只改变显示形式，不改变底层数值或计费精度。
 */
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
