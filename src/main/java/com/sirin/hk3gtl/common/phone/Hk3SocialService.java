package com.sirin.hk3gtl.common.phone;

import com.mojang.brigadier.builder.LiteralArgumentBuilder;
import com.sirin.hk3gtl.common.communication.Hk3CommunicationData;
import net.minecraft.commands.*;
import net.minecraft.nbt.*;
import net.minecraft.server.level.ServerPlayer;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;

@Mod.EventBusSubscriber(modid="hk3gtl")
public final class Hk3SocialService {
    private Hk3SocialService(){}
    public static LiteralArgumentBuilder<CommandSourceStack> commands(){return Commands.literal("social").executes(c->open(c.getSource().getPlayerOrException(),false))
        .then(Commands.literal("preview").requires(c->c.hasPermission(2)).executes(c->open(c.getSource().getPlayerOrException(),true)));}
    public static int stage(ServerPlayer p){
        var d=Hk3SocialData.get(p);int s=d.stage(p.getUUID());if(Hk3CommunicationData.get(p).state(p.getUUID()).hasObservationData())s=Math.max(1,s);
        if(s>=3&&com.sirin.hk3gtl.common.event.Hk3EventService.hasTriggered(p,"E-HQ-005"))s=4;return s;
    }
    /** 后续一审/二审真实结算应分别调用2/3；目前不从阅读/持有物推断通过。 */
    public static void reviewCompleted(ServerPlayer p,int stage){if(stage==2||stage==3||stage==4)Hk3SocialData.get(p).advance(p.getUUID(),stage);}
    private static boolean usable(ServerPlayer p){return Hk3PhoneData.get(p).installed(p.getUUID())&&Hk3PhoneRuntime.requirePower(p);}
    public static int open(ServerPlayer p,boolean preview){handle(p,new Hk3SocialPacket("list","","",preview));return 1;}
    public static void handle(ServerPlayer p,Hk3SocialPacket packet){
        if(!usable(p)||packet.preview()&&!p.hasPermissions(2))return;
        if(packet.action().equals("enable_ai")||packet.action().equals("disable_ai")){
            if(!packet.preview()){var state=com.sirin.hk3gtl.common.easter.Hk3EggRuntime.state(p);if(packet.action().equals("enable_ai")){state.putBoolean("socialAiEnabled",true);state.remove("socialAiDisabled");}else if(state.getBoolean("socialAiEnabled")){state.remove("socialAiEnabled");state.putBoolean("socialAiDisabled",true);}}return;
        }
        if(packet.action().equals("topics")||packet.action().equals("welcome")){
            if(!packet.preview()){if(packet.action().equals("topics"))Hk3SocialBuiltinTopics.menu(p,packet.contact());else Hk3SocialBuiltinTopics.welcome(p,packet.contact());}return;
        }
        boolean builtin=packet.action().equals("topic"),sent=false;
        if(builtin){if(packet.preview()||Hk3SocialBuiltinTopics.topic(packet.contact(),packet.text())==null)return;packet=new Hk3SocialPacket("send",packet.contact(),packet.text(),false);}
        boolean preview=packet.preview();int stage=stage(p);var data=Hk3SocialData.get(p);var v=new CompoundTag();v.putBoolean("Preview",preview);v.putInt("Stage",stage);
        var rows=new ListTag();String action=packet.action();var c=Hk3SocialCatalog.get(packet.contact());
        if(action.equals("list")){
            v.putString("Mode","social");for(var item:Hk3SocialCatalog.all())if(preview||item.available(stage)||!data.history(p.getUUID(),item.id()).isEmpty()){
                var n=new CompoundTag();n.putString("Id",item.id());n.putString("Name",item.name());n.putBoolean("Active",preview||item.available(stage));rows.add(n);
            }
        }else if(action.equals("feed")||action.equals("like")){
            if(!preview){data.publish(p.getUUID(),stage,p.server.overworld().getGameTime());if(action.equals("like"))data.like(p.getUUID(),packet.contact());}
            v.putString("Mode","social_feed");rows=data.feed(p.getUUID());
        }else if((action.equals("chat")||action.equals("send"))&&c!=null){
            boolean active=preview||c.available(stage);var old=data.history(p.getUUID(),c.id());if(!active&&old.isEmpty())return;
            if(action.equals("send")&&active&&!preview&&Hk3SocialCatalog.validInput(packet.text())){
                long now=p.server.overworld().getGameTime();var persistent=p.getPersistentData();long last=persistent.getLong("hk3_social_last");
                if(persistent.contains("hk3_social_last")&&now>=last&&now-last<20)v.putString("Status","消息发送太快，请稍候一秒再发送。");
                else{
                    persistent.putLong("hk3_social_last",now);
                    var eggState=com.sirin.hk3gtl.common.easter.Hk3EggRuntime.state(p);
                    if(eggState.getBoolean("deathFirstMessage")){if(c.id().equals("V10"))com.sirin.hk3gtl.common.easter.Hk3EggVanilla.caseEvent(p,120);eggState.remove("deathFirstMessage");}
                    long time=p.level().getDayTime();boolean raining=p.level().isRainingAt(p.blockPosition());
                    int rotation=data.nextReply(p.getUUID(),c.id(),Hk3SocialCatalog.topic(packet.text(),time,raining));
                    var reply=c.reply(packet.text(),time,raining,rotation);
                    data.append(p.getUUID(),c.id(),"我",packet.text(),"player",now);data.append(p.getUUID(),c.id(),c.name(),c.finish(reply.text()),reply.source(),now);v.putString("Accepted",packet.text());sent=true;
                    com.sirin.hk3gtl.common.easter.Hk3EggRuntime.observe(p,"social_sent",com.sirin.hk3gtl.common.easter.Hk3EggRuntime.fields(
                        "contact",c.id(),"note20",Boolean.toString(com.sirin.hk3gtl.common.easter.Hk3EggRuntime.state(p).getBoolean("note20")),
                        "high_overworld",Boolean.toString(p.level().dimension()==net.minecraft.world.level.Level.OVERWORLD&&p.getY()>p.level().getSeaLevel()+64)));

                }
            }
            v.putString("Mode","social_chat");v.putString("Contact",c.id());v.putString("Name",c.name());v.putBoolean("Active",active&&!preview);
            if(!preview&&active&&action.equals("chat")&&(c.id().equals("V11")||c.id().equals("V12")))com.sirin.hk3gtl.common.easter.Hk3EggVanilla.caseEvent(p,419);
            rows=preview?new ListTag():data.history(p.getUUID(),c.id());
            if(preview)for(var l:c.lines()){var n=new CompoundTag();n.putString("Who",c.name());n.putString("Body",l.text());rows.add(n);}
        }else return;
        v.put("Rows",rows);Hk3PhoneService.send(p,v);
        if(builtin&&sent)Hk3SocialBuiltinTopics.replied(p,packet.contact(),packet.text());
    }
    @SubscribeEvent public static void tick(TickEvent.PlayerTickEvent e){
        if(e.phase!=TickEvent.Phase.END||!(e.player instanceof ServerPlayer p)||p.tickCount%1200!=0)return;
        if(!Hk3PhoneData.get(p).installed(p.getUUID()))return;
        if(Hk3SocialData.get(p).publish(p.getUUID(),stage(p),p.server.overworld().getGameTime()))
            Hk3PhoneService.notify(p,"social_feed_"+Math.floorDiv(p.server.overworld().getGameTime(),24000),"微讯息 · 朋友圈","联系人更新了动态，可在微讯息中查看。","chatter");
    }
}
