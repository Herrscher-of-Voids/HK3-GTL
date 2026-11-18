package com.sirin.hk3gtl.common.review;

import java.util.UUID;

public record Hk3ReviewFrame(UUID meeting,UUID scope,String dialogue,String segment,int nonce) {
    public static Hk3ReviewFrame issue(UUID meeting,UUID scope,String dialogue,String segment){
        return new Hk3ReviewFrame(meeting,scope,dialogue,segment,java.util.concurrent.ThreadLocalRandom.current().nextInt());
    }
    public boolean accepts(UUID currentScope,String dialogue,String segment,int nonce){
        return scope.equals(currentScope)&&this.dialogue.equals(dialogue)&&this.segment.equals(segment)&&this.nonce==nonce;
    }
}
