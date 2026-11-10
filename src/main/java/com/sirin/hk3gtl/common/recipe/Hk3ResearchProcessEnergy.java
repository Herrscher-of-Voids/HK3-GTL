package com.sirin.hk3gtl.common.recipe;

import java.util.Map;
import java.util.Set;

/** Energy polarity and accepted rating limits for industrial recipe roles. */
public final class Hk3ResearchProcessEnergy {
    private static final Set<String> GENERATORS = Set.of("I19", "I20", "I21", "I22", "I23");
    private static final Map<String, Integer> RATED_TIERS = Map.ofEntries(
            Map.entry("I01-1", 15), Map.entry("I01-2", 19), Map.entry("I01-3", 20), Map.entry("I01-4", 26),
            Map.entry("I05", 15), Map.entry("I06", 15), Map.entry("I07", 15), Map.entry("I18", 15),
            Map.entry("I19", 15), Map.entry("I20", 19), Map.entry("I21", 23), Map.entry("I22", 28),
            Map.entry("I23", 20));

    private Hk3ResearchProcessEnergy() {}

    public static boolean isGenerator(String role) { return GENERATORS.contains(role); }

    /** Returns zero when the role has no accepted voltage mapping yet. */
    public static int ratedVoltageTier(String role) { return RATED_TIERS.getOrDefault(role, 0); }
}
