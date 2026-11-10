package com.sirin.hk3gtl.test.research;



/**
 * 【文件职责／本轮边界】验证固定实验离线续做、停电暂停、重启、防重复扣费及工装原NBT返还。
 * 【变更记录 #1】2026-09-29 21:06:40（第 1 次编号备注 · 内测5修订100）
 * 删除：取消已被批准规则替代的研究个人独占、旧数值或在线限定分支；历史备注与其他系统保留。
 * 新增／修改：验证固定实验离线续做、停电暂停、重启、防重复扣费及工装原NBT返还。
 * 用途：接通实际证据→付款→研究完成与权限检查；不授予缺真实证据的课题。
 * 边界：编译和账本测试不代表游戏验收；S02至S05正式结构及未接线课题仍未完成。
 * 追溯：logs/research-mainline-r100；R100_FINAL_RECORD。
 */

import com.sirin.hk3gtl.common.research.*;
import net.minecraft.nbt.*;
import java.util.*;

/** 修订100 · 2026-09-29：独立实验占槽、离线、暂停重启、工装托管和成功证据边界。 */
/**
 * 【变更记录 #2】2026-09-29 23:37:35（内测5修订101）
 * 删除：本轮被替代的单前置或旧提示分支；其余历史保留。
 * 新增／修改：回归OPR批次快照、托管、取消、重启、继承边界和原有两类实验。
 * 用途：补足研究接线并如实保留未接物理执行器及结构审批边界。
 * 追溯：logs/research-mainline-r101；R101_FINAL_RECORD。
 */
