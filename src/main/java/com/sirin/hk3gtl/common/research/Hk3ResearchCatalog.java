package com.sirin.hk3gtl.common.research;

import com.google.gson.JsonObject;
import com.google.gson.JsonParser;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.Collections;
import java.util.HashSet;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Set;

/** 中文说明：该处备注已按当前代码行为整理，不使用问号占位。*/
public final class Hk3ResearchCatalog {
    /** 研究所级别1..5，能力窗口0(MAX)..16；前置为全部满足，机器仅关联元数据。 / Lab 1..5, capability 0(MAX)..16; all prerequisites required, machines are metadata. */
    public record Topic(String id, int lab, int tier, List<String> prerequisites) {
        public Topic {
            if (id == null || !id.matches("RN-[A-Z0-9]+") || lab < 1 || lab > 5 || tier < 0 || tier > 16) {
                throw new IllegalArgumentException("Invalid industrial topic: " + id);
            }
            prerequisites = List.copyOf(prerequisites);
            if (new HashSet<>(prerequisites).size() != prerequisites.size()) throw new IllegalArgumentException("Duplicate prerequisite: " + id);
        }
    }

    private final Map<String, Topic> topics;

    /** 中文说明：该处说明已按当前代码行为整理。*/
    public Hk3ResearchCatalog(List<Topic> definitions) {
        Map<String, Topic> map = new LinkedHashMap<>();
        for (Topic topic : definitions) {
            if (map.putIfAbsent(topic.id(), topic) != null) throw new IllegalArgumentException("Duplicate topic: " + topic.id());
        }
        if (map.isEmpty()) throw new IllegalArgumentException("Empty research catalog");
        Set<String> complete = new HashSet<>();
        for (String id : map.keySet()) visit(id, map, new HashSet<>(), complete);
        topics = Collections.unmodifiableMap(map);
    }

    /** DFS三色检查；缺失/循环不可视为已完成。 / DFS rejects missing dependencies and cycles rather than considering them complete. */
    private static void visit(String id, Map<String, Topic> map, Set<String> active, Set<String> complete) {
        if (complete.contains(id)) return;
        Topic topic = map.get(id);
        if (topic == null) throw new IllegalArgumentException("Missing prerequisite: " + id);
        if (!active.add(id)) throw new IllegalArgumentException("Research cycle: " + id);
        for (String parent : topic.prerequisites()) visit(parent, map, active, complete);
        active.remove(id); complete.add(id);
    }

    /** 中文说明：该处说明已按当前代码行为整理。*/
    public Topic get(String id) { return topics.get(id); }
    public Map<String, Topic> topics() { return topics; }

    /** 中文说明：该处说明已按当前代码行为整理。*/
    public boolean prerequisitesMet(String id, Set<String> completed, int lab) {
        Topic topic = get(id);
        return topic != null && lab >= topic.lab() && lab <= 5 && completed.containsAll(topic.prerequisites());
    }

    /** 中文说明：该处说明已按当前代码行为整理。*/
    public static Hk3ResearchCatalog bundled() { return Holder.INSTANCE; }
    private static final class Holder {
        private static final Hk3ResearchCatalog INSTANCE = load();
    }
    private static Hk3ResearchCatalog load() {
        try (InputStream in = Hk3ResearchCatalog.class.getResourceAsStream("/data/hk3gtl/research/research_catalog.json")) {
            if (in == null) throw new IllegalStateException("Missing industrial research catalog");
            JsonObject root = JsonParser.parseReader(new InputStreamReader(in, StandardCharsets.UTF_8)).getAsJsonObject();
            if (root.get("schema").getAsInt() != 1) throw new IllegalArgumentException("Unsupported research catalog schema");
            List<Topic> definitions = new ArrayList<>();
            for (var value : root.getAsJsonArray("topics")) {
                JsonObject object = value.getAsJsonObject();
                List<String> parents = new ArrayList<>();
                for (var parent : object.getAsJsonArray("prerequisites")) parents.add(parent.getAsString());
                definitions.add(new Topic(object.get("id").getAsString(), object.get("lab").getAsInt(),
                        object.get("tier").getAsInt(), parents));
            }
            return new Hk3ResearchCatalog(definitions);
        } catch (Exception exception) {
            throw new IllegalStateException("Cannot load industrial research catalog", exception);
        }
    }
}

// 【变更记录 · 修订161】2026-10-17 14:11:55：本轮仅将活动类名、资源与工业配方引用迁移为长期业务命名；历史备注保留，不代表旧逻辑已全部按现行设计重写。
