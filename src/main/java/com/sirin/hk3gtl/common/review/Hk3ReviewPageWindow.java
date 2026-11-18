package com.sirin.hk3gtl.common.review;
import java.util.*;

public final class Hk3ReviewPageWindow {
    private final ArrayDeque<Hk3ReviewFrame> sent=new ArrayDeque<>();
    public void sent(Hk3ReviewFrame frame){
        if(!sent.isEmpty()&&!sent.peekLast().meeting().equals(frame.meeting()))sent.clear();
        sent.addLast(frame);while(sent.size()>32)sent.removeFirst();
    }
    public boolean mayPause(UUID scope,String dialogue,String segment,int nonce){return sent.stream().anyMatch(f->f.accepts(scope,dialogue,segment,nonce));}
    public int size(){return sent.size();}
}
