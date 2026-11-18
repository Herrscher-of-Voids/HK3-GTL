package com.sirin.hk3gtl.common.recipe.main;

import java.util.Map;

 







public final class Hk3MainMaterialUnits {
    private static final Map<String, Integer> UNITS = Map.ofEntries(
            Map.entry("billet", 144), Map.entry("plate", 144), Map.entry("rod", 72),
            Map.entry("fine_wire", 18), Map.entry("ring", 36), Map.entry("foil", 36),
            Map.entry("frame", 576), Map.entry("rejected_batch", 144), Map.entry("classified_scrap", 144),
            Map.entry("recovered_fraction", 18), Map.entry("unrecoverable_tailings", 18));

    private Hk3MainMaterialUnits() {}

    public static int perItem(String form) {
        if (form == null) throw new IllegalArgumentException("主材相含量形态不得为空");
        if (form != null && form.matches("stage_[1-8]")) return 144;
        Integer units = UNITS.get(form);
        if (units == null) throw new IllegalArgumentException("未知主材相含量形态：" + form);
        return units;
    }

    public static long amount(String form, int count) {
        if (count <= 0) throw new IllegalArgumentException("形态数量必须为正数");
        return Math.multiplyExact((long) perItem(form), count);
    }

    public static void requireBalanced(long input, long output) {
        if (input <= 0 || output <= 0 || input != output) {
            throw new IllegalArgumentException("主材相含量不守恒：投入=" + input + "，产出=" + output);
        }
    }

    public static void requireConversion(String inputForm, int inputCount, String outputForm, int outputCount) {
        requireBalanced(amount(inputForm, inputCount), amount(outputForm, outputCount));
    }
}
