package com.sirin.hk3gtl.test.dialogue;

import com.sirin.hk3gtl.common.finale.*;
import com.sirin.hk3gtl.common.badending.Hk3BadEndingData;
import net.minecraft.nbt.*;
import java.nio.file.*;
import java.util.*;

/** 【变更记录 #1】2026-10-01 16:49:18（修订135）：删除无；新增完整准入/缺项/快照持久化/个人隔离/重试及实际调用接线回归；修改check入口；用途：输入为隔离测试夹具，不代表真实奇观提供者或实机终审通过。 */
public final class FinaleAdmissionTest {
    private static int checks;
    private static void check(boolean pass,String label){checks++;if(!pass)throw new AssertionError(label);}
    private static void reject(Runnable action){try{action.run();throw new AssertionError("接受损坏账本");}catch(IllegalStateException expected){checks++;}}
    private static Map<String,Hk3FinaleRequirements.Fact> fixtures(){
        var facts=new HashMap<String,Hk3FinaleRequirements.Fact>();
        for(var r:Hk3FinaleRequirements.REQUIREMENTS){var n=new CompoundTag();n.putString("Source","isolated_test_only:"+r.key());facts.put(r.key(),Hk3FinaleRequirements.Fact.complete(n));}
        return facts;
    }
    public static void main(String[] args)throws Exception{
        UUID actor=UUID.randomUUID(),other=UUID.randomUUID(),team=UUID.randomUUID();
        var facts=fixtures();var ready=Hk3FinaleRequirements.evaluate(actor,team,40,facts);
        check(Hk3FinaleRequirements.REQUIREMENTS.size()==24,"固定24项准入，15奇观分别核验");
        check(ready.ready()&&Hk3FinaleRequirements.validSnapshot(ready.sources(),actor),"完整夹具建立来源");
        check(!Hk3FinaleRequirements.validSnapshot(ready.sources(),other),"不能借用他人快照");
        for(var r:Hk3FinaleRequirements.REQUIREMENTS){
            var value=facts.remove(r.key());
            var missing=Hk3FinaleRequirements.evaluate(actor,team,40,facts);
            check(!missing.ready()&&missing.sources().isEmpty(),"缺一项不能得到部分资格："+r.key());
            check(missing.items().stream().anyMatch(i->i.requirement().key().equals(r.key())&&i.state()==Hk3FinaleRequirements.State.WAITING),"未提供来源与未完成有区别");
            facts.put(r.key(),Hk3FinaleRequirements.Fact.missing("实际未完成"));
            check(!Hk3FinaleRequirements.evaluate(actor,team,40,facts).ready(),"尚未完成拒绝");
            facts.put(r.key(),Hk3FinaleRequirements.Fact.complete(new CompoundTag()));
            check(!Hk3FinaleRequirements.evaluate(actor,team,40,facts).ready(),"空证据不能冒充完成");
            facts.put(r.key(),value);
        }
        var leaked=ready.sources();leaked.getCompound("Facts").remove("W01");
        check(ready.ready()&&ready.sources().getCompound("Facts").contains("W01"),"快照防外部修改");
        var ledger=new Hk3FinaleLedger();UUID meeting=UUID.randomUUID();
        check(!ledger.begin(other,meeting,ready,"F01"),"其他玩家不能入场");
        check(ledger.begin(actor,meeting,ready,"F01"),"本人首次入场");
        check(!ledger.begin(actor,UUID.randomUUID(),ready,"F01"),"重复申请不覆盖检查点");
        var otherReady=Hk3FinaleRequirements.evaluate(other,team,41,fixtures());
        check(!ledger.begin(other,meeting,otherReady,"F01"),"会面UUID不可共享");
        UUID otherMeeting=UUID.randomUUID();check(ledger.begin(other,otherMeeting,otherReady,"F01"),"同队分别入场");
        check(!ledger.advance(actor,otherMeeting,"FU01"),"他人会面不能推进");
        check(!ledger.finish(actor,meeting,Hk3FinaleLedger.State.PASSED),"未抵终点不能毕业");
        check(ledger.advance(actor,meeting,"F06"),"合法服务端检查点保存");
        var changedTeam=Hk3FinaleRequirements.evaluate(actor,UUID.randomUUID(),42,Map.of());
        check(!changedTeam.ready()&&ledger.open(actor)&&ledger.sources(actor).getUUID("Team").equals(team),"入场后团队变化不撤销旧快照");
        var reloaded=Hk3FinaleLedger.load(ledger.save());
        check(reloaded.open(actor)&&reloaded.meeting(actor).equals(meeting)&&reloaded.checkpoint(actor).equals("F06"),"重启续读同次快照与检查点");
        check(reloaded.checkpoint(other).equals("F01"),"不同玩家进度不混用");
        var sources=reloaded.sources(actor);sources.remove("Facts");
        check(reloaded.sources(actor).contains("Facts"),"账本来源副本不外泄");
        check(reloaded.finish(actor,meeting,Hk3FinaleLedger.State.BAD),"本人坏结局终止会面");
        check(!reloaded.finish(actor,meeting,Hk3FinaleLedger.State.BAD),"坏结局结算幂等");
        check(!reloaded.begin(actor,UUID.randomUUID(),changedTeam,"F01"),"坏结局后重新核验，不能复用失效事实");
        UUID retry=UUID.randomUUID();check(reloaded.begin(actor,retry,ready,"F01"),"重新通过后创建新会面");
        check(!reloaded.advance(actor,meeting,"FU01"),"旧会面包不能推进新会面");
        check(reloaded.advance(actor,retry,"FU01")&&reloaded.finish(actor,retry,Hk3FinaleLedger.State.PASSED),"新会面终点唯一通过");
        check(!reloaded.begin(actor,UUID.randomUUID(),ready,"F01"),"通过后不能重复领奖会面");
        var saved=reloaded.save();
        check(!Hk3FinaleLedger.load(saved).open(actor)&&Hk3FinaleLedger.load(saved).open(other),"终止结果重载不影响他人");
        var broken=saved.copy();broken.getCompound("People").getCompound(actor.toString()).getCompound("Sources").putUUID("Actor",other);
        reject(()->Hk3FinaleLedger.load(broken));reject(()->Hk3FinaleLedger.load(new CompoundTag()));
        var missingProof=saved.copy();missingProof.getCompound("People").getCompound(actor.toString()).getCompound("Sources").getCompound("Facts").remove("W15");
        reject(()->Hk3FinaleLedger.load(missingProof));
        var bad=new Hk3BadEndingData();
        check(bad.beginQualifiedEncounter(actor,changedTeam)==null,"无资格不改坏结局数据");
        UUID badMeeting=bad.beginEncounter(actor);check(bad.erase(actor,badMeeting),"准备历史坏结局");
        check(bad.beginQualifiedEncounter(actor,ready)==null,"尚未收尾不能跳过");
        for(int line=1;line<=9;line++)bad.advanceLine(actor,line);
        check(bad.complete(actor),"真实收尾完成");
        UUID retried=bad.beginQualifiedEncounter(actor,ready);
        check(retried!=null&&!retried.equals(badMeeting)&&bad.badCount(actor)==1&&bad.getStage(actor)==0,"重试保留历史，更换身份");
        bad=Hk3BadEndingData.load(bad.save(new CompoundTag()));
        check(bad.badCount(actor)==1&&bad.meeting(actor).equals(retried),"重试跨重启保留历史");
        FinaleNonceTest.run();
        wiring();
        System.out.println("Finale admission: "+checks+" checks passed; real engineering providers and in-game acceptance pending");
    }
    private static String read(String name)throws Exception{return Files.readString(Path.of("src/main/java/com/sirin/hk3gtl/"+name+".java"));}
    private static void wiring()throws Exception{
        var event=read("common/event/Hk3EventManagerImpl");check(!event.contains("teleportToImaginaryDimension("),"里程碑不再隐式传送");
        var manager=read("common/dialogue/DialogueSessionManager");
        check(manager.contains("Hk3FinaleAdmission.requireSession(player)")&&manager.contains("Hk3FinaleAdmission.advance(player,nextSegment)"),"正式入口与合法分支写权威检查点");
        check(!manager.contains("getString(\"hk3gtl_finale_checkpoint_v5\")"),"旧NBT不是资格");
        check(read("common/dialogue/handler/SirinDialogueEndHandler").contains("Hk3FinaleAdmission.canSettle(player)"),"通过处理器二次守卫");
        check(read("common/command/Hk3DebugCommands").contains("Hk3ApprovedDialogues.FINALE_PREVIEW"),"管理员正文走独立预览");
        check(!read("common/command/Hk3IfArchiveCommand").contains("Hk3FinaleAdmission"),"普通玩家免费26条入口不锁");
        check(read("common/narrative/Hk3PersonalArchive").contains("Hk3FinaleAdmission.summary(player)"),"手机与卷轴共用结果");
        var service=read("common/finale/Hk3FinaleAdmission");check(service.contains("Fact.waiting("),"缺真实工程提供者明确等待");
        check(service.indexOf("if(!result.ready())return") < service.indexOf("beginQualifiedEncounter"),"拒绝资格时不创建本人会面");
        var dimension=read("common/dimension/ImaginaryDimensionHandler");
        var travel=dimension.substring(dimension.indexOf("public static void onDimensionTravel("),dimension.indexOf("public static void onBlockPlace("));
        check(!travel.contains("setGameMode") && !travel.contains("Hk3FinalePlayerMode.enter"),"取消传送不提前改个人模式");
        check(dimension.contains("Hk3FinalePlayerMode.enter(player)") && dimension.contains("Hk3FinalePlayerMode.leave(player)"),"成功入场与返程共用本人模式记录");
        var cinematic=read("common/badending/SirinBadEndingManager");
        check(cinematic.contains("Hk3FinaleAdmission.hasSession(player)") && !cinematic.contains("UUID meeting=data.beginEncounter(player.getUUID())"),"攻击只读取本人已核验会面");
        var screen=read("client/dialogue/Hk3DialogueScreen");
        var keys=screen.substring(screen.indexOf("public boolean keyPressed("));
        check(keys.indexOf("if (awaitingChoiceAck) return true;") < keys.indexOf("GLFW.GLFW_KEY_ESCAPE"),"选择待确认时不能发送旧令牌关闭");
        check(manager.contains("session.accepts(dialogueId, nonce)") && manager.contains("next.nonce()"),"选择和关闭校验逐段令牌");
        check(cinematic.contains("ERASED_SUFFIX")&&cinematic.contains("disconnect("),"坏结局改名踢出逻辑保留");
    }
}
