package com.sirin.hk3gtl.test.research;

/**
 * 【文件职责／本轮边界】验证个人付款、离队与解散、完成后解锁、全队离线暂停及退款幂等和证据来源继承。
 * 【变更记录 #1】2026-09-29 21:06:40（第 1 次编号备注 · 内测5修订100）
 * 删除：取消已被批准规则替代的研究个人独占、旧数值或在线限定分支；历史备注与其他系统保留。
 * 新增／修改：验证个人付款、离队与解散、完成后解锁、全队离线暂停及退款幂等和证据来源继承。
 * 用途：接通实际证据→付款→研究完成与权限检查；不授予缺真实证据的课题。
 * 边界：编译和账本测试不代表游戏验收；S02至S05正式结构及未接线课题仍未完成。
 * 追溯：logs/research-mainline-r100；R100_FINAL_RECORD。
 */

import com.sirin.hk3gtl.common.research.*;
import dev.ftb.mods.ftbteams.api.Team;
import net.minecraft.nbt.*;
import java.lang.reflect.Proxy;
import java.util.*;
import java.math.BigInteger;

/** 【变更记录 #2】2026-10-31 03:33:10（修订187）：回归FTB个人队真实owner与党团owner隔离，防止NIL owner锁死本人或以scope越权。 */

