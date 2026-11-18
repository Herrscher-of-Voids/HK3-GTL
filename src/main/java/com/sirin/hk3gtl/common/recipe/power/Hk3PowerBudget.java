package com.sirin.hk3gtl.common.recipe.power;

import java.math.BigInteger;
import java.util.List;

/**
 * 以任意精度核对输入额定值、实际工况与余额，不将多安培或多仓功率当作升压。
 */
public final class Hk3PowerBudget {
    private Hk3PowerBudget() {}

    public record Input(long voltage, long amperage) {
        public Input {
            if (voltage < 0 || amperage < 0) throw new IllegalArgumentException("额定输入不能为负数");
        }
    }

    public record Rating(long highestVoltage, BigInteger totalPower) {}

    public static Rating rating(List<Input> inputs) {
        long highest = 0;
        BigInteger power = BigInteger.ZERO;
        for (Input input : inputs) {
            if (input.amperage() == 0) continue;
            highest = Math.max(highest, input.voltage());
            power = power.add(BigInteger.valueOf(input.voltage()).multiply(BigInteger.valueOf(input.amperage())));
        }
        return new Rating(highest, power);
    }

    public static boolean sufficientRating(Rating rating, long requiredVoltage, BigInteger cost) {
        return requiredVoltage > 0 && cost.compareTo(BigInteger.valueOf(requiredVoltage)) >= 0
                && rating.totalPower().compareTo(cost) >= 0;
    }

    /** 不接受负数或空费用；消费金额与模拟、提交使用同一个精确总额。 */
    public static BigInteger cost(List<Long> amounts) {
        BigInteger total = BigInteger.ZERO;
        for (Long value : amounts) {
            if (value == null || value <= 0) throw new IllegalArgumentException("运行耗电必须为正整数");
            total = total.add(BigInteger.valueOf(value));
        }
        if (total.signum() == 0) throw new IllegalArgumentException("高阶工况缺少耗电");
        return total;
    }
}
