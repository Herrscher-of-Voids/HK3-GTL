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
        var facts=facts(server,Hk3ResearchData.get(server),Hk3ReviewData.get(server),team);
        return new Status(team,Hk3CivilizationData.get(server).highest(team),Hk3CivilizationRules.achieved(facts::contains),facts);
    }
    public static Set<String> facts(MinecraftServer server,Hk3ResearchData research,Hk3ReviewData review,UUID team){
        var result=new HashSet<>(facts(research,review,team));int wonders=0;
        for(int i=1;i<=15;i++)if(!Hk3EngineeringFacts.receipt(server,research,team,String.format(Locale.ROOT,"W%02d",i)).isEmpty())wonders++;
        if(wonders>0)result.add("engineering:any_wonder");
        if(wonders==15)result.add("engineering:15_wonders");
        if(!Hk3EngineeringFacts.receipt(server,research,team,"H01").isEmpty())result.add("engineering:hyperion");
        return Set.copyOf(result);
    }
    public static Status status(Hk3ResearchData research,Hk3ReviewData review,Hk3CivilizationData history,UUID team){
        var facts=facts(research,review,team);
        int high=history.highest(team);
        return new Status(team,high,Hk3CivilizationRules.achieved(facts::contains),facts);
    }
    /** 只报告缺少实际提供者，不能据结构成型、耗电或研究推断工程验收。 */
    public static String pendingSource(String key){return switch(key){
        case "engineering:any_wonder" -> "至少一座奇观实际完成生产，且原机当前加载并完整成型";
        case "engineering:15_wonders" -> "十五座奇观均完成生产并保持原机完整";
        case "engineering:hyperion" -> "休伯利安实际完成舰载工程，且原舰当前完整成型";
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
                p.sendSystemMessage(Component.literal("未满足："+r.label()+(pending.isEmpty()?"":"；完成条件："+pending)));
            }
            p.sendSystemMessage(Component.literal("等级不锁机器/配方；终审当前工程资格与个人经历另查。"));return 1;
        }));
    }
}

 
