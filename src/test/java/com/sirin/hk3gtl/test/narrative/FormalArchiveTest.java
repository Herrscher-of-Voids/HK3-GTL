package com.sirin.hk3gtl.test.narrative;

import com.sirin.hk3gtl.common.narrative.*;
import com.sirin.hk3gtl.common.communication.*;
import com.sirin.hk3gtl.common.review.Hk3ReviewLedger;
import com.sirin.hk3gtl.common.finale.Hk3FinaleRequirements.State;
import net.minecraft.nbt.CompoundTag;
import java.util.*;

/** 【变更记录 #1】2026-10-01 20:34:36（修订148）：删除无；新增目录去重、收藏隔离与资格保守检查；修改无；用途：验证生产核验器，不代替实机验收。 */
/** 【变更记录 #2】2026-10-01 22:50:14（第2次备注 · 内测5修订155）：删除玩家展示中的旧电压及开发说明；新增现行正文投影或对应回归；修改仅限呈现与检索，不改变进度、回执、触发条件或权限；用途：统一发布版玩家文案，历史备注保留。 */
/**
 * 【变更记录 #3】2026-11-04 05:57:01（第3次备注 · 内测5修订196）
 * 删除：64条全部等待的旧断言；新增：首信两分支四步、错令牌/错成员、加载恢复与只读核验。
 * 修改：172项不变，63条未接事实不被共享研究或他人经历替代；用途：验证真实生产适配器，不代替专服UI验收。
 */
