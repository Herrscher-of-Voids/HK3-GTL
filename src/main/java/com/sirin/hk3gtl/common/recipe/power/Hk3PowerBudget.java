package com.sirin.hk3gtl.common.recipe.power;

import java.math.BigInteger;
import java.util.List;

/**
 * 【文件职责】以任意精度核对输入额定值、实际工况与余额，不将多安培或多仓功率当作升压。
 * 【变更记录 #1】2026-10-17 16:27:36（第1次备注 · 修订165）
 * 删除：无；新增：单路额定电压、总额定功率和精确耗电的独立算术校验。
 * 修改：所有乘加先转BigInteger；用途：配方服务端守卫与边界测试共用，检查本身不扣电。
 */
/**
 * 【变更记录 #2】2026-10-17 16:43:35（第2次备注 · 修订165）
 * 删除：将最高单路电压作为新增准入限制的判断。
 * 新增：无；修改：功率校验继承现有GTL的Σ(V×A)，阶段基准和实际金额独立核对。
 * 用途：保留long上界精度，不擅自限制已批准由MAX现有设备承载的启动路线。
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
