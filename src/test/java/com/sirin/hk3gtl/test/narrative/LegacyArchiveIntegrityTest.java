package com.sirin.hk3gtl.test.narrative;

import com.sirin.hk3gtl.common.narrative.*;
import com.sirin.hk3gtl.common.phone.*;
import com.sirin.hk3gtl.common.research.Hk3ResearchCatalog;
import net.minecraft.nbt.*;
import java.util.*;
import java.util.function.Consumer;

/** 【变更记录 #1】2026-11-04 06:10:05（第1次备注 · 内测5修订196）：删除无；新增生产正式回执损坏、来源隔离、历史保留与正文同源反例；修改无；用途：校验真实存取代码，测试构造的来源不代表游戏工业首通。 */
public final class LegacyArchiveIntegrityTest {
    private static void check(boolean value,String reason) {if(!value)throw new AssertionError(reason);}
    private static void ancestors(String id,Set<String> result) {
        if(result.add(id))for(String parent:Hk3ResearchCatalog.bundled().get(id).prerequisites())ancestors(parent,result);
    }
    private static CompoundTag source(UUID actor,UUID scope,Hk3LegacyArchiveMigration.Rule rule) {
        var n=new CompoundTag();n.putInt("MigrationVersion",2);n.putUUID("Actor",actor);n.putUUID("Scope",scope);
        n.putString("Event",rule.eventId());n.putString("Kind",rule.kind().name());n.putString("Source",rule.source());n.putString("RuleHash",rule.fingerprint());
        var proof=new CompoundTag();proof.putUUID("Scope",scope);proof.putString("Research",rule.source());
        var completed=new TreeSet<String>();ancestors(rule.source(),completed);var list=new ListTag();
        completed.forEach(id->list.add(StringTag.valueOf(id)));proof.put("Completed",list);n.put("ResearchProof",proof);return n;
    }
    private static CompoundTag row(CompoundTag root,UUID actor,String event) {return root.getCompound("Players").getCompound(actor.toString()).getCompound(event);}
    private static void corrupt(CompoundTag saved,UUID actor,String event,Consumer<CompoundTag> change) {
        var changed=saved.copy();change.accept(row(changed,actor,event));var original=changed.copy();
        boolean rejected=false;try{Hk3LegacyArchiveData.load(changed);}catch(IllegalArgumentException expected){rejected=true;}
        check(rejected,"损坏正式回执必须拒绝加载");check(changed.equals(original),"加载失败不得清空或重写原始数据");
        check(Hk3LegacyArchiveData.load(saved).experienced(actor,Hk3LegacyArchiveMigration.all().get(event)),"损坏副本不得破坏原始正确历史");
    }
    public static void run() {
        var rules=Hk3LegacyArchiveMigration.all().values().stream().filter(r->r.kind()==Hk3LegacyArchiveMigration.SourceKind.RESEARCH).toList();
        check(rules.size()>1,"需要独立事件做账本隔离反例");var first=rules.get(0);var second=rules.get(1);
        UUID actor=UUID.randomUUID(),scope=UUID.randomUUID();var data=new Hk3LegacyArchiveData();
        for(var rule:List.of(first,second))check(data.record(actor,scope,rule,UUID.randomUUID(),10,1,source(actor,scope,rule)),"单片全文可形成合法服务端回执");
        var saved=data.save(new CompoundTag());check(Hk3LegacyArchiveData.load(saved).experienced(actor,first),"完整来源及全读长度加载成功");
        check(!data.experienced(UUID.randomUUID(),first),"其他成员不能继承本人回执");
        var returned=data.receipt(actor,first);returned.putString("Source","RN-FAKE");check(data.experienced(actor,first),"返回副本不能污染权威账本");
        var invalid=source(actor,scope,first);invalid.getCompound("ResearchProof").putUUID("Scope",UUID.randomUUID());
        check(!new Hk3LegacyArchiveData().record(actor,scope,first,UUID.randomUUID(),10,1,invalid),"跨队来源快照不记录");
        for(String key:List.of("Actor","Scope","ReadToken","Event","Kind","Source","RuleHash","CompletedAt","Pieces","BodyLength","ReadLength","ResearchProof"))
            corrupt(saved,actor,first.eventId(),n->n.remove(key));
        corrupt(saved,actor,first.eventId(),n->n.putUUID("Actor",UUID.randomUUID()));
        corrupt(saved,actor,first.eventId(),n->n.putString("Event",second.eventId()));
        corrupt(saved,actor,first.eventId(),n->n.putString("Source","RN-UNKNOWN"));
        corrupt(saved,actor,first.eventId(),n->n.putInt("ReadLength",n.getInt("BodyLength")-1));
        corrupt(saved,actor,first.eventId(),n->n.putInt("Pieces",n.getInt("ReadLength")+1));
        corrupt(saved,actor,first.eventId(),n->n.getCompound("ResearchProof").putUUID("Scope",UUID.randomUUID()));
        corrupt(saved,actor,first.eventId(),n->n.getCompound("ResearchProof").putString("Research",first.source()+"-WRONG"));
        corrupt(saved,actor,first.eventId(),n->n.getCompound("ResearchProof").put("Completed",new ListTag()));
        corrupt(saved,actor,first.eventId(),n->{var list=n.getCompound("ResearchProof").getList("Completed",Tag.TAG_STRING);list.add(list.get(0).copy());});
        var old=saved.copy();row(old,actor,first.eventId()).putString("RuleHash","0".repeat(64));
        var restored=Hk3LegacyArchiveData.load(old);check(!restored.experienced(actor,first),"旧正文指纹不能授当前资格");
        check(restored.experienced(actor,second),"旧指纹不阻断其他正确事件");check(restored.save(new CompoundTag()).equals(old),"历史指纹和来源原样保留");
        for(int version:List.of(0,1,3)){var wrong=saved.copy();wrong.putInt("Version",version);boolean rejected=false;try{Hk3LegacyArchiveData.load(wrong);}catch(IllegalArgumentException expected){rejected=true;}check(rejected,"旧版和未来账本不升级为完成");}
        for(var rule:Hk3LegacyArchiveMigration.all().values())for(var node:Hk3NarrativeNodes.byEventIdAll(rule.eventId())) {
            check(Hk3CollectionRecords.body(node,k->"旧文"+k).equals(rule.body()),"所有别名使用同一新版正文");
            check(Hk3CollectionRecords.title(node,k->"旧标题").equals(rule.title()),"收藏标题与正文对应同一迁移");
            var entry=new Hk3PhoneData.Entry("narrative_"+node.id(),"原历史标题","原历史正文",1,false,"narrative",node.id(),true);
            var projected=Hk3PhonePresentation.current(entry,k->"旧文"+k);
            check(projected.title().equals("旧版历史｜原历史标题")&&projected.body().equals("原历史正文")&&!projected.pending(),"旧通知原文保留并明确历史身份");
            check(entry.body().equals("原历史正文")&&entry.pending(),"历史投影不改原信箱对象");
        }
        System.out.println("LegacyArchiveIntegrityTest passed: corruption, source provenance, history isolation and current prose");
    }
}
