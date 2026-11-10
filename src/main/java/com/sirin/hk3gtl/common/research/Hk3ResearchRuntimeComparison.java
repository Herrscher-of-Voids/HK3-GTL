package com.sirin.hk3gtl.common.research;

import com.google.gson.JsonObject;
import java.util.ArrayList;
import java.util.List;

/**
 * 【文件职责】比较已批准配方与整包加载后快照；只返回差异，不修补或解锁游戏状态。
 * 【变更记录 #1】2026-09-30 00:54:00（第1次备注 · 内测5修订103）
 * 删除：无。新增：配方缺失、定义、门槛及空标签检查；修改：无旧机制替换。
 * 用途：让KubeJS覆盖、空标签和丢失门槛在实际实例验收中明确失败，不把静态检查当成可玩证明。
 */
public final class Hk3ResearchRuntimeComparison {
    private Hk3ResearchRuntimeComparison() {}

    public static List<String> compare(JsonObject expected, JsonObject actual) {
        var failures = new ArrayList<String>();
        if (actual == null) return List.of("missing_recipe");
        for (String key : List.of("id", "type", "definition", "gates", "resolved_inputs", "resolved_outputs")) {
            if (!expected.has(key) || !actual.has(key) || !expected.get(key).equals(actual.get(key)))
                failures.add("mismatch:" + key);
        }
        if (!actual.has("empty_ingredients") || actual.getAsJsonArray("empty_ingredients").size() != 0)
            failures.add("empty_ingredients");
        return List.copyOf(failures);
    }
}
