package com.sirin.hk3gtl.test.dialogue;
import com.sirin.hk3gtl.common.badending.Hk3BadEndingData;
import com.sirin.hk3gtl.common.badending.Hk3FinaleAttackData;
import com.sirin.hk3gtl.common.dimension.Hk3GraduationData;
import net.minecraft.nbt.CompoundTag;
import java.util.*;

/** 【变更记录 #1】2026-09-30 23:35:44（修订119）：删除无；新增个人结果、断线续读、旧世界数据不广播及损坏存盘检查；修改无；用途：验证多人账本边界，不代替游戏内踢出/动画验收。 */
public final class FinalePersonalTest {
    private static int checks;
    private static void check(boolean value,String message){if(!value)throw new AssertionError(message);checks++;}
    public static void run(){
        UUID a=UUID.randomUUID(),b=UUID.randomUUID();
        var legacy=new CompoundTag();legacy.putBoolean("Graduated",true);
        var good=Hk3GraduationData.load(legacy);
        check(!good.isGraduated(a)&&!good.isGraduated(b),"旧世界标记不授予所有玩家通过");
        check(good.markGraduated(a)&&!good.markGraduated(a),"通过结果幂等");
        check(good.isGraduated(a)&&!good.isGraduated(b),"同服他人不毕业");
        good=Hk3GraduationData.load(good.save(new CompoundTag()));
        check(good.isGraduated(a)&&!good.isGraduated(b),"个人通过跨重启");
        good.markGraduated(b);good.resetForDebug(a);
        check(!good.isGraduated(a)&&good.isGraduated(b),"调试只重置本人");
        var oldBad=new CompoundTag();oldBad.putInt("AttackCount",9);oldBad.putInt("Stage",1);
        var bad=Hk3BadEndingData.load(oldBad);var attacks=new Hk3FinaleAttackData();
        check(bad.getStage(a)==0&&bad.getStage(b)==0,"旧世界坏结局不误伤新玩家");
        UUID am=bad.beginEncounter(a),bm=bad.beginEncounter(b);
        check(!am.equals(bm)&&am.equals(bad.beginEncounter(a)),"玩家会面独立，重连不刷新");
        attacks.begin(a,am);attacks.begin(b,bm);
        for(int i=0;i<9;i++)attacks.recordDirectHit(a,am);
        check(attacks.recordDirectHit(b,bm)==1&&attacks.count(a,am)==9,"9+1不同玩家不合成10次");
        check(!bad.erase(a,bm)&&!bad.erase(b,am),"跨玩家会面不能结算");
        check(attacks.recordDirectHit(a,am)==10&&bad.erase(a,am),"本人第10次触发");
        check(!bad.erase(a,am)&&bad.badCount(a)==1,"重复触发不多记历史");
        check(bad.getStage(b)==0&&attacks.count(b,bm)==1,"他人状态与攻击保留");
        check(bad.beginEncounter(a)==null,"坏结局不能直接冒充新资格重开");
        check(!bad.complete(a),"没读完收尾不结算");
        bad.markReturned(a);bad.advanceLine(a,2);
        check(bad.line(a)==0,"收尾不能跳句");
        for(int i=1;i<=4;i++)bad.advanceLine(a,i);
        bad=Hk3BadEndingData.load(bad.save(new CompoundTag()));
        check(bad.returned(a)&&bad.line(a)==4&&bad.meeting(a).equals(am),"断线重启保留同次会面/回城/行进度");
        for(int i=5;i<=9;i++)bad.advanceLine(a,i);
        check(bad.complete(a)&&!bad.complete(a),"收尾仅一次完成");
        check(bad.getStage(a)==2&&bad.badCount(a)==1&&bad.getStage(b)==0,"个人坏结局历史，不影响他人");
        check(!good.isGraduated(a),"坏结局不生成正常通过");
        bad.resetForDebug(a);check(bad.meeting(a)==null&&bad.meeting(b).equals(bm),"个人调试不清他人记录");
        for(int i=0;i<200;i++){
            UUID id=new UUID(1,i);UUID m=bad.beginEncounter(id);attacks.begin(id,m);
            for(int hit=1;hit<=10;hit++)check(attacks.recordDirectHit(id,m)==hit,"200玩家独立计数");
            check(bad.erase(id,m),"独立坏结局可并存存盘");
            for(int line=1;line<=9;line++)bad.advanceLine(id,line);
            check(bad.complete(id),"个人独立收尾");
        }
        var saved=bad.save(new CompoundTag());var loaded=Hk3BadEndingData.load(saved);
        for(int i=0;i<200;i++)check(loaded.getStage(new UUID(1,i))==2&&loaded.badCount(new UUID(1,i))==1,"批量重启隔离");
        check(loaded.getStage(b)==0,"未触发玩家始终不受影响");
        saved.getCompound("Personal").getCompound(b.toString()).putInt("Line",99);
        expectFailure(()->Hk3BadEndingData.load(saved));
        var malformed=new CompoundTag();malformed.putString("PassedPlayers","损坏");expectFailure(()->Hk3GraduationData.load(malformed));
        var oldAgain=loaded.save(new CompoundTag());check(oldAgain.getInt("AttackCount")==9&&oldAgain.getInt("Stage")==1,"保留不可归属的旧世界历史");
        System.out.println("Finale personal: "+checks+" checks passed; ledger only, multiplayer cinematic acceptance pending");
    }
    private static void expectFailure(Runnable action){try{action.run();throw new AssertionError("损坏状态被接受");}catch(IllegalStateException expected){checks++;}}
}
