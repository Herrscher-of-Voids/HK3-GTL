package com.sirin.hk3gtl.common.narrative;

import com.google.gson.Gson;
import java.io.InputStreamReader;
import java.nio.charset.StandardCharsets;
import java.util.*;

 





public final class Hk3ApprovedProse {
    public record Choice(String text, String target) {}
    public record Entry(String id, String system, String title, String speaker, String source,
                        int lineCount, String next, List<Choice> choices) {
        public String key() { return "hk3gtl.approved." + id; }
        public List<Choice> routes() { return choices == null ? List.of() : choices; }
    }
    private record Catalog(int schema, List<Entry> entries) {}
    private static final Map<String, Entry> ENTRIES = load();
    private Hk3ApprovedProse() {}

    private static Map<String, Entry> load() {
        try (var stream = Hk3ApprovedProse.class.getResourceAsStream("/assets/hk3gtl/narrative/approved.json")) {
            if (stream == null) throw new IllegalStateException("剧情档案目录缺失");
            Catalog catalog = new Gson().fromJson(new InputStreamReader(stream, StandardCharsets.UTF_8), Catalog.class);
            if (catalog.schema != 1) throw new IllegalStateException("正文目录版本错误");
            Map<String, Entry> result = new LinkedHashMap<>();
            for (Entry e : catalog.entries) {
                if (e.lineCount < 1 || e.lineCount > 256 || result.put(e.id, e) != null)
                    throw new IllegalStateException("无效或重复的正文：" + e.id);
            }
            for (Entry e : result.values()) {
                if (e.next != null && !result.containsKey(e.next)) throw new IllegalStateException("缺失后续正文：" + e.id);
                for (Choice c : e.routes()) if (!result.containsKey(c.target))
                    throw new IllegalStateException("缺失选项正文：" + e.id);
            }
            return Collections.unmodifiableMap(result);
        } catch (java.io.IOException exception) {
            throw new IllegalStateException("无法读取剧情档案", exception);
        }
    }
    public static Entry get(String id) { return ENTRIES.get(id); }
    public static Collection<Entry> all() { return ENTRIES.values(); }
    public static List<Entry> system(String id) {
        return ENTRIES.values().stream().filter(e -> id.equals(e.system)).toList();
    }
}
