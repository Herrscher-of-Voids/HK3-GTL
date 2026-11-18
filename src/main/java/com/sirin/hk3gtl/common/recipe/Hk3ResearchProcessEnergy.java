package com.sirin.hk3gtl.common.recipe;

import com.gregtechceu.gtceu.api.recipe.GTRecipeType;
import com.sirin.hk3gtl.common.machine.wonder.Hk3WonderCatalog;
import java.util.Arrays;
import java.util.HashMap;
import java.util.Map;
import java.util.Set;

/** 工业工艺的能源方向与可执行电压上限；建筑名义档位由机器注册保留。 */
public final class Hk3ResearchProcessEnergy {
    private static final Set<String> GENERATORS = Set.of("I19", "I20", "I21", "I22", "I23");
    private static final Map<String, Integer> RATED_TIERS = Map.ofEntries(
            Map.entry("I01-1", 15), Map.entry("I01-2", 19), Map.entry("I01-3", 20), Map.entry("I01-4", 26),
            Map.entry("I05", 15), Map.entry("I06", 15), Map.entry("I07", 15), Map.entry("I18", 15),
            Map.entry("I14", 14), Map.entry("I15", 14), Map.entry("I16", 26),
            Map.entry("I19", 15), Map.entry("I20", 19), Map.entry("I21", 23), Map.entry("I22", 28),
            Map.entry("I23", 20),
            Map.entry("I24", 21), Map.entry("I25", 21), Map.entry("I26", 22),
            Map.entry("I27", 23), Map.entry("I28", 23), Map.entry("I29", 24),
            Map.entry("I30", 24), Map.entry("I31", 24), Map.entry("I32", 29),
            Map.entry("I33", 29), Map.entry("I34", 25), Map.entry("I35", 25),
            Map.entry("I36", 19), Map.entry("I37", 27), Map.entry("I38", 26),
            Map.entry("I39", 24), Map.entry("I40", 27), Map.entry("I41", 26),
            Map.entry("I42", 27), Map.entry("I43", 29), Map.entry("I44", 20),
            Map.entry("I45", 20));

    private Hk3ResearchProcessEnergy() {}

    public static boolean isGenerator(String role) { return GENERATORS.contains(role); }

    /** 未指定专用上限的早期工艺继续使用自身配方档。 */
    public static int ratedVoltageTier(String role) { return role.startsWith("W") ? Hk3WonderCatalog.get(role).runtimeTier() : role.equals("H01") ? 28 : RATED_TIERS.getOrDefault(role, 0); }

    public static int executionVoltageTier(GTRecipeType[] types, int registrationTier) {
        return Arrays.stream(types).mapToInt(type -> ExecutionTiers.BY_TYPE.getOrDefault(type, registrationTier))
                .max().getAsInt();
    }

    // 计划加载本身读取额定档，因此运行映射在首次机器查询时再生成。
    private static final class ExecutionTiers {
        private static final Map<GTRecipeType, Integer> BY_TYPE = load();
        private static Map<GTRecipeType, Integer> load() {
            var tiers = new HashMap<GTRecipeType, Integer>();
            RATED_TIERS.forEach((role, tier) -> tiers.merge(Hk3ResearchProcessTypes.get(role), tier, Math::max));
            Hk3ResearchProcessPlans.all().stream().filter(plan -> !plan.provisional()).forEach(plan ->
                    tiers.merge(Hk3ResearchProcessTypes.get(plan.role()), plan.energyTier(), Math::max));
            return Map.copyOf(tiers);
        }
    }
}
