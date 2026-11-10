package com.sirin.hk3gtl.common.dialogue.definition;

/** 【变更记录 #2】2026-09-29 19:50:20（内测5修订99）：删除：只读全文目录的贸易分类；新增：无；修改：按负责人决定撤下五方贸易；用途：保留其他系统独立运行。 */
import com.sirin.hk3gtl.common.dialogue.*;
import com.sirin.hk3gtl.common.narrative.Hk3ApprovedProse;
import java.util.*;

/**
 * 从审核原文生成逐句对白、二审分支与分系统校对目录；校对入口没有结算处理器。
 * 【变更记录 #1】2026-09-29 17:51:46（内测5修订93）
 * 删除：无。新增：全正文阅读入口和正式终审图。修改：不再混用旧版本对白。
 * 用途：原文、人物及分支共用一套定义；校对不授予研究、外交或工程资格。
 */
/** 【变更记录 #3】2026-10-01 18:42:57（修订140）：删除无；新增正式审查图注册；修改批准正文注册后初始化一二审显示；用途：客户端服务端共用图，校对仍无结算。 */
/** 【变更记录 #4】2026-10-01 19:03:37（修订141）：删除：无；新增／修改：终审正文、选项、IF共用一个名字键，一审与二审主题保持各自角色；用途：琪亚娜二审形象和终审统一称谓，保留其他会话行为。 */
public final class Hk3ApprovedDialogues {
    public static final String LIBRARY = "hk3_approved_library";
    public static final String REVIEW_PREVIEW = "hk3_second_review_preview";
    public static final String FINALE_PREVIEW = "hk3_finale_preview";
    public static final String[] SYSTEMS = {"communication", "npc", "update", "first_review", "observation", "review", "finale"};
    private Hk3ApprovedDialogues() {}

    public static List<DialogueLine> lines(Hk3ApprovedProse.Entry entry, List<DialogueChoice> choices) {
        List<DialogueLine> result = new ArrayList<>();
        for (int i = 0; i < entry.lineCount(); i++)
            result.add(new DialogueLine("approved." + entry.id(), entry.key()+".line."+i, null,
                    i == entry.lineCount()-1 && !choices.isEmpty() ? List.copyOf(choices) : null));
        return List.copyOf(result);
    }

    public static void register() {
        for (var e : Hk3ApprovedProse.all()) {
            DialogueRegistry.registerSpeaker(new DialogueSpeakerTheme("approved."+e.id(), "finale".equals(e.system()) ? "hk3gtl.dialogue.speaker.sirin" : e.key()+".speaker",
                    null, 0xFFE6C5FF, 0xFFAA7ADB));
        }
        Map<String,List<DialogueLine>> segments = new LinkedHashMap<>();
        List<DialogueChoice> systems = new ArrayList<>();
        for (String system : SYSTEMS) {
            systems.add(new DialogueChoice("hk3gtl.prose.system."+system,system+".0"));
            List<Hk3ApprovedProse.Entry> items = Hk3ApprovedProse.system(system);
            for (int first=0; first<items.size(); first+=5) {
                int page=first/5; String menu=system+"."+page;
                List<DialogueChoice> options=new ArrayList<>();
                for (int j=first;j<Math.min(first+5,items.size());j++) {
                    var e=items.get(j);
                    options.add(new DialogueChoice(e.key()+".title",e.id()));
                    segments.put(e.id(),lines(e,List.of(new DialogueChoice("hk3gtl.prose.back",menu))));
                }
                if (page>0) options.add(new DialogueChoice("hk3gtl.prose.previous",system+"."+(page-1)));
                if (first+5<items.size()) options.add(new DialogueChoice("hk3gtl.prose.next",system+"."+(page+1)));
                options.add(new DialogueChoice("hk3gtl.prose.home","library"));
                segments.put(menu,List.of(new DialogueLine("system","hk3gtl.prose.readonly",null,options)));
            }
        }
        segments.put("library",List.of(new DialogueLine("system","hk3gtl.prose.readonly",null,systems)));
        DialogueRegistry.registerDialogue(new DialogueDefinition(LIBRARY,Map.copyOf(segments),"library",true,null));
        DialogueRegistry.registerDialogue(new DialogueDefinition(REVIEW_PREVIEW,reviewGraph(),"S201",true,null));
        DialogueRegistry.registerDialogue(new DialogueDefinition(FINALE_PREVIEW,finaleGraph(),"F01",true,null));
        com.sirin.hk3gtl.common.review.Hk3ReviewDialogues.register();
    }

    private static List<DialogueChoice> routes(Hk3ApprovedProse.Entry e) {
        List<DialogueChoice> choices=new ArrayList<>();
        for (int i=0;i<e.routes().size();i++) choices.add(new DialogueChoice(e.key()+".choice."+i,e.routes().get(i).target()));
        if (choices.isEmpty() && e.next()!=null) choices.add(new DialogueChoice("hk3gtl.prose.continue",e.next()));
        return choices;
    }
    public static Map<String,List<DialogueLine>> reviewGraph() {
        Map<String,List<DialogueLine>> result=new LinkedHashMap<>();
        for (var e:Hk3ApprovedProse.system("review")) result.put(e.id(),lines(e,routes(e)));
        return Map.copyOf(result);
    }
    public static Map<String,List<DialogueLine>> finaleGraph() {
        Map<String,List<DialogueLine>> result=new LinkedHashMap<>();
        for (var e:Hk3ApprovedProse.system("finale")) {
            if (e.id().equals("IF_MENU")) continue;
            result.put(e.id(),lines(e,routes(e)));
        }
        for (int page=0;page<6;page++) {
            List<DialogueChoice> options=new ArrayList<>();
            for (int i=page*5;i<Math.min(page*5+5,26);i++) {
                String id=String.format(Locale.ROOT,"IF-%02d",i+1);
                options.add(new DialogueChoice(Hk3ApprovedProse.get(id).key()+".title",id));
            }
            if (page>0) options.add(new DialogueChoice("hk3gtl.prose.previous",page==1?"IF_MENU":"IF_MENU_"+(page-1)));
            if (page<5) options.add(new DialogueChoice("hk3gtl.prose.next","IF_MENU_"+(page+1)));
            options.add(new DialogueChoice("hk3gtl.prose.return_finale","F06"));
            result.put(page==0?"IF_MENU":"IF_MENU_"+page,lines(Hk3ApprovedProse.get("IF_MENU"),options));
        }
        return Map.copyOf(result);
    }
    public static int ifIndex(String segment) {
        if (segment == null || !segment.matches("IF-[0-9]{2}")) return -1;
        int n=Integer.parseInt(segment.substring(3))-1;
        return n>=0 && n<26 ? n : -1;
    }
}
