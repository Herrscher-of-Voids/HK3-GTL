package com.sirin.hk3gtl.test.communication;

import com.sirin.hk3gtl.common.communication.*;
import com.sirin.hk3gtl.common.phone.Hk3PhoneData;
import com.sirin.hk3gtl.common.research.Hk3ResearchData;
import com.sirin.hk3gtl.common.narrative.Hk3FormalArchive;
import com.sirin.hk3gtl.common.narrative.Hk3LegacyArchiveMigration;
import com.sirin.hk3gtl.common.finale.Hk3FinaleRequirements.State;
import net.minecraft.nbt.*;
import java.util.*;

/**
 * 【变更记录 #1】2026-10-01 00:59:10（修订124）
 * 删除：无；新增：五方32种同意/拒绝组合的完整通信生命周期集成测试。
 * 修改：使用生产投递、真实账本序列化、授权、研究来源和本人通信目录，不另写假业务算法。
 * 用途：覆盖离线入箱、重启、成员隔离及不重发奖励。工况由隔离夹具提供，不代表机器或GUI实机验收。
 */
/** 【变更记录 #2】2026-10-01 01:01:52（修订124）：删除无；新增嵌套容器损坏原样保留检查；修改拒绝覆盖场景；用途：整系统恢复不静默删除历史。 */
/** 【变更记录 #3】2026-10-01 20:34:36（修订148）：删除无；新增32种路线的正式档案集成断言；修改复用已生成的真实回执；用途：验证互斥路线与玩家隔离。 */
/**
 * 【变更记录 #4】2026-11-04 06:40:01（第4次备注 · 内测5修订196）
 * 删除：把整份正式档案完成数固定为六组通信的旧聚合断言。
 * 新增：32种路线逐项核对六通信及六同源事件的准确ID、来源类型、来源主题与完成集合。
 * 修改：分组仍严格六组通信、全卷只完成对应十二项，其他研究/审查及未亲历成员不完成。
 * 用途：适配获准的正式事件同源迁移，保留并加强通信资格隔离，不修改任何生产链路。
 */
