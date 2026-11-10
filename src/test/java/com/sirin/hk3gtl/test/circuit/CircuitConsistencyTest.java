package com.sirin.hk3gtl.test.circuit;

import com.google.gson.JsonObject;
import com.google.gson.JsonParser;
import com.sirin.hk3gtl.common.constants.Hk3Tiers;
import com.sirin.hk3gtl.common.item.Hk3CircuitCatalog;
import net.minecraft.resources.ResourceLocation;

import java.io.InputStreamReader;
import java.nio.charset.StandardCharsets;
import java.util.HashSet;
import java.util.Set;
import java.util.stream.Collectors;

/**
 * 【变更记录 #1】2026-09-27 04:23:30（第 1 次备注 · 内测5修订90）
 * 删除：无。新增：实际Java目录、等级函数与打包用标签资源的交叉验证。
 * 修改：无物品注册或配方变更；用途：52项映射与192组等级别名回归，不宣称Forge运行注册已验收。
 */
/**
 * 【变更记录 #2】2026-09-27 04:24:55（第 2 次备注 · 内测5修订90）
 * 删除：纯JVM中创建需Forge引导的TagKey断言。新增：共享标签路径的实际调用验证。
 * 修改：资源仍逐项比对；用途：使逻辑测试不伪装游戏加载，不跳过等级/标签成员核对。
 */
/**
 * 【变更记录 #3】2026-09-27 04:26:03（第 3 次备注 · 内测5修订90）
 * 删除：无断言。新增：标签核对数量的独立计数。
 * 修改：第1条备注中的192为笔误，实际16等级×2命名空间×3别名共96组。
 * 用途：日志按实际循环计数报告，不夸大测试覆盖。
 */
/**
 * 【变更记录 #4】2026-09-30 02:17:47（第4次备注 · 内测5修订107）
 * 删除：本文件可执行代码中的旧电压键及常量引用，不保留旧键注册别名。
 * 新增：16档正式缩写作为唯一电压标识；逐文件映射见logs/voltage-keys-r107。
 * 修改：注册、配方、查询或标签引用按原tier序号一一迁移；数值、层级与资源内容保持原义。
 * 用途：避免显示名与实际注册键不一致；历史备注保留，旧存档不自动改写。
 */
/** 【变更记录 #5】2026-10-01 20:59:23（修订149）：删除无；新增电子研究门槛测试入口；修改电路检查包含新版多前置；用途：防止旧绑定与种子自锁回归。 */
/** 【变更记录 #6】2026-10-01 21:12:01（修订150）：删除无；新增门槛合并回归调用；修改测试入口；用途：验证单项追加及并发不丢条件。 */
public final class CircuitConsistencyTest {
    private static int checks;
    public static void main(String[] args) throws Exception {
        ElectronicResearchTest.run();
        RecipeGateMergeTest.run();
        var entries = Hk3CircuitCatalog.ENTRIES;
        check(entries.size() == 52 && new HashSet<>(Hk3CircuitCatalog.paths()).size() == 52, "52 distinct IDs");
        check(entries.stream().filter(Hk3CircuitCatalog.Entry::primary).count() == 16, "16 stable primary IDs");
        var families = entries.stream().collect(Collectors.groupingBy(Hk3CircuitCatalog.Entry::family));
        check(families.size() == 13, "13 families");
        for (var family : families.values()) {
            check(family.size() == 4, "four forms");
            int first = family.stream().mapToInt(Hk3CircuitCatalog.Entry::tier).min().orElseThrow();
            for (int form = 0; form < 4; form++) {
                int expected = form;
                var entry = family.stream().filter(e -> e.form() == expected).findFirst().orElseThrow();
                check(entry.tier() == first + form, "consecutive form voltage");
                check(Hk3CircuitCatalog.tier(new ResourceLocation("hk3gtl", entry.id())) == entry.tier(), "actual tier lookup");
            }
        }
        check(Hk3CircuitCatalog.tier(new ResourceLocation("minecraft", "hbv_processor")) == -1, "namespace isolation");
        check(Hk3CircuitCatalog.tier(new ResourceLocation("hk3gtl", "hbv_processor_mainframe")) == -1, "legacy placeholder not official");
        // 修订107：只发布正式缩写标签，旧别名删除。
        int tagChecks = 0;
        for (int index = 0; index < 16; index++) {
            int tier = 15 + index;
            Set<String> expected = entries.stream().filter(e -> e.tier() == tier).map(e -> "hk3gtl:" + e.id()).collect(Collectors.toSet());
            String key = Hk3Tiers.voltageKey(tier);
            check(Hk3CircuitCatalog.tagId(tier).toString().equals("forge:circuits/" + key), "actual generic tag");
            for (String namespace : new String[]{"forge", "gtceu"}) {
                for (String alias : new String[]{key}) {
                    check(tag(namespace + ":circuits/" + alias, new HashSet<>()).equals(expected), "same-tier alternatives " + namespace + ":" + alias);
                    tagChecks++;
                }
            }
        }
        System.out.println("Circuit consistency: " + checks + " checks passed; 52 circuits and " + tagChecks + " voltage tags");
    }
    private static Set<String> tag(String id, Set<String> visiting) throws Exception {
        if (!visiting.add(id)) throw new AssertionError("Tag cycle " + id);
        String[] parts = id.split(":", 2);
        String path = "data/" + parts[0] + "/tags/items/" + parts[1] + ".json";
        Set<String> values = new HashSet<>();
        try (var stream = CircuitConsistencyTest.class.getClassLoader().getResourceAsStream(path)) {
            if (stream == null) throw new AssertionError("Missing tag " + path);
            JsonObject json = JsonParser.parseReader(new InputStreamReader(stream, StandardCharsets.UTF_8)).getAsJsonObject();
            for (var element : json.getAsJsonArray("values")) {
                String value = element.isJsonPrimitive() ? element.getAsString() : element.getAsJsonObject().get("id").getAsString();
                if (value.startsWith("#")) values.addAll(tag(value.substring(1), visiting)); else values.add(value);
            }
        }
        visiting.remove(id); return values;
    }
    private static void check(boolean condition, String message) { checks++; if (!condition) throw new AssertionError(message); }
}
