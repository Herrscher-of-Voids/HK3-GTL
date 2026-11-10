package com.sirin.hk3gtl.test.industry;

import com.google.gson.JsonObject;
import com.google.gson.JsonParser;
import com.sirin.hk3gtl.common.multiblock.pattern.Hk3ApprovedArchitecture;
import com.sirin.hk3gtl.common.multiblock.pattern.Hk3LateIndustrialPatterns;
import com.sirin.hk3gtl.common.research.Hk3IndustrialExtensionPolicy;

import java.io.InputStreamReader;
import java.nio.ByteBuffer;
import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.util.Arrays;
import java.util.HashMap;
import java.util.HashSet;
import java.util.HexFormat;
import java.util.List;
import java.util.Map;

/** 2026-10-30（修订182）：六台批准版本逐格预览、控制器身份、独立三态及未开放工艺边界回归。 */
public final class BatchTenArchitectureTest {
    private record Expected(String machine, int[] size, int[] controller, int blocks, int ports, int tier) {}
    private static final Map<String, Expected> EXPECTED = Map.of(
            "i40", new Expected("i40_civilization_wonder_material_synthesis_center", new int[]{601, 291, 481}, new int[]{300, 27, 0}, 12697362, 12, 27),
            "i41", new Expected("i41_civilization_energy_dispatch_hub", new int[]{529, 289, 529}, new int[]{264, 24, 0}, 12119638, 6, 26),
            "i42", new Expected("i42_wonder_component_prefabrication_factory", new int[]{641, 295, 449}, new int[]{320, 26, 0}, 14747313, 8, 27),
            "i43", new Expected("i43_civilization_engineering_acceptance_center", new int[]{641, 297, 481}, new int[]{320, 24, 0}, 19280741, 8, 28),
            "i44", new Expected("i44_imitation_thousand_realms_beacon", new int[]{281, 209, 741}, new int[]{140, 14, 16}, 4206990, 8, 20),
            "i45", new Expected("i45_imitation_thousand_realms_train", new int[]{121, 181, 821}, new int[]{60, 108, 0}, 3200871, 8, 20));

    public static void main(String[] args) throws Exception {
        check(Hk3ApprovedArchitecture.IDS.size() == 52 && Hk3LateIndustrialPatterns.IDS.size() == 26, "正式结构或巨构数量错误");
        check(!Hk3ApprovedArchitecture.IDS.contains("i37"), "未批准I37被接入");
        verifyPlanBoundary();
        var names = Map.of("zh_cn", json("/assets/hk3gtl/lang/zh_cn.json"), "en_us", json("/assets/hk3gtl/lang/en_us.json"));
        var pictures = new HashSet<String>();
        long blocks = 0;
        for (String key : EXPECTED.keySet().stream().sorted().toList()) {
            Expected expected = EXPECTED.get(key);
            blocks += BatchEightArchitectureTest.verify(key, 182, layout -> {
                check(Arrays.equals(layout.size(), expected.size()) && Arrays.equals(layout.controller(), expected.controller()), "批准版本尺寸或主控改变：" + key);
                check(layout.blocks().size() == expected.blocks() && layout.ports().size() == expected.ports(), "批准实体或接口数改变：" + key);
            });
            var meta = json("/data/hk3gtl/structures/approved/" + key + ".json");
            check(meta.get("machine").getAsString().equals("hk3gtl:" + expected.machine()), "控制器注册身份不符：" + key);
            for (var language : names.entrySet()) {
                String name = "block.hk3gtl." + expected.machine();
                check(language.getValue().has(name) && language.getValue().get(name).equals(language.getValue().get("gtceu.industrial_process_" + key)), "双语名称不一致：" + language.getKey() + "/" + key);
            }
            for (String suffix : List.of("", "_active", "_paused")) {
                String path = "/assets/hk3gtl/textures/block/overlay/" + key + "_unique_r182/overlay_front" + suffix + ".png";
                try (var stream = BatchTenArchitectureTest.class.getResourceAsStream(path)) {
                    check(stream != null, "缺少独立面板：" + path);
                    byte[] bytes = stream.readAllBytes();
                    check(bytes.length >= 24 && ByteBuffer.wrap(bytes).getLong() == 0x89504e470d0a1a0aL, "面板不是PNG：" + path);
                    check(ByteBuffer.wrap(bytes, 16, 8).getInt() == 64 && ByteBuffer.wrap(bytes, 20, 4).getInt() == 64, "面板分辨率改变：" + path);
                    check(pictures.add(HexFormat.of().formatHex(MessageDigest.getInstance("SHA-256").digest(bytes))), "面板重复复用：" + path);
                }
            }
        }
        check(pictures.size() == 18, "六套三态必须全部独立");
        System.out.println("第10批六台批准版本、完整预览与18张独立面板通过：" + blocks + "块；工艺、调度、旅行和游戏运行未验收。");
    }

    private static void verifyPlanBoundary() throws Exception {
        Map<String, Integer> counts = new HashMap<>();
        Map<String, java.util.Set<String>> required = new HashMap<>();
        int overRated = 0;
        for (var raw : json("/data/hk3gtl/research/industrial_processes.json").getAsJsonArray("recipes")) {
            var plan = raw.getAsJsonObject();
            String key = plan.get("role").getAsString().toLowerCase(java.util.Locale.ROOT);
            if (!EXPECTED.containsKey(key)) continue;
            String role = plan.get("role").getAsString();
            check(plan.get("provisional").getAsBoolean() && !Hk3IndustrialExtensionPolicy.permits(role, true), "暂定工艺被开放：" + plan.get("id"));
            check(Hk3IndustrialExtensionPolicy.permits(role, false), "已批准工艺入口被误锁：" + key);
            counts.merge(key, 1, Integer::sum);
            var groups = required.computeIfAbsent(key, unused -> new HashSet<>());
            for (var port : Map.of("item_inputs", "item_input", "item_outputs", "item_output",
                    "fluid_inputs", "fluid_input", "fluid_outputs", "fluid_output").entrySet())
                if (plan.getAsJsonArray(port.getKey()).size() > 0) groups.add(port.getValue());
            if (plan.get("energy_tier").getAsInt() > EXPECTED.get(key).tier()) {
                check(key.equals("i43"), "意外超额定工艺：" + key);
                overRated++;
            }
        }
        check(counts.equals(Map.of("i40", 1, "i42", 1, "i43", 17, "i44", 2)), "本批既有工单数量改变：" + counts);
        check(overRated == 6, "I43六项超WSV暂定工单限制改变，需重新审核");
        for (var entry : required.entrySet()) {
            var installed = new HashSet<String>();
            json("/data/hk3gtl/structures/approved/" + entry.getKey() + ".json").getAsJsonObject("installed_hatches")
                    .entrySet().forEach(hatch -> installed.add(hatch.getValue().getAsString()));
            check(installed.containsAll(entry.getValue()), "预览缺少已有工单所需真实仓室：" + entry.getKey() + "/" + entry.getValue());
        }
        for (String key : List.of("i41", "i45"))
            check(!Hk3IndustrialExtensionPolicy.permits(key.toUpperCase(java.util.Locale.ROOT), true), "空角色绕过暂定守卫：" + key);
    }

    private static JsonObject json(String resource) throws Exception {
        try (var stream = BatchTenArchitectureTest.class.getResourceAsStream(resource)) {
            check(stream != null, "缺少资源：" + resource);
            return JsonParser.parseReader(new InputStreamReader(stream, StandardCharsets.UTF_8)).getAsJsonObject();
        }
    }

    private static void check(boolean value, String message) { if (!value) throw new AssertionError(message); }
}
