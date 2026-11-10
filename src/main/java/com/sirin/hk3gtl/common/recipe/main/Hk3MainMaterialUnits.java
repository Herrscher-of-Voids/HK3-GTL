package com.sirin.hk3gtl.common.recipe.main;

import java.util.Map;

/**
 * 【文件职责】维护主材相含量的形态折算；不是所有外加树脂、导体与溶剂的原子质量模型。
 * 【变更记录 #1】2026-10-17 16:28:36（第1次备注 · 修订165）
 * - 删除：无；不继承GT自动冶炼、粉碎或材料回收配方。
 * - 新增：坯/板144、棒72、细线18、环/箔36、框架576与回收细分18的统一账本。
 * - 修改：形态配方显式验算相含量，负值和不守恒转换拒绝注册。
 * - 用途：防止棒、环、细线、箔与框架的分割/回收出现增殖；独立于Minecraft注册表便于负例测试。
 */
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
