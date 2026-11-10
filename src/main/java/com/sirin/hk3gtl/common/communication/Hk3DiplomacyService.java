package com.sirin.hk3gtl.common.communication;

/** 【变更记录 #10】2026-10-31 02:01:05（第10次备注 · 修订187）：删除专服翻译表的正文/标题展开；新增已批准原文同源解析；修改未知文档拒绝；用途：五方预览、历史与个人补谈不发送裸键。 */

/** 【变更记录 #9】2026-10-31 01:06:22（第9次备注 · 修订187）：删除失效预览无反馈分支；新增无；修改消费失败时返回联络首页；用途：避免旧页保留可点击动作。 */

/** 【变更记录 #8】2026-10-31 00:46:39（第8次备注 · 修订187）：删除未读即可消费预览的路径；新增阅读动作校验；修改未读时保留预览；用途：封住同源确认入口的绕过。 */

/** 【变更记录 #4】2026-10-01 00:20:13（修订122）：删除无；新增/修改：五方按配置时序投递，待处理回执动态一致，正文可返回本主题；用途：服务端主题状态与阅读权限一致。 */

/** 【变更记录 #3】2026-10-01 00:17:25（修订122）：删除无；新增/修改：五方署名在通知、阅读抬头和历史同步；正文成功打开后才确认已读；用途：五方首信与团队限定交流保持一致。 */

/** 【变更记录 #2】2026-10-01 00:14:30（修订122）：删除无；新增/修改：五方独立首信与回信；新增两方仅有限联络，不凭空设工业交换条件；用途：五方首信与真实批次分开记账，防止错误公开。 */
import com.sirin.hk3gtl.common.research.*;
import com.sirin.hk3gtl.common.narrative.Hk3ApprovedProse;
import com.sirin.hk3gtl.common.narrative.Hk3ApprovedText;
import com.sirin.hk3gtl.common.phone.*;
import com.sirin.hk3gtl.common.network.Hk3Network;
import net.minecraft.nbt.*;
import net.minecraft.network.chat.Component;
import net.minecraft.commands.Commands;
import com.mojang.brigadier.arguments.*;
import net.minecraft.server.level.ServerPlayer;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.event.entity.player.PlayerEvent;
import net.minecraftforge.event.server.ServerStoppedEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import net.minecraftforge.network.PacketDistributor;
import java.util.*;

