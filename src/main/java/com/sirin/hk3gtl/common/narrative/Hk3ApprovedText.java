package com.sirin.hk3gtl.common.narrative;

import com.google.gson.JsonParser;
import java.io.InputStreamReader;
import java.nio.charset.StandardCharsets;
import java.util.LinkedHashMap;
import java.util.Map;

/**
 * 【变更记录 #1】2026-10-31 02:01:05（第1次备注 · 修订187）
 * 删除：无；新增：已批准中文资源的只读解析器；修改：无。
 * 用途：专服全文回执使用精确原文，不依赖客户端语言表；资源或键缺失直接拒绝，不把裸键当正文。
 */
public final class Hk3ApprovedText {
    private static final Map<String, String> TEXT = load();
    private Hk3ApprovedText() {}

    private static Map<String, String> load() {
        try (var stream = Hk3ApprovedText.class.getResourceAsStream("/assets/hk3gtl/lang/zh_cn.json")) {
            if (stream == null) throw new IllegalStateException("已批准中文正文资源缺失");
            var source = JsonParser.parseReader(new InputStreamReader(stream, StandardCharsets.UTF_8)).getAsJsonObject();
            var result = new LinkedHashMap<String, String>();
            for (var entry : source.entrySet()) if (entry.getKey().startsWith("hk3gtl.approved.")) {
                if (!entry.getValue().isJsonPrimitive() || !entry.getValue().getAsJsonPrimitive().isString())
                    throw new IllegalStateException("已批准中文正文不是字符串：" + entry.getKey());
                result.put(entry.getKey(), entry.getValue().getAsString());
            }
            if (result.isEmpty()) throw new IllegalStateException("已批准中文正文资源为空");
            return Map.copyOf(result);
        } catch (java.io.IOException exception) {
            throw new IllegalStateException("无法读取已批准中文正文", exception);
        }
    }

    public static String text(String key) {
        String value = TEXT.get(key);
        if (value == null || value.isBlank()) throw new IllegalStateException("已批准中文正文缺键或为空：" + key);
        return value;
    }

    public static String title(Hk3ApprovedProse.Entry entry) {
        if (entry == null) throw new IllegalArgumentException("已批准正文条目不存在");
        return text(entry.key() + ".title");
    }

    public static String body(Hk3ApprovedProse.Entry entry) {
        if (entry == null) throw new IllegalArgumentException("已批准正文条目不存在");
        var body = new StringBuilder();
        for (int i = 0; i < entry.lineCount(); i++) {
            if (i > 0) body.append("\n\n");
            body.append(text(entry.key() + ".line." + i));
        }
        return body.toString();
    }
}