/** 修订100 · 2026-09-29：真实SavedData团队生命周期、付款与精确一次退款，不接触玩家存档。 */
public final class ResearchTeamTest {
    private static final UUID A=UUID.randomUUID(), B=UUID.randomUUID(), T=UUID.randomUUID(), U=UUID.randomUUID();
    public static void main(String[] args) {
        transitions(); dissolution(); materialReceipts(); sharedCompletion(); ftbOwnerSemantics();
        System.out.println("ResearchTeamTest: personal payer, leave/join, provenance, dissolution and exactly-once refunds passed");
    }
    private static Hk3ResearchData funded() {
        CompoundTag root=new CompoundTag(), accounts=new CompoundTag(), payer=new CompoundTag();
        payer.putString("Points","100"); accounts.put(A.toString(),payer); root.put("Accounts",accounts);
        return Hk3ResearchData.load(root);
    }
    private static Hk3ResearchWorkQueue.Quote quote(String mode,CompoundTag paid) {
        return new Hk3ResearchWorkQueue.Quote("RN-HED","minecraft:overworld@123",1,10,32,mode,paid);
    }
    private static CompoundTag points() { var t=new CompoundTag();t.putString("Points","20");return t; }
    private static void transitions() {
        var data=funded();
        data.recordExperiment(A,"RN-HED","minecraft:overworld@42/real_sample");
        data.reconcileTeams(Map.of(A,T,B,T),Set.of(T));
        check(data.hasExperiment(T,"RN-HED"),"joining merges genuine evidence");
        check(data.points(T).equals(BigInteger.ZERO),"points not shared");
        check(!data.startResearchWithPoints(T,B,quote("points",points()),true),"poor teammate cannot spend payer balance");
        check(data.startResearchWithPoints(T,A,quote("points",points()),true),"team starts on actual payer account");
        check(data.points(A).intValueExact()==80,"exact personal debit");
        check(!data.startResearchWithPoints(T,A,quote("points",points()),true),"duplicate start refused");
        check(!data.cancelResearch(T,B,"RN-HED"),"teammate cannot cancel");
        data.advanceResearch(T,"RN-HED","minecraft:overworld@123",1,true,true,1,()->true);
        data.reconcileTeams(Map.of(A,U,B,T),Set.of(T,U));
        check(data.hasExperiment(U,"RN-HED"),"leaver brings completed experiment");
        check(data.researchJob(U,"RN-HED")==null,"pending progress never copied");
        check(data.researchJob(T,"RN-HED").progress()==1,"job remains old team");
        data=Hk3ResearchData.load(data.save(new CompoundTag()));
        check(data.cancelResearch(T,A,"RN-HED"),"ex-member still original payer");
        check(data.points(A).intValueExact()==100,"refund to payer after leave");
        check(!data.cancelResearch(T,A,"RN-HED"),"duplicate cancel refused");
        data=Hk3ResearchData.load(data.save(new CompoundTag()));
        check(data.points(A).intValueExact()==100,"refund survives restart exactly once");
        var sources=data.save(new CompoundTag()).getCompound("Accounts").getCompound(U.toString()).getList("EvidenceSources",Tag.TAG_STRING);
        check(sources.size()==1 && sources.getString(0).contains("@42/real_sample"),"original provenance inherited");
    }
    private static void dissolution() {
        var data=funded();data.reconcileTeams(Map.of(A,T,B,T),Set.of(T));
        data.recordExperiment(T,"RN-HED","real_sample");
        check(data.startResearchWithPoints(T,A,quote("points",points()),true),"start before dissolution");
        data.reconcileTeams(Map.of(A,A,B,B),Set.of());
        check(data.points(A).intValueExact()==100 && data.researchJob(T,"RN-HED")==null,"dissolution refunds pending job");
        check(data.hasExperiment(A,"RN-HED") && data.hasExperiment(B,"RN-HED"),"former members inherit completed evidence");
        check(!data.completed(A,"RN-HED"),"unfinished research never inherited as complete");
        data.reconcileTeams(Map.of(A,A,B,B),Set.of());
        check(data.points(A).intValueExact()==100,"repeat reconciliation cannot refund twice");
    }
    private static void materialReceipts() {
        var data=funded();data.reconcileTeams(Map.of(A,T),Set.of(T));
        CompoundTag paid=new CompoundTag(), stack=new CompoundTag(), nbt=new CompoundTag();ListTag items=new ListTag();
        stack.putString("id","minecraft:paper");stack.putByte("Count",(byte)12);nbt.putString("Sample","original");stack.put("tag",nbt);items.add(stack);paid.put("Items",items);
        check(data.startResearch(T,Hk3ResearchData.withPayer(quote("materials",paid),A),true,()->true),"escrow real receipt");
        data.reconcileTeams(Map.of(A,A),Set.of());
        data=Hk3ResearchData.load(data.save(new CompoundTag()));
        var refund=data.refundItems(A);check(refund.size()==1 && refund.getCompound(0).equals(stack),"refund retains full item NBT/count");
        refund.clear();check(data.refundItems(A).size()==1,"refund getter defensive copy");
        check(data.points(A).intValueExact()==100,"material refund cannot mint points");
    }
    private static void sharedCompletion() {
        var data=funded();data.reconcileTeams(Map.of(A,T,B,T),Set.of(T));
        data.recordExperiment(T,"RN-HED","settled-sample");
        check(data.startResearchWithPoints(T,A,quote("points",points()),true),"payer starts shared research");
        check(data.advanceResearch(T,"RN-HED","minecraft:overworld@123",1,true,false,1,()->{
            throw new AssertionError("offline formal research must not charge power");
        })==Hk3ResearchWorkQueue.Outcome.PAUSED,"whole team offline pauses formal research");
        check(!data.permits(T,"RN-HED"),"paid research does not unlock before completion");
        data.reconcileTeams(Map.of(A,U,B,T),Set.of(T,U));
        for(int tick=2;tick<=11;tick++)data.advanceResearch(T,"RN-HED","minecraft:overworld@123",tick,true,true,1,()->true);
        check(data.permits(data.scope(B),"RN-HED"),"remaining teammate gets actual completion unlock");
        check(!data.permits(data.scope(A),"RN-HED"),"payer cannot bring later old-team completion to new team");
        check(data.researchJob(T,"RN-HED")==null && !data.cancelResearch(T,A,"RN-HED"),"completed task cannot be refunded");
        check(data.points(A).intValueExact()==80,"completion retains actual paid cost");
        data.reconcileTeams(Map.of(A,U,B,U),Set.of(T,U));
        check(data.permits(U,"RN-HED"),"member carries genuinely completed knowledge on later join");
        check(data.points(B).signum()==0,"knowledge inheritance cannot mint points");
    }
    private static void ftbOwnerSemantics() {
        UUID player=UUID.randomUUID(), party=UUID.randomUUID(), owner=UUID.randomUUID();
        check(ftbOwner(team(true,player,new UUID(0,0))).equals(player),"FTB个人队必须以自身玩家ID为答复队长");
        check(ftbOwner(team(false,party,owner)).equals(owner),"FTB党团只认实际队长，不能以团队scope越权");
        check(ftbOwner(null)==null,"未知FTB团队不得回退为scope授权");
    }
    private static UUID ftbOwner(Team team) {
        try {
            Class<?> bridge=Class.forName(Hk3ResearchTeams.class.getName()+"$Ftb");
            var owner=bridge.getDeclaredMethod("owner",Team.class); owner.setAccessible(true);
            return (UUID) owner.invoke(null,team);
        } catch (ReflectiveOperationException failure) { throw new AssertionError("FTB owner桥接不可调用",failure); }
    }
    private static Team team(boolean player,UUID id,UUID owner) {
        return (Team) Proxy.newProxyInstance(Team.class.getClassLoader(),new Class<?>[]{Team.class},(proxy,method,args)->switch(method.getName()) {
            case "isPlayerTeam" -> player;
            case "getId" -> id;
            case "getOwner" -> owner;
            case "equals" -> proxy==args[0];
            case "hashCode" -> System.identityHashCode(proxy);
            case "toString" -> "ftb-owner-regression";
            default -> throw new AssertionError("测试代理意外调用："+method.getName());
        });
    }
    private static void check(boolean ok,String message) { if(!ok)throw new AssertionError(message); }
}

// 【变更记录 · 修订161】2026-10-17 14:11:55：本轮仅将活动类名、资源与工业配方引用迁移为长期业务命名；历史备注保留，不代表旧逻辑已全部按现行设计重写。
