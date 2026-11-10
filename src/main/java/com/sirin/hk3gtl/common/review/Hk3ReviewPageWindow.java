package com.sirin.hk3gtl.common.review;
import java.util.*;
/** 【变更记录 #1】2026-10-01 18:54:07（修订140）：删除无；新增有界的本次会面已发页面窗口；修改关闭允许匹配同会面最近页面，选择仍只认当前令牌；用途：解决组播推进与ESC交错造成的隐形等待，不接受上次会面请求。 */
public final class Hk3ReviewPageWindow {
    private final ArrayDeque<Hk3ReviewFrame> sent=new ArrayDeque<>();
    public void sent(Hk3ReviewFrame frame){
        if(!sent.isEmpty()&&!sent.peekLast().meeting().equals(frame.meeting()))sent.clear();
        sent.addLast(frame);while(sent.size()>32)sent.removeFirst();
    }
    public boolean mayPause(UUID scope,String dialogue,String segment,int nonce){return sent.stream().anyMatch(f->f.accepts(scope,dialogue,segment,nonce));}
    public int size(){return sent.size();}
}
