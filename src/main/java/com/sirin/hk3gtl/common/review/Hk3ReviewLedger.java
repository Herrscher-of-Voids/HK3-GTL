package com.sirin.hk3gtl.common.review;

import java.util.*;
import net.minecraft.nbt.*;

/**
 * 【变更记录 #1】2026-09-30 20:31:18（修订117）
 * 删除：无；新增：一审代表/三问/重播/替补、二审检查点、个人补行与团队一次性许可账本。
 * 修改：资格、会面与结算分开；用途：服务端主线程状态机。此类不推断机器资格、不传送、不生成实体、不接受客户端资格字段。
 */
/** 【变更记录 #2】2026-10-01 01:30:10（修订125）：删除换队后旧二审永久占用个人会面的路径；新增中止历史阶段及换队处理；修改忙碌、重启和新会面检查统一忽略中止历史；用途：个人已完成经历保留，未完成会面不携带旧队资格或自动结算。 */
public final class Hk3ReviewLedger {
    public enum Kind { FIRST, SECOND }
    public enum Phase { OPENING, MENU, ANSWER, CLOSING, PAUSED, COMPLETE, ABANDONED }
    public record Result(boolean personalCompleted,boolean firstTeamSettlement,UUID scope,Kind kind,UUID meeting){}
    public record Snapshot(UUID id,UUID scope,Kind kind,UUID representative,Set<UUID> participants,List<Integer> questions,Phase phase,int replayIndex,String checkpoint,boolean supplement){}
    private static final class Meeting {
        UUID id,scope,representative;Kind kind;final Set<UUID> participants=new LinkedHashSet<>();
        final List<Integer> questions=new ArrayList<>();Phase phase;int replayIndex;String checkpoint;boolean supplement;
        Snapshot snapshot(){return new Snapshot(id,scope,kind,representative,Set.copyOf(participants),List.copyOf(questions),phase,replayIndex,checkpoint,supplement);}
    }
    private final Map<UUID,EnumSet<Kind>> qualified=new HashMap<>(),settled=new HashMap<>(),personal=new HashMap<>();
    private final Map<UUID,Meeting> meetings=new LinkedHashMap<>();
    private final Map<String,CompoundTag> qualificationSources=new HashMap<>();
    private final Map<String,UUID> settlementMeetings=new HashMap<>();
    public boolean qualified(UUID scope,Kind kind){return qualified.getOrDefault(scope,EnumSet.noneOf(Kind.class)).contains(kind);}
    public boolean settled(UUID scope,Kind kind){return settled.getOrDefault(scope,EnumSet.noneOf(Kind.class)).contains(kind);}
    public boolean experienced(UUID player,Kind kind){return personal.getOrDefault(player,EnumSet.noneOf(Kind.class)).contains(kind);}
    public UUID settlement(UUID scope,Kind kind){return settlementMeetings.get(scope+"/"+kind);}
    /** 只供真实资格验证器提交有来源的完整快照；本轮没有客户端/管理指令授权入口。 */
    public boolean qualify(UUID scope,Kind kind,CompoundTag verifiedSources){
        if(scope==null||kind==null||verifiedSources==null||verifiedSources.isEmpty()||qualified(scope,kind))return false;
        if(kind==Kind.SECOND&&!settled(scope,Kind.FIRST))return false;
        qualificationSources.put(scope+"/"+kind,verifiedSources.copy());qualified.computeIfAbsent(scope,k->EnumSet.noneOf(Kind.class)).add(kind);return true;
    }
    public CompoundTag sources(UUID scope,Kind kind){var source=qualificationSources.get(scope+"/"+kind);return source==null?new CompoundTag():source.copy();}
    public Snapshot meeting(UUID id){var m=meetings.get(id);return m==null?null:m.snapshot();}
    public List<Snapshot> sessions(UUID scope){return meetings.values().stream().filter(m->m.scope.equals(scope)).map(Meeting::snapshot).toList();}
    private static boolean ended(Meeting m){return m.phase==Phase.COMPLETE||m.phase==Phase.ABANDONED;}
    public boolean busy(UUID player){return meetings.values().stream().anyMatch(m->m.phase!=Phase.PAUSED&&!ended(m)&&m.participants.contains(player)&&!experienced(player,m.kind));}
    private boolean eligible(UUID player,Kind kind){return !experienced(player,kind)&&!busy(player);}
    public Snapshot beginFirst(UUID scope,List<UUID> onlineMembers,java.util.random.RandomGenerator random){
        if(!qualified(scope,Kind.FIRST))return null;
        if(meetings.values().stream().anyMatch(m->m.scope.equals(scope)&&m.kind==Kind.FIRST&&!ended(m)))return null;
        var candidates=onlineMembers.stream().filter(Objects::nonNull).distinct().filter(p->eligible(p,Kind.FIRST)).toList();if(candidates.isEmpty())return null;
        var m=new Meeting();m.id=UUID.randomUUID();m.scope=scope;m.kind=Kind.FIRST;m.representative=candidates.get(random.nextInt(candidates.size()));
        m.participants.addAll(candidates);m.phase=Phase.OPENING;m.checkpoint="first_review.open";m.supplement=settled(scope,Kind.FIRST);meetings.put(m.id,m);return m.snapshot();
    }
    /** 重开由仍在原队且未完成的在线成员发起；保留问题及其顺序，从开场重播。 */
    public Snapshot restartFirst(UUID meeting,UUID requester,List<UUID> currentOnlineMembers,java.util.random.RandomGenerator random){
        var m=meetings.get(meeting);if(m==null||m.kind!=Kind.FIRST||m.phase!=Phase.PAUSED)return null;
        var candidates=currentOnlineMembers.stream().filter(Objects::nonNull).distinct().filter(p->eligible(p,Kind.FIRST)).toList();
        if(!candidates.contains(requester))return null;
        m.participants.clear();m.participants.addAll(candidates);m.representative=candidates.get(random.nextInt(candidates.size()));m.replayIndex=0;m.phase=Phase.OPENING;m.checkpoint="first_review.open";return m.snapshot();
    }
    private boolean controls(Meeting m,UUID player){return m!=null&&m.kind==Kind.FIRST&&m.representative.equals(player)&&m.participants.contains(player);}
    public boolean openingRead(UUID id,UUID player){
        var m=meetings.get(id);if(!controls(m,player)||m.phase!=Phase.OPENING)return false;m.replayIndex=0;
        m.phase=m.questions.isEmpty()?Phase.MENU:Phase.ANSWER;return true;
    }
    public boolean choose(UUID id,UUID player,int question){
        var m=meetings.get(id);if(!controls(m,player)||m.phase!=Phase.MENU||question<1||question>8||m.questions.size()>=3||m.questions.contains(question))return false;
        m.questions.add(question);m.replayIndex=m.questions.size()-1;m.phase=Phase.ANSWER;return true;
    }
    public boolean answerRead(UUID id,UUID player,int expectedQuestion){
        var m=meetings.get(id);if(!controls(m,player)||m.phase!=Phase.ANSWER||m.questions.get(m.replayIndex)!=expectedQuestion)return false;
        if(++m.replayIndex<m.questions.size())return true;
        m.phase=m.questions.size()==3?Phase.CLOSING:Phase.MENU;return true;
    }
    /** 每个在场者亲自读完收束才记个人经历；团队许可最多生成一次，不替离线成员签到。 */
    public Result finishFirst(UUID id,UUID player){
        var m=meetings.get(id);if(m==null||m.kind!=Kind.FIRST||m.phase!=Phase.CLOSING||m.questions.size()!=3||!m.participants.contains(player)||experienced(player,Kind.FIRST))return null;
        return complete(m,player);
    }
    public Snapshot beginSecond(UUID scope,UUID player){
        if(!qualified(scope,Kind.SECOND)||!experienced(player,Kind.FIRST)||!eligible(player,Kind.SECOND))return null;
        if(meetings.values().stream().anyMatch(m->m.kind==Kind.SECOND&&!ended(m)&&m.representative.equals(player)))return null;
        var m=new Meeting();m.id=UUID.randomUUID();m.scope=scope;m.kind=Kind.SECOND;m.representative=player;m.participants.add(player);m.phase=Phase.OPENING;
        m.supplement=settled(scope,Kind.SECOND);m.checkpoint=m.supplement?"SP01":"S201";meetings.put(m.id,m);return m.snapshot();
    }
    /** 实际合法边由批准正文图校验；客户端不能传任意目标或完成旗标。 */
    public boolean advanceSecond(UUID id,UUID player,String expected,int choice){
        var m=meetings.get(id);if(m==null||m.kind!=Kind.SECOND||!m.representative.equals(player)||m.phase!=Phase.OPENING||!m.checkpoint.equals(expected))return false;
        var entry=com.sirin.hk3gtl.common.narrative.Hk3ApprovedProse.get(expected);if(entry==null||!entry.system().equals("review"))return false;
        String next;
        if(!entry.routes().isEmpty()){if(choice<0||choice>=entry.routes().size())return false;next=entry.routes().get(choice).target();}
        else {if(choice!=0||entry.next()==null)return false;next=entry.next();}
        if(next.equals("S207")&&(m.supplement||settled(m.scope,Kind.SECOND))){m.supplement=true;next="SP02";}
        m.checkpoint=next;return true;
    }
    public Result finishSecond(UUID id,UUID player){
        var m=meetings.get(id);if(m==null||m.kind!=Kind.SECOND||m.phase!=Phase.OPENING||!m.representative.equals(player)||!m.checkpoint.equals("S209")||experienced(player,Kind.SECOND))return null;
        return complete(m,player);
    }
    private Result complete(Meeting m,UUID player){
        personal.computeIfAbsent(player,k->EnumSet.noneOf(Kind.class)).add(m.kind);boolean first=settled.computeIfAbsent(m.scope,k->EnumSet.noneOf(Kind.class)).add(m.kind);
        if(first)settlementMeetings.put(m.scope+"/"+m.kind,m.id);
        if(m.participants.stream().allMatch(p->experienced(p,m.kind)))m.phase=Phase.COMPLETE;
        return new Result(true,first,m.scope,m.kind,m.id);
    }
    /** 非代表离开仅移除本人，代表未完成时中断整场；二审保留同次会面检查点。 */
    public void depart(UUID player){
        for(var m:meetings.values())if(!ended(m)&&m.participants.contains(player)){
            if(!experienced(player,m.kind)&&m.representative.equals(player))m.phase=Phase.PAUSED;
            if(m.kind==Kind.FIRST)m.participants.remove(player);
            if(m.phase!=Phase.PAUSED&&m.participants.stream().allMatch(p->experienced(p,m.kind)))m.phase=Phase.COMPLETE;
        }
    }
    public Snapshot resumeSecond(UUID id,UUID player){var m=meetings.get(id);if(m==null||m.kind!=Kind.SECOND||m.phase!=Phase.PAUSED||!m.representative.equals(player)||busy(player))return null;m.phase=Phase.OPENING;return m.snapshot();}
    /** 离队与普通断线不同：一审仍留给原队重开，个人二审保留中止历史但不能携旧资格继续。 */
    public void leaveTeam(UUID player){
        depart(player);
        for(var m:meetings.values())if(!ended(m)&&m.kind==Kind.SECOND&&m.representative.equals(player))m.phase=Phase.ABANDONED;
    }
    /** 服务器重启后不能把此前的在线列表当作现在仍在场。 */
    public void suspendAll(){for(var m:meetings.values())if(!ended(m)){m.phase=Phase.PAUSED;if(m.kind==Kind.FIRST)m.participants.clear();}}
    public CompoundTag save(){
        var root=new CompoundTag();root.putInt("Schema",1);root.put("Qualified",flags(qualified));root.put("Settled",flags(settled));root.put("Personal",flags(personal));
        var sources=new CompoundTag();qualificationSources.forEach((key,value)->sources.put(key,value.copy()));root.put("Sources",sources);
        var receipts=new CompoundTag();settlementMeetings.forEach(receipts::putUUID);root.put("Settlements",receipts);
        var rows=new ListTag();for(var m:meetings.values()){
            var n=new CompoundTag();n.putUUID("Id",m.id);n.putUUID("Scope",m.scope);n.putUUID("Representative",m.representative);n.putString("Kind",m.kind.name());n.putString("Phase",m.phase.name());
            var people=new ListTag();m.participants.forEach(p->people.add(StringTag.valueOf(p.toString())));n.put("Participants",people);
            n.putIntArray("Questions",m.questions.stream().mapToInt(Integer::intValue).toArray());n.putInt("Replay",m.replayIndex);n.putString("Checkpoint",m.checkpoint);n.putBoolean("Supplement",m.supplement);rows.add(n);
        }root.put("Meetings",rows);return root;
    }
    private static CompoundTag flags(Map<UUID,EnumSet<Kind>> input){var n=new CompoundTag();input.forEach((id,kinds)->{var list=new ListTag();kinds.forEach(k->list.add(StringTag.valueOf(k.name())));n.put(id.toString(),list);});return n;}
    private static void flags(CompoundTag n,Map<UUID,EnumSet<Kind>> result){for(String id:n.getAllKeys()){if(!n.contains(id,Tag.TAG_LIST))throw new IllegalArgumentException("审查标记类型错误");var list=n.getList(id,Tag.TAG_STRING);if(((ListTag)n.get(id)).size()!=list.size())throw new IllegalArgumentException("审查标记内容错误");var set=EnumSet.noneOf(Kind.class);for(Tag raw:list)if(!set.add(Kind.valueOf(raw.getAsString())))throw new IllegalArgumentException("重复审查标记");result.put(UUID.fromString(id),set);}}
    public static Hk3ReviewLedger load(CompoundTag root){
        if(root.getInt("Schema")!=1||!root.contains("Meetings",Tag.TAG_LIST)||!root.contains("Qualified",Tag.TAG_COMPOUND)||!root.contains("Settled",Tag.TAG_COMPOUND)||!root.contains("Personal",Tag.TAG_COMPOUND))throw new IllegalArgumentException("审查账本结构损坏");
        var data=new Hk3ReviewLedger();flags(root.getCompound("Qualified"),data.qualified);flags(root.getCompound("Settled"),data.settled);flags(root.getCompound("Personal"),data.personal);
        if(((ListTag)root.get("Meetings")).size()!=root.getList("Meetings",Tag.TAG_COMPOUND).size())throw new IllegalArgumentException("会面条目类型错误");
        var sources=root.getCompound("Sources");for(String key:sources.getAllKeys())data.qualificationSources.put(key,sources.getCompound(key).copy());
        var receipts=root.getCompound("Settlements");for(String key:receipts.getAllKeys())data.settlementMeetings.put(key,receipts.getUUID(key));
        for(Tag raw:root.getList("Meetings",Tag.TAG_COMPOUND)){
            var n=(CompoundTag)raw;var m=new Meeting();m.id=n.getUUID("Id");m.scope=n.getUUID("Scope");m.representative=n.getUUID("Representative");m.kind=Kind.valueOf(n.getString("Kind"));m.phase=Phase.valueOf(n.getString("Phase"));
            for(Tag person:n.getList("Participants",Tag.TAG_STRING))m.participants.add(UUID.fromString(person.getAsString()));
            for(int q:n.getIntArray("Questions")){if(q<1||q>8||m.questions.contains(q))throw new IllegalArgumentException("无效三问记录");m.questions.add(q);}
            m.replayIndex=n.getInt("Replay");m.checkpoint=n.getString("Checkpoint");m.supplement=n.getBoolean("Supplement");
            if(m.questions.size()>3||m.replayIndex<0||m.replayIndex>m.questions.size()||!data.qualified(m.scope,m.kind)||data.sources(m.scope,m.kind).isEmpty()||data.meetings.putIfAbsent(m.id,m)!=null)throw new IllegalArgumentException("无效审查会面");
            if(m.kind==Kind.FIRST&&((m.phase==Phase.ANSWER&&m.replayIndex>=m.questions.size())||(m.phase==Phase.CLOSING&&m.questions.size()!=3)))throw new IllegalArgumentException("三问阶段与记录不一致");
            if(m.kind==Kind.SECOND){var entry=com.sirin.hk3gtl.common.narrative.Hk3ApprovedProse.get(m.checkpoint);if(entry==null||!entry.system().equals("review"))throw new IllegalArgumentException("二审检查点未知");}
        }
        data.qualified.forEach((scope,kinds)->kinds.forEach(kind->{if(data.sources(scope,kind).isEmpty())throw new IllegalArgumentException("缺资格来源");}));
        data.settled.forEach((scope,kinds)->kinds.forEach(kind->{
            var m=data.meetings.get(data.settlement(scope,kind));if(m==null||!m.scope.equals(scope)||m.kind!=kind)throw new IllegalArgumentException("许可缺完整会面来源");
            if(kind==Kind.FIRST&&m.questions.size()!=3||kind==Kind.SECOND&&!m.checkpoint.equals("S209"))throw new IllegalArgumentException("许可引用未完成会面");
        }));
        data.personal.forEach((player,kinds)->{if(kinds.contains(Kind.SECOND)&&!kinds.contains(Kind.FIRST))throw new IllegalArgumentException("个人二审缺一审经历");});
        data.qualified.forEach((scope,kinds)->{if(kinds.contains(Kind.SECOND)&&!data.settled(scope,Kind.FIRST))throw new IllegalArgumentException("二审资格缺本队一审许可");});
        for(var entry:data.settlementMeetings.entrySet()){var m=data.meetings.get(entry.getValue());if(m==null||!entry.getKey().equals(m.scope+"/"+m.kind)||!data.settled(m.scope,m.kind))throw new IllegalArgumentException("许可来源错位");}
        return data;
    }
}
