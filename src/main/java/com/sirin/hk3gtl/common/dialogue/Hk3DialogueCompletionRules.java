package com.sirin.hk3gtl.common.dialogue;
 
public final class Hk3DialogueCompletionRules {
    private Hk3DialogueCompletionRules(){}
    public static boolean maySettle(DialogueDefinition definition,String segment,boolean completed){
        if(!completed||definition==null)return false;
        var lines=definition.segments().get(segment);return lines!=null&&!lines.isEmpty()&&lines.stream().allMatch(line->line.choices()==null||line.choices().isEmpty());
    }
}
