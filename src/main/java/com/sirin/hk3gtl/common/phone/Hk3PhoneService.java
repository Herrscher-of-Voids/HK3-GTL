package com.sirin.hk3gtl.common.phone;




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

@Mod.EventBusSubscriber(modid="hk3gtl")
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
                    .executes(c->showInbox(c.getSource().getPlayerOrException(),StringArgumentType.getString(c,"filter"),IntegerArgumentType.getInteger(c,"page"),StringArgumentType.getString(c,"query"),false))))))
            .then(Commands.literal("read_all").then(Commands.argument("filter",StringArgumentType.word())
                .then(Commands.argument("page",IntegerArgumentType.integer(0))
                    .executes(c->showInbox(c.getSource().getPlayerOrException(),StringArgumentType.getString(c,"filter"),IntegerArgumentType.getInteger(c,"page"),"",true))
                    .then(Commands.argument("query",StringArgumentType.greedyString())
                        .executes(c->showInbox(c.getSource().getPlayerOrException(),StringArgumentType.getString(c,"filter"),IntegerArgumentType.getInteger(c,"page"),StringArgumentType.getString(c,"query"),true))))))
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
    public static void send(ServerPlayer player,CompoundTag view){
        Hk3PhoneAppHints.view(player,view);
        com.sirin.hk3gtl.common.easter.Hk3EggReading.attach(player,view);
        if(!view.getString("Mode").equals("toast"))view.put("Runtime",Hk3PhoneRuntime.status(player));
        Hk3Network.CHANNEL.send(PacketDistributor.PLAYER.with(()->player),new Hk3PhonePacket(view));
    }
    public static int open(ServerPlayer player,String mode,int page,String filter){
        if(!installed(player))return 0;
        if(!mode.equals("home")&&!Hk3PhoneRuntime.requirePower(player))return 0;
        sendPage(player,mode,page,filter);
        com.sirin.hk3gtl.common.easter.Hk3EggPhone.opened(player,mode);
        return 1;
    }
    private static void sendPage(ServerPlayer player,String mode,int page,String filter){
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
        view.put("Rows",rows);send(player,view);
    }
    private static int showInbox(ServerPlayer player,String filter,int page,String query,boolean readAll){
        if(!installed(player)||!Hk3PhoneRuntime.requirePower(player)||query.length()>64)return 0;
        var data=Hk3PhoneData.get(player);var user=player.getUUID();
        if(readAll)data.readAll(user);
        if(query.isEmpty()){
            sendPage(player,"notifications",page,filter);
            return 1;
        }
        var all=data.search(user,filter,query,e->Hk3PhonePresentation.current(e,k->Component.translatable(k).getString()));page=Math.min(page,Math.max(0,(all.size()-1)/8));
        var v=new CompoundTag();v.putString("Mode","notifications");v.putString("Filter",filter);v.putString("Query",query);v.putInt("Page",page);v.putInt("Total",all.size());
        var rows=new ListTag();all.stream().skip(page*8L).limit(8).forEach(e->{var r=new CompoundTag();r.putString("Id",e.id());r.putString("Title",e.title());r.putString("Preview",e.body().replace("\n"," ").substring(0,Math.min(100,e.body().length())));r.putBoolean("Read",e.read());r.putBoolean("Pending",e.pending());rows.add(r);});
        v.put("Rows",rows);send(player,v);return 1;
    }
    private static int detail(ServerPlayer player,String id){
        if(!installed(player)||!Hk3PhoneRuntime.requirePower(player))return 0;
        var entry=Hk3PhonePresentation.current(Hk3PhoneData.get(player).entry(player.getUUID(),id),k->Component.translatable(k).getString());if(entry==null)return 0;
        if(entry.kind().equals("story")){
            String[] target=entry.target().split("/",2);
            return com.sirin.hk3gtl.common.narrative.story.Hk3StoryService.open(player,UUID.fromString(target[0]),target[1]);
        }
        if(entry.kind().equals("formal_archive"))return com.sirin.hk3gtl.common.narrative.Hk3LegacyArchiveService.open(player,entry.target());
        if(entry.kind().equals("progress_letter")){
            String[] target=entry.target().split("/",2);UUID origin=UUID.fromString(target[0]);
            return entry.id().startsWith("progress_reply_")?com.sirin.hk3gtl.common.communication.Hk3ProgressCorrespondence.feedback(player,origin,target[1]):com.sirin.hk3gtl.common.communication.Hk3ProgressCorrespondence.read(player,origin,target[1]);
        }
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

