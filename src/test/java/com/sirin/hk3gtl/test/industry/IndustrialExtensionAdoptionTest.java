package com.sirin.hk3gtl.test.industry;

import com.google.gson.JsonObject;
import com.google.gson.JsonParser;
import com.sirin.hk3gtl.common.research.Hk3IndustrialExtensionPolicy;
import java.nio.charset.StandardCharsets;
import java.util.HashMap;
import java.util.Map;
import java.util.Set;



/**
 * 核验新接入工业结构的真实仓容量合同与当前32项暂定工单关闭边界。
 */
public final class IndustrialExtensionAdoptionTest {
    private IndustrialExtensionAdoptionTest() {}

    public static void main(String[] args) throws Exception {
        var expected = Map.ofEntries(
                Map.entry("I14", 1), Map.entry("I15", 1), Map.entry("I16", 30), Map.entry("I18", 2),
                Map.entry("I19", 1), Map.entry("I20", 1), Map.entry("I21", 1), Map.entry("I22", 1),
                Map.entry("I24", 2), Map.entry("I25", 1),
                Map.entry("I34", 1), Map.entry("I35", 1), Map.entry("I36", 2));
        var counts = new HashMap<String, Integer>();
        JsonObject source = json("/data/hk3gtl/research/industrial_processes.json");
        boolean fallback = source.get("provisional").getAsBoolean();
        for (var element : source.getAsJsonArray("recipes")) {
            var plan = element.getAsJsonObject();
            String role = plan.get("role").getAsString();
            if (!expected.containsKey(role)) continue;
            boolean provisional = plan.has("provisional") ? plan.get("provisional").getAsBoolean() : fallback;
            boolean approved = Set.of("I14", "I15", "I16").contains(role);
            check(provisional != approved, "工单与允许范围不符：" + plan.get("id"));
            check(Hk3IndustrialExtensionPolicy.permits(role, provisional) == approved,
                    "工单运行守卫与批准不符：" + plan.get("id"));
            counts.merge(role, 1, Integer::sum);
        }
        check(counts.equals(expected), "暂定工单覆盖数变化：" + counts);
        for (String role : Set.of("I14", "I15", "I16", "I18"))
            check(Hk3IndustrialExtensionPolicy.permits(role, false), "非暂定工艺应继续既有运行校验：" + role);
        for (String role : Set.of("I19", "I20", "I21", "I22", "I24", "I25"))
            check(!Hk3IndustrialExtensionPolicy.permits(role, true), "后期暂定工艺不得运行：" + role);
        for (String role : Set.of("I23", "I26", "I27", "I28"))
            check(!Hk3IndustrialExtensionPolicy.permits(role, true), "后期空角色也不得绕过暂定守卫：" + role);
        for (String role : Set.of("I34", "I35", "I36", "I38", "I39")) {
            check(!Hk3IndustrialExtensionPolicy.permits(role, true), "第9批暂定工艺不得运行：" + role);
            check(Hk3IndustrialExtensionPolicy.permits(role, false), "非暂定工艺应继续原有运行校验：" + role);
        }
        check(Hk3IndustrialExtensionPolicy.permits("I17", true), "不得改变既有浓缩角色许可");
        for (String key : Set.of("i14", "i15", "i16", "i17", "i18")) {
            var manifest = json("/data/hk3gtl/structures/approved/" + key + ".json");
            var layout = json("/data/hk3gtl/approved_architecture/" + key + ".json");
            var abilities = new java.util.HashSet<String>();
            manifest.getAsJsonObject("installed_hatches").entrySet().forEach(e -> abilities.add(e.getValue().getAsString()));
            check(abilities.equals(Set.of("item_input", "item_output", "fluid_input", "fluid_output")), "真实仓四能力：" + key);
            check(!manifest.get("game_verified").getAsBoolean(), "不可把静态接入标成实机通过：" + key);
            check(layout.getAsJsonObject("approved_source").get("approval").getAsString().equals("实装这一些吧"), "批准身份：" + key);
            check(layout.getAsJsonObject("approved_source").get("sha256").getAsString()
                    .equals(manifest.get("approved_blueprint_sha256").getAsString()), "蓝图身份不一致：" + key);
        }
        var concentration = json("/data/hk3gtl/structures/approved/i17.json");
        check(concentration.get("machine").getAsString().equals("hk3gtl:honkai_fuel_concentration_plant"), "I17不得更换原控制器身份");
        var hatches = concentration.getAsJsonObject("installed_hatch_blocks");
        check(hatches.get("LIQUID_FUEL").getAsString().equals("gtceu:max_input_hatch_4x"), "三流体输入需多槽仓");
        check(hatches.get("CONCENTRATE").getAsString().equals("gtceu:max_output_hatch_4x"), "三流体输出需多槽仓");
        System.out.println("工业扩展接入：五结构来源与四能力、I17多槽仓、32项批准工单及其余暂定守卫通过；实机另行验收。");
    }

    private static JsonObject json(String path) throws Exception {
        try (var stream = IndustrialExtensionAdoptionTest.class.getResourceAsStream(path)) {
            check(stream != null, "缺少资源：" + path);
            return JsonParser.parseString(new String(stream.readAllBytes(), StandardCharsets.UTF_8)).getAsJsonObject();
        }
    }

    private static void check(boolean value, String message) { if (!value) throw new AssertionError(message); }
}
