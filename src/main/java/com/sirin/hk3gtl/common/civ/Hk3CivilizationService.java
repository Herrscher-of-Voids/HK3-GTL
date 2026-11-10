package com.sirin.hk3gtl.common.civ;
import com.sirin.hk3gtl.common.research.*;
import com.sirin.hk3gtl.common.review.*;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.commands.Commands;
import net.minecraft.network.chat.Component;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.event.RegisterCommandsEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import java.util.*;

/** 【变更记录 #1】2026-09-30 23:43:42（修订120）：删除无；新增/修改：读取已完成RN、真实工况与团队审查记录，每五秒按在线队伍更新，新增只读查询；C6/C7工程验收仍待真实提供者；用途：按真实团队事实展示文明进度，不给机器/配方增加等级锁。 */
/** 【变更记录 #2】2026-11-04（修订197）：删除查询推进历史等级；新增回信授权核验、当前缺项目标及工程来源待接入说明；修改仅周期核验提升本队历史；用途：历史称号不代替当前资格，未接工程不冒充完成。 */
@Mod.EventBusSubscriber(modid="hk3gtl")
public final class Hk3CivilizationService {
    public record Status(UUID team,int highest,int currentlyVerified,Set<String> facts){
        public Status{facts=Set.copyOf(facts);}
        public int nextTarget(){return Math.min(7,currentlyVerified+1);}
        public List<Hk3CivilizationRules.Requirement> missing(){return Hk3CivilizationRules.missingThrough(nextTarget(),facts::contains);}
    }
    private Hk3CivilizationService(){}
    /** 仅投影已有服务端账本；没有工程验收执行器时不拿研究、合成或旧旗标冒充15奇观验收。 */
    public static Set<String> facts(Hk3ResearchData research,Hk3ReviewData review,UUID team){
        var result=new HashSet<String>();
        for(String id:Hk3ResearchExecutionContracts.all().keySet())if(research.completed(team,id))result.add("research:"+id);
        if(Hk3ResearchExecutionContracts.all().size()==100&&Hk3ResearchExecutionContracts.all().keySet().stream().allMatch(id->research.completed(team,id)))result.add("all_research");
        for(var level:Hk3CivilizationRules.LEVELS)for(var r:level.requirements()){
            if(r.key().startsWith("experiment:")&&research.hasExperiment(team,r.key().substring(11)))result.add(r.key());
            if(r.key().startsWith("fact:")&&research.hasProcessFact(team,r.key().substring(5)))result.add(r.key());
        }
        var contact=research.processFactReceipt(team,"formal_communication");
        // 换队时的历史回信投影不具有原队归属，不能据此把旧队外交成果带到新队。
        if(Hk3ResearchBatchProofs.valid(contact)&&contact.hasUUID("Team")&&team.equals(contact.getUUID("Team"))
                &&contact.getString("Authority").equals("team_owner_or_explicit_delegate")
                &&contact.getString("Recipe").equals("hk3gtl:first_contact_reply")&&!contact.contains("TimeBasis")
                &&contact.getCompound("Inputs").getString("Letter").equals("otto_first_contact")
                &&Set.of("accepted","declined").contains(contact.getCompound("Outputs").getString("Reply")))result.add("contact");
        if(review.settled(team,Hk3ReviewLedger.Kind.FIRST))result.add("review:1");
        if(review.settled(team,Hk3ReviewLedger.Kind.SECOND))result.add("review:2");
        return Set.copyOf(result);
    }
    public static Status status(ServerPlayer player){
        var team=Hk3ResearchTeams.scope(player.server,player.getUUID());return status(player.server,team);
    }
    public static Status status(MinecraftServer server,UUID team){
        return status(Hk3ResearchData.get(server),Hk3ReviewData.get(server),Hk3CivilizationData.get(server),team);
    }
    public static Status status(Hk3ResearchData research,Hk3ReviewData review,Hk3CivilizationData history,UUID team){
        var facts=facts(research,review,team);
        int high=history.highest(team);
        return new Status(team,high,Hk3CivilizationRules.achieved(facts::contains),facts);
    }
    /** 只报告缺少实际提供者，不能据结构成型、耗电或研究推断工程验收。 */
    public static String pendingSource(String key){return switch(key){
        case "engineering:any_wonder" -> "W01功能运行验收来源未接入";
        case "engineering:15_wonders" -> "W02–W15结构与运行参数待批准";
        case "engineering:hyperion" -> "H01结构与运行参数待批准";
        default -> "";
    };}
    /** 每五秒按在线队伍去重，只读内存账本，不扫描方块、不加载区块。 */
    @SubscribeEvent public static void tick(TickEvent.ServerTickEvent event){
        if(event.phase!=TickEvent.Phase.END)return;var server=event.getServer();
        if(server.getTickCount()%100!=0)return;
        var teams=new HashSet<UUID>();for(var p:server.getPlayerList().getPlayers())teams.add(Hk3ResearchTeams.scope(server,p.getUUID()));
        var history=Hk3CivilizationData.get(server);
        for(UUID team:teams){var snapshot=status(server,team);history.observe(team,snapshot.facts::contains);}
    }
    @SubscribeEvent public static void commands(RegisterCommandsEvent event){
        event.getDispatcher().register(Commands.literal("hk3civilization").executes(c->{
            var p=c.getSource().getPlayerOrException();var status=status(p);
            p.sendSystemMessage(Component.literal("本队历史最高："+Hk3CivilizationRules.title(status.highest)+"；当前事实："+Hk3CivilizationRules.title(status.currentlyVerified)));
            p.sendSystemMessage(Component.literal("当前核验目标："+Hk3CivilizationRules.title(status.nextTarget())));
            for(var r:status.missing()){
                String pending=pendingSource(r.key());
                p.sendSystemMessage(Component.literal("未满足："+r.label()+(pending.isEmpty()?"":"；待接入："+pending)));
            }
            p.sendSystemMessage(Component.literal("等级不锁机器/配方；终审当前工程资格与个人经历另查。"));return 1;
        }));
    }
}

// 【变更记录 · 修订161】2026-10-17 14:11:55：本轮仅将活动类名、资源与工业配方引用迁移为长期业务命名；历史备注保留，不代表旧逻辑已全部按现行设计重写。