public final class LabExperimentTest {
    private static final UUID TEAM=UUID.randomUUID(), PAYER=UUID.randomUUID();
    public static void main(String[] args) { ale(); erm(); opr(); allocation();System.out.println("LabExperimentTest: shared slots, offline evidence, restart, escrow, tools, OPR receipts and paired ERM passed"); }
    private static void opr(){
        var data=ready("RN-OPR");var initial=quote("LAB-OPR",1);
        check(!data.startResearch(TEAM,initial,true,()->{throw new AssertionError("charged before receipts");}),"OPR rejects missing actual recovery");
        for(String category:Hk3ResearchBatchProofs.RECOVERY)data.recordRecovery(TEAM,category,ResearchMainlineTest.receipt(UUID.randomUUID()));
        check(!data.startResearch(TEAM,initial,true,()->true),"OPR quote must bind the actual three receipts");
        var paid=initial.paid();paid.put("RecoveryProofs",data.recoveryProofs(TEAM));
        var q=new Hk3ResearchWorkQueue.Quote(initial.topic(),initial.facility(),1,initial.ticks(),initial.eut(),initial.payment(),paid);
        check(data.startResearch(TEAM,q,true,()->true),"start OPR with bound batch receipts");
        data.advanceResearch(TEAM,q.topic(),q.facility(),1,true,false,3,()->true);
        data=Hk3ResearchData.load(data.save(new CompoundTag()));
        check(data.researchJob(TEAM,q.topic()).progress()==1,"OPR resumes exact progress after restart");
        check(!data.cancelResearch(TEAM,UUID.randomUUID(),q.topic()),"other member cannot claim OPR input");
        check(data.cancelResearch(TEAM,PAYER,q.topic()),"payer cancels OPR");
        check(data.refundItems(PAYER).size()==2&&!data.hasExperiment(TEAM,"RN-OPR"),"cancel restores exact escrow without evidence");
        check(!data.cancelResearch(TEAM,PAYER,q.topic()),"OPR cannot refund twice");
        check(data.startResearch(TEAM,q,true,()->true),"OPR can restart with a new payment");
        for(int t=2;t<=1801;t++)data.advanceResearch(TEAM,q.topic(),q.facility(),t,true,false,3,()->true);
        check(data.hasExperiment(TEAM,"RN-OPR")&&!data.completed(TEAM,"RN-OPR"),"OPR success still requires paid research");
        var next=UUID.randomUUID();data.reconcileTeams(Map.of(PAYER,next),Set.of(TEAM,next));
        check(data.hasExperiment(next,"RN-OPR")&&!data.recoveryAuditReady(next),"completed experimental knowledge inherits; raw team production batches do not");
    }
    private static Hk3ResearchData ready(String topic) {
        var data=new Hk3ResearchData(); data.reconcileTeams(Map.of(PAYER,TEAM),Set.of(TEAM));
        prepare(data,topic);return data;
    }
    private static void prepare(Hk3ResearchData data,String topic) {
        for(String parent:Hk3ResearchCatalog.bundled().get(topic).prerequisites()) {
            prepare(data,parent); data.recordCompletion(TEAM,parent,5);
        }
    }
    private static Hk3ResearchWorkQueue.Quote quote(String id,int lab) {
        CompoundTag paper=new CompoundTag(); paper.putString("id","minecraft:paper");paper.putByte("Count",(byte)4);
        CompoundTag tool=new CompoundTag();tool.putString("id","minecraft:diamond");tool.putByte("Count",(byte)1);
        CompoundTag nbt=new CompoundTag();nbt.putString("calibration","original");tool.put("tag",nbt);
        ListTag items=new ListTag(),tools=new ListTag();items.add(paper);items.add(tool);tools.add(tool.copy());
        CompoundTag paid=new CompoundTag();paid.put("Items",items);paid.put("Tools",tools);
        var spec=Hk3LabExperimentRules.get(id);
        return Hk3ResearchData.withPayer(new Hk3ResearchWorkQueue.Quote(id,"lab@1",lab,spec.ticks(),32,"materials",paid),PAYER);
    }
    private static void ale() {
        var data=ready("RN-ALE");var q=quote("LAB-ALE",1);
        check(data.startResearch(TEAM,q,true,()->true),"start real escrow job");
        check(!data.startResearch(TEAM,q,true,()->{throw new AssertionError("duplicate charged");}),"duplicate experiment blocked");
        CompoundTag paid=new CompoundTag();paid.putString("Points","1");
        var other=new Hk3ResearchWorkQueue.Quote("RN-OPR","lab@1",1,10,32,"points",paid);
        check(!data.startResearch(TEAM,other,true,()->{throw new AssertionError("borrowed slot charged");}),"S01 shared slot occupied");
        check(data.advanceResearch(TEAM,q.topic(),q.facility(),1,false,false,3,()->true)==Hk3ResearchWorkQueue.Outcome.PAUSED,"unformed pauses offline experiment");
        check(data.advanceResearch(TEAM,q.topic(),q.facility(),2,true,false,3,()->false)==Hk3ResearchWorkQueue.Outcome.PAUSED,"no energy no progress");
        data.advanceResearch(TEAM,q.topic(),q.facility(),3,true,false,3,()->true);
        check(data.researchJob(TEAM,q.topic()).progress()==1,"offline runs at fixed unboosted speed");
        data=Hk3ResearchData.load(data.save(new CompoundTag()));
        check(data.advanceResearch(TEAM,q.topic(),q.facility(),3,true,false,1,()->{throw new AssertionError("replay");})==Hk3ResearchWorkQueue.Outcome.DUPLICATE_TICK,"restart duplicate tick");
        check(!data.hasExperiment(TEAM,"RN-ALE"),"partial work is not evidence");
        for(int tick=4;tick<=2402;tick++)data.advanceResearch(TEAM,q.topic(),q.facility(),tick,true,false,3,()->true);
        check(data.hasExperiment(TEAM,"RN-ALE") && !data.completed(TEAM,"RN-ALE"),"success records evidence but still requires paid research");
        check(data.researchJob(TEAM,q.topic())==null,"finished experiment releases slot");
        var refund=data.refundItems(PAYER);check(refund.size()==1 && refund.getCompound(0).getCompound("tag").getString("calibration").equals("original"),"success returns only actual tool with NBT");
        check(!data.cancelResearch(TEAM,PAYER,q.topic()),"finished consumables cannot be refunded");
        var cancelled=ready("RN-ALE");cancelled.startResearch(TEAM,q,true,()->true);cancelled.cancelResearch(TEAM,PAYER,q.topic());
        check(cancelled.refundItems(PAYER).size()==2 && !cancelled.hasExperiment(TEAM,"RN-ALE"),"cancel returns consumables and tool without evidence");
    }
    private static void erm() {
        var data=ready("RN-ERM");var aid=quote("LAB-ERM-AID",2);var base=quote("LAB-ERM-BASE",2);
        check(!data.startResearch(TEAM,aid,true,()->true),"aid requires actual baseline");
        check(data.startResearch(TEAM,base,true,()->true),"start baseline");
        for(int i=1;i<=6000;i++)data.advanceResearch(TEAM,base.topic(),base.facility(),i,true,false,3,()->true);
        check(data.hasLabBaseline(TEAM) && !data.hasExperiment(TEAM,"RN-ERM"),"baseline alone is insufficient");
        data=Hk3ResearchData.load(data.save(new CompoundTag()));
        check(data.startResearch(TEAM,aid,true,()->true),"paired aid after restart");
        for(int i=6001;i<=12000;i++)data.advanceResearch(TEAM,aid.topic(),aid.facility(),i,true,false,3,()->true);
        check(data.hasExperiment(TEAM,"RN-ERM") && !data.completed(TEAM,"RN-ERM"),"paired evidence without research completion");
    }
    private static void allocation() {
        var plan=Hk3MaterialAllocation.allocateDetailed(new long[]{1,2},new long[]{2,1},new boolean[][]{{true,true},{true,false}});
        check(plan!=null && plan.assigned()[0][1]==1 && plan.assigned()[1][0]==2,"overlapping tool tag allocation preserves required tool");
    }
    private static void check(boolean ok,String message){if(!ok)throw new AssertionError(message);}
}

// 【变更记录 · 修订161】2026-10-17 14:11:55：本轮仅将活动类名、资源与工业配方引用迁移为长期业务命名；历史备注保留，不代表旧逻辑已全部按现行设计重写。
