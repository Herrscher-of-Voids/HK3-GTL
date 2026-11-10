package com.sirin.hk3gtl.test.communication;
import com.sirin.hk3gtl.common.communication.*;
import com.sirin.hk3gtl.common.narrative.Hk3ApprovedProse;
import net.minecraft.nbt.*;
import java.util.*;
/** 【变更记录 #1】2026-10-01 00:17:25（修订122）：删除无；新增五方覆盖、隐私白名单、并行数量、版本竞争、重谈、200团队持久化及署名测试；修改无；用途：验证通信流程，不冒充真实机器/多人界面验收。 */
public final class DiplomacyTest {
    private static int checks;
    private static void check(boolean ok,String label){if(!ok)throw new AssertionError(label);checks++;}
    private static CompoundTag raw(){var r=new CompoundTag();r.putUUID("Batch",UUID.randomUUID());r.putString("Recipe","hk3gtl:test");r.putString("Facility","private:dimension@secret-position");r.putUUID("Actor",UUID.randomUUID());r.putLong("Tick",17);
        for(String side:List.of("Inputs","Outputs")){var c=new CompoundTag();var list=new ListTag();var line=new CompoundTag();var alternatives=new ListTag();var item=new CompoundTag();item.putString("id","minecraft:stone");item.putByte("Count",(byte)0);item.putLong("ActualCount",4096);var secret=new CompoundTag();secret.putString("PrivateNote","PRIVATE");item.put("tag",secret);alternatives.add(item);line.put("Alternatives",alternatives);line.putFloat("Chance",1);list.add(line);c.put("Items",list);r.put(side,c);}return r;}
    private static CompoundTag envelope(String topic){var e=new CompoundTag();for(String key:switch(topic){case "public","anti_entropy"->List.of("稳定化");case "schicksal"->List.of("首次采样","光谱分析");default->List.of("魂钢成型","重构退火");})e.put(key,Hk3CommunicationEvidence.publicCopy(raw()));return e;}
    public static void main(String[] args){
        check(Hk3DiplomacyData.TOPICS.size()==5,"五个势力");check(Hk3FactionLetters.all().size()==12,"两方十二篇新增正文");
        for(var t:Hk3DiplomacyData.TOPICS)for(String id:List.of(t.first(),t.yes(),t.no(),t.agreed(),t.refused(),t.feedback(),t.retry(),t.resumed()))check(Hk3ApprovedProse.get("communication."+id)!=null||!Hk3FactionLetters.body(id).isBlank(),"每个流程正文存在："+id);
        for(var e:Hk3FactionLetters.all())if(e.speaker().equals("爱莉希雅"))for(String line:e.lines())check(line.endsWith("～♪"),"爱莉希雅句尾");
        check(Hk3ApprovedProse.get("communication.A01").speaker().equals("奥托"),"天命奥托署名");check(Hk3ApprovedProse.get("communication.A08").speaker().equals("爱因斯坦博士、特斯拉博士"),"逆熵两博士署名");check(Hk3ApprovedProse.get("communication.A09").speaker().equals("灰蛇"),"世界蛇灰蛇署名");check(Hk3FactionLetters.speaker("SF01").equals("德丽莎学园长"),"学园长署名");check(Hk3FactionLetters.speaker("ER01").equals("爱莉希雅"),"乐土爱莉希雅署名");
        var raw=raw();var clean=Hk3CommunicationEvidence.publicCopy(raw);check(Hk3CommunicationEvidence.validPublic(clean),"公开白名单有效");check(!clean.toString().contains("PRIVATE")&&!clean.contains("Actor")&&!clean.contains("Facility"),"隐私字段全部移除");
        check(Hk3CommunicationEvidence.describe(clean).contains("4096"),"并行数不被字节截断");var leak=clean.copy();leak.putString("Facility","secret");check(!Hk3CommunicationEvidence.validPublic(leak),"夹带字段拒绝");
        UUID team=UUID.randomUUID(),actor=UUID.randomUUID();var evidence=new Hk3CommunicationEvidence();check(evidence.record(team,"stabilization",raw),"生产首次记录");check(!evidence.record(team,"stabilization",raw()),"证据去重有界");
        evidence.source(team,"stabilization").putString("Facility","tampered");check(evidence.source(team,"stabilization").getString("Facility").contains("secret-position"),"返回副本不可写穿");check(evidence.source(UUID.randomUUID(),"stabilization").isEmpty(),"换队无证据");
        evidence=Hk3CommunicationEvidence.load(evidence.save(new CompoundTag()));check(evidence.source(team,"stabilization").equals(raw),"真实快照持久化");
        var d=new Hk3DiplomacyData();check(!d.publish(team,actor,false,envelope("public"),100),"普通成员不得公开");check(!d.publish(team,actor,true,envelope("schicksal"),100),"错误主题拒绝公开");
        check(d.publish(team,actor,true,envelope("public"),100),"真实公开");check(!d.publish(team,actor,true,envelope("public"),101),"公开幂等");check(d.documents(team).contains("N19"),"公开留下正文");
        for(var t:Hk3DiplomacyData.TOPICS){
            d.offer(team,t.id(),false);int v=d.version(team,t.id());check(!d.apply(team,t.id(),"accept",actor,false,v,new CompoundTag()),"只读无法提交");
            check(d.apply(team,t.id(),"decline",actor,true,v,new CompoundTag()),"真实拒绝");check(!d.apply(team,t.id(),"accept",actor,true,v,new CompoundTag()),"同版本相反答复拒绝");
            check(d.apply(team,t.id(),"retry",actor,true,d.version(team,t.id()),new CompoundTag()),"再次联系");check(d.documents(team).contains(t.no()),"重谈保留拒绝历史");
            if(t.id().equals("schicksal"))check(d.apply(team,t.id(),"accept",actor,true,d.version(team,t.id()),new CompoundTag()),"天命重谈范围再次确认");
            if(!t.submit().isEmpty()){
                check(!d.apply(team,t.id(),"submit",actor,true,d.version(team,t.id()),new CompoundTag()),"空生产记录拒绝");var e=envelope(t.id());check(d.apply(team,t.id(),"submit",actor,true,d.version(team,t.id()),e),"真实提交");check(d.submitted(team,t.id()).equals(e),"仅保存预览的资料");
            }
            check(d.state(team,t.id()).equals("COMPLETED"),"限定交流完成");check(!d.apply(team,t.id(),"retry",actor,true,d.version(team,t.id()),new CompoundTag()),"完成不循环刷重谈");
        }
        d=Hk3DiplomacyData.load(d.save(new CompoundTag()));for(var t:Hk3DiplomacyData.TOPICS)check(d.state(team,t.id()).equals("COMPLETED"),"重启保持主题结果");
        var ids=new ArrayList<UUID>();for(int i=0;i<200;i++){UUID id=UUID.randomUUID();ids.add(id);d.offer(id,"st_freya",false);check(d.apply(id,"st_freya",i%2==0?"accept":"decline",id,true,1,new CompoundTag()),"独立团队答复");}
        d=Hk3DiplomacyData.load(d.save(new CompoundTag()));for(int i=0;i<200;i++)check(d.state(ids.get(i),"st_freya").equals(i%2==0?"COMPLETED":"DECLINED"),"200队持久化隔离");
        var timed=new Hk3DiplomacyData();UUID timeTeam=UUID.randomUUID();check(!timed.due(timeTeam,"anti_entropy",9999),"未公开不投递其他首信");timed.publish(timeTeam,actor,true,envelope("public"),100);
        for(var id:List.of("anti_entropy","world_serpent","elysian_realm","st_freya")){long delay=Hk3DiplomacyData.contactDelay(id);check(!timed.due(timeTeam,id,100+delay-1),"到期前不投递"+id);check(timed.due(timeTeam,id,100+delay),"按时可投递"+id);}
        timed.offer(timeTeam,"anti_entropy",false);check(timed.pendingDocument(timeTeam,"A08"),"邀请为待处理");timed.apply(timeTeam,"anti_entropy","accept",actor,true,1,new CompoundTag());check(!timed.pendingDocument(timeTeam,"A08")&&timed.pendingDocument(timeTeam,"N09"),"同意后转待提交");
        timed.apply(timeTeam,"anti_entropy","submit",actor,true,2,envelope("anti_entropy"));check(!timed.pendingDocument(timeTeam,"N09"),"结算清待处理");
        var damaged=timed.save(new CompoundTag());var row=damaged.getCompound("Teams").getCompound(timeTeam.toString());row.putString("Published","future");row.putString("world_serpent","future");var blocked=Hk3DiplomacyData.load(damaged);
        check(!blocked.due(timeTeam,"st_freya",9999)&&!blocked.publish(timeTeam,actor,true,envelope("public"),200),"损坏公开不可冒充来源或重置");blocked.offer(timeTeam,"world_serpent",false);check(blocked.save(new CompoundTag()).getCompound("Teams").getCompound(timeTeam.toString()).getString("world_serpent").equals("future"),"未知主题原样保留");
        var phone=new com.sirin.hk3gtl.common.phone.Hk3PhoneData();phone.add(actor,"diplomacy_test","来信","正文",0,"diplomacy",timeTeam+"/A08",true);phone.read(actor,"diplomacy_test");check(phone.entry(actor,"diplomacy_test").pending(),"阅读不等于处理");phone.pending(actor,"diplomacy_test",false);phone.pending(actor,"diplomacy_test",true);check(phone.entry(actor,"diplomacy_test").read()&&phone.count(actor)==1,"重谈不伪造未读或新增消息");phone.resolveForeignDiplomacy(actor,UUID.randomUUID());check(!phone.entry(actor,"diplomacy_test").pending(),"换队旧记录只读");
        System.out.println("DiplomacyTest: "+checks+" checks passed");
    }
}
