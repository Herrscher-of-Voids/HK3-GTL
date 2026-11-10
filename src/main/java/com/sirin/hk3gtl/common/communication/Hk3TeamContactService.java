package com.sirin.hk3gtl.common.communication;

/** 【变更记录 #10】2026-10-31 02:01:05（第10次备注 · 修订187）：删除专服语言表展开正文；新增公共已批准中文原文解析；修改全文回执同源正文；用途：专服未载入客户端语言表时拒绝裸翻译键，不改变原信。 */

/** 【变更记录 #9】2026-10-31 01:06:22（第9次备注 · 修订187）：删除失效补谈无反馈分支；新增无；修改消费失败返回本队当前页；用途：撤权与过期预览及时刷新。 */

/** 【变更记录 #8】2026-10-31 00:46:39（第8次备注 · 修订187）：删除打开即已读；新增完整阅读回调；修改答复与补谈消费前核验当前正文；用途：保持团队授权及个人经历隔离。 */

/** 【变更记录 #3】2026-10-01 00:14:30（修订122）：删除无；新增/修改：首信命令接入五方主题与成果摘要子入口；用途：真实成果、团队授权与个人阅读分离，不开放贸易或免费完成研究。 */

/** 【变更记录 #2】2026-10-01 00:00:53（修订121）：删除无；新增/修改：已有通知的跨队历史只读，不跳转或改写新队立场；用途：个人与团队记录隔离，保留历史与权限。 */
import com.mojang.brigadier.arguments.*;
import com.sirin.hk3gtl.common.research.*;
import com.sirin.hk3gtl.common.phone.*;
import com.sirin.hk3gtl.common.network.*;
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

/** 【变更记录 #1】2026-09-30 23:58:50（修订121）：删除旧个人答复自动代表新队的生产路径；新增/修改：原首信入口改团队答复、两步预览令牌、队长授权命令和三步个人补谈；离线投递不算亲历；用途：团队外交、阅读与个人经历分账，不发研究或物品奖励。 */
/** 【变更记录 #4】2026-10-01 00:44:40（修订123）：删除无；新增/修改：持有卷轴可只读本人的权威经历，不要求安装手机；用途：个人交流、团队决定及额外收藏分开，保留真实记录。 */
/** 【变更记录 #5】2026-10-01 00:59:10（修订124）：删除无；新增/修改：首信和附件四步补谈；生产与整链测试复用离线去重投递；提供离队预览清理；用途：按五方交流系统整链收口，真实权限和本人经历不混用。 */
/** 【变更记录 #6】2026-10-01 01:01:52（修订124）：删除无；新增指令授权变更时清旧预览；修改与手机授权入口一致；用途：撤权后再授权也不能复用撤权前页面。 */
@Mod.EventBusSubscriber(modid="hk3gtl")
/** 【变更记录 #7】2026-10-01 04:19:02（修订128）：删除：旧固定上限或被替代的分支；新增/修改：天命首信使用服务端同源正文验证逐页阅读，旧队历史仍只读；用途：已审核彩蛋独立执行，不授研究或审查资格。 */
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
        if(d.settled(t))Hk3ResearchData.get(p.server).recordFormalCommunication(t,d.receipt(t));
    }
    static void announce(net.minecraft.server.MinecraftServer server,Hk3CommunicationDelivery.Notice notice){
        var player=server.getPlayerList().getPlayer(notice.recipient());
        if(player!=null)Hk3PhoneService.toast(player,notice.id(),notice.title(),notice.body(),notice.kind(),notice.pending()?2:1);
    }
    public static void clearPreview(UUID actor){SESSIONS.clear(actor);}
    public static int open(ServerPlayer p,int doc){
        if(doc<0||doc>5)return 0;ensure(p);UUID t=team(p);var d=Hk3TeamContactData.get(p.server);
        if(!d.available(t)){p.sendSystemMessage(Component.translatable("hk3gtl.letter.locked"));return 0;}
        boolean accepted=d.state(t).equals("ACCEPTED"),settled=d.settled(t);
        if((doc==4&&!accepted)||(doc==5&&!d.state(t).equals("DECLINED")))return 0;
        boolean permitted=d.canDecide(t,p.getUUID(),Hk3ResearchTeams.owner(p.server,t),Hk3ResearchData.get(p).isMember(p.getUUID(),t));
        var context=new CompoundTag();context.putBoolean("CanDecide",permitted);context.putBoolean("PersonalDone",d.personalStep(t,p.getUUID())==Hk3TeamContactData.PERSONAL_STEPS);
        context.putString("MessageId",doc==0?"contact_"+t:doc>=4?"contact_reply_"+t:"");
        SESSIONS.clear(p.getUUID());
        if(!settled&&permitted&&(doc==1||doc==2)&&d.hasRead(t,p.getUUID()))context.putString("Token",SESSIONS.issue(p.getUUID(),t,d.event(t),doc==1?"accept":"decline",0,tick(p)).token().toString());
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
        if(!com.sirin.hk3gtl.common.easter.Hk3EggReading.consumeAction(p,token)){p.sendSystemMessage(Component.literal("请按顺序读完当前回信预览，再确认发送。"));return 0;}
        var preview=SESSIONS.consume(p.getUUID(),uuid,t,action,tick(p));
        if(preview==null||!d.decide(t,p.getUUID(),Hk3ResearchTeams.owner(p.server,t),Hk3ResearchData.get(p).isMember(p.getUUID(),t),preview.event(),action.equals("accept"),tick(p))){p.sendSystemMessage(Component.literal("未发送：团队、授权或预览已变化；请重新打开当前来信。"));return open(p,0);}
        ensure(p);return open(p,action.equals("accept")?4:5);
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
        return root;
    }
    @SubscribeEvent public static void logout(PlayerEvent.PlayerLoggedOutEvent e){SESSIONS.clear(e.getEntity().getUUID());}
    @SubscribeEvent public static void stopped(ServerStoppedEvent e){SESSIONS.clear();}
}

// 【变更记录 · 修订161】2026-10-17 14:11:55：本轮仅将活动类名、资源与工业配方引用迁移为长期业务命名；历史备注保留，不代表旧逻辑已全部按现行设计重写。
