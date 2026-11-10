package com.sirin.hk3gtl.test.communication;

import com.sirin.hk3gtl.common.communication.*;
import net.minecraft.nbt.*;
import java.util.*;

/** 【变更记录 #1】2026-10-01 00:44:40（修订123）：删除无；新增五方分支、本人隔离、断点持久化、重谈版本与损坏记录测试；修改check挂接；用途：验证正式经历不由阅读/他人/重复确认生成，不代替游戏验收。 */
/** 【变更记录 #2】2026-10-01 00:46:24（修订123）：新增末步缺完成时间与提前完成时间的损坏测试；删除无，修改覆盖边界；用途：防止异常读取越界。 */
/** 【变更记录 #3】2026-10-01 00:47:26（修订123）：新增直接同意及最初拒绝路线验证；删除无；修改五方路径覆盖；用途：避免必须先拒绝/重谈才能完成。 */
/** 【变更记录 #4】2026-10-01 00:59:10（修订124）：删除无；新增/修改：首信测试覆盖新增批准附件步骤，保留既有隔离和存盘断言；用途：按五方交流系统整链收口，真实权限和本人经历不混用。 */
public final class PersonalCommunicationTest {
    private static int checks;
    private static void check(boolean value,String label){if(!value)throw new AssertionError(label);checks++;}
    private static CompoundTag evidence(String id){
        var proof=new CompoundTag();proof.putUUID("Batch",UUID.randomUUID());proof.putString("Recipe","hk3gtl:test");proof.putString("Facility","test");proof.putLong("Tick",12);
        for(String side:List.of("Inputs","Outputs")){
            var section=new CompoundTag();var lines=new ListTag();var line=new CompoundTag();var items=new ListTag();var item=new CompoundTag();
            item.putString("id","minecraft:stone");item.putByte("Count",(byte)1);item.putLong("ActualCount",1);items.add(item);line.put("Alternatives",items);line.putFloat("Chance",1);lines.add(line);section.put("Items",lines);proof.put(side,section);
        }
        var envelope=new CompoundTag();for(String key:switch(id){case "schicksal"->List.of("首次采样","光谱分析");case "anti_entropy"->List.of("稳定化");default->List.of("魂钢成型","重构退火");})envelope.put(key,Hk3CommunicationEvidence.publicCopy(proof));return envelope;
    }
    public static void main(String[] args){
        UUID team=UUID.randomUUID(),actor=UUID.randomUUID(),other=UUID.randomUUID();
        var diplomacy=new Hk3DiplomacyData();var data=new Hk3PersonalCommunicationData();
        for(var topic:Hk3DiplomacyData.TOPICS){
            String id=topic.id();check(diplomacy.personalPath(team,id).isEmpty(),"未接触不得补谈");diplomacy.offer(team,id,false);
            check(diplomacy.personalPath(team,id).isEmpty(),"未答复不得补成完整经历");
            check(diplomacy.apply(team,id,"decline",actor,true,1,new CompoundTag()),"确定拒绝路线");
            var route=diplomacy.personalPath(team,id);int version=diplomacy.version(team,id);var before=diplomacy.save(new CompoundTag());
            check(route.equals(List.of("N20",topic.first(),topic.no(),topic.refused())),"拒绝仅本路线");
            check(!data.begin(actor,team,id,version,route,false),"非成员不得开始");check(!data.experienced(actor,id),"未开始无经历");
            check(data.begin(actor,team,id,version,route,true),"成员开始");
            var snapshot=data.snapshot(actor,team,id);var attempt=snapshot.getUUID("Attempt");snapshot.putInt("Step",99);
            check(data.snapshot(actor,team,id).getInt("Step")==0,"读取副本隔离");
            check(data.begin(actor,team,id,version,route,true)&&data.snapshot(actor,team,id).getUUID("Attempt").equals(attempt),"反复预览保持同次");
            check(!data.advance(other,team,id,attempt,version,0,route,true,1),"他人不能使用快照");
            check(!data.advance(actor,UUID.randomUUID(),id,attempt,version,0,route,true,1),"换队不能混进度");
            check(!data.advance(actor,team,id,attempt,version,0,route,false,1),"离队不能确认");
            check(!data.advance(actor,team,id,attempt,version+1,0,route,true,1),"旧版本不能确认");
            check(!data.advance(actor,team,id,UUID.randomUUID(),version,0,route,true,1),"其他会面拒绝");
            for(int step=0;step<route.size();step++){
                check(!data.experienced(actor,id),"最后一步以前无完整经历");
                check(!data.advance(actor,team,id,attempt,version,step+1,route,true,step),"不能跳步");
                check(data.advance(actor,team,id,attempt,version,step,route,true,step),"本步确认");
                check(!data.advance(actor,team,id,attempt,version,step,route,true,step),"重复包不推进");
                data=Hk3PersonalCommunicationData.load(data.save(new CompoundTag()));
                check(data.snapshot(actor,team,id).getInt("Step")==step+1,"每步断线恢复");
            }
            check(data.experienced(actor,id)&&!data.experienced(other,id),"本人完成不传给队员");
            check(data.completedCurrent(actor,team,id,version,route),"当前路线完成");check(before.equals(diplomacy.save(new CompoundTag())),"补谈不改团队账本");
            check(diplomacy.apply(team,id,"retry",actor,true,version,new CompoundTag()),"团队重谈");
            if(id.equals("schicksal"))check(diplomacy.apply(team,id,"accept",actor,true,diplomacy.version(team,id),new CompoundTag()),"天命重谈重新同意");
            if(!topic.submit().isEmpty()){
                check(diplomacy.personalPath(team,id).isEmpty(),"待交付不提前补成");
                check(diplomacy.apply(team,id,"submit",actor,true,diplomacy.version(team,id),evidence(id)),"真实附件结算");
            }
            var newRoute=diplomacy.personalPath(team,id);check(!newRoute.isEmpty()&&!newRoute.contains(topic.no()),"同意路线不强制互斥拒绝");
            check(!data.completedCurrent(actor,team,id,diplomacy.version(team,id),newRoute)&&data.experienced(actor,id),"新路线待补且本人历史保留");
            check(data.begin(actor,team,id,diplomacy.version(team,id),newRoute,true),"新路线快照");
            check(!data.snapshot(actor,team,id).getUUID("Attempt").equals(attempt)&&data.snapshot(actor,team,id).getInt("Step")==0,"旧路线步骤不混入");
            check(!data.advance(actor,team,id,attempt,version,0,route,true,88),"旧快照令牌拒绝");
        }
        var direct=new Hk3DiplomacyData();
        for(var t:Hk3DiplomacyData.TOPICS){
            direct.offer(team,t.id(),false);direct.apply(team,t.id(),"accept",actor,true,1,new CompoundTag());
            if(!t.submit().isEmpty())direct.apply(team,t.id(),"submit",actor,true,2,evidence(t.id()));
            var path=direct.personalPath(team,t.id());
            check(!path.isEmpty()&&path.contains(t.yes())&&!path.contains(t.no())&&!path.contains(t.retry()),"直接同意不强制拒绝或重谈");
        }
        var initiallyRefused=new Hk3DiplomacyData();initiallyRefused.offer(team,"schicksal",true);
        check(initiallyRefused.personalPath(team,"schicksal").equals(List.of("N20","A06")),"最初拒绝也可补谈，不强制合作");
        var first=new Hk3TeamContactData();first.discover(team,actor,1);first.read(team,actor);first.decide(team,actor,actor,true,first.event(team),true,2);
        check(!first.experienced(actor),"决定与阅读仍非个人补谈");for(int step=0;step<Hk3TeamContactData.PERSONAL_STEPS;step++)first.advancePersonal(team,actor,first.event(team),step,true);
        check(first.experienced(actor)&&!first.experienced(other),"首信历史本人隔离");
        var broken=data.snapshot(actor,team,"schicksal");broken.putInt("Step",Hk3PersonalCommunicationData.documents(broken).size());
        check(!Hk3PersonalCommunicationData.valid(broken),"末步缺完成时间拒绝");
        broken=data.snapshot(actor,team,"schicksal");broken.putLong("CompletedAt",88);check(!Hk3PersonalCommunicationData.valid(broken),"未完成却有完成时间拒绝");
        var saved=data.save(new CompoundTag());var active=saved.getCompound("Players").getCompound(actor.toString()).getCompound("Active");
        active.getCompound(team+"/schicksal").putInt("Step",999);var bad=Hk3PersonalCommunicationData.load(saved);
        var before=bad.save(new CompoundTag());var route=diplomacy.personalPath(team,"schicksal");
        check(!bad.begin(actor,team,"schicksal",diplomacy.version(team,"schicksal"),route,true),"损坏步数不重置");
        check(before.equals(bad.save(new CompoundTag())),"损坏原始数据保留");
        saved=data.save(new CompoundTag());saved.getCompound("Players").getCompound(actor.toString()).getCompound("Completed").getCompound("schicksal").putUUID("Actor",other);
        check(!Hk3PersonalCommunicationData.load(saved).experienced(actor,"schicksal"),"完成回执人不符拒绝");
        saved=data.save(new CompoundTag());saved.putInt("Version",99);boolean failed=false;try{Hk3PersonalCommunicationData.load(saved);}catch(IllegalArgumentException expected){failed=true;}check(failed,"未知账本版本拒绝载入");
        System.out.println("PersonalCommunicationTest: "+checks+" checks passed");
    }
}
