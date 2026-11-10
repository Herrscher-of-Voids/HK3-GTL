package com.sirin.hk3gtl.common.narrative;

import com.sirin.hk3gtl.common.communication.*;
import com.sirin.hk3gtl.common.finale.Hk3FinaleRequirements;
import com.sirin.hk3gtl.common.research.*;
import com.sirin.hk3gtl.common.review.*;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerPlayer;
import java.util.*;
import java.util.function.Predicate;

/**
 * 【变更记录 #1】2026-10-01 20:33:47（修订148）
 * 删除：无；新增：研究、通信、审查与旧正式事件共用的只读核验目录。
 * 修改：按事件去重；互斥交流读取完成任一路线的本人回执；旧展示解锁不作为亲历证明。
 * 用途：手机、卷轴和终审查询同源；未迁移事件逐项等待，终审自身与纯彩蛋不构成前置。
 */
/** 【变更记录 #2】2026-10-01 22:50:14（第2次备注 · 内测5修订155）：删除玩家展示中的旧电压及开发说明；新增现行正文投影或对应回归；修改仅限呈现与检索，不改变进度、回执、触发条件或权限；用途：统一发布版玩家文案，历史备注保留。 */
/**
 * 【变更记录 #3】2026-11-04 05:57:01（第3次备注 · 内测5修订196）
 * 删除：64旧事件统一占位原因；新增：逐项迁移来源与未接条件。
 * 修改：仅OT001按本人完整首信衔接，63原要求仍等待；逐项详情进入手机与卷轴共用正文。
 * 用途：保持172条原目录及收藏隔离，不将候选研究、物品或旧解锁当正式资格。
 */
