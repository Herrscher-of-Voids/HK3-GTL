package com.sirin.hk3gtl.common.finale;

import net.minecraft.nbt.*;
import java.util.*;

/**
 * 【变更记录 #1】2026-10-01 16:49:18（修订135）
 * 删除：无；新增：按玩家保存会面UUID、完整资格快照和已确认段落，终止结果幂等。
 * 修改：暂停不清资格，入场后换队或工程变化不改本次快照，坏结局新申请必须重新评估。
 * 用途：服务端单线程个人终审账本；返回防御性副本，损坏存盘不能当新档解锁。
 */
public final class Hk3FinaleLedger {
    public enum State { OPEN, PASSED, BAD }
    private record Entry(UUID meeting,State state,String checkpoint,CompoundTag sources){}
    private final Map<UUID,Entry> people=new HashMap<>();
    public boolean open(UUID actor){var e=people.get(actor);return e!=null&&e.state==State.OPEN;}
    public UUID meeting(UUID actor){var e=people.get(actor);return e==null?null:e.meeting;}
    public String checkpoint(UUID actor){var e=people.get(actor);return e==null?"":e.checkpoint;}
    public CompoundTag sources(UUID actor){var e=people.get(actor);return e==null?new CompoundTag():e.sources.copy();}
    /** 已入场会面只由恢复入口继续；新申请不能覆盖活跃或已通过会面。 */
    public boolean begin(UUID actor,UUID meeting,Hk3FinaleRequirements.Evaluation evaluation,String first){
        var previous=people.get(actor);
        if(previous!=null&&previous.state!=State.BAD)return false;
        if(meeting==null||people.values().stream().anyMatch(e->e.meeting.equals(meeting))||!evaluation.ready()||!Hk3FinaleRequirements.validSnapshot(evaluation.sources(),actor)
                ||!validCheckpoint(first)||previous!=null&&previous.meeting.equals(meeting))return false;
        people.put(actor,new Entry(meeting,State.OPEN,first,evaluation.sources()));return true;
    }
    public boolean advance(UUID actor,UUID meeting,String checkpoint){
        var e=people.get(actor);
        if(e==null||e.state!=State.OPEN||!e.meeting.equals(meeting)||!validCheckpoint(checkpoint))return false;
        if(e.checkpoint.equals(checkpoint))return false;
        people.put(actor,new Entry(e.meeting,e.state,checkpoint,e.sources));return true;
    }
    public boolean finish(UUID actor,UUID meeting,State result){
        var e=people.get(actor);
        if(e==null||e.state!=State.OPEN||!e.meeting.equals(meeting)||result==null||result==State.OPEN)return false;
        if(result==State.PASSED&&!e.checkpoint.equals("FU01"))return false;
        people.put(actor,new Entry(e.meeting,result,e.checkpoint,e.sources));return true;
    }
    public void resetForDebug(UUID actor){people.remove(actor);}
    private static boolean validCheckpoint(String s){return s!=null&&!s.isBlank()&&s.length()<=128;}
    public CompoundTag save(){
        var root=new CompoundTag();root.putInt("Version",1);var rows=new CompoundTag();
        people.forEach((actor,e)->{var n=new CompoundTag();n.putUUID("Meeting",e.meeting);n.putString("State",e.state.name());
            n.putString("Checkpoint",e.checkpoint);n.put("Sources",e.sources.copy());rows.put(actor.toString(),n);});
        root.put("People",rows);return root;
    }
    public static Hk3FinaleLedger load(CompoundTag root){
        if(root.getInt("Version")!=1||!root.contains("People",Tag.TAG_COMPOUND))throw new IllegalStateException("终审会面账本格式损坏");
        var ledger=new Hk3FinaleLedger();var rows=root.getCompound("People");var meetings=new HashSet<UUID>();
        for(String key:rows.getAllKeys()){
            try{
                UUID actor=UUID.fromString(key);var n=rows.getCompound(key);State state=State.valueOf(n.getString("State"));
                if(!n.hasUUID("Meeting")||!meetings.add(n.getUUID("Meeting"))||!validCheckpoint(n.getString("Checkpoint"))
                    ||!Hk3FinaleRequirements.validSnapshot(n.getCompound("Sources"),actor)
                    ||state==State.PASSED&&!n.getString("Checkpoint").equals("FU01"))throw new IllegalStateException("终审会面字段损坏");
                ledger.people.put(actor,new Entry(n.getUUID("Meeting"),state,n.getString("Checkpoint"),n.getCompound("Sources").copy()));
            }catch(IllegalArgumentException e){throw new IllegalStateException("终审会面身份或状态损坏",e);}
        }
        return ledger;
    }
}
