package com.sirin.hk3gtl.common.integration;

import com.google.gson.*;
import com.sirin.hk3gtl.common.research.Hk3ResearchCatalog;
import java.io.InputStreamReader;
import java.nio.charset.StandardCharsets;
import java.util.*;

/** 任务清单与纯数据判定；不引用可选FTB类，任何客户端/任务字段均不能反向授予研究。 */
public final class Hk3QuestCatalog {
    public record Entry(String key,String kind,String value,String quest,String task,String chapter) {
        public long taskId(){return Long.parseUnsignedLong(task,16);}
        public long questId(){return Long.parseUnsignedLong(quest,16);}
        public String tag(){return "hk3gtl_quest_"+key.toLowerCase(Locale.ROOT).replace('-','_');}
    }
    public record Facts(Set<String> research,int civilization,boolean firstReview,boolean secondReview,boolean graduated,
                        Set<String> processes,Set<String> playerEvents) {
        public Facts { research=Set.copyOf(research);processes=Set.copyOf(processes);playerEvents=Set.copyOf(playerEvents);if(civilization<0||civilization>7)throw new IllegalArgumentException("文明等级越界"); }
        public Facts(Set<String> research,int civilization,boolean firstReview,boolean secondReview,boolean graduated) {
            this(research,civilization,firstReview,secondReview,graduated,Set.of(),Set.of());
        }
    }
    private static final List<Entry> ALL=load();
    private Hk3QuestCatalog(){}
    public static List<Entry> all(){return ALL;}
    public static boolean satisfied(Entry e,Facts f){return switch(e.kind()){
        case "research" -> f.research().contains(e.value());
        case "civilization" -> f.civilization()>=Integer.parseInt(e.value());
        case "review" -> e.value().equals("1")?f.firstReview():f.secondReview();
        case "graduation" -> f.graduated();
        case "process" -> Arrays.stream(e.value().split("\\|")).anyMatch(f.processes()::contains);
        case "player_event" -> f.playerEvents().contains(e.value());
        default -> false;
    };}
    private static List<Entry> load(){
        try(var stream=Hk3QuestCatalog.class.getResourceAsStream("/data/hk3gtl/guide/quest_catalog.json")){
            if(stream==null)throw new IllegalStateException("内测5任务清单缺失");
            var root=JsonParser.parseReader(new InputStreamReader(stream,StandardCharsets.UTF_8)).getAsJsonObject();
            var rows=new ArrayList<Entry>();var tasks=new HashSet<Long>();var quests=new HashSet<Long>();var keys=new HashSet<String>();
            for(var raw:root.getAsJsonArray("entries")){
                var e=new Gson().fromJson(raw,Entry.class);
                if(!keys.add(e.key())||!e.quest().matches("4B5[0-9A-F]{13}")||!e.task().matches("4B5[0-9A-F]{13}")||!tasks.add(e.taskId()))throw new IllegalStateException("任务ID冲突");
                quests.add(e.questId());
                if(e.kind().equals("research")){
                    if(Hk3ResearchCatalog.bundled().get(e.value())==null)throw new IllegalStateException("未知研究任务");
                }else if(e.kind().equals("civilization")){if(!e.value().matches("[1-7]"))throw new IllegalStateException("文明任务越界");}
                else if(e.kind().equals("review")){if(!e.value().matches("[12]"))throw new IllegalStateException("审查任务越界");}
                else if(!Set.of("reading","graduation","process","player_event").contains(e.kind()))throw new IllegalStateException("未知任务来源");
                rows.add(e);
            }
            if(!Collections.disjoint(tasks,quests))throw new IllegalStateException("任务ID冲突");
            return List.copyOf(rows);
        }catch(java.io.IOException ex){throw new IllegalStateException("任务目录读取失败",ex);}
    }
}