/** 【变更记录 #4】2026-11-04 06:12:15（第4次备注 · 内测5修订196）：删除首信单项阶段适配；新增完整64条现行来源及56研究型本人全文账本读取；修改手机/卷轴/终审共用同一172项目录；用途：精确区分未完成与真实上游未开放，不以旧收藏或目录存在授资格。 */
public final class Hk3FormalArchive {
    public enum Group { RESEARCH, COMMUNICATION, REVIEW, LEGACY }
    public record Entry(String id, String label, Group group, Hk3FinaleRequirements.State state, String detail) {}
    public record Result(List<Entry> entries) {
        public Result { entries=List.copyOf(entries); }
        public long count(Hk3FinaleRequirements.State state) { return entries.stream().filter(e->e.state()==state).count(); }
        public boolean complete() { return !entries.isEmpty()&&count(Hk3FinaleRequirements.State.COMPLETE)==entries.size(); }
        public String counts() { return "已完成 "+count(Hk3FinaleRequirements.State.COMPLETE)+"；未完成 "+count(Hk3FinaleRequirements.State.MISSING)+"；尚未开放 "+count(Hk3FinaleRequirements.State.WAITING); }
        public Hk3FinaleRequirements.Fact fact() {
            if(count(Hk3FinaleRequirements.State.WAITING)>0)return Hk3FinaleRequirements.Fact.waiting(counts()+"。详情见文明档案逐项目录");
            if(!complete())return Hk3FinaleRequirements.Fact.missing(counts()+"。详情见文明档案逐项目录");
            var proof=new CompoundTag();proof.putInt("CatalogVersion",2);
            for(var entry:entries)proof.putString(entry.id(),entry.group().name());
            return Hk3FinaleRequirements.Fact.complete(proof);
        }
    }
    private Hk3FormalArchive() {}
    public static Result evaluate(ServerPlayer player) {
        UUID actor=player.getUUID(),team=Hk3ResearchTeams.scope(player.server,actor);
        var data=Hk3ResearchData.get(player);
        return evaluate(id->data.completed(team,id),Hk3TeamContactData.get(player.server),
            Hk3PersonalCommunicationData.get(player.server),Hk3ReviewData.get(player.server).snapshot(),Hk3LegacyArchiveData.get(player.server),actor);
    }
    /** 同一适配路径供服务器与隔离账本测试调用；没有收藏、持物或客户端自报参数。 */
    public static Result evaluate(Predicate<String> research, Hk3TeamContactData contacts,
            Hk3PersonalCommunicationData personal, Hk3ReviewLedger reviews, UUID actor) {
        return evaluate(research,contacts,personal,reviews,new Hk3LegacyArchiveData(),actor);
    }
    public static Result evaluate(Predicate<String> research, Hk3TeamContactData contacts,
            Hk3PersonalCommunicationData personal, Hk3ReviewLedger reviews,Hk3LegacyArchiveData readings, UUID actor) {
        var rows=new ArrayList<Entry>();
        for(var plan:Hk3ResearchPlans.all().values())rows.add(record(plan.id(),Component.translatable(plan.nameKey()).getString(),
            Group.RESEARCH,research.test(plan.id()),"本队研究账本；在对应研究所完成课题"));
        rows.add(record("communication:first_contact","奥托首信、答复与观察附件",Group.COMMUNICATION,
            contacts.experienced(actor),"手机信件 → 奥托首信 → 个人补谈"));
        for(var topic:Hk3DiplomacyData.TOPICS)rows.add(record("communication:"+topic.id(),topic.name()+"正式交流",
            Group.COMMUNICATION,personal.experienced(actor,topic.id()),"手机信件 → "+topic.name()+" → 亲自补行本段交流；互斥路线择一"));
        for(var kind:Hk3ReviewLedger.Kind.values())rows.add(record("review:"+kind.name(),kind==Hk3ReviewLedger.Kind.FIRST?"本人一审会面":"本人二审会面",
            Group.REVIEW,reviews.experienced(actor,kind),"请亲自前往会面"));
        // 同一事件的旧摘要及全文合并；最终会面只作历史，不可能成为自己的入场门槛。
        var legacy=new TreeMap<String,Hk3NarrativeNode>();
        for(var node:Hk3NarrativeNodes.all())if(Hk3CollectionCatalog.kind(node.id())==Hk3CollectionCatalog.Kind.FORMAL
                &&!node.unlockEventId().equals("E-HQ-005"))legacy.put(node.unlockEventId(),node);
        for(var event:legacy.entrySet()) {
            var fact=Hk3LegacyArchiveMigration.evaluate(event.getKey(),research,contacts,personal,reviews,readings,actor);
            rows.add(new Entry(event.getKey(),Hk3LegacyArchiveMigration.all().get(event.getKey()).title(),
                Group.LEGACY,fact.state(),fact.detail()));
        }
        return new Result(rows);
    }
    private static Entry record(String id,String label,Group group,boolean completed,String detail) {
        return new Entry(id,label,group,completed?Hk3FinaleRequirements.State.COMPLETE:Hk3FinaleRequirements.State.MISSING,detail);
    }
    public static String summary(Result result) {
        var text=new StringBuilder("正式文明档案 · 逐项核验\n").append(result.counts()).append("\n");
        text.append("研究进度由团队共享；交流与审查记录你亲自走过的旅程。\n");
        for(var group:Group.values()) {
            text.append('\n').append(switch(group){case RESEARCH->"全部研究";case COMMUNICATION->"正式通信";case REVIEW->"正式会面";case LEGACY->"更多经历";}).append('\n');
            for(var e:result.entries())if(e.group()==group) {
                text.append(switch(e.state()){case COMPLETE->"[已完成] ";case MISSING->"[未完成] ";case WAITING->"[尚未开放] ";})
                    .append(e.id()).append(" · ").append(e.label()).append('\n');
                if(group==Group.COMMUNICATION||group==Group.REVIEW||group==Group.LEGACY)text.append(e.detail()).append('\n');
            }
        }
        return text.append("").toString();
    }
}

// 【变更记录 · 修订161】2026-10-17 14:11:55：本轮仅将活动类名、资源与工业配方引用迁移为长期业务命名；历史备注保留，不代表旧逻辑已全部按现行设计重写。
