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

/**
 * 【变更记录 #1】2026-10-01 16:49:18（修订135）
 * 删除：无；新增：终审查询、主动申请、同次恢复和游戏账本适配。
 * 修改：准入只读权威记录；未接入的完整卷轴、W01至W15、舰船及W15申请生产者明确等待。
 * 用途：在不提前启用新结构的前提下关闭持物绕行；普通指令不能授予工程、研究或毕业。
 */
@Mod.EventBusSubscriber(modid="hk3gtl")
/** 【变更记录 #2】2026-10-01 20:33:47（修订148）：删除固定目录等待文案；新增/修改：终审档案事实读取共用目录的完成、未完成、等待接入结果；用途：逐项核验本人经历，保留真实未接来源，不授予虚假资格。 */
/** 【变更记录 #3】2026-10-01 22:50:14（第3次备注 · 内测5修订155）：删除玩家展示中的旧电压及开发说明；新增现行正文投影或对应回归；修改仅限呈现与检索，不改变进度、回执、触发条件或权限；用途：统一发布版玩家文案，历史备注保留。 */
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
        var civilizationFacts=com.sirin.hk3gtl.common.civ.Hk3CivilizationService.facts(research,reviews,team);
        int currentLevel=com.sirin.hk3gtl.common.civ.Hk3CivilizationRules.achieved(civilizationFacts::contains);
        facts.put("c7",recorded(currentLevel==7,"civilization:current_c7","当前核验 C"+currentLevel+"；目标 C7"));
        facts.put("archive",com.sirin.hk3gtl.common.narrative.Hk3FormalArchive.evaluate(p).fact());
        for(int i=1;i<=15;i++)facts.put(String.format(Locale.ROOT,"W%02d",i),Hk3FinaleRequirements.Fact.waiting("该工程尚未开放"));
        facts.put("hyperion",Hk3FinaleRequirements.Fact.waiting("休伯利安工程尚未开放"));
        facts.put("application",Hk3FinaleRequirements.Fact.waiting("申请设施尚未开放"));
        return Hk3FinaleRequirements.evaluate(actor,team,p.server.overworld().getGameTime(),facts);
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
        Hk3FinaleData.get(p.server).change(l->l.finish(p.getUUID(),meeting,good?Hk3FinaleLedger.State.PASSED:Hk3FinaleLedger.State.BAD));
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

// 【变更记录 · 修订161】2026-10-17 14:11:55：本轮仅将活动类名、资源与工业配方引用迁移为长期业务命名；历史备注保留，不代表旧逻辑已全部按现行设计重写。
