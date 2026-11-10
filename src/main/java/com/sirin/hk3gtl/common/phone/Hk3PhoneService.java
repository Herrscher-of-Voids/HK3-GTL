package com.sirin.hk3gtl.common.phone;

/** 【变更记录 #10】2026-10-01 00:14:30（修订122）：删除无；新增/修改：收件箱按原团队和正文ID打开五方历史，不发任何合作奖励；用途：真实成果、团队授权与个人阅读分离，不开放贸易或免费完成研究。 */

/** 【变更记录 #9】2026-10-01 00:00:53（修订121）：删除无；新增/修改：跨队通知保留原队历史，禁止已收旧信打开新队同编号业务；用途：个人与团队记录隔离，保留历史与权限。 */

/** 【变更记录 #1】2026-09-29 18:57:18（内测5修订95）：快捷键同源命令、私人通知分页与已读校验；不接受客户端正文。 */
/** 【变更记录 #2】2026-09-29 19:19:27（内测5修订96）：删除免费打开入口；全部命令分支按服务器安装记录校验，通知入账仍可在安装前发生。 */

import com.mojang.brigadier.arguments.IntegerArgumentType;
import com.mojang.brigadier.arguments.StringArgumentType;
import com.sirin.hk3gtl.common.network.Hk3Network;
import com.sirin.hk3gtl.common.communication.Hk3FirstContactService;
import com.sirin.hk3gtl.common.research.*;
import net.minecraft.commands.Commands;
import net.minecraft.nbt.*;
import net.minecraft.network.chat.Component;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.level.ServerPlayer;
import net.minecraftforge.event.RegisterCommandsEvent;
import net.minecraftforge.event.entity.player.PlayerEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import net.minecraftforge.network.PacketDistributor;
import java.util.UUID;

/**
 * 【变更记录 #3】2026-09-30 16:17:42（内测5修订110）
 * 删除：被新版通知读取流程替代的旧分支，历史备注保留。
 * 新增／修改：增加八条过滤分页、本人正文读取与客户端打开确认；离线研究成果逐人入账，重连只汇总未读；手机安装资格保持。
 * 用途：通知与业务结果分离，服务端授权和个人持久化；不改结构、贴图和贸易。
 */
/**
 * 【变更记录 #4】2026-09-30 18:18:05（内测5修订112）
 * 删除：无；新增：权限2的纯消息验收命令与三条内置function入口。
 * 修改：测试不再修改真实研究/剧情；用途：免手动安装测试数据包，保留安装门槛。
 */
/**
 * 【变更记录 #5】2026-09-30 18:44:46（内测5修订113）
 * 删除：无；新增：手机状态同步和AE终端入口。
 * 修改：信箱读取需实体电量，首页可显示缺电引导；用途：右键/快捷键同源且保留已安装资格。
 */
/** 【变更记录 #11】2026-10-01 00:59:10（修订124）：删除无；新增/修改：共用通信投递完成后只发送在线提示，不重复入箱；用途：按五方交流系统整链收口，真实权限和本人经历不混用。 */
@Mod.EventBusSubscriber(modid="hk3gtl")
/**
 * 【变更记录 #6】2026-09-30 19:08:08（内测5修订114）
 * 删除：无；新增应用命令和本人信箱搜索；修改分页附带短摘要，共用带电量的响应发送。
 * 用途：手机应用集成，保留既有电量和阅读权限；交易只展示不结算。
 */
