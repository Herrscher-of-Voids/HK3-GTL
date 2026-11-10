package com.sirin.hk3gtl.test.review;
import com.sirin.hk3gtl.common.review.*;
import com.sirin.hk3gtl.common.dialogue.*;
import com.sirin.hk3gtl.common.research.Hk3ResearchData;
import net.minecraft.nbt.*;
import java.util.*;
/** 【变更记录 #1】2026-09-30 20:31:18（修订117）：删除无；新增多人三问、补行、重启、重入、许可独立与关闭防误结算测试；修改无；用途：真实资格和传送/降临尚未接入，不将此测试记为游戏通过。 */
/** 【变更记录 #2】2026-10-01 01:30:10（修订125）：删除无；新增未完成二审换队中止、保存重启与新队再申请检查；修改确认普通断线仍继续原检查点；用途：延期多人实测期间保留自动边界验证，不能当作实机通过。 */
public final class ReviewLedgerTest {
    private static int checks;
    private static void check(boolean v,String message){if(!v)throw new AssertionError(message);checks++;}
    private static CompoundTag sources(){var n=new CompoundTag();n.putString("Source","仅单元测试，不是生产资格");return n;}
    private static UUID team=UUID.randomUUID(),a=UUID.randomUUID(),b=UUID.randomUUID(),late=UUID.randomUUID();
    private static final Random RANDOM=new Random(117);
    private static Hk3ReviewLedger.Snapshot single(Hk3ReviewLedger d,UUID scope,UUID player){d.qualify(scope,Hk3ReviewLedger.Kind.FIRST,sources());return d.beginFirst(scope,List.of(player),RANDOM);}
    private static void questions(Hk3ReviewLedger d,Hk3ReviewLedger.Snapshot m){
        check(d.openingRead(m.id(),m.representative()),"读完开场");
        for(int q:new int[]{1,4,8}){check(d.choose(m.id(),m.representative(),q),"选问题");check(d.answerRead(m.id(),m.representative(),q),"读完答案");}
    }
    private static void secondToEnd(Hk3ReviewLedger d,UUID id,UUID player){
        for(int i=0;i<30;i++){var m=d.meeting(id);if(m.checkpoint().equals("S209"))return;check(d.advanceSecond(id,player,m.checkpoint(),0),"合法二审分支");}throw new AssertionError("二审图存在未预期循环");
    }
    public static void main(String[] args){
        var d=new Hk3ReviewLedger();check(d.beginFirst(team,List.of(a,b),RANDOM)==null,"无资格不能开会");
        check(!d.qualify(team,Hk3ReviewLedger.Kind.FIRST,new CompoundTag()),"空来源不合格");check(!d.qualify(team,Hk3ReviewLedger.Kind.SECOND,sources()),"二审前必须已完成本队一审");
        d.qualify(team,Hk3ReviewLedger.Kind.FIRST,sources());var m=d.beginFirst(team,List.of(a,b),RANDOM);UUID rep=m.representative(),other=rep.equals(a)?b:a;
        check(m.participants().size()==2&&!m.participants().contains(late),"仅在线成员进入");check(!d.openingRead(m.id(),other),"只有代表推进三问");
        check(d.finishFirst(m.id(),rep)==null,"开场不能结算");d.openingRead(m.id(),rep);
        check(!d.choose(m.id(),other,1)&&!d.choose(m.id(),rep,9),"越权/越界提问拒绝");
        d.choose(m.id(),rep,2);check(!d.answerRead(m.id(),rep,3),"错误答案回执拒绝");d.answerRead(m.id(),rep,2);d.choose(m.id(),rep,7);d.answerRead(m.id(),rep,7);
        d.depart(other);check(d.meeting(m.id()).phase()==Hk3ReviewLedger.Phase.MENU,"普通成员退出不打断代表");
        d.depart(rep);check(d.meeting(m.id()).phase()==Hk3ReviewLedger.Phase.PAUSED,"代表断线全场暂停");
        var restored=Hk3ReviewLedger.load(d.save());var again=restored.restartFirst(m.id(),other,List.of(other),RANDOM);
        check(again!=null&&again.questions().equals(List.of(2,7))&&again.representative().equals(other),"替补保留已问顺序");
        restored.openingRead(m.id(),other);check(!restored.choose(m.id(),other,4),"重播期间不能偷选新问题");
        restored.answerRead(m.id(),other,2);restored.answerRead(m.id(),other,7);check(restored.meeting(m.id()).phase()==Hk3ReviewLedger.Phase.MENU,"只剩一个新问题");
        check(!restored.choose(m.id(),other,2),"不能重复已问问题");restored.choose(m.id(),other,4);restored.answerRead(m.id(),other,4);
        check(!restored.choose(m.id(),other,6),"整场不能第四问");check(restored.finishFirst(m.id(),rep)==null,"原代表缺席不能算亲历");
        var first=restored.finishFirst(m.id(),other);check(first!=null&&first.firstTeamSettlement(),"首次完整会面才产生团队许可");check(restored.finishFirst(m.id(),other)==null,"重复结算拒绝");
        check(!restored.experienced(rep,Hk3ReviewLedger.Kind.FIRST)&&!restored.experienced(late,Hk3ReviewLedger.Kind.FIRST),"断线/离线者不代签");
        var supplement=restored.beginFirst(team,List.of(other,rep,late),RANDOM);check(supplement.supplement()&&!supplement.participants().contains(other),"已完成者不再取得三问次数");
        questions(restored,supplement);var result=restored.finishFirst(supplement.id(),rep);check(result!=null&&!result.firstTeamSettlement(),"个人补行不重复授团队许可");
        restored.finishFirst(supplement.id(),late);check(restored.beginFirst(team,List.of(a,b,late),RANDOM)==null,"全完成队伍没有新问答");
        UUID newTeam=UUID.randomUUID();restored.qualify(newTeam,Hk3ReviewLedger.Kind.FIRST,sources());check(restored.beginFirst(newTeam,List.of(rep),RANDOM)==null&&!restored.settled(newTeam,Hk3ReviewLedger.Kind.FIRST),"换队不刷新个人三问或复制许可");
        check(restored.qualify(team,Hk3ReviewLedger.Kind.SECOND,sources()),"本队完成一审后接二审资格");var s=restored.beginSecond(team,rep);
        check(s!=null&&!s.supplement()&&restored.finishSecond(s.id(),rep)==null,"二审开场不能结算");
        check(!restored.advanceSecond(s.id(),rep,"S209",0),"伪造终点无效");restored.advanceSecond(s.id(),rep,"S201",0);restored.advanceSecond(s.id(),rep,"S202",0);
        restored.depart(rep);check(restored.meeting(s.id()).checkpoint().equals("S203"),"二审中断保存检查点");
        var data=Hk3ReviewData.load(restored.save());var saved=data.snapshot();check(saved.meeting(s.id()).phase()==Hk3ReviewLedger.Phase.PAUSED,"重启后不假定仍在线");
        var state=saved.resumeSecond(s.id(),rep);check(state!=null&&state.checkpoint().equals("S203"),"从检查点继续同次二审");secondToEnd(saved,s.id(),rep);
        check(saved.finishSecond(s.id(),rep).firstTeamSettlement(),"二审完整结束首次许可");var s2=saved.beginSecond(team,other);check(s2.supplement()&&s2.checkpoint().equals("SP01"),"后来者补行专用开场");
        boolean sawSupplement=false;for(int i=0;i<25;i++){var at=saved.meeting(s2.id());if(at.checkpoint().equals("SP02"))sawSupplement=true;if(at.checkpoint().equals("S209"))break;saved.advanceSecond(s2.id(),other,at.checkpoint(),0);}
        check(sawSupplement&&!saved.finishSecond(s2.id(),other).firstTeamSettlement(),"补行绕过首次团队裁定正文并不重复授予");
        check(saved.settlement(team,Hk3ReviewLedger.Kind.FIRST).equals(first.meeting()),"团队许可来源不会被补行覆盖");
        var corrupted=saved.save();corrupted.getCompound("Settlements").putUUID(team+"/FIRST",UUID.randomUUID());boolean bad=false;try{Hk3ReviewLedger.load(corrupted);}catch(IllegalArgumentException ex){bad=true;}check(bad,"坏许可回执拒绝读取");
        var isolated=new Hk3ReviewData();boolean rejected=false;try{isolated.change(outer->isolated.change(inner->null));}catch(IllegalStateException ex){rejected=true;}check(rejected,"保存事务防重入");
        try{isolated.change(ledger->{ledger.qualify(team,Hk3ReviewLedger.Kind.FIRST,sources());throw new IllegalStateException();});}catch(IllegalStateException ignored){}check(!isolated.snapshot().qualified(team,Hk3ReviewLedger.Kind.FIRST),"异常不发布半份资格");
        var research=new Hk3ResearchData();check(!research.hasProcessFact(team,"cocoon_authorization"),"默认没有茧授权");check(!research.recordReviewPermission(team,2,UUID.randomUUID()),"不能先写二审许可");
        research.recordReviewPermission(team,1,first.meeting());check(research.hasProcessFact(team,"cocoon_authorization")&&!research.completed(team,"RN-WCP"),"一审许可只开放前置，不免费研究");
        research.recordReviewPermission(team,2,s.id());check(Hk3ResearchData.load(research.save(new CompoundTag())).hasReviewPermission(team,2),"研究许可独立持久化");
        check(!research.hasReviewPermission(newTeam,1),"不向新队复制旧队许可");
        var terminal=new DialogueLine("system","done",null,null);var option=new DialogueLine("system","choose",null,List.of(new DialogueChoice("yes","end")));var def=new DialogueDefinition("test",Map.of("start",List.of(option),"end",List.of(terminal)),"start",true,"handler");
        check(!Hk3DialogueCompletionRules.maySettle(def,"end",false),"主动关闭不奖励");check(!Hk3DialogueCompletionRules.maySettle(def,"start",true),"客户端完成标记不能越过选择");check(Hk3DialogueCompletionRules.maySettle(def,"end",true),"终点正常结束可结算");
        var closing=new Hk3ReviewLedger();closing.qualify(team,Hk3ReviewLedger.Kind.FIRST,sources());var closingMeeting=closing.beginFirst(team,List.of(a,b),RANDOM);questions(closing,closingMeeting);
        UUID closingRep=closingMeeting.representative(),closingOther=closingRep.equals(a)?b:a;closing.finishFirst(closingMeeting.id(),closingRep);closing.depart(closingOther);
        check(closing.meeting(closingMeeting.id()).phase()==Hk3ReviewLedger.Phase.COMPLETE,"代表结束后其余人退出不留下永久占用");
        check(closing.beginFirst(team,List.of(closingOther),RANDOM)!=null,"退出者之后仍能补行");
        for(int q1=1;q1<=8;q1++)for(int q2=1;q2<=8;q2++)for(int q3=1;q3<=8;q3++)if(q1!=q2&&q1!=q3&&q2!=q3){
            var permutations=new Hk3ReviewLedger();var q=single(permutations,UUID.randomUUID(),UUID.randomUUID());UUID actor=q.representative();permutations.openingRead(q.id(),actor);
            check(permutations.choose(q.id(),actor,q1)&&permutations.answerRead(q.id(),actor,q1),"全部首问选择");
            check(permutations.choose(q.id(),actor,q2)&&permutations.answerRead(q.id(),actor,q2),"全部第二问选择");permutations.depart(actor);
            var re=Hk3ReviewLedger.load(permutations.save());check(re.restartFirst(q.id(),actor,List.of(actor),RANDOM)!=null,"所有顺序中断后可重开");re.openingRead(q.id(),actor);
            check(re.answerRead(q.id(),actor,q1)&&re.answerRead(q.id(),actor,q2)&&re.choose(q.id(),actor,q3)&&re.answerRead(q.id(),actor,q3),"重播原两问后仅补第三问");
            check(re.meeting(q.id()).questions().equals(List.of(q1,q2,q3))&&re.finishFirst(q.id(),actor)!=null&&re.finishFirst(q.id(),actor)==null,"全部336种三问顺序保留且结算一次");
        }
        var transfer=new Hk3ReviewLedger();var oldScope=UUID.randomUUID();var migrant=UUID.randomUUID();
        var entry=single(transfer,oldScope,migrant);questions(transfer,entry);transfer.finishFirst(entry.id(),migrant);
        transfer.qualify(oldScope,Hk3ReviewLedger.Kind.SECOND,sources());var unfinished=transfer.beginSecond(oldScope,migrant);
        transfer.advanceSecond(unfinished.id(),migrant,"S201",0);transfer.leaveTeam(migrant);
        check(transfer.meeting(unfinished.id()).phase()==Hk3ReviewLedger.Phase.ABANDONED,"换队二审留中止历史");
        var loaded=Hk3ReviewData.load(transfer.save()).snapshot();
        check(loaded.meeting(unfinished.id()).phase()==Hk3ReviewLedger.Phase.ABANDONED,"重启不复活中止二审");
        check(loaded.resumeSecond(unfinished.id(),migrant)==null&&!loaded.experienced(migrant,Hk3ReviewLedger.Kind.SECOND),"旧队会面不能继续或自动通过");
        UUID destination=UUID.randomUUID(),resident=UUID.randomUUID();var target=single(loaded,destination,resident);questions(loaded,target);loaded.finishFirst(target.id(),resident);
        check(loaded.beginSecond(destination,migrant)==null,"新队仍需自身二审资格");loaded.qualify(destination,Hk3ReviewLedger.Kind.SECOND,sources());
        var fresh=loaded.beginSecond(destination,migrant);check(fresh!=null&&fresh.checkpoint().equals("S201"),"旧队中止会面不锁住新队重新核验");
        check(loaded.experienced(migrant,Hk3ReviewLedger.Kind.FIRST)&&!loaded.settled(oldScope,Hk3ReviewLedger.Kind.SECOND),"个人一审历史保留，旧队二审未被授予");
        System.out.println("Review ledger: "+checks+" checks passed; live review scenes remain pending");
    }
}

// 【变更记录 · 修订161】2026-10-17 14:11:55：本轮仅将活动类名、资源与工业配方引用迁移为长期业务命名；历史备注保留，不代表旧逻辑已全部按现行设计重写。
