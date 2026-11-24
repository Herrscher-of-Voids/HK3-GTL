package com.sirin.hk3gtl.common.integration.ae.exact;

import java.math.BigInteger;
import java.util.Map;
import java.util.Optional;

/** 仅接受已确认机器语义的概率元数据；期望次数只是投料建议，不代表产出保证。 */
public record Hk3ExactProbabilityPlan<K>(String metadataId, BigInteger target,
        BigInteger chance, BigInteger chanceScale, BigInteger successYield,
        Map<K, BigInteger> inputsPerAttempt, Map<K, BigInteger> inputCaps,
        BigInteger attemptLimit, int maxBatch) {
    public Hk3ExactProbabilityPlan {
        inputsPerAttempt = Map.copyOf(inputsPerAttempt);
        inputCaps = Map.copyOf(inputCaps);
        if (metadataId.isBlank() || target.signum() <= 0 || chanceScale.signum() <= 0
                || chance.signum() < 0
                || successYield.signum() <= 0 || attemptLimit.signum() <= 0 || maxBatch <= 0) {
            throw new IllegalArgumentException("概率计划参数无效");
        }
        for (var input : inputsPerAttempt.entrySet()) {
            BigInteger cap = inputCaps.get(input.getKey());
            if (input.getValue().signum() <= 0 || cap == null || cap.signum() < 0) {
                throw new IllegalArgumentException("每种投料必须有非负预算及正数单次耗量");
            }
        }
        if (inputCaps.values().stream().anyMatch(value -> value.signum() < 0)) {
            throw new IllegalArgumentException("投料预算不能为负数");
        }
    }

    public BigInteger attemptCapacity() {
        BigInteger capacity = attemptLimit;
        for (var input : inputsPerAttempt.entrySet()) {
            capacity = capacity.min(inputCaps.get(input.getKey()).divide(input.getValue()));
        }
        return capacity;
    }

    public Optional<BigInteger> expectedAttempts() {
        return expectedAttempts(target);
    }

    Optional<BigInteger> expectedAttempts(BigInteger remaining) {
        if (chance.signum() == 0) return Optional.empty();
        BigInteger successes = remaining.add(successYield).subtract(BigInteger.ONE).divide(successYield);
        BigInteger dividend = successes.multiply(chanceScale);
        return Optional.of(dividend.add(chance).subtract(BigInteger.ONE).divide(chance));
    }

    public Map<K, BigInteger> allocatedInputs(BigInteger attempts) {
        if (attempts.signum() < 0 || attempts.compareTo(attemptCapacity()) > 0) {
            throw new IllegalArgumentException("投料次数超出预算");
        }
        var allocated = new java.util.LinkedHashMap<K, BigInteger>();
        inputsPerAttempt.forEach((key, cost) -> allocated.put(key, cost.multiply(attempts)));
        return Map.copyOf(allocated);
    }
}
