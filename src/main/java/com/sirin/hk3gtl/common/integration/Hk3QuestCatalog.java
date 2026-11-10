package com.sirin.hk3gtl.common.integration;

import com.google.gson.*;
import com.sirin.hk3gtl.common.research.Hk3ResearchCatalog;
import java.io.InputStreamReader;
import java.nio.charset.StandardCharsets;
import java.util.*;

/** 任务清单与纯数据判定；不引用可选FTB类，任何客户端/任务字段均不能反向授予研究。 */
/** 【变更记录 #1】2026-10-01 14:10:35（修订129）：删除：无；新增/修改：增加100课题清单、稳定ID与只读完成判定；用途：任务和进度只投影真实账本，不授研究、物品或审查资格。 */
public final class Hk3QuestCatalog {
    public record Entry(String key,String kind,String value,String quest,String task,String chapter) {
        public long taskId(){return Long.parseUnsignedLong(task,16);}
        public long questId(){return Long.parseUnsignedLong(quest,16);}
        public String tag(){return "hk3gtl_quest_"+key.toLowerCase(Locale.ROOT).replace('-','_');}
    }
    public record Facts(Set<String> research,int civilization,boolean firstReview,boolean secondReview) {
        public Facts { research=Set.copyOf(research);if(civilization<0||civilization>7)throw new IllegalArgumentException("文明等级越界"); }
    }
    private static final List<Entry> ALL=load();
    private Hk3QuestCatalog(){}
    public static List<Entry> all(){return ALL;}
    public static boolean satisfied(Entry e,Facts f){return switch(e.kind()){
        case "research" -> f.research().contains(e.value());
        case "civilization" -> f.civilization()>=Integer.parseInt(e.value());
        case "review" -> e.value().equals("1")?f.firstReview():f.secondReview();
        default -> false;
    };}
    private static List<Entry> load(){
        try(var stream=Hk3QuestCatalog.class.getResourceAsStream("/data/hk3gtl/guide/quest_catalog.json")){
            if(stream==null)throw new IllegalStateException("内测5任务清单缺失");
            var root=JsonParser.parseReader(new InputStreamReader(stream,StandardCharsets.UTF_8)).getAsJsonObject();
            var rows=new ArrayList<Entry>();var ids=new HashSet<Long>();var topics=new HashSet<String>();var keys=new HashSet<String>();
            for(var raw:root.getAsJsonArray("entries")){
                var e=new Gson().fromJson(raw,Entry.class);
                if(!keys.add(e.key())||!e.quest().matches("4B5[0-9A-F]{13}")||!e.task().matches("4B5[0-9A-F]{13}")||!ids.add(e.taskId())||!ids.add(e.questId()))throw new IllegalStateException("任务ID冲突");
                if(e.kind().equals("research")){
                    if(Hk3ResearchCatalog.bundled().get(e.value())==null||!topics.add(e.value()))throw new IllegalStateException("未知或重复研究任务");
                }else if(e.kind().equals("civilization")){if(!e.value().matches("[1-7]"))throw new IllegalStateException("文明任务越界");}
                else if(e.kind().equals("review")){if(!e.value().matches("[12]"))throw new IllegalStateException("审查任务越界");}
                else if(!e.kind().equals("reading"))throw new IllegalStateException("未知任务来源");
                rows.add(e);
            }
            if(!topics.equals(Hk3ResearchCatalog.bundled().topics().keySet()))throw new IllegalStateException("任务未覆盖100课题");
            return List.copyOf(rows);
        }catch(java.io.IOException ex){throw new IllegalStateException("任务目录读取失败",ex);}
    }
}

// 【变更记录 · 修订161】2026-10-17 14:11:55：本轮仅将活动类名、资源与工业配方引用迁移为长期业务命名；历史备注保留，不代表旧逻辑已全部按现行设计重写。