public final class CommunicationSystemTest {
    private static int checks;
    private static void check(boolean value,String text){if(!value)throw new AssertionError(text);checks++;}
    private static CompoundTag batch(){
        var r=new CompoundTag();r.putUUID("Batch",UUID.randomUUID());r.putString("Recipe","hk3gtl:isolated_test_batch");
        r.putString("Facility","private/test-only");r.putLong("Tick",10);
        for(String side:List.of("Inputs","Outputs")){
            var section=new CompoundTag();var lines=new ListTag();var line=new CompoundTag();var items=new ListTag();var item=new CompoundTag();
            item.putString("id","minecraft:stone");item.putByte("Count",(byte)4);item.putLong("ActualCount",4);
            items.add(item);line.put("Alternatives",items);line.putFloat("Chance",1);lines.add(line);section.put("Items",lines);r.put(side,section);
        }
        return r;
    }
    private static CompoundTag envelope(String topic,Hk3CommunicationEvidence source,UUID team){
        var out=new CompoundTag();
        switch(topic){
            case "public","anti_entropy"->out.put("稳定化",Hk3CommunicationEvidence.publicCopy(source.source(team,"stabilization")));
            case "schicksal"->{out.put("首次采样",Hk3CommunicationEvidence.publicCopy(source.source(team,"sampling")));out.put("光谱分析",Hk3CommunicationEvidence.publicCopy(source.source(team,"spectrum")));}
            case "world_serpent"->{out.put("魂钢成型",Hk3CommunicationEvidence.publicCopy(batch()));out.put("重构退火",Hk3CommunicationEvidence.publicCopy(batch()));}
        }
        return out;
    }
    private static CompoundTag disk(CompoundTag data)throws Exception{
        var bytes=new java.io.ByteArrayOutputStream();NbtIo.writeCompressed(data,bytes);return NbtIo.readCompressed(new java.io.ByteArrayInputStream(bytes.toByteArray()));
    }
    private static void scenario(int choices)throws Exception{
        UUID owner=UUID.randomUUID(),member=UUID.randomUUID(),late=UUID.randomUUID(),team=UUID.randomUUID();
        var members=List.of(owner,member);var notices=new ArrayList<Hk3CommunicationDelivery.Notice>();
        var contacts=new Hk3TeamContactData();var diplomacy=new Hk3DiplomacyData();var inbox=new Hk3PhoneData();
        var personal=new Hk3PersonalCommunicationData();var source=new Hk3CommunicationEvidence();var research=new Hk3ResearchData();
        check(!Hk3CommunicationCompletion.status(contacts,personal,owner).complete(),"新档不完整");
        Hk3CommunicationDelivery.first(contacts,inbox,team,members,0,notices::add);check(notices.isEmpty(),"未触发不投信");
        check(contacts.discover(team,owner,1),"首信实际触发建档");
        Hk3CommunicationDelivery.first(contacts,inbox,team,members,1,notices::add);check(notices.size()==2&&inbox.count(member)==1,"离线接收人照常入箱");
        Hk3CommunicationDelivery.first(contacts,inbox,team,members,2,notices::add);check(notices.size()==2,"重复扫描不再弹窗");
        inbox.read(owner,"contact_"+team);check(inbox.entry(owner,"contact_"+team).pending(),"已读不清待处理");
        contacts.read(team,member);check(!contacts.canDecide(team,member,owner,true),"成员不自动获权");
        check(contacts.delegate(team,owner,owner,member,true,true),"显式授权");
        check(contacts.decide(team,member,owner,true,contacts.event(team),true,3),"授权代表答复");
        check(research.recordFormalCommunication(team,contacts.receipt(team)),"真实回信接研究来源");
        check(!research.completed(team,"RN-HCCO")&&!research.hasExperiment(team,"RN-HCCO"),"来源不赠课题或实验");
        Hk3CommunicationDelivery.first(contacts,inbox,team,members,4,notices::add);check(!inbox.entry(owner,"contact_"+team).pending()&&inbox.count(member)==2,"后续来信与待处理一致");
        for(int step=0;step<Hk3TeamContactData.PERSONAL_STEPS;step++){
            if(step==3)check(!contacts.experienced(owner),"未补附件不算首信整段完成");
            check(contacts.advancePersonal(team,owner,contacts.event(team),step,true),"首信与附件逐篇确认");
        }
        check(contacts.experienced(owner)&&!contacts.experienced(member),"团队答复人不自动补全个人经历");
        for(String kind:List.of("sampling","spectrum","stabilization"))check(source.record(team,kind,batch()),"隔离生产来源夹具");
        check(!diplomacy.publish(team,owner,false,envelope("public",source,team),100),"未经授权不公开");
        check(diplomacy.publish(team,owner,true,envelope("public",source,team),100),"确认确定摘要");
        check(!diplomacy.published(team).toString().contains("private/test-only"),"设备隐私未进入公开资料");
        diplomacy.offer(team,"schicksal",false);
        int index=0;
        for(var topic:Hk3DiplomacyData.TOPICS){
            String id=topic.id();if(!id.equals("schicksal")){
                long delay=Hk3DiplomacyData.contactDelay(id);check(!diplomacy.due(team,id,100+delay-1)&&diplomacy.due(team,id,100+delay),"逐方按游戏时间开放");diplomacy.offer(team,id,false);
            }
            Hk3CommunicationDelivery.diplomacy(diplomacy,inbox,team,members,10,notices::add);
            String notice="diplomacy_"+team+"_"+topic.first();check(inbox.entry(member,notice).pending(),"来信待答复");
            inbox.read(member,notice);check(!personal.experienced(member,id),"正文回看不等于个人补谈");
            boolean accept=(choices&(1<<index++))!=0;
            check(!diplomacy.apply(team,id,accept?"accept":"decline",member,false,1,new CompoundTag()),"只读预览不能提交");
            check(diplomacy.apply(team,id,accept?"accept":"decline",owner,true,1,new CompoundTag()),"本主题实际选择");
            if(accept&&!topic.submit().isEmpty()){
                check(diplomacy.personalPath(team,id).isEmpty(),"交付前不能补成整段");
                check(diplomacy.apply(team,id,"submit",owner,true,2,envelope(id,source,team)),"确定摘要一次结算");
            }
            Hk3CommunicationDelivery.diplomacy(diplomacy,inbox,team,members,11,notices::add);check(!inbox.entry(member,notice).pending()&&inbox.entry(member,notice).read(),"处理后保留本人已读");
            var path=diplomacy.personalPath(team,id);int version=diplomacy.version(team,id);
            check(!path.isEmpty()&&personal.begin(owner,team,id,version,path,true),"选定路线可补谈");
            UUID attempt=personal.snapshot(owner,team,id).getUUID("Attempt");
            for(int step=0;step<path.size();step++){
                check(personal.advance(owner,team,id,attempt,version,step,path,true,1000+step),"本人逐篇完成");
                personal=Hk3PersonalCommunicationData.load(disk(personal.save(new CompoundTag())));
            }
            check(personal.experienced(owner,id)&&!personal.experienced(member,id),"本人回执隔离");
            contacts=Hk3TeamContactData.load(disk(contacts.save(new CompoundTag())));
            diplomacy=Hk3DiplomacyData.load(disk(diplomacy.save(new CompoundTag())));
            inbox=Hk3PhoneData.load(disk(inbox.save(new CompoundTag())));
        }
        check(Hk3CommunicationCompletion.status(contacts,personal,owner).complete(),"整条通信六组可完结");
        var archive=com.sirin.hk3gtl.common.narrative.Hk3FormalArchive.evaluate(id->false,contacts,personal,new com.sirin.hk3gtl.common.review.Hk3ReviewLedger(),owner);
        var projected=Map.of("E-OT-001","first_contact","E-OT-002","schicksal","E-WS-001","world_serpent",
            "E-AE-001","anti_entropy","E-SF-001","st_freya","E-EL-001","elysian_realm");
        var expectedCommunications=Set.of("communication:first_contact","communication:schicksal","communication:world_serpent",
            "communication:anti_entropy","communication:st_freya","communication:elysian_realm");
        var communicationIds=new HashSet<String>();var completedIds=new HashSet<String>();
        for(var entry:archive.entries()) {
            if(entry.state()==State.COMPLETE)completedIds.add(entry.id());
            if(entry.group()==Hk3FormalArchive.Group.COMMUNICATION) {
                check(entry.state()==State.COMPLETE,"32种互斥路线逐条完成本人通信："+entry.id());
                communicationIds.add(entry.id());
            }
            if(entry.group()==Hk3FormalArchive.Group.RESEARCH||entry.group()==Hk3FormalArchive.Group.REVIEW)
                check(entry.state()!=State.COMPLETE,"通信不能授研究或本人审查："+entry.id());
        }
        check(communicationIds.equals(expectedCommunications),"正式通信必须恰好是原六组准确ID，不要求互斥另一分支");
        for(var projection:projected.entrySet()) {
            var rule=Hk3LegacyArchiveMigration.all().get(projection.getKey());
            check(rule!=null&&rule.kind()==Hk3LegacyArchiveMigration.SourceKind.COMMUNICATION
                &&rule.source().equals(projection.getValue()),"逐条事件只能投影指定本人通信来源："+projection.getKey());
            check(archive.entries().stream().anyMatch(e->e.id().equals(projection.getKey())
                &&e.group()==Hk3FormalArchive.Group.LEGACY&&e.state()==State.COMPLETE),"准确同源旧事件须完成："+projection.getKey());
        }
        var expectedCompleted=new HashSet<>(expectedCommunications);expectedCompleted.addAll(projected.keySet());
        check(completedIds.equals(expectedCompleted)&&archive.count(State.COMPLETE)==12,"整份档案只完成六通信及其六同源事件，不额外授资格");
        var memberArchive=com.sirin.hk3gtl.common.narrative.Hk3FormalArchive.evaluate(id->false,contacts,personal,new com.sirin.hk3gtl.common.review.Hk3ReviewLedger(),member);
        check(memberArchive.count(com.sirin.hk3gtl.common.finale.Hk3FinaleRequirements.State.COMPLETE)==0,"真实通信账本不向队员复制本人经历");
        check(Hk3CommunicationCompletion.status(contacts,personal,member).completed()==0,"队员没有被自动毕业");
        var originalState=diplomacy.save(new CompoundTag());int n=notices.size();
        Hk3CommunicationDelivery.first(contacts,inbox,team,members,20,notices::add);Hk3CommunicationDelivery.diplomacy(diplomacy,inbox,team,members,20,notices::add);
        check(notices.size()==n,"重启重新投影无重复提示");
        var withLate=List.of(owner,member,late);
        Hk3CommunicationDelivery.first(contacts,inbox,team,withLate,21,notices::add);Hk3CommunicationDelivery.diplomacy(diplomacy,inbox,team,withLate,21,notices::add);
        check(inbox.count(late)==inbox.count(owner)&&!Hk3CommunicationCompletion.status(contacts,personal,late).complete(),"后来成员有历史但无亲历");
        check(originalState.equals(diplomacy.save(new CompoundTag())),"入队与阅读不更改外交");
        int oldCount=inbox.count(member);inbox.resolveForeignDiplomacy(member,UUID.randomUUID());
        check(inbox.count(member)==oldCount&&inbox.count(member,"pending")==0,"换队历史保留且不再待处理");
        check(!research.recordFormalCommunication(team,contacts.receipt(team)),"完整流程重放不重复发研究来源");
    }
    public static void main(String[] args)throws Exception{
        for(int choices=0;choices<32;choices++)scenario(choices);
        UUID team=UUID.randomUUID(),actor=UUID.randomUUID();var contact=new Hk3TeamContactData();var inbox=new Hk3PhoneData();
        contact.discover(team,actor,0);Hk3CommunicationDelivery.first(contact,inbox,team,List.of(actor),0,n->{});
        inbox.resolveForeignDiplomacy(actor,UUID.randomUUID());check(!inbox.entry(actor,"contact_"+team).pending(),"未答复首信离队后只读");
        Hk3CommunicationDelivery.first(contact,inbox,team,List.of(actor),1,n->{});check(inbox.entry(actor,"contact_"+team).pending(),"回原队恢复真实待处理");
        var invalid=new CompoundTag();invalid.putString("Teams","broken");boolean rejected=false;
        try{Hk3DiplomacyData.load(invalid);}catch(IllegalArgumentException expected){rejected=true;}check(rejected,"损坏外交根不重置");
        rejected=false;try{Hk3CommunicationEvidence.load(invalid);}catch(IllegalArgumentException expected){rejected=true;}check(rejected,"损坏证据根不重置");
        rejected=false;try{Hk3TeamContactData.load(invalid);}catch(IllegalArgumentException expected){rejected=true;}check(rejected,"损坏首信根不重置");
        var nested=new CompoundTag();var rows=new CompoundTag();rows.putString(team.toString(),"future-format");nested.put("Teams",rows);
        var badDiplomacy=Hk3DiplomacyData.load(nested);var before=badDiplomacy.save(new CompoundTag());badDiplomacy.offer(team,"schicksal",false);
        check(badDiplomacy.save(new CompoundTag()).equals(before),"损坏团队不能被来信重置");
        var testSource=new Hk3CommunicationEvidence();testSource.record(team,"stabilization",batch());
        check(!badDiplomacy.publish(team,actor,true,envelope("public",testSource,team),0),"损坏团队不能被公开重置");
        var badSource=Hk3CommunicationEvidence.load(nested);check(!badSource.record(team,"sampling",batch()),"损坏团队批次拒绝新输出覆盖");
        var personal=new Hk3PersonalCommunicationData();var raw=personal.save(new CompoundTag());var player=new CompoundTag();player.putString("Completed","broken-history");raw.getCompound("Players").put(actor.toString(),player);
        personal=Hk3PersonalCommunicationData.load(raw);before=personal.save(new CompoundTag());
        check(!personal.begin(actor,team,"schicksal",1,List.of("N20","A06"),true),"损坏个人历史拒绝新补谈覆盖");
        check(before.equals(personal.save(new CompoundTag())),"损坏个人历史保留原样");
        System.out.println("CommunicationSystemTest: "+checks+" checks passed; 32 complete five-faction routes; production structures and live UI not simulated");
    }
}

// 【变更记录 · 修订161】2026-10-17 14:11:55：本轮仅将活动类名、资源与工业配方引用迁移为长期业务命名；历史备注保留，不代表旧逻辑已全部按现行设计重写。
