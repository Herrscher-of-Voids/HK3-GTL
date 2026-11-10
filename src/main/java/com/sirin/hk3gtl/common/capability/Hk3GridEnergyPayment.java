package com.sirin.hk3gtl.common.capability;

import java.math.BigInteger;
import java.util.ArrayList;
import java.util.List;
import java.util.Objects;
import java.util.function.Predicate;
import java.util.function.Supplier;

/**
 * 【文件职责】机器EU配方及直接取电的精确金额适配；后端负责实际账户和团队归属。
 * 【变更记录 #1】2026-10-01 17:33:35（修订138）
 * 删除：无；新增：任意精度求和、可变剩余清单、模拟/实际支付结果及long有符号改量。
 * 修改：不改价、不改后端余额，只有后端确认成功才报告已处理金额。
 * 用途：防合并费用饱和少付、扣款失败伪成功及Long.MIN_VALUE取反溢出；不代表跨EU/HW事务。
 */
public final class Hk3GridEnergyPayment {
    private static final BigInteger LONG_MAX = BigInteger.valueOf(Long.MAX_VALUE);
    private Hk3GridEnergyPayment() {}

    /** remaining沿用GT的null代表全部处理；未处理条目返回独立可变清单。 */
    public record Result(BigInteger transferred, List<Long> remaining) {}

    public static BigInteger total(List<Long> amounts) {
        Objects.requireNonNull(amounts, "缺少EU数量清单");
        BigInteger result = BigInteger.ZERO;
        for (Long value : amounts) {
            if (value == null) continue;
            if (value < 0) throw new IllegalArgumentException("EU配方数量不能为负数");
            result = result.add(BigInteger.valueOf(value));
        }
        return result;
    }

    public static Result input(List<Long> amounts, Supplier<BigInteger> balance,
                               Predicate<BigInteger> change, boolean simulate) {
        BigInteger requested = total(amounts);
        if (requested.signum() == 0) return new Result(BigInteger.ZERO, null);
        BigInteger drawn = available(balance.get()).min(requested);
        if (!simulate && drawn.signum() > 0 && !change.test(drawn.negate())) drawn = BigInteger.ZERO;
        return new Result(drawn, remainder(amounts, drawn));
    }

    public static Result output(List<Long> amounts, Predicate<BigInteger> change, boolean simulate) {
        BigInteger requested = total(amounts);
        if (requested.signum() == 0) return new Result(BigInteger.ZERO, null);
        BigInteger stored = simulate || change.test(requested) ? requested : BigInteger.ZERO;
        return new Result(stored, remainder(amounts, stored));
    }

    /** 跨多个long条目按顺序分摊已付款额，不用单个long强装总剩余量。 */
    private static List<Long> remainder(List<Long> amounts, BigInteger transferred) {
        var result = new ArrayList<Long>();
        BigInteger remainingPaid = transferred;
        for (Long value : amounts) {
            if (value == null || value == 0) continue;
            BigInteger amount = BigInteger.valueOf(value);
            BigInteger paid = amount.min(remainingPaid);
            remainingPaid = remainingPaid.subtract(paid);
            long left = amount.subtract(paid).longValueExact();
            if (left > 0) result.add(left);
        }
        return result.isEmpty() ? null : result;
    }

    /** 正数存入、负数取出；先转BigInteger再取反，允许合法Long.MIN_VALUE请求。 */
    public static long change(long difference, Supplier<BigInteger> balance, Predicate<BigInteger> commit) {
        if (difference == 0) return 0;
        BigInteger actual = BigInteger.valueOf(difference);
        if (difference < 0) actual = available(balance.get()).min(actual.negate()).negate();
        if (actual.signum() == 0 || !commit.test(actual)) return 0;
        return actual.longValueExact();
    }

    public static long visibleBalance(BigInteger balance) {
        return available(balance).min(LONG_MAX).longValueExact();
    }

    private static BigInteger available(BigInteger balance) {
        return Objects.requireNonNull(balance, "电网未返回余额").max(BigInteger.ZERO);
    }
}
