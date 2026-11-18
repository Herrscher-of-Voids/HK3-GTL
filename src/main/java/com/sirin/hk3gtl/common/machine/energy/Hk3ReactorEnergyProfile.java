package com.sirin.hk3gtl.common.machine.energy;

import com.sirin.hk3gtl.common.constants.Hk3Tiers;
import com.sirin.hk3gtl.common.recipe.Hk3ResearchProcessPlans;

import java.math.BigInteger;
import java.util.Collections;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.Set;

/**
 * I19-I22 当前工艺计划的只读能源合同。
 */
public record Hk3ReactorEnergyProfile(Hk3ResearchProcessPlans.Plan plan) {
    private static final Set<String> REACTOR_ROLES = Set.of("I19", "I20", "I21", "I22");
    private static final Map<String, Hk3ReactorEnergyProfile> PROFILES;

    static {
        Map<String, Hk3ReactorEnergyProfile> values = new LinkedHashMap<>();
        Set<String> roles = new java.util.HashSet<>();
        for (Hk3ResearchProcessPlans.Plan plan : Hk3ResearchProcessPlans.all()) {
            if (!REACTOR_ROLES.contains(plan.role())) continue;
            Hk3ReactorEnergyProfile profile = new Hk3ReactorEnergyProfile(plan);
            if (values.putIfAbsent(profile.recipeId(), profile) != null) {
                throw new IllegalStateException("反应堆能源配方ID重复：" + profile.recipeId());
            }
            roles.add(profile.role());
        }
        if (!roles.equals(REACTOR_ROLES)) throw new IllegalStateException("I19-I22能源计划不完整");
        PROFILES = Collections.unmodifiableMap(values);
    }

    public Hk3ReactorEnergyProfile {
        Objects.requireNonNull(plan, "缺少反应堆工业计划");
        if (!REACTOR_ROLES.contains(plan.role()) || !"output".equals(plan.energyDirection())
                || plan.inputs().isEmpty() || plan.outputs().isEmpty()
                || plan.ticks() <= 0 || plan.energyTier() < Hk3Tiers.HBV || plan.energyTier() > Hk3Tiers.CEV) {
            throw new IllegalArgumentException("反应堆能源合同无效");
        }
    }

    public String role() {
        return plan.role();
    }

    public String recipeId() {
        return plan.id();
    }

    public int voltageTier() {
        return plan.energyTier();
    }

    public int totalTicks() {
        return plan.ticks();
    }

    public boolean provisional() {
        return plan.provisional();
    }

    public static Map<String, Hk3ReactorEnergyProfile> all() {
        return PROFILES;
    }

    public static List<Hk3ReactorEnergyProfile> forRole(String role) {
        return PROFILES.values().stream().filter(profile -> profile.role().equals(role)).toList();
    }

    public static Hk3ReactorEnergyProfile get(String recipeId) {
        Hk3ReactorEnergyProfile profile = PROFILES.get(recipeId);
        if (profile == null) throw new IllegalArgumentException("未登记反应堆能源配方：" + recipeId);
        return profile;
    }

    public BigInteger euPerTick() {
        return BigInteger.valueOf(plan.outputEut());
    }

    public BigInteger totalEu() {
        return euPerTick().multiply(BigInteger.valueOf(totalTicks()));
    }
}
