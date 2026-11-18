package com.sirin.hk3gtl.common.recipe.honkai;

import java.util.List;
import java.util.Set;
import java.util.stream.Collectors;
import java.util.stream.Stream;

public final class Hk3ReactorFuels {
    public record Rod(String path, List<String> research, double heatPerTick) {
        public String bundle(int count) { return path + "_" + count + "x"; }
        public boolean highGrade() { return research.contains("RN-CFR"); }
    }

    public record Fuel(String slug, boolean dense, String raw, int amount, String additive, int additiveAmount,
                       double heatPerTick) {
        public String item(String suffix) { return "honkai_" + slug + suffix; }
        public List<String> research() { return dense ? List.of("RN-FRP", "RN-CFR") : List.of("RN-FRP"); }
    }
    public static final List<Fuel> ALL = List.of(
            new Fuel("carbon", false, "gtceu:activated_carbon_dust", 8, "", 0, 6.5),
            new Fuel("zeolite", false, "gtceu:zeolite_sieving_pellets_dust", 8, "", 0, 6.0),
            new Fuel("silica_gel", false, "gtceu:silica_gel_dust", 8, "", 0, 7.0),
            new Fuel("silicon_carbide", false, "gtceu:silicon_carbide_dust", 8, "", 0, 5.5),
            new Fuel("boron_carbide", false, "gtceu:boron_carbide_dust", 8, "", 0, 7.5),
            new Fuel("zirconia", false, "gtceu:zirconium_oxide_dust", 8, "gtceu:yttrium_oxide_dust", 1, 9.5),
            new Fuel("diamond_copper", true, "gtceu:diamond_dust", 8, "gtceu:copper_dust", 8, 4.5),
            new Fuel("graphene", true, "gtceu:graphene_dust", 8, "", 0, 5.0),
            new Fuel("titanium_carbide", true, "gtceu:titanium_carbide_dust", 8, "gtceu:cobalt_dust", 4, 10.5),
            new Fuel("alumina", true, "gtceu:alumina_dust", 8, "", 0, 10.0),
            new Fuel("tungsten", true, "gtceu:tungsten_plate", 8, "", 0, 9.0),
            new Fuel("ptfe_membrane", true, "gtceu:polytetrafluoroethylene_foil", 8, "", 0, 3.5),
            new Fuel("pbi_microcapsule", true, "gtceu:polybenzimidazole_foil", 8, "", 0, 4.0));
    public static final List<Integer> BUNDLE_SIZES = List.of(4, 8, 16);
    public static final List<Rod> RODS = Stream.concat(
            Stream.of(new Rod("honkai_fuel_rod", List.of("RN-FRP"), 8.0),
                    new Rod("dense_honkai_fuel_rod", List.of("RN-FRP", "RN-CFR"), 11.5)),
            ALL.stream().map(fuel -> new Rod(fuel.item("_fuel"), fuel.research(), fuel.heatPerTick()))).toList();
    public static final Set<String> FUEL_IDS = RODS.stream().flatMap(rod -> Stream.concat(
            Stream.of("hk3gtl:" + rod.path()),
            BUNDLE_SIZES.stream().map(count -> "hk3gtl:" + rod.bundle(count))))
            .collect(Collectors.toUnmodifiableSet());
    private Hk3ReactorFuels() {}

    public static int bundleSize(String id) {
        if (id.endsWith("_4x")) return 4;
        if (id.endsWith("_8x")) return 8;
        return id.endsWith("_16x") ? 16 : 1;
    }

    public static boolean reactor(String role) {
        return role.equals("I19") || role.equals("I20") || role.equals("I21") || role.equals("I22");
    }
}