/** 【变更记录 #7】2026-09-30 19:20:11（内测5修订115）：删除无；新增服务器校验的背包终端槽位命令；修改AE入口支持选择；用途：打开玩家持有的实体终端。 */
/** 【变更记录 #8】2026-09-30 19:49:34（修订116）：删除无；新增微讯息接入；修改：注册社交与管理员只读预览命令；用途：保留原手机布局与权限，AI不进入服务器业务。 */
/** 【变更记录 #12】2026-10-01 01:57:59（修订127）：删除：被替代的旧分支；新增/修改：收件箱旧消息回看也使用同源分类与完整条件，不覆盖原投递快照或阅读状态；用途：个人收藏与正式资格分离，保留历史记录。 */
/** 【变更记录 #13】2026-10-01 04:19:02（修订128）：删除：旧固定上限或被替代的分支；新增/修改：向真实阅读正文附加独立会话，已读状态不再当成彩蛋全文读完；用途：已审核彩蛋独立执行，不授研究或审查资格。 */
/** 【变更记录 #14】2026-10-01 04:27:55（修订128）：删除：旧固定上限或被替代的分支；新增/修改：已授权首页与通知视图记录实际打开状态，节日使用服务器时区；用途：已审核彩蛋独立执行，不授研究或审查资格。 */
/** 【变更记录 #15】2026-10-01 22:50:14（第15次备注 · 内测5修订155）：删除玩家展示中的旧电压及开发说明；新增现行正文投影或对应回归；修改仅限呈现与检索，不改变进度、回执、触发条件或权限；用途：统一发布版玩家文案，历史备注保留。 */
/** 【变更记录 #16】2026-11-04 06:12:15（第16次备注 · 内测5修订196）：删除无；新增新版正式档案通知路由；修改仅正式独立消息进入准确来源/本人全文服务；用途：保留历史收件箱与手机供电，旧已读不授正式经历。 */
public final class Hk3PhoneService {
    private Hk3PhoneService(){}
    @SubscribeEvent public static void commands(RegisterCommandsEvent e){
        var inbox=Commands.literal("notifications").executes(c->open(c.getSource().getPlayerOrException(),"notifications",0,"all"))
            .then(Commands.argument("page",IntegerArgumentType.integer(0)).executes(c->open(c.getSource().getPlayerOrException(),"notifications",IntegerArgumentType.getInteger(c,"page"),"all")));
        for(String filter:new String[]{"all","unread","pending"})inbox.then(Commands.literal(filter)
            .executes(c->open(c.getSource().getPlayerOrException(),"notifications",0,filter))
            .then(Commands.argument("page",IntegerArgumentType.integer(0)).executes(c->open(c.getSource().getPlayerOrException(),"notifications",IntegerArgumentType.getInteger(c,"page"),filter))));
        e.getDispatcher().register(Commands.literal("hk3phone").executes(c->open(c.getSource().getPlayerOrException(),"home",0))
            .then(inbox)
            .then(Hk3PhoneAppService.commands())
            .then(Hk3SocialService.commands())
            .then(Commands.literal("search").then(Commands.argument("filter",StringArgumentType.word())
                .then(Commands.argument("page",IntegerArgumentType.integer(0)).then(Commands.argument("query",StringArgumentType.greedyString())
                    .executes(c->search(c.getSource().getPlayerOrException(),StringArgumentType.getString(c,"filter"),IntegerArgumentType.getInteger(c,"page"),StringArgumentType.getString(c,"query")))))))
            .then(Commands.literal("status").executes(c->Hk3PhoneRuntime.poll(c.getSource().getPlayerOrException())))
            .then(Commands.literal("ae").executes(c->Hk3PhoneRuntime.openAe(c.getSource().getPlayerOrException()))
                .then(Commands.argument("slot",IntegerArgumentType.integer(0,40)).executes(c->Hk3PhoneRuntime.openAe(c.getSource().getPlayerOrException(),IntegerArgumentType.getInteger(c,"slot")))))
            .then(Commands.literal("test").requires(c->c.hasPermission(2))
                .then(Commands.argument("batch",StringArgumentType.word()).suggests((c,b)->net.minecraft.commands.SharedSuggestionProvider.suggest(java.util.List.of("research_pair","burst","history_more"),b))
                    .executes(c->testMessages(c.getSource().getPlayerOrException(),StringArgumentType.getString(c,"batch")))))
            .then(Commands.literal("message").then(Commands.argument("id",StringArgumentType.word()).executes(c->detail(c.getSource().getPlayerOrException(),StringArgumentType.getString(c,"id")))))
            .then(Commands.literal("seen").then(Commands.argument("id",StringArgumentType.word()).executes(c->{
                var player=c.getSource().getPlayerOrException();var data=Hk3PhoneData.get(player);
                String id=StringArgumentType.getString(c,"id");var entry=data.entry(player.getUUID(),id);
                if(entry==null||(!data.installed(player.getUUID())&&!entry.kind().equals("letter")))return 0;
                data.read(player.getUUID(),id);return 1;
            })))
            .then(Commands.literal("read").then(Commands.argument("id",StringArgumentType.word())
                .then(Commands.argument("page",IntegerArgumentType.integer(0)).executes(c->detail(c.getSource().getPlayerOrException(),StringArgumentType.getString(c,"id")))))));
    }
    private static int testMessages(ServerPlayer player,String batch){
        if(!installed(player))return 0;
        var messages=Hk3PhoneTestMessages.batch(batch);
        if(messages.isEmpty())return 0;
        for(var message:messages)notify(player,message.id(),message.title(),message.body(),message.kind());
        player.sendSystemMessage(Component.literal("界面测试消息已提交："+messages.size()+" 条；相同批次重复执行不重复入箱。未改动研究或剧情。"));
        return messages.size();
    }
    public static int open(ServerPlayer player,String mode,int page){return open(player,mode,page,"all");}
    private static boolean installed(ServerPlayer player){
        if(Hk3PhoneData.get(player).installed(player.getUUID()))return true;
        player.sendSystemMessage(Component.literal("需要先制作并安装 HK3GTL 通讯终端。"));return false;
    }
    static void send(ServerPlayer player,CompoundTag view){
        Hk3PhoneAppHints.view(player,view);
        com.sirin.hk3gtl.common.easter.Hk3EggReading.attach(player,view);
        if(!view.getString("Mode").equals("toast"))view.put("Runtime",Hk3PhoneRuntime.status(player));
        Hk3Network.CHANNEL.send(PacketDistributor.PLAYER.with(()->player),new Hk3PhonePacket(view));
    }
    public static int open(ServerPlayer player,String mode,int page,String filter){
        if(!installed(player))return 0;
        if(!mode.equals("home")&&!Hk3PhoneRuntime.requirePower(player))return 0;
        var data=Hk3PhoneData.get(player);var view=new CompoundTag();int total=data.count(player.getUUID(),filter);
        page=Math.max(0,Math.min(page,Math.max(0,(total-1)/8)));
        view.putString("Mode",mode);view.putString("Filter",filter);view.putInt("Page",page);view.putInt("Total",total);
        view.putInt("Unread",data.unread(player.getUUID()));var rows=new ListTag();
        if(mode.equals("notifications"))for(var stored:data.page(player.getUUID(),page,filter)){
            var entry=Hk3PhonePresentation.current(stored,k->Component.translatable(k).getString());
            var row=new CompoundTag();row.putString("Id",entry.id());row.putString("Title",entry.title());
            row.putString("Preview",entry.body().replace("\n"," ").substring(0,Math.min(100,entry.body().length())));row.putLong("Time",entry.time());
            row.putBoolean("Read",entry.read());row.putBoolean("Pending",entry.pending());row.putString("Kind",entry.kind());rows.add(row);
        }
        view.put("Rows",rows);send(player,view);com.sirin.hk3gtl.common.easter.Hk3EggPhone.opened(player,mode);return 1;
    }
    private static int search(ServerPlayer player,String filter,int page,String query){
        if(!installed(player)||!Hk3PhoneRuntime.requirePower(player)||query.length()>64)return 0;
        var all=Hk3PhoneData.get(player).search(player.getUUID(),filter,query,e->Hk3PhonePresentation.current(e,k->Component.translatable(k).getString()));page=Math.min(page,Math.max(0,(all.size()-1)/8));
        var v=new CompoundTag();v.putString("Mode","notifications");v.putString("Filter",filter);v.putString("Query",query);v.putInt("Page",page);v.putInt("Total",all.size());
        var rows=new ListTag();all.stream().skip(page*8L).limit(8).forEach(e->{var r=new CompoundTag();r.putString("Id",e.id());r.putString("Title",e.title());r.putString("Preview",e.body().replace("\n"," ").substring(0,Math.min(100,e.body().length())));r.putBoolean("Read",e.read());r.putBoolean("Pending",e.pending());rows.add(r);});
        v.put("Rows",rows);send(player,v);return 1;
    }
    private static int detail(ServerPlayer player,String id){
        if(!installed(player)||!Hk3PhoneRuntime.requirePower(player))return 0;
        var entry=Hk3PhonePresentation.current(Hk3PhoneData.get(player).entry(player.getUUID(),id),k->Component.translatable(k).getString());if(entry==null)return 0;
        if(entry.kind().equals("formal_archive"))return com.sirin.hk3gtl.common.narrative.Hk3LegacyArchiveService.open(player,entry.target());
        if(entry.kind().equals("diplomacy")){
            String[] target=entry.target().split("/",2);if(target.length!=2)return 0;
            try{return com.sirin.hk3gtl.common.communication.Hk3DiplomacyService.read(player,UUID.fromString(target[0]),target[1]);}catch(IllegalArgumentException bad){return 0;}
        }
        if(entry.kind().equals("letter")){
            try{
                int document=Integer.parseInt(entry.target());String prefix=entry.id().startsWith("contact_reply_")?"contact_reply_":entry.id().startsWith("contact_")?"contact_":"";
                if(!prefix.isEmpty()){
                    UUID original=UUID.fromString(entry.id().substring(prefix.length()));
                    if(!original.equals(Hk3ResearchTeams.scope(player.server,player.getUUID())))return com.sirin.hk3gtl.common.communication.Hk3TeamContactService.history(player,original,document);
                }
                return Hk3FirstContactService.open(player,document);
            }catch(IllegalArgumentException ignored){return 0;}
        }
        var view=new CompoundTag();view.putString("Mode","detail");view.putString("Id",entry.id());view.putString("Title",entry.title());
        String body=entry.body();
        view.putString("Body",body);view.putBoolean("Pending",entry.pending());send(player,view);return 1;
    }
    /** 仅持久化投递，允许离线接收人；在线时附带短通知，不触发研究或奖励。 */
    public static void deliver(MinecraftServer server,UUID recipient,String id,String title,String body,String kind,String target,boolean pending){
        var data=Hk3PhoneData.get(server);
        if(!data.add(recipient,id,title,body,System.currentTimeMillis(),kind,target,pending))return;
        var player=server.getPlayerList().getPlayer(recipient);if(player==null)return;
        toast(player,id,title,body,kind,pending?2:kind.equals("chatter")?0:1);
    }
    public static void toast(ServerPlayer player,String id,String title,String body,String kind,int priority){
        var current=Hk3PhonePresentation.current(new Hk3PhoneData.Entry(id,title,body,0,false,kind,"",false),k->Component.translatable(k).getString());
        title=current.title();body=current.body();
        var view=new CompoundTag();view.putString("Mode","toast");view.putString("Id",id);view.putString("Title",title);
        view.putString("Body",body.length()>240?body.substring(0,240):body);view.putString("Kind",kind);view.putInt("Priority",priority);
        view.putBoolean("Installed",Hk3PhoneData.get(player).installed(player.getUUID()));send(player,view);
    }
    public static void notify(ServerPlayer player,String id,String title,String body){notify(player,id,title,body,"notice");}
    public static void notify(ServerPlayer player,String id,String title,String body,String kind){
        deliver(player.server,player.getUUID(),id,title,body,kind,"",false);
    }
    public static void letter(ServerPlayer player,String id,String title,String body,int document,boolean pending){
        deliver(player.server,player.getUUID(),id,title,body,"letter",Integer.toString(document),pending);
    }
    public static void researchCompleted(MinecraftServer server,UUID team,String task){
        var experiment=Hk3LabExperimentRules.get(task);String topic=experiment==null?task:experiment.research();
        var plan=Hk3ResearchPlans.get(topic);if(plan==null)return;
        String name=Component.translatable(plan.nameKey()).getString();
        String title=experiment==null?"研究完成｜"+name:experiment.baseline()?"对照基线已记录｜"+name:"实验记录已取得｜"+name;
        String body=experiment==null?"已开放："+plan.result()+"\n\n"+Hk3ResearchStory.get(topic):
            experiment.baseline()?"普通演算基线已保存。继续完成辅助运行，取得完整实验凭据。":
            "实验成果已记入团队档案。请带上实验凭据与所需材料，继续完成对应课题。";
        for(UUID user:Hk3ResearchData.get(server).members(team))
            deliver(server,user,"research_"+team+"_"+task,title,body,experiment==null?"research":"experiment",topic,false);
    }
    @SubscribeEvent public static void login(PlayerEvent.PlayerLoggedInEvent event){
        if(!(event.getEntity() instanceof ServerPlayer player))return;
        Hk3PhoneRuntime.migrate(player);
        var state=com.sirin.hk3gtl.common.communication.Hk3CommunicationData.get(player).state(player.getUUID());
        if(state==com.sirin.hk3gtl.common.communication.Hk3FirstContactState.ACCEPTED
                ||state==com.sirin.hk3gtl.common.communication.Hk3FirstContactState.DECLINED)
            Hk3PhoneData.get(player).resolve(player.getUUID(),"first_contact_letter");
        int count=Hk3PhoneData.get(player).unread(player.getUUID());
        if(count>0)toast(player,"session_unread","收件箱有 "+count+" 条未读消息","历史正文和待处理事项已保留，可打开消息中心查看。","notice",2);
    }
}

// 【变更记录 · 修订161】2026-10-17 14:11:55：本轮仅将活动类名、资源与工业配方引用迁移为长期业务命名；历史备注保留，不代表旧逻辑已全部按现行设计重写。
