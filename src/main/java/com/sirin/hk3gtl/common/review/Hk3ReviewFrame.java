package com.sirin.hk3gtl.common.review;

import java.util.UUID;

/** 【变更记录 #1】2026-10-01 18:42:57（修订140）：删除无；新增逐页会面令牌；修改每次显示均刷新随机令牌；用途：旧页面、旧会面和重复网络包不能推进当前审查。 */
public record Hk3ReviewFrame(UUID meeting,UUID scope,String dialogue,String segment,int nonce) {
    public static Hk3ReviewFrame issue(UUID meeting,UUID scope,String dialogue,String segment){
        return new Hk3ReviewFrame(meeting,scope,dialogue,segment,java.util.concurrent.ThreadLocalRandom.current().nextInt());
    }
    public boolean accepts(UUID currentScope,String dialogue,String segment,int nonce){
        return scope.equals(currentScope)&&this.dialogue.equals(dialogue)&&this.segment.equals(segment)&&this.nonce==nonce;
    }
}
