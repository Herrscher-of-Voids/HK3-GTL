package com.sirin.hk3gtl.common.finale;

import com.sirin.hk3gtl.common.research.*;
import com.sirin.hk3gtl.common.review.*;
import com.sirin.hk3gtl.common.communication.*;
import com.sirin.hk3gtl.common.badending.Hk3BadEndingData;
import com.sirin.hk3gtl.common.dimension.*;
import com.sirin.hk3gtl.common.dialogue.DialogueSessionManager;
import net.minecraft.nbt.*;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.network.chat.Component;
import net.minecraft.commands.Commands;
import net.minecraftforge.event.RegisterCommandsEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import java.util.*;

@Mod.EventBusSubscriber(modid="hk3gtl")
public final class Hk3FinaleAdmission {
    private Hk3FinaleAdmission(){}
    private static Hk3FinaleRequirements.Fact recorded(boolean ready,String source,String detail){
        if(!ready)return Hk3FinaleRequirements.Fact.missing(detail);
        var n=new CompoundTag();n.putString("Source",source);return Hk3FinaleRequirements.Fact.complete(n);
    }
    public static Hk3FinaleRequirements.Evaluation evaluate(ServerPlayer p){
        UUID actor=p.getUUID(),team=Hk3ResearchTeams.scope(p.server,actor);
        var research=Hk3ResearchData.get(p);var reviews=Hk3ReviewData.get(p.server);
        var completed=Hk3ResearchExecutionContracts.all().keySet().stream().filter(id->research.completed(team,id)).sorted().toList();
        var facts=new HashMap<String,Hk3FinaleRequirements.Fact>();
        facts.put("research",recorded(Hk3ResearchExecutionContracts.all().size()==100&&completed.size()==100,
            "industrial_research_account:"+String.join(",",completed),"本队已完成 "+completed.size()+" / 100 项"));
        facts.put("first_person",recorded(reviews.experienced(actor,Hk3ReviewLedger.Kind.FIRST),"reviews:personal:first","请亲自完成一审会面"));
        facts.put("second_person",recorded(reviews.experienced(actor,Hk3ReviewLedger.Kind.SECOND),"reviews:personal:second","请亲自完成二审会面"));
        UUID permit=reviews.settlement(team,Hk3ReviewLedger.Kind.SECOND);
        facts.put("second_team",recorded(permit!=null,"reviews:settlement:"+permit,"当前团队尚无二审许可"));
        var communication=Hk3CommunicationCompletion.status(Hk3TeamContactData.get(p.server),Hk3PersonalCommunicationData.get(p.server),actor);
        facts.put("communication",recorded(communication.complete(),"personal_communication:six_groups","尚缺："+String.join("、",communication.missing())));
        var civilizationFacts=com.sirin.hk3gtl.common.civ.Hk3CivilizationService.facts(p.server,research,reviews,team);
        int currentLevel=com.sirin.hk3gtl.common.civ.Hk3CivilizationRules.achieved(civilizationFacts::contains);
        facts.put("c7",recorded(currentLevel==7,"civilization:current_c7","当前核验 C"+currentLevel+"；目标 C7"));
        facts.put("archive",com.sirin.hk3gtl.common.narrative.Hk3FormalArchive.evaluate(p).fact());
        for(int i=1;i<=15;i++){
            String role=String.format(Locale.ROOT,"W%02d",i);facts.put(role,engineering(p,research,team,role));
        }
        facts.put("hyperion",engineering(p,research,team,"H01"));
        facts.put("application",engineering(p,research,team,"application"));
        return Hk3FinaleRequirements.evaluate(actor,team,p.server.overworld().getGameTime(),facts);
    }
    private static Hk3FinaleRequirements.Fact engineering(ServerPlayer player,Hk3ResearchData research,UUID team,String role){
        var receipt=com.sirin.hk3gtl.common.civ.Hk3EngineeringFacts.accepted(player.server,research,team,role);
        return receipt.isEmpty()?Hk3FinaleRequirements.Fact.missing("尚无有效工程验收回执，或原机加载后未通过成型验证")
                :Hk3FinaleRequirements.Fact.complete(receipt);
    }
    public static String summary(ServerPlayer p){
        var text=new StringBuilder("终审准备\n");
        var ledger=Hk3FinaleData.get(p.server).snapshot();
        if(Hk3GraduationData.get(p.serverLevel()).isGraduated(p.getUUID()))text.append("你已通过终审。\n");
        else if(hasSession(p))text.append("会面进度：").append(ledger.checkpoint(p.getUUID())).append("。使用 /hk3finale resume 继续会面。\n");
        else if(Hk3BadEndingData.get(p.serverLevel()).getStage(p.getUUID())==Hk3BadEndingData.STAGE_ERASED)text.append("本人坏结局收尾尚未结束；先完成收尾，再重新申请。\n");
        for(var item:evaluate(p).items()){
            text.append(switch(item.state()){case COMPLETE->"[已完成] ";case MISSING->"[未完成] ";case WAITING->"[尚未开放] ";});
            text.append(item.requirement().label());if(!item.detail().isEmpty())text.append("：").append(item.detail());text.append('\n');
        }
        return text.append("\n查询：/hk3finale status；申请：/hk3finale apply；继续会面：/hk3finale resume。").toString();
    }
    public static boolean hasSession(ServerPlayer p){
        var ledger=Hk3FinaleData.get(p.server).snapshot();var bad=Hk3BadEndingData.get(p.serverLevel());
        return ledger.open(p.getUUID())&&bad.getStage(p.getUUID())==0&&Objects.equals(ledger.meeting(p.getUUID()),bad.meeting(p.getUUID()));
    }
    public static String checkpoint(ServerPlayer p){return Hk3FinaleData.get(p.server).snapshot().checkpoint(p.getUUID());}
    public static boolean requireSession(ServerPlayer p){
        if(hasSession(p))return true;
        p.sendSystemMessage(Component.literal("尚无已核验的本次终审会面。请在文明档案查看缺项，或使用 /hk3finale status。"));return false;
    }
    public static void advance(ServerPlayer p,String checkpoint){
        if(!hasSession(p))return;var meeting=Hk3BadEndingData.get(p.serverLevel()).meeting(p.getUUID());
        Hk3FinaleData.get(p.server).change(l->l.advance(p.getUUID(),meeting,checkpoint));
    }
    public static boolean canSettle(ServerPlayer p){return hasSession(p)&&"FU01".equals(checkpoint(p));}
    public static void finish(ServerPlayer p,boolean good){
        var meeting=Hk3BadEndingData.get(p.serverLevel()).meeting(p.getUUID());
        boolean settled=Hk3FinaleData.get(p.server).change(l->l.finish(p.getUUID(),meeting,good?Hk3FinaleLedger.State.PASSED:Hk3FinaleLedger.State.BAD));
        if(settled)com.sirin.hk3gtl.common.narrative.story.Hk3StoryService.fact(p,good?"finale_passed":"finale_bad");
    }
    /** 查询无副作用；正式申请在入场前重新采集，当前未接入提供者会拒绝，不生成占位快照。 */
    public static int apply(ServerPlayer p){
        if(Hk3GraduationData.get(p.serverLevel()).isGraduated(p.getUUID()))return message(p,"本人已通过终审，无需重新申请。",0);
        if(hasSession(p))return message(p,"已有会面，请使用 /hk3finale resume 恢复。",0);
        if(DialogueSessionManager.hasActiveDialogue(p.getUUID()))return message(p,"请先结束当前对话，再申请终审。",0);
        var bad=Hk3BadEndingData.get(p.serverLevel());
        if(bad.getStage(p.getUUID())==Hk3BadEndingData.STAGE_ERASED)return message(p,"请先完成坏结局收尾；历史将保留。",0);
        var result=evaluate(p);if(!result.ready())return message(p,summary(p),0);
        var level=p.server.getLevel(Hk3Dimensions.IMAGINARY);if(level==null)return message(p,"终审维度不可用，未创建申请。",0);
        com.sirin.hk3gtl.common.entity.VoidQueenSirinEntity.ensurePlatformAndEntity(level);
        UUID meeting=bad.beginQualifiedEncounter(p.getUUID(),result);
        if(meeting==null)return message(p,"当前会面状态不允许新申请。",0);
        boolean begun=Hk3FinaleData.get(p.server).change(l->l.begin(p.getUUID(),meeting,result,"F01"));
        if(!begun)return message(p,"终审会面记录不一致，未传送；请保留存档供检查。",0);
        com.sirin.hk3gtl.common.narrative.story.Hk3StoryService.fact(p,"finale_admitted");
        // 传送意外失败仍保留本人快照，恢复命令可重试同次入场，不重新占用名额。
        return enter(p);
    }
    public static int resume(ServerPlayer p){
        if(Hk3GraduationData.get(p.serverLevel()).isGraduated(p.getUUID()))return message(p,"本人已通过终审。",0);
        if(!requireSession(p))return 0;
        if(DialogueSessionManager.hasActiveDialogue(p.getUUID()))return message(p,"当前对话尚未结束。",0);
        return enter(p);
    }
    private static int enter(ServerPlayer p){
        var level=p.server.getLevel(Hk3Dimensions.IMAGINARY);if(level==null)return message(p,"终审维度暂不可用，已保留会面记录。",0);
        if(com.sirin.hk3gtl.common.badending.SirinBadEndingManager.isCinematicBusy())return message(p,"演出正在进行，稍后可恢复本次会面。",0);
        if(p.level()!=level){
            com.sirin.hk3gtl.common.entity.VoidQueenSirinEntity.ensurePlatformAndEntity(level);
            p.teleportTo(level,Hk3Dimensions.SPAWN_X+0.5,Hk3Dimensions.SPAWN_Y,Hk3Dimensions.SPAWN_Z+0.5,0,0);
            if(p.level()!=level)return message(p,"传送未完成，保留记录，可稍后恢复。",0);
            Hk3FinalePlayerMode.enter(p);
            return message(p,"本次资格已固定。触碰裂隙、等待登场后，右键开始或继续会面。",1);
        }
        return DialogueSessionManager.startDialogue(p,"sirin_finale")?1:0;
    }
    private static int message(ServerPlayer p,String text,int result){p.sendSystemMessage(Component.literal(text));return result;}
    @SubscribeEvent public static void commands(RegisterCommandsEvent event){
        event.getDispatcher().register(Commands.literal("hk3finale")
            .executes(c->message(c.getSource().getPlayerOrException(),summary(c.getSource().getPlayerOrException()),1))
            .then(Commands.literal("status").executes(c->message(c.getSource().getPlayerOrException(),summary(c.getSource().getPlayerOrException()),1)))
            .then(Commands.literal("apply").executes(c->apply(c.getSource().getPlayerOrException())))
            .then(Commands.literal("resume").executes(c->resume(c.getSource().getPlayerOrException()))));
    }
}