/** 【变更记录 #4】2026-11-04 06:10:00（第4次备注 · 内测5修订196）：删除首信单条阶段断言；新增64条准确来源与共享研究不替本人全文的回归；修改全部现行来源接入后的状态核验；用途：保留172项与原事件身份，不以目录可评估冒充上游可玩。 */
public final class FormalArchiveTest {
    private static void check(boolean value,String reason) { if(!value)throw new AssertionError(reason); }
    private static Hk3FormalArchive.Entry event(Hk3FormalArchive.Result result,String id) {
        return result.entries().stream().filter(e->e.id().equals(id)).findFirst().orElseThrow();
    }
    public static void run() {
        var contacts=new Hk3TeamContactData();var personal=new Hk3PersonalCommunicationData();var reviews=new Hk3ReviewLedger();
        var readings=new Hk3LegacyArchiveData();var actor=UUID.randomUUID();
        var empty=Hk3FormalArchive.evaluate(id->false,contacts,personal,reviews,readings,actor);
        check(empty.entries().size()==172&&empty.count(State.COMPLETE)==0&&!empty.complete(),"172条原目录不减少，新玩家无正式完成");
        long legacy=Hk3NarrativeNodes.all().stream().filter(n->Hk3CollectionCatalog.kind(n.id())==Hk3CollectionCatalog.Kind.FORMAL)
            .map(Hk3NarrativeNode::unlockEventId).filter(id->!id.equals("E-HQ-005")).distinct().count();
        check(legacy==64&&Hk3LegacyArchiveMigration.all().size()==64,"64事件逐项映射并去重");
        check(empty.entries().stream().map(Hk3FormalArchive.Entry::id).distinct().count()==172,"目录ID无重复");
        check(empty.entries().stream().noneMatch(e->e.id().equals("E-HQ-005")||e.id().startsWith("E-EG-")),"不要求终审自身和彩蛋");
        var flags=new CompoundTag();for(var node:Hk3NarrativeNodes.all())Hk3NarrativeLog.unlock(flags,node.id());
        check(Hk3FormalArchive.evaluate(id->false,contacts,personal,reviews,readings,actor).equals(empty),"旧解锁及调试标记不能授资格");
        var studied=Hk3FormalArchive.evaluate(id->true,contacts,personal,reviews,readings,actor);
        check(studied.count(State.COMPLETE)==100&&studied.count(State.MISSING)==72&&studied.count(State.WAITING)==0,"全部准确研究仍不能替代本人56篇全文和其他个人经历");
        check(studied.fact().state()==State.MISSING&&studied.fact().source().isEmpty(),"共享研究不产生完整档案回执");
        for(var rule:Hk3LegacyArchiveMigration.all().values()) {
            check(event(studied,rule.eventId()).state()==State.MISSING,"有研究但没本人回执不完成任何旧事件");
            if(rule.kind()==Hk3LegacyArchiveMigration.SourceKind.RESEARCH) {
                var source=Hk3LegacyArchiveMigration.prerequisite(rule,id->id.equals(rule.source()),contacts,personal,reviews,actor);
                check(source.state()==State.COMPLETE&&source.source().getString("Source").equals(rule.source()),"准确课题只建立本人阅读前置");
                check(Hk3LegacyArchiveMigration.prerequisite(rule,id->id.equals("RN-NOT-REAL"),contacts,personal,reviews,actor).state()!=State.COMPLETE,"错误课题不建立阅读前置");
            }
        }
        String text=Hk3FormalArchive.summary(studied);
        check(text.contains("RN-HED")&&text.contains("E-OT-001")&&text.contains("本人"),"逐项输出真实缺项");
        check(text.getBytes(java.nio.charset.StandardCharsets.UTF_8).length<50000,"正文保持NBT单字符串安全余量");
        boolean immutable=false;try{studied.entries().clear();}catch(UnsupportedOperationException expected){immutable=true;}
        check(immutable,"查询结果不可变");
        firstContact(true);firstContact(false);
        check(Hk3LegacyArchiveMigration.evaluate("E-HQ-005",id->true,contacts,personal,reviews,readings,actor).state()==State.WAITING,"终审自身不注入目录");
        check(Hk3LegacyArchiveMigration.evaluate("E-OT-999",id->true,contacts,personal,reviews,readings,actor).source().isEmpty(),"未知事件不生成来源");
        System.out.println("FormalArchiveTest passed: 172 entries, 64 exact-source migrations; shared research cannot replace personal full reading, communication or review");
    }
    private static void firstContact(boolean accepted) {
        var contacts=new Hk3TeamContactData();var personal=new Hk3PersonalCommunicationData();var reviews=new Hk3ReviewLedger();var readings=new Hk3LegacyArchiveData();
        UUID actor=UUID.randomUUID(),team=UUID.randomUUID(),other=UUID.randomUUID();
        check(contacts.discover(team,actor,10),"发现首信");contacts.read(team,actor);
        check(contacts.decide(team,actor,actor,true,contacts.event(team),accepted,11),"本人明确接受或拒绝");
        check(event(Hk3FormalArchive.evaluate(id->true,contacts,personal,reviews,readings,actor),"E-OT-001").state()==State.MISSING,"仅团队答复未授本人完整经历");
        check(!contacts.advancePersonal(team,actor,UUID.randomUUID(),0,true),"错令牌拒绝");
        check(!contacts.advancePersonal(team,actor,contacts.event(team),0,false),"非成员拒绝");
        check(!contacts.advancePersonal(team,actor,contacts.event(team),1,true),"跳步拒绝");
        for(int step=0;step<3;step++)check(contacts.advancePersonal(team,actor,contacts.event(team),step,true),"合法补谈逐步推进");
        check(event(Hk3FormalArchive.evaluate(id->true,contacts,personal,reviews,readings,actor),"E-OT-001").state()==State.MISSING,"旧三步没有附件不完成");
        contacts=Hk3TeamContactData.load(contacts.save(new CompoundTag()));
        check(contacts.advancePersonal(team,actor,contacts.event(team),3,true),"重载后补齐附件");
        var before=contacts.save(new CompoundTag());var readBefore=readings.save(new CompoundTag());
        var result=Hk3FormalArchive.evaluate(id->true,contacts,personal,reviews,readings,actor);
        check(result.count(State.COMPLETE)==102,"本人首信与同义旧事件完成，其他事件不按组织豁免");
        var fact=Hk3LegacyArchiveMigration.evaluate("E-OT-001",id->true,contacts,personal,reviews,readings,actor);
        check(fact.source().getUUID("Actor").equals(actor)&&fact.source().getString("Event").equals("E-OT-001"),"来源绑定准确本人和事件");
        check(Hk3LegacyArchiveMigration.evaluate("E-OT-001",id->true,contacts,personal,reviews,readings,other).state()==State.MISSING,"他人不能继承本人经历");
        check(Hk3LegacyArchiveMigration.evaluate("E-OT-001",id->true,Hk3TeamContactData.load(before),personal,reviews,readings,actor).state()==State.COMPLETE,"跨队历史按本人原账本恢复");
        fact.source().putString("Event","E-WL-001");
        Hk3FormalArchive.summary(result);
        check(contacts.save(new CompoundTag()).equals(before)&&readings.save(new CompoundTag()).equals(readBefore),"来源副本及目录查询不写原账本");
        check(result.fact().source().isEmpty(),"局部完成不能产生完整档案资格");
    }
}
