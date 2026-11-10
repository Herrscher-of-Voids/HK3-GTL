package com.sirin.hk3gtl.common.phone;

import java.util.*;

/**
 * 【变更记录 #1】2026-09-30 16:16:37（内测5修订110）
 * 删除：被新版通知读取流程替代的旧分支，历史备注保留。
 * 新增／修改：新增纯逻辑浮层队列：最多32待显示组、6秒、研究2秒合并、待处理优先、溢出汇总；不修改收件箱已读。
 * 用途：通知与业务结果分离，服务端授权和个人持久化；不改结构、贴图和贸易。
 */
public final class Hk3NotificationQueue {
    public record Notice(String id,String title,String body,String kind,int priority) {}
    public record Card(String title,String body,int count,int priority,String kind) {}
    private static final class Group {
        final String kind;final long created;final int priority;
        final String title,body;int count=1;long shown=-1;
        Group(Notice n,long now){kind=n.kind();created=now;priority=n.priority();title=n.title();body=n.body();}
        Card card(){return new Card(title,body,count,priority,kind);}
    }
    private final List<Group> waiting=new ArrayList<>(),active=new ArrayList<>();
    private final LinkedHashSet<String> seen=new LinkedHashSet<>();
    private int overflow;
    public boolean offer(Notice n,long now){
        if(!seen.add(n.id()))return false;
        while(seen.size()>2048)seen.remove(seen.iterator().next());
        if(n.kind().equals("research"))for(var g:waiting)if(g.kind.equals("research")&&now-g.created<2000){g.count++;return true;}
        var group=new Group(n,now);
        if(waiting.size()>=32){
            var lowest=waiting.stream().min(Comparator.comparingInt((Group g)->g.priority).thenComparingLong(g->g.created)).orElseThrow();
            if(n.priority()>lowest.priority){waiting.remove(lowest);overflow+=lowest.count;}else{overflow++;return true;}
        }
        waiting.add(group);return true;
    }
    public List<Card> visible(long now,int slots){
        slots=Math.max(1,Math.min(2,slots));
        // 窄屏收起第二张时重新排队；队列已满则归入汇总，持久正文不受影响。
        active.removeIf(g->now-g.shown>=6000);
        while(active.size()>slots){var g=active.remove(active.size()-1);g.shown=-1;if(waiting.size()<32)waiting.add(g);else overflow+=g.count;}
        waiting.sort(Comparator.comparingInt((Group g)->-g.priority).thenComparingLong(g->g.created));
        while(active.size()<slots){
            var next=waiting.stream().filter(g->!g.kind.equals("research")||now-g.created>=2000).findFirst().orElse(null);
            if(next==null){
                if(waiting.isEmpty()&&overflow>0){next=new Group(new Notice("summary","更多消息已保存","请到收件箱逐项查看，未读状态保持不变。","notice",1),now);next.count=overflow;overflow=0;}
                else break;
            }else waiting.remove(next);
            next.shown=now;active.add(next);
        }
        return active.stream().map(Group::card).toList();
    }
    public int pendingGroups(){return waiting.size();}
    public int overflowCount(){return overflow;}
    public void clear(){waiting.clear();active.clear();seen.clear();overflow=0;}
}
