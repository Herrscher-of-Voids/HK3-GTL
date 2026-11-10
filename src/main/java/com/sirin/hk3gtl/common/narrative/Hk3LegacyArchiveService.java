package com.sirin.hk3gtl.common.narrative;

import com.sirin.hk3gtl.common.communication.*;
import com.sirin.hk3gtl.common.easter.*;
import com.sirin.hk3gtl.common.finale.Hk3FinaleRequirements.State;
import com.sirin.hk3gtl.common.phone.*;
import com.sirin.hk3gtl.common.research.*;
import com.sirin.hk3gtl.common.review.*;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.level.ServerPlayer;
import net.minecraftforge.event.entity.player.PlayerEvent;
import net.minecraftforge.event.server.ServerStoppedEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import java.util.*;

/**
 * 【变更记录 #1】2026-11-04 06:12:15（第1次备注 · 内测5修订196）
 * 删除：无；新增：正式新版档案补投递、本人全文会话及完成回执服务。
 * 修改：复用原手机和连续分片阅读，不增加研究/赠物/许可；用途：准确来源、原队、正文与令牌全程绑定，离线漏投可补，换队或断线未完会话作废。
 */
@Mod.EventBusSubscriber(modid="hk3gtl")
public final class Hk3LegacyArchiveService {
    private record Pending(MinecraftServer server,UUID scope,String event,String hash,UUID token,String action,long expires) {}
    private static final Map<UUID,Pending> ACTIVE=new HashMap<>();
    private Hk3LegacyArchiveService() {}
    public static String messageId(Hk3LegacyArchiveMigration.Rule rule) {return "formal_"+rule.eventId()+"_"+rule.fingerprint();}
    private static UUID scope(ServerPlayer p){return Hk3ResearchTeams.scope(p.server,p.getUUID());}
    private static java.util.function.Function<Hk3LegacyArchiveMigration.Rule,com.sirin.hk3gtl.common.finale.Hk3FinaleRequirements.Fact> sources(ServerPlayer p) {
        UUID team=scope(p);var research=Hk3ResearchData.get(p);var contacts=Hk3TeamContactData.get(p.server);
        var personal=Hk3PersonalCommunicationData.get(p.server);var reviews=Hk3ReviewData.get(p.server).snapshot();
        return rule->Hk3LegacyArchiveMigration.prerequisite(rule,id->research.completed(team,id),contacts,personal,reviews,p.getUUID());
    }
    private static com.sirin.hk3gtl.common.finale.Hk3FinaleRequirements.Fact prerequisite(ServerPlayer p,Hk3LegacyArchiveMigration.Rule rule) {
        return sources(p).apply(rule);
    }
    /** 只读实际来源，供手机和卷轴决定能否呈现现行事实正文；不投递、不登记阅读。 */
    public static boolean available(ServerPlayer p,String event) {
        var rule=Hk3LegacyArchiveMigration.all().get(event);
        return rule!=null&&(Hk3LegacyArchiveData.get(p.server).experienced(p.getUUID(),rule)||prerequisite(p,rule).state()==State.COMPLETE);
    }
    /** 只投递已具备准确来源或已完成本人阅读的记录；登录、轮询可补回漏投，不调用旧事件奖励链。 */
    public static void ensure(ServerPlayer p) {
        var pending=ACTIVE.get(p.getUUID());
        if(pending!=null&&(pending.server()!=p.server||!pending.scope().equals(scope(p))||p.server.overworld().getGameTime()>=pending.expires()))ACTIVE.remove(p.getUUID());
        var readings=Hk3LegacyArchiveData.get(p.server);
        var source=sources(p);
        for(var rule:Hk3LegacyArchiveMigration.all().values()) {
            if(!readings.experienced(p.getUUID(),rule)&&source.apply(rule).state()!=State.COMPLETE)continue;
            boolean pendingRead=rule.kind()==Hk3LegacyArchiveMigration.SourceKind.RESEARCH&&!readings.experienced(p.getUUID(),rule);
            Hk3PhoneService.deliver(p.server,p.getUUID(),messageId(rule),rule.title(),rule.body(),"formal_archive",rule.eventId(),pendingRead);
            if(!pendingRead)unlockCollection(p,rule);
        }
    }
    /** 正文打开只创建临时阅读会话；安装与电量沿用手机规则，源不足和未知ID不发包。 */
    public static int open(ServerPlayer p,String eventId) {
        var rule=Hk3LegacyArchiveMigration.all().get(eventId);
        if(rule==null||!Hk3PhoneData.get(p).installed(p.getUUID())||!Hk3PhoneRuntime.requirePower(p))return 0;
        if(!available(p,eventId))return 0;
        var view=new CompoundTag();String action=UUID.randomUUID().toString();
        view.putString("Mode","detail");view.putString("Id",messageId(rule));view.putString("Title",rule.title());view.putString("Body",rule.body());
        view.putString("Token",action);view.put("Runtime",Hk3PhoneRuntime.status(p));
        Hk3EggReading.attach(p,view);
        if(!view.hasUUID("ReadToken"))return 0;
        ACTIVE.put(p.getUUID(),new Pending(p.server,scope(p),eventId,rule.fingerprint(),view.getUUID("ReadToken"),action,p.server.overworld().getGameTime()+36000));
        com.sirin.hk3gtl.common.network.Hk3Network.CHANNEL.send(net.minecraftforge.network.PacketDistributor.PLAYER.with(()->p),new Hk3PhonePacket(view));
        return 1;
    }
    /** 仅共享阅读器实际连续读完的当前会话可提交；结束时重核队伍、准确来源及新版指纹。 */
    public static boolean readCompleted(ServerPlayer p,Hk3ReadingSessions.Session session) {
        var pending=ACTIVE.remove(p.getUUID());
        if(pending==null||pending.server()!=p.server||!pending.scope().equals(scope(p))||!pending.token().equals(session.token())
                ||!pending.action().equals(session.action())||!session.cursor().done()
                ||p.server.overworld().getGameTime()>=pending.expires())return false;
        var rule=Hk3LegacyArchiveMigration.all().get(pending.event());
        if(rule==null||!rule.fingerprint().equals(pending.hash())||!messageId(rule).equals(session.id()))return false;
        if(rule.kind()!=Hk3LegacyArchiveMigration.SourceKind.RESEARCH)return prerequisite(p,rule).state()==State.COMPLETE;
        var data=Hk3LegacyArchiveData.get(p.server);
        if(data.experienced(p.getUUID(),rule))return true;
        var source=prerequisite(p,rule);if(source.state()!=State.COMPLETE)return false;
        var proof=source.source();proof.putUUID("Scope",pending.scope());
        var needed=new TreeSet<String>();ancestors(rule.source(),needed);
        var completed=Hk3ResearchData.get(p).save(new CompoundTag()).getCompound("Accounts")
            .getCompound(pending.scope().toString()).getList("Completed",net.minecraft.nbt.Tag.TAG_STRING);
        var actual=new HashSet<String>();completed.forEach(tag->actual.add(tag.getAsString()));
        if(!actual.containsAll(needed))return false;
        var researchProof=new CompoundTag();researchProof.putUUID("Scope",pending.scope());researchProof.putString("Research",rule.source());
        var observed=new net.minecraft.nbt.ListTag();needed.forEach(id->observed.add(net.minecraft.nbt.StringTag.valueOf(id)));
        researchProof.put("Completed",observed);proof.put("ResearchProof",researchProof);
        boolean recorded=data.record(p.getUUID(),pending.scope(),rule,session.token(),p.server.overworld().getGameTime(),session.cursor().pages(),proof);
        if(recorded){Hk3PhoneData.get(p).resolve(p.getUUID(),messageId(rule));unlockCollection(p,rule);}
        return recorded;
    }
    private static void ancestors(String id,Set<String> result) {
        if(!result.add(id))return;
        for(String parent:Hk3ResearchCatalog.bundled().get(id).prerequisites())ancestors(parent,result);
    }
    private static void unlockCollection(ServerPlayer p,Hk3LegacyArchiveMigration.Rule rule) {
        for(var node:Hk3NarrativeNodes.byEventIdAll(rule.eventId()))Hk3NarrativeLog.unlock(p,node.id());
    }
    public static void clear(UUID actor){ACTIVE.remove(actor);}
    @SubscribeEvent public static void login(PlayerEvent.PlayerLoggedInEvent e){if(e.getEntity() instanceof ServerPlayer p)ensure(p);}
    @SubscribeEvent public static void tick(net.minecraftforge.event.TickEvent.PlayerTickEvent e){
        if(e.phase==net.minecraftforge.event.TickEvent.Phase.END&&e.player instanceof ServerPlayer p) {
            var pending=ACTIVE.get(p.getUUID());if(pending!=null&&!pending.scope().equals(scope(p)))clear(p.getUUID());
            if(p.tickCount%100==0)ensure(p);
        }
    }
    @SubscribeEvent public static void logout(PlayerEvent.PlayerLoggedOutEvent e){clear(e.getEntity().getUUID());}
    @SubscribeEvent public static void stopped(ServerStoppedEvent e){ACTIVE.clear();}
}