/** 【变更记录 #1】2026-10-01 00:14:30（修订122）：删除无；新增/修改：五方全文预览、真实摘要、权限复核与延迟公开联络；回信版本比较防重复结算；用途：真实成果、团队授权与个人阅读分离，不开放贸易或免费完成研究。 */
/** 【变更记录 #5】2026-10-01 00:44:06（修订123）：删除无；新增/修改：五方主题提供明确个人补谈入口，普通队员可补谈但不能改团队立场；用途：个人交流、团队决定及额外收藏分开，保留真实记录。 */
/** 【变更记录 #6】2026-10-01 00:59:10（修订124）：删除无；新增/修改：五方联络页接历史/权限；原摘要与正文一起回看；稍后处理与时钟回退保护；离队待处理同步覆盖所有成员；用途：按五方交流系统整链收口，真实权限和本人经历不混用。 */
@Mod.EventBusSubscriber(modid="hk3gtl")
/** 【变更记录 #7】2026-10-01 04:19:02（修订128）：删除：旧固定上限或被替代的分支；新增/修改：五方历史正文阅读附加可选收藏页进度，不改合作许可；用途：已审核彩蛋独立执行，不授研究或审查资格。 */
public final class Hk3DiplomacyService {
    private record Draft(UUID token,UUID team,String topic,String action,int version,CompoundTag evidence,long until){}
    private static final Map<UUID,Draft> DRAFTS=new HashMap<>();
    private static final String PREFIX="hk3letter diplomacy";
    private Hk3DiplomacyService(){}
    private static UUID team(ServerPlayer p){return Hk3ResearchTeams.scope(p.server,p.getUUID());}
    static boolean allowed(ServerPlayer p){return Hk3PhoneData.get(p).installed(p.getUUID())&&Hk3PhoneRuntime.requirePower(p);}
    private static boolean authorized(ServerPlayer p,UUID t){return Hk3TeamContactData.get(p.server).canDecide(t,p.getUUID(),Hk3ResearchTeams.owner(p.server,t),Hk3ResearchData.get(p).isMember(p.getUUID(),t));}
    static String prose(String id){var e=Hk3ApprovedProse.get("communication."+id);if(e!=null)return e.speaker()+"\n\n"+Hk3ApprovedText.body(e);requireFaction(id);return Hk3FactionLetters.speaker(id)+"\n\n"+Hk3FactionLetters.body(id);}
    static String title(String id){var e=Hk3ApprovedProse.get("communication."+id);if(e!=null)return e.speaker()+"｜"+Hk3ApprovedText.title(e);requireFaction(id);return Hk3FactionLetters.speaker(id)+"｜"+Hk3FactionLetters.title(id);}
    private static void requireFaction(String id){if(Hk3FactionLetters.body(id).isBlank())throw new IllegalArgumentException("已批准五方正文不存在："+id);}
    // 【变更记录 #208】2026-11-05：信件页独立发送时同步实际App入口，保留原阅读与供电校验。
    static void send(ServerPlayer p,CompoundTag v){com.sirin.hk3gtl.common.phone.Hk3PhoneAppHints.opened(p,v.getString("Mode"));com.sirin.hk3gtl.common.easter.Hk3EggReading.attach(p,v);v.put("Runtime",Hk3PhoneRuntime.status(p));Hk3Network.CHANNEL.send(PacketDistributor.PLAYER.with(()->p),new Hk3PhonePacket(v));}
    static CompoundTag view(String mode){var v=new CompoundTag();v.putString("Mode",mode);return v;}
    static void button(CompoundTag v,String label,String command){var rows=v.getList("Actions",Tag.TAG_COMPOUND);var b=new CompoundTag();b.putString("Title",label);b.putString("Command",command);rows.add(b);v.put("Actions",rows);}
    /** 公开后按服务器游戏时间延迟投递；没有真实摘要，不根据研究标记猜测已公开。 */
    public static void refresh(ServerPlayer p){
        Hk3TeamContactService.ensure(p);UUID t=team(p);var contacts=Hk3TeamContactData.get(p.server);var d=Hk3DiplomacyData.get(p.server);
        if(contacts.settled(t))d.offer(t,"schicksal",contacts.state(t).equals("DECLINED"));
        if(contacts.available(t)&&!d.published(t).isEmpty()){
            for(var topic:Hk3DiplomacyData.TOPICS)if(d.due(t,topic.id(),p.server.overworld().getGameTime()))d.offer(t,topic.id(),false);
        }
        Hk3CommunicationDelivery.diplomacy(d,Hk3PhoneData.get(p.server),t,Hk3ResearchData.get(p).members(t),System.currentTimeMillis(),n->Hk3TeamContactService.announce(p.server,n));
    }
    public static void clearPreview(UUID actor){DRAFTS.remove(actor);}
    public static int home(ServerPlayer p){if(!allowed(p))return 0;refresh(p);DRAFTS.remove(p.getUUID());UUID t=team(p);var d=Hk3DiplomacyData.get(p.server);var v=view("diplomacy");
        v.putString("Title","五方联络");v.putString("Body","公开与提交均需预览确认。只发送选定批次，不公开设备位置、工厂布局或私人通信。");
        button(v,"奥托首信与个人补谈","hk3letter");
        button(v,d.published(t).isEmpty()?"预览公开稳定化成果":"回看已公开成果",PREFIX+" preview public publish");
        for(var topic:Hk3DiplomacyData.TOPICS)button(v,topic.name()+" · "+label(d.state(t,topic.id())),PREFIX+" topic "+topic.id());button(v,"联络记录与授权",PREFIX+" records");send(p,v);return 1;
    }
    private static String label(String state){return switch(state){case "OFFERED"->"待答复";case "ACCEPTED"->"待提交";case "DECLINED"->"已拒绝";case "COMPLETED"->"已反馈";default->"等待来信";};}
    public static int topic(ServerPlayer p,String id){if(!allowed(p))return 0;refresh(p);DRAFTS.remove(p.getUUID());var t=Hk3DiplomacyData.topic(id);if(t==null)return 0;UUID team=team(p);var d=Hk3DiplomacyData.get(p.server);String state=d.state(team,id);var v=view("diplomacy");v.putString("Title",t.name()+" · "+label(state));
        v.putString("Body",state.equals("LOCKED")?"先主动公开本队真实稳定化成果；确认公开后，逆熵、世界蛇、往世乐土、圣芙蕾雅学园依次在约30、60、90、120秒游戏运行时间来信。":"由队长或明确授权成员确认，普通队员可预览；回看不算个人亲历。");
        if(!state.equals("LOCKED"))button(v,"阅读来信",PREFIX+" read "+(d.documents(team).contains(t.first())?t.first():"A06"));
        if(state.equals("OFFERED")){button(v,"预览同意本主题",PREFIX+" preview "+id+" accept");button(v,"预览拒绝本主题",PREFIX+" preview "+id+" decline");}
        if(state.equals("ACCEPTED"))button(v,"预览真实批次摘要",PREFIX+" preview "+id+" submit");
        if(state.equals("DECLINED")){if(d.documents(team).contains(t.refused()))button(v,"回看拒绝回复",PREFIX+" read "+t.refused());button(v,"预览再次联系",PREFIX+" preview "+id+" retry");}
        if(state.equals("COMPLETED")){button(v,"阅读组织反馈",PREFIX+" read "+t.feedback());if(!d.submitted(team,id).isEmpty())button(v,"回看已提交的批次",PREFIX+" submitted "+id);}
        var path=d.personalPath(team,id);
        if(!path.isEmpty()){
            boolean done=Hk3PersonalCommunicationData.get(p.server).completedCurrent(p.getUUID(),team,id,d.version(team,id),path);
            button(v,done?"本段个人交流已完成":"亲自补行本段交流",PREFIX+" supplement "+id);
        }
        button(v,"返回五方联络",PREFIX);send(p,v);return 1;
    }
    private static CompoundTag evidence(ServerPlayer p,String topic){UUID t=team(p);var records=Hk3CommunicationEvidence.get(p.server);var r=new CompoundTag();
        if(topic.equals("public")||topic.equals("anti_entropy")){var proof=Hk3CommunicationEvidence.publicCopy(records.source(t,"stabilization"));if(!proof.isEmpty())r.put("稳定化",proof);}
        else if(topic.equals("schicksal")){var sample=Hk3CommunicationEvidence.publicCopy(records.source(t,"sampling"));var spectrum=Hk3CommunicationEvidence.publicCopy(records.source(t,"spectrum"));if(!sample.isEmpty()&&!spectrum.isEmpty()){r.put("首次采样",sample);r.put("光谱分析",spectrum);}}
        else if(topic.equals("world_serpent")){var research=Hk3ResearchData.get(p);var forming=Hk3CommunicationEvidence.publicCopy(research.processFactReceipt(t,"soulium_polymerization"));var annealing=Hk3CommunicationEvidence.publicCopy(research.processFactReceipt(t,"soulium_reconstruction"));if(!forming.isEmpty()&&!annealing.isEmpty()){r.put("魂钢成型",forming);r.put("重构退火",annealing);}}
        return r;
    }
    static String describe(CompoundTag proofs){var b=new StringBuilder();for(String k:new TreeSet<>(proofs.getAllKeys()))b.append("\n\n【").append(k).append("】\n").append(Hk3CommunicationEvidence.describe(proofs.getCompound(k)));return b.toString();}
    private static boolean validAction(String state,String action){return switch(action){case "accept","decline"->state.equals("OFFERED");case "retry"->state.equals("DECLINED");case "submit"->state.equals("ACCEPTED");default->false;};}
    public static int preview(ServerPlayer p,String id,String action){
        if(!allowed(p))return 0;refresh(p);DRAFTS.remove(p.getUUID());UUID team=team(p);var d=Hk3DiplomacyData.get(p.server);var t=Hk3DiplomacyData.topic(id);boolean publish=id.equals("public")&&action.equals("publish");
        if(!publish&&(t==null||!validAction(d.state(team,id),action)))return 0;
        var proof=publish||action.equals("submit")?evidence(p,id):new CompoundTag();
        if(publish&&!d.published(team).isEmpty())return show(p,"已公开的稳定化摘要",describe(d.published(team)),"",false);
        if((publish||action.equals("submit"))&&proof.isEmpty()){return show(p,"还缺少实际批次记录","请在本队设备上完成所需生产与实际输出。旧研究、库存物品和静态标记不能补造批次；输出受阻时不会取得记录。", "",false);}
        String doc=publish?"N19":switch(action){case "accept"->t.yes();case "decline"->t.no();case "retry"->t.retry();default->t.submit();};
        String body=prose(doc)+describe(proof)+"\n\n仅在确认后发送；关闭本页不作答复。";
        String token="";if(authorized(p,team)){UUID key=UUID.randomUUID();DRAFTS.put(p.getUUID(),new Draft(key,team,id,action,publish?0:d.version(team,id),proof.copy(),p.server.overworld().getGameTime()+12000));token=key.toString();}
        return show(p,title(doc),body,token,!authorized(p,team));
    }
    private static int show(ServerPlayer p,String title,String body,String token,boolean readonly){var v=view("diplomacy_read");v.putString("Title",title);v.putString("Body",body);v.putString("Token",token);v.putBoolean("ReadOnly",readonly);send(p,v);return 1;}
    public static int confirm(ServerPlayer p,String token){
        if(!allowed(p))return 0;refresh(p);UUID parsed;try{parsed=UUID.fromString(token);}catch(IllegalArgumentException bad){return 0;}
        if(!com.sirin.hk3gtl.common.easter.Hk3EggReading.consumeAction(p,token)){p.sendSystemMessage(Component.literal("请按顺序读完当前预览，再确认发送。"));return 0;}
        var draft=DRAFTS.remove(p.getUUID());
        if(draft==null||!draft.token.equals(parsed)||!draft.team.equals(team(p))||(p.server.overworld().getGameTime()>=draft.until||p.server.overworld().getGameTime()<draft.until-12000)||!authorized(p,draft.team)){p.sendSystemMessage(Component.literal("未发送：预览、团队或授权已变化，请重新打开。"));return home(p);}
        var d=Hk3DiplomacyData.get(p.server);boolean ok;
        if(draft.action.equals("publish")){
            var stable=draft.evidence.getCompound("稳定化");ok=!stable.isEmpty()&&d.publish(draft.team,p.getUUID(),true,draft.evidence,p.server.overworld().getGameTime());
        }else ok=d.apply(draft.team,draft.topic,draft.action,p.getUUID(),true,draft.version,draft.evidence);
        if(!ok){p.sendSystemMessage(Component.literal("主题已处理或状态改变，未重复发送。"));return home(p);}refresh(p);return home(p);
    }
    public static int read(ServerPlayer p,UUID origin,String id){
        if(!allowed(p))return 0;var d=Hk3DiplomacyData.get(p.server);if(!d.documents(origin).contains(id))return 0;
        if(!origin.equals(team(p))&&Hk3PhoneData.get(p).entry(p.getUUID(),"diplomacy_"+origin+"_"+id)==null)return 0;
        var v=view("diplomacy_read");v.putString("Title",title(id));v.putString("Body",prose("N22")+"\n\n"+historicalBody(d,origin,id));v.putString("Id","diplomacy_"+origin+"_"+id);
        if(origin.equals(team(p)))for(var topic:Hk3DiplomacyData.TOPICS)if(List.of(topic.first(),topic.yes(),topic.no(),topic.agreed(),topic.refused(),topic.submit(),topic.feedback(),topic.retry(),topic.resumed()).contains(id)){v.putString("Topic",topic.id());break;}
        send(p,v);return 1;
    }
    static String historicalBody(Hk3DiplomacyData data,UUID team,String doc){
        var text=new StringBuilder(prose(doc));
        if(doc.equals("N19"))text.append(describe(data.published(team)));
        for(var topic:Hk3DiplomacyData.TOPICS)if(!topic.submit().isEmpty()&&doc.equals(topic.submit()))text.append(describe(data.submitted(team,topic.id())));
        return text.toString();
    }
    private static int defer(ServerPlayer p){
        if(!allowed(p))return 0;clearPreview(p.getUUID());Hk3PersonalCommunicationService.clearPreview(p.getUUID());
        return show(p,title("N21"),prose("N21"),"",false);
    }
    public static com.mojang.brigadier.builder.LiteralArgumentBuilder<net.minecraft.commands.CommandSourceStack> commands(){
        return Commands.literal("diplomacy").executes(c->home(c.getSource().getPlayerOrException()))
            .then(Hk3CommunicationPages.commands())
            .then(Commands.literal("defer").executes(c->defer(c.getSource().getPlayerOrException())))
            .then(Commands.literal("topic").then(Commands.argument("id",StringArgumentType.word()).executes(c->topic(c.getSource().getPlayerOrException(),StringArgumentType.getString(c,"id")))))
            .then(Commands.literal("read").then(Commands.argument("id",StringArgumentType.word()).executes(c->{var p=c.getSource().getPlayerOrException();return read(p,team(p),StringArgumentType.getString(c,"id"));})))
            .then(Commands.literal("preview").then(Commands.argument("id",StringArgumentType.word()).then(Commands.argument("action",StringArgumentType.word()).executes(c->preview(c.getSource().getPlayerOrException(),StringArgumentType.getString(c,"id"),StringArgumentType.getString(c,"action"))))))
            .then(Commands.literal("confirm").then(Commands.argument("token",StringArgumentType.word()).executes(c->confirm(c.getSource().getPlayerOrException(),StringArgumentType.getString(c,"token")))))
            .then(Commands.literal("supplement").then(Commands.argument("id",StringArgumentType.word()).executes(c->Hk3PersonalCommunicationService.open(c.getSource().getPlayerOrException(),StringArgumentType.getString(c,"id")))))
            .then(Commands.literal("continue").then(Commands.argument("token",StringArgumentType.word()).executes(c->Hk3PersonalCommunicationService.advance(c.getSource().getPlayerOrException(),StringArgumentType.getString(c,"token")))))
            .then(Commands.literal("submitted").then(Commands.argument("id",StringArgumentType.word()).executes(c->{var p=c.getSource().getPlayerOrException();if(!allowed(p))return 0;var proof=Hk3DiplomacyData.get(p.server).submitted(team(p),StringArgumentType.getString(c,"id"));return proof.isEmpty()?0:show(p,"本队已提交批次",describe(proof),"",false);})));
    }
    @SubscribeEvent public static void tick(TickEvent.ServerTickEvent e){if(e.phase!=TickEvent.Phase.END)return;var s=net.minecraftforge.server.ServerLifecycleHooks.getCurrentServer();if(s==null||s.getTickCount()%100!=0)return;var teams=new HashSet<UUID>();for(var p:s.getPlayerList().getPlayers()){UUID current=team(p);Hk3PhoneData.get(p).resolveForeignDiplomacy(p.getUUID(),current);if(teams.add(current))refresh(p);}}
    @SubscribeEvent public static void logout(PlayerEvent.PlayerLoggedOutEvent e){DRAFTS.remove(e.getEntity().getUUID());}
    @SubscribeEvent public static void stop(ServerStoppedEvent e){DRAFTS.clear();}
}

// 【变更记录 · 修订161】2026-10-17 14:11:55：本轮仅将活动类名、资源与工业配方引用迁移为长期业务命名；历史备注保留，不代表旧逻辑已全部按现行设计重写。
