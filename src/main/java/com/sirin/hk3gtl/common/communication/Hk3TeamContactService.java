package com.sirin.hk3gtl.common.communication;

 

 

 

 

 
import com.mojang.brigadier.arguments.*;
import com.sirin.hk3gtl.common.research.*;
import com.sirin.hk3gtl.common.phone.*;
import com.sirin.hk3gtl.common.network.*;
import com.sirin.hk3gtl.common.narrative.story.Hk3StoryService;
import net.minecraft.commands.Commands;
import net.minecraft.commands.arguments.EntityArgument;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerPlayer;
import net.minecraftforge.event.entity.player.PlayerEvent;
import net.minecraftforge.event.server.ServerStoppedEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import net.minecraftforge.network.PacketDistributor;
import java.util.*;

 
 
 
 
@Mod.EventBusSubscriber(modid="hk3gtl")
 
 
public final class Hk3TeamContactService {
    private static final Hk3ContactSessions SESSIONS=new Hk3ContactSessions();
    private Hk3TeamContactService(){}
    private static UUID team(ServerPlayer p){return Hk3ResearchTeams.scope(p.server,p.getUUID());}
    /** 只把已送达的资料共享给本队；旧个人合作立场保留历史，不自动代表本队。 */
    public static void ensure(ServerPlayer p){
        UUID t=team(p),owner=Hk3ResearchTeams.owner(p.server,t);var d=Hk3TeamContactData.get(p.server);
        var research=Hk3ResearchData.get(p.server);var members=research.members(t);
        if(!d.available(t)&&members.stream().anyMatch(id->Hk3CommunicationData.get(p.server).state(id).hasObservationData()))d.discover(t,owner,p.server.overworld().getGameTime());
        d.reconcile(t,owner,new HashSet<>(members));if(!d.available(t))return;
        for(UUID id:members)Hk3CommunicationData.get(p.server).discover(id);
        Hk3CommunicationDelivery.first(d,Hk3PhoneData.get(p.server),t,members,System.currentTimeMillis(),n->announce(p.server,n));
        Hk3StoryService.teamFact(p.server,t,"first_contact_received");
        if(d.settled(t)){
            Hk3ResearchData.get(p.server).recordFormalCommunication(t,d.receipt(t));
            Hk3StoryService.teamFact(p.server,t,d.state(t).equals("ACCEPTED")?"otto_accepted":"otto_declined");
            if(d.route(t).equals("STOPPED"))Hk3StoryService.teamFact(p.server,t,"otto_stopped");
            Hk3StoryService.choice(p,"otto_route",d.route(t));
        }
    }
    static void announce(net.minecraft.server.MinecraftServer server,Hk3CommunicationDelivery.Notice notice){
        var player=server.getPlayerList().getPlayer(notice.recipient());
        if(player!=null)Hk3PhoneService.toast(player,notice.id(),notice.title(),notice.body(),notice.kind(),notice.pending()?2:1);
    }
    public static void clearPreview(UUID actor){SESSIONS.clear(actor);Hk3ProgressCorrespondence.clearPreview(actor);}
    public static int open(ServerPlayer p,int doc){
        if(doc<0||doc>5)return 0;ensure(p);UUID t=team(p);var d=Hk3TeamContactData.get(p.server);
        if(!d.available(t)){p.sendSystemMessage(Component.translatable("hk3gtl.letter.locked"));return 0;}
        boolean accepted=d.state(t).equals("ACCEPTED"),settled=d.settled(t);
        if((doc==4&&!accepted)||(doc==5&&!d.state(t).equals("DECLINED")))return 0;
        boolean permitted=d.canDecide(t,p.getUUID(),Hk3ResearchTeams.owner(p.server,t),Hk3ResearchData.get(p).isMember(p.getUUID(),t));
        var context=new CompoundTag();context.putBoolean("CanDecide",permitted);context.putBoolean("PersonalDone",d.personalStep(t,p.getUUID())==Hk3TeamContactData.PERSONAL_STEPS);
        context.putString("MessageId",doc==0?"contact_"+t:doc>=4?"contact_reply_"+t:"");
        SESSIONS.clear(p.getUUID());
        if(!settled&&permitted&&(doc==1||doc==2))context.putString("Token",SESSIONS.issue(p.getUUID(),t,d.event(t),doc==1?"accept":"decline",0,tick(p)).token().toString());
        send(p,doc,settled?d.state(t):"READ",context);return 1;
    }
    /** 仅由已经核验收件人拥有该通知的收件箱调用；旧队历史不暴露可执行按钮。 */
    public static int history(ServerPlayer p,UUID originalTeam,int doc){
        if(doc<0||doc>5)return 0;var d=Hk3TeamContactData.get(p.server);if(!d.available(originalTeam))return 0;
        boolean accepted=d.state(originalTeam).equals("ACCEPTED");
        if((doc==4&&!accepted)||(doc==5&&!d.state(originalTeam).equals("DECLINED")))return 0;
        var c=new CompoundTag();c.putBoolean("HistoryOnly",true);c.putString("MessageId",doc==0?"contact_"+originalTeam:"contact_reply_"+originalTeam);
        send(p,doc,d.state(originalTeam),c);return 1;
    }
    static String canonicalBody(int doc){
        String[] ids={"A01","A02","A03","A04","A05","A06"};
        if(doc<0||doc>=ids.length)throw new IllegalArgumentException("首信正文编号无效");
        return com.sirin.hk3gtl.common.narrative.Hk3ApprovedText.body(com.sirin.hk3gtl.common.narrative.Hk3ApprovedProse.get("communication."+ids[doc]));
    }
    private static void send(ServerPlayer p,int doc,String state,CompoundTag context){
        var body=new StringBuilder(canonicalBody(doc));
        if(context.getInt("SupplementStep")>0)body.insert(0,"个人补谈第 "+context.getInt("SupplementStep")+" / "+context.getInt("SupplementTotal")+" 步：保留本队原决定，不重发奖励。阅读后亲自确认继续。\n\n");
        if(context.getBoolean("HistoryOnly"))body.insert(0,"原队往来历史 · 仅供回看，不算当前团队决定或个人补谈。\n\n");
        var read=new CompoundTag();read.putString("Mode","letter");read.putString("Id",context.getString("MessageId"));read.putString("Body",body.toString());read.putString("Token",context.getString("Token"));
        if(read.getString("Id").isEmpty())read.putString("Id",doc==0?"contact_"+team(p):"letter_document_"+doc);
        com.sirin.hk3gtl.common.easter.Hk3EggReading.attach(p,read);
        if(read.hasUUID("ReadToken")){context.putUUID("ReadToken",read.getUUID("ReadToken"));context.putString("ReadCanonical",body.toString());}
        Hk3Network.CHANNEL.send(PacketDistributor.PLAYER.with(()->p),new Hk3LetterOpenPacket(doc,state,context));}
    /** 原信完整阅读后才记入本人账本；旧队历史不改当前队。 */
    public static void readCompleted(ServerPlayer p,String messageId){
        if(!messageId.startsWith("contact_"))return;
        UUID t=team(p);
        if(messageId.equals("contact_"+t)&&Hk3TeamContactData.get(p.server).available(t)){
            Hk3TeamContactData.get(p.server).read(t,p.getUUID());
            Hk3CommunicationData.get(p).read(p.getUUID());
        }
    }
    private static long tick(ServerPlayer p){return p.server.overworld().getGameTime();}
    public static int reply(ServerPlayer p,String action,String token){
        ensure(p);UUID t=team(p);var d=Hk3TeamContactData.get(p.server);UUID uuid;try{uuid=UUID.fromString(token);}catch(IllegalArgumentException bad){return 0;}
        var preview=SESSIONS.consume(p.getUUID(),uuid,t,action,tick(p));
        if(preview==null||!d.decide(t,p.getUUID(),Hk3ResearchTeams.owner(p.server,t),Hk3ResearchData.get(p).isMember(p.getUUID(),t),preview.event(),action.equals("accept"),tick(p))){p.sendSystemMessage(Component.literal("未发送：团队、授权或预览已变化；请重新打开当前来信。"));return open(p,0);}
        p.sendSystemMessage(Component.literal("回信已发送，奥托的回复已送达。"));Hk3DiplomacyService.refresh(p);return open(p,action.equals("accept")?4:5);
    }
    public static int supplement(ServerPlayer p){
        ensure(p);UUID t=team(p);var d=Hk3TeamContactData.get(p.server);if(!d.settled(t))return 0;int step=d.personalStep(t,p.getUUID());
        if(step<0){p.sendSystemMessage(Component.literal("个人交流记录异常，已保留原始记录，请联系管理员核查。"));return 0;}
        if(step==Hk3TeamContactData.PERSONAL_STEPS){p.sendSystemMessage(Component.literal("你已亲自完成本队首次交流，回看不会再次结算。"));return open(p,0);}
        int doc=step==0?0:step==1?(d.state(t).equals("ACCEPTED")?1:2):step==2?(d.state(t).equals("ACCEPTED")?4:5):3;
        var c=new CompoundTag();c.putInt("SupplementStep",step+1);c.putInt("SupplementTotal",Hk3TeamContactData.PERSONAL_STEPS);c.putString("Token",SESSIONS.issue(p.getUUID(),t,d.event(t),"continue",step,tick(p)).token().toString());send(p,doc,d.state(t),c);return 1;
    }
    public static int advance(ServerPlayer p,String token){
        ensure(p);UUID t=team(p),id;try{id=UUID.fromString(token);}catch(IllegalArgumentException bad){return 0;}
        if(!com.sirin.hk3gtl.common.easter.Hk3EggReading.consumeAction(p,token)){p.sendSystemMessage(Component.literal("请按顺序读完当前补谈正文，再确认继续。"));return 0;}
        var preview=SESSIONS.consume(p.getUUID(),id,t,"continue",tick(p));var d=Hk3TeamContactData.get(p.server);
        if(preview==null||!d.advancePersonal(t,p.getUUID(),preview.event(),preview.step(),Hk3ResearchData.get(p).isMember(p.getUUID(),t))){p.sendSystemMessage(Component.literal("本次补谈预览已失效，请重新进入；已确认步骤保留。"));return open(p,0);}
        return supplement(p);
    }
    public static com.mojang.brigadier.builder.LiteralArgumentBuilder<net.minecraft.commands.CommandSourceStack> commands(){
        var root=Commands.literal("hk3letter").executes(c->open(c.getSource().getPlayerOrException(),0));
        root.then(Commands.literal("view").then(Commands.argument("document",IntegerArgumentType.integer(0,5)).executes(c->open(c.getSource().getPlayerOrException(),IntegerArgumentType.getInteger(c,"document")))));
        for(String action:List.of("accept","decline"))root.then(Commands.literal(action).then(Commands.argument("token",StringArgumentType.word()).executes(c->reply(c.getSource().getPlayerOrException(),action,StringArgumentType.getString(c,"token")))));
        root.then(Commands.literal("supplement").executes(c->supplement(c.getSource().getPlayerOrException())));
        root.then(Commands.literal("continue").then(Commands.argument("token",StringArgumentType.word()).executes(c->advance(c.getSource().getPlayerOrException(),StringArgumentType.getString(c,"token")))));
        for(boolean grant:List.of(true,false))root.then(Commands.literal(grant?"delegate":"revoke").then(Commands.argument("player",EntityArgument.player()).executes(c->{
            var p=c.getSource().getPlayerOrException();ensure(p);UUID t=team(p);var target=EntityArgument.getPlayer(c,"player");
            boolean ok=Hk3TeamContactData.get(p.server).delegate(t,p.getUUID(),Hk3ResearchTeams.owner(p.server,t),target.getUUID(),Hk3ResearchData.get(p).isMember(target.getUUID(),t),grant);
            if(ok){clearPreview(target.getUUID());Hk3DiplomacyService.clearPreview(target.getUUID());}
            p.sendSystemMessage(Component.literal(ok?(grant?"已授权该成员处理团队正式交流。":"已撤销该成员的外交授权。"):"未更改：仅队长能授权/撤销本队成员，或目标已处于该状态。"));return ok?1:0;
        })));
        root.then(Commands.literal("archive").executes(c->com.sirin.hk3gtl.common.narrative.Hk3PersonalArchive.openCodex(c.getSource().getPlayerOrException())));
        root.then(Hk3DiplomacyService.commands());
        root.then(Hk3ProgressCorrespondence.commands());
        return root;
    }
    @SubscribeEvent public static void logout(PlayerEvent.PlayerLoggedOutEvent e){SESSIONS.clear(e.getEntity().getUUID());}
    @SubscribeEvent public static void stopped(ServerStoppedEvent e){SESSIONS.clear();}
}

 
