package com.sirin.hk3gtl.common.review;

import com.sirin.hk3gtl.common.dialogue.*;
import com.sirin.hk3gtl.common.dialogue.definition.Hk3ApprovedDialogues;
import com.sirin.hk3gtl.common.narrative.Hk3ApprovedProse;
import java.util.*;

/** 【变更记录 #1】2026-10-01 18:42:57（修订140）：删除无；新增正式审查逐句图及三问菜单；修改首次和补行使用不同收束；用途：仅定义显示，许可由服务端会面核验，不改已批准正文。 */
public final class Hk3ReviewDialogues {
    public static final String FIRST="hk3_review_first", SECOND="hk3_review_second", NOTICE="hk3_review_notice";
    private Hk3ReviewDialogues(){}
    public static boolean formal(String id){return FIRST.equals(id)||SECOND.equals(id);}
    public static String id(Hk3ReviewLedger.Kind kind){return kind==Hk3ReviewLedger.Kind.FIRST?FIRST:SECOND;}
    public static List<Integer> remaining(int mask){
        List<Integer> result=new ArrayList<>();for(int q=1;q<=8;q++)if((mask&(1<<(q-1)))==0)result.add(q);return List.copyOf(result);
    }
    public static int mask(Hk3ReviewLedger.Snapshot m){int mask=0;for(int q:m.questions())mask|=1<<(q-1);return mask;}
    private static List<DialogueLine> text(String key,List<DialogueChoice> choices){return List.of(new DialogueLine("system",key,null,choices));}
    private static List<DialogueChoice> confirm(){return List.of(new DialogueChoice("hk3gtl.review.confirm","wait"));}
    public static void register(){
        Map<String,List<DialogueLine>> first=new LinkedHashMap<>();
        for(var e:Hk3ApprovedProse.system("first_review"))first.put(e.id(),Hk3ApprovedDialogues.lines(e,confirm()));
        first.put("supplement",text("hk3gtl.review.supplement",confirm()));
        first.put("wait",text("hk3gtl.review.wait",List.of(new DialogueChoice("hk3gtl.review.refresh","wait"))));
        for(int mask=0;mask<256;mask++)if(Integer.bitCount(mask)<3){
            var choices=new ArrayList<DialogueChoice>();for(int q:remaining(mask))choices.add(new DialogueChoice("hk3gtl.approved.first_review.question."+q+".title","first_review.question."+q));
            first.put("menu."+mask,text("hk3gtl.review.choose."+Integer.bitCount(mask),choices));
        }
        DialogueRegistry.registerDialogue(new DialogueDefinition(FIRST,Map.copyOf(first),"first_review.open",true,null));
        Map<String,List<DialogueLine>> second=new LinkedHashMap<>(Hk3ApprovedDialogues.reviewGraph());
        for(String id:List.of("S209","SP06"))second.put(id,Hk3ApprovedDialogues.lines(Hk3ApprovedProse.get(id),List.of(new DialogueChoice("hk3gtl.review.confirm",id))));
        DialogueRegistry.registerDialogue(new DialogueDefinition(SECOND,Map.copyOf(second),"S201",true,null));
        DialogueRegistry.registerDialogue(new DialogueDefinition(NOTICE,Map.of("SP04",Hk3ApprovedDialogues.lines(Hk3ApprovedProse.get("SP04"),List.of()),"SP05",Hk3ApprovedDialogues.lines(Hk3ApprovedProse.get("SP05"),List.of())),"SP04",true,null));
    }
}
