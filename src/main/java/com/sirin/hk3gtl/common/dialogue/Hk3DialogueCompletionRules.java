package com.sirin.hk3gtl.common.dialogue;
/** 【变更记录 #1】2026-09-30 20:31:18（修订117）：删除无；新增服务端正常结束检查；修改无；用途：关闭/断线不调用奖励处理器，客户端完成字段不能越过当前未作选择的节点。 */
public final class Hk3DialogueCompletionRules {
    private Hk3DialogueCompletionRules(){}
    public static boolean maySettle(DialogueDefinition definition,String segment,boolean completed){
        if(!completed||definition==null)return false;
        var lines=definition.segments().get(segment);return lines!=null&&!lines.isEmpty()&&lines.stream().allMatch(line->line.choices()==null||line.choices().isEmpty());
    }
}
