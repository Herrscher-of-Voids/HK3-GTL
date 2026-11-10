package com.sirin.hk3gtl.test.communication;

/** 【变更记录 #3】2026-10-31 00:46:39（第3次备注 · 修订187）：删除无；新增生产阅读凭据回归入口；修改团队测试先运行阅读检查；用途：授权、持久化与全读门禁一并校验。 */
import com.sirin.hk3gtl.common.communication.*;
import com.sirin.hk3gtl.common.research.*;
import net.minecraft.nbt.*;
import java.util.*;

/** 【变更记录 #1】2026-10-01 00:00:53（修订121）：删除无；新增授权撤销、并发竞争、迁队、预览令牌、逐步补谈、200队持久化及损坏状态测试；修改无；用途：验证业务隔离，不冒充多人游戏验收。 */
/** 【变更记录 #2】2026-10-01 00:59:10（修订124）：删除无；新增/修改：首信测试覆盖新增批准附件步骤，保留既有隔离和存盘断言；用途：按五方交流系统整链收口，真实权限和本人经历不混用。 */
public final class TeamContactTest {
    private static int checks;
    private static void check(boolean value,String reason){if(!value)throw new AssertionError(reason);checks++;}
    public static void main(String[] args){
        CommunicationReadingTest.main(args);
        UUID t=UUID.randomUUID(),owner=UUID.randomUUID(),a=UUID.randomUUID(),b=UUID.randomUUID(),foreign=UUID.randomUUID();
        var d=new Hk3TeamContactData();check(!d.available(t),"无来源不能开始");check(d.discover(t,owner,0),"发现唯一首信");UUID event=d.event(t);
        check(!d.discover(t,owner,1)&&event.equals(d.event(t)),"发现幂等");
        check(!d.decide(t,owner,owner,true,event,true,1),"未阅读拒绝确认");d.read(t,owner);d.read(t,a);d.read(t,b);
        check(!d.decide(t,a,owner,true,event,true,2),"普通成员不得决定");check(!d.delegate(t,a,owner,b,true,true),"普通成员不得授权");
        check(!d.delegate(t,owner,owner,foreign,false,true),"不能授权外队成员");check(d.delegate(t,owner,owner,a,true,true),"队长明确授权");
        check(d.canDecide(t,a,owner,true),"授权生效");check(!d.canDecide(t,a,owner,false),"离队即失效");
        check(d.delegate(t,owner,owner,a,true,false),"撤销成功");check(!d.decide(t,a,owner,true,event,true,3),"旧界面撤权后拒绝");
        d.delegate(t,owner,owner,a,true,true);d.revokeDeparted(a);check(!d.canDecide(t,a,owner,true),"离队回队不恢复旧授权");
        d.delegate(t,owner,owner,a,true,true);d.reconcile(t,b,Set.of(owner,a,b));check(!d.canDecide(t,a,b,true),"队长变更旧授权清除");
        check(d.canDecide(t,b,b,true)&&!d.canDecide(t,owner,b,true),"新旧队长权限正确");
        check(!d.decide(t,b,b,true,UUID.randomUUID(),true,4),"错误事件拒绝");
        check(d.decide(t,b,b,true,event,false,4),"真实拒绝生效");check(!d.decide(t,b,b,true,event,true,4),"并发相反回复拒绝");
        check(d.state(t).equals("DECLINED")&&d.personalStep(t,b)==0,"决定与个人完整经历分账");
        check(d.receipt(t).getCompound("Outputs").getString("Reply").equals("declined"),"拒绝同样有真实来源");
        check(!d.available(UUID.randomUUID()),"新队不能继承旧决定");
        d.read(t,a);check(d.personalStep(t,a)==0,"仅回看不完成个人经历");
        check(!d.advancePersonal(t,a,event,1,true),"不能跳步");check(!d.advancePersonal(t,a,event,0,false),"外队不能补谈");
        for(int step=0;step<Hk3TeamContactData.PERSONAL_STEPS;step++){
            check(d.advancePersonal(t,a,event,step,true),"实际逐步确认"+step);check(!d.advancePersonal(t,a,event,step,true),"重发步骤幂等"+step);
            d=Hk3TeamContactData.load(d.save(new CompoundTag()));check(d.personalStep(t,a)==step+1,"断线存盘继续"+step);
        }
        check(d.personalStep(t,b)==0&&d.state(t).equals("DECLINED"),"补谈不覆盖他人/团队决定");
        check(!d.advancePersonal(t,a,event,Hk3TeamContactData.PERSONAL_STEPS,true),"完成后不重复推进");
        var research=new Hk3ResearchData();var old=Hk3CommunicationResearchProof.receipt(a,t,true,1);old.putString("TimeBasis","verification_time_original_reply_time_unavailable");
        research.recordProcessFact(t,"formal_communication",old);check(!research.hasProcessFact(t,"formal_communication"),"旧投影不能作为新工况");
        check(research.recordFormalCommunication(t,d.receipt(t)),"真实本队答复修复旧投影占位");check(research.hasProcessFact(t,"formal_communication"),"真实交流可作工况");
        check(!research.hasExperiment(t,"RN-HCCO")&&!research.completed(t,"RN-HCCO"),"交流不直接发实验/研究");
        check(!research.recordFormalCommunication(t,d.receipt(t)),"研究来源重放幂等");
        check(research.save(new CompoundTag()).getCompound("Accounts").getCompound(t.toString()).getCompound("ArchivedPersonalContactProjection").equals(old),"保留原投影历史");
        check(!research.recordFormalCommunication(UUID.randomUUID(),d.receipt(t)),"错误团队不可接收来源");
        var bad=d.receipt(t);bad.getCompound("Outputs").putString("Reply","unknown");check(!new Hk3ResearchData().recordFormalCommunication(t,bad),"未知回复拒绝");
        var sessions=new Hk3ContactSessions();var p=sessions.issue(a,t,event,"accept",0,100);
        check(sessions.consume(b,p.token(),t,"accept",101)==null,"他人令牌拒绝");check(sessions.consume(a,p.token(),UUID.randomUUID(),"accept",101)==null,"换队旧令牌拒绝");
        check(sessions.consume(a,p.token(),t,"decline",101)==null,"不同动作拒绝");check(sessions.consume(a,p.token(),t,"accept",101)!=null,"正确预览提交");
        check(sessions.consume(a,p.token(),t,"accept",101)==null,"重复令牌拒绝");p=sessions.issue(a,t,event,"continue",1,100);check(sessions.consume(a,p.token(),t,"continue",2500)==null,"到期令牌拒绝");
        p=sessions.issue(a,t,event,"accept",0,100);sessions.clear(a);check(sessions.consume(a,p.token(),t,"accept",101)==null,"登出清理");
        var ids=new ArrayList<UUID>();for(int i=0;i<200;i++){
            UUID id=UUID.randomUUID();ids.add(id);check(d.discover(id,id,i),"独立团队发现");d.read(id,id);check(d.decide(id,id,id,true,d.event(id),i%2==0,i),"独立决定");
        }
        var saved=d.save(new CompoundTag());d=Hk3TeamContactData.load(saved);for(int i=0;i<ids.size();i++){UUID id=ids.get(i);check(d.state(id).equals(i%2==0?"ACCEPTED":"DECLINED"),"200团队重启隔离");}
        UUID broken=UUID.randomUUID();var root=new CompoundTag();var rows=new CompoundTag();rows.putString(broken.toString(),"future");root.put("Teams",rows);var corrupt=Hk3TeamContactData.load(root);
        check(!corrupt.available(broken)&&!corrupt.discover(broken,broken,1),"未知状态拒绝重置");check(corrupt.save(new CompoundTag()).getCompound("Teams").equals(rows),"损坏原数据保留");
        var invalid=d.save(new CompoundTag());var r=invalid.getCompound("Teams").getCompound(t.toString());var steps=r.getCompound("Personal");steps.putInt(a.toString(),999);r.put("Personal",steps);
        var badPersonal=Hk3TeamContactData.load(invalid);check(badPersonal.personalStep(t,a)==-1,"异常步数不能变成完成");check(!badPersonal.advancePersonal(t,a,event,0,true),"异常数据不能重置刷补谈");
        r.remove("Actor");var missingActor=Hk3TeamContactData.load(invalid);check(!missingActor.settled(t),"结算缺本人来源拒绝识别");
        System.out.println("TeamContactTest: "+checks+" checks passed");
    }
}

// 【变更记录 · 修订161】2026-10-17 14:11:55：本轮仅将活动类名、资源与工业配方引用迁移为长期业务命名；历史备注保留，不代表旧逻辑已全部按现行设计重写。
