package com.sirin.hk3gtl.common.research;

import com.google.gson.JsonParser;
import java.io.InputStreamReader;
import java.nio.charset.StandardCharsets;
import java.util.LinkedHashMap;
import java.util.Map;

/** 中文说明：该处说明已按当前代码行为整理。*/
public final class Hk3ResearchStory {
    private Hk3ResearchStory() {}
    private static final class Holder { private static final Map<String,String> STORIES=load(); }
    /** 中文说明：该处说明已按当前代码行为整理。*/
    public static String get(String id) {
        String story=Holder.STORIES.get(id);
        if(story==null) throw new IllegalArgumentException("Missing research story: "+id);
        return story;
    }
    private static Map<String,String> load() {
        try(var input=Hk3ResearchStory.class.getResourceAsStream("/data/hk3gtl/research/research_story.json")) {
            if(input==null) throw new IllegalStateException("Missing research story resource");
            var entries=JsonParser.parseReader(new InputStreamReader(input,StandardCharsets.UTF_8)).getAsJsonObject().getAsJsonArray("chapters");
            Map<String,String> stories=new LinkedHashMap<>();
            var ids=Hk3ResearchPlans.all().keySet().iterator();
            for(var raw:entries) {
                var entry=raw.getAsJsonObject(); String id=entry.get("id").getAsString(),text=entry.get("text").getAsString();
                if(!ids.hasNext() || !ids.next().equals(id) || text.isBlank() || stories.putIfAbsent(id,text)!=null)
                    throw new IllegalArgumentException("Invalid story order or content: "+id);
            }
            if(ids.hasNext() || stories.size()!=100) throw new IllegalArgumentException("Expected 100 research chapters");
            return Map.copyOf(stories);
        } catch(Exception e) { throw new IllegalStateException("Cannot load research narrative",e); }
    }
}

// 【变更记录 · 修订161】2026-10-17 14:11:55：本轮仅将活动类名、资源与工业配方引用迁移为长期业务命名；历史备注保留，不代表旧逻辑已全部按现行设计重写。
