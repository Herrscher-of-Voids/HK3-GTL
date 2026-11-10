package com.sirin.hk3gtl.common.communication;

/** 【变更记录 #5】2026-10-31 02:01:05（第5次备注 · 修订187）：删除无；新增可核验的个人补谈原文组装入口；修改复用已批准资源正文；用途：与团队预览使用相同中文原文，不依赖专服语言表。 */

/** 【变更记录 #4】2026-10-31 01:06:22（第4次备注 · 修订187）：删除失效预览无反馈分支；新增无；修改消费失败返回联络首页；用途：避免个人补谈旧页停留。 */

/** 【变更记录 #3】2026-10-31 00:46:39（第3次备注 · 修订187）：删除仅持预览令牌即可推进的路径；新增全读校验；修改未读时保留待处理页；用途：补谈不能跳读或重复结算。 */

import com.sirin.hk3gtl.common.phone.*;
import com.sirin.hk3gtl.common.research.*;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerPlayer;
import net.minecraftforge.event.entity.player.PlayerEvent;
import net.minecraftforge.event.server.ServerStoppedEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import java.util.*;

/**
 * 【变更记录 #1】2026-10-01 00:41:04（修订123）
 * 删除：无；新增：五方补谈逐篇预览、本人确认与断线恢复。
 * 修改：仅复用已有已发生分支正文，普通读信不产生个人完成回执。
 * 用途：每人一个临时令牌，服务端复核队伍、主题版本及检查点；不调用团队结算和奖励接口。
 */
/** 【变更记录 #2】2026-10-01 00:59:10（修订124）：删除无；新增/修改：补谈展示当时已提交的固定脱敏摘要；离队及时清令牌并拒绝时钟回退；用途：按五方交流系统整链收口，真实权限和本人经历不混用。 */
@Mod.EventBusSubscriber(modid="hk3gtl")
public final class Hk3PersonalCommunicationService {
    private record Preview(UUID token, UUID team, String topic, UUID attempt, int version, int step, long expires) {}
    private static final Map<UUID,Preview> PREVIEWS = new java.util.concurrent.ConcurrentHashMap<>();
    private Hk3PersonalCommunicationService() {}
    public static void clearPreview(UUID actor){PREVIEWS.remove(actor);}
    private static boolean allowed(ServerPlayer player) {
        return Hk3PhoneData.get(player).installed(player.getUUID()) && Hk3PhoneRuntime.requirePower(player);
    }
    public static int open(ServerPlayer player, String topic) {
        if (!allowed(player)) return 0;
        PREVIEWS.remove(player.getUUID()); Hk3DiplomacyService.refresh(player);
        UUID team = Hk3ResearchTeams.scope(player.server, player.getUUID());
        var diplomacy = Hk3DiplomacyData.get(player.server); var path = diplomacy.personalPath(team, topic);
        if (path.isEmpty()) {
            player.sendSystemMessage(Component.literal("本主题尚无可补谈的完整路线；团队须先完成答复及该路线要求的真实提交。")); return 0;
        }
        var data = Hk3PersonalCommunicationData.get(player.server);
        if (!data.begin(player.getUUID(), team, topic, diplomacy.version(team, topic), path,
                Hk3ResearchData.get(player).isMember(player.getUUID(), team))) {
            player.sendSystemMessage(Component.literal("补谈记录或成员身份异常，保留原记录，请重新进入或联系管理员核查。")); return 0;
        }
        var n = data.snapshot(player.getUUID(), team, topic);
        if (Hk3PersonalCommunicationData.complete(n)) {
            player.sendSystemMessage(Component.literal("本段个人交流已记录。回看不重复结算，也不改变团队立场。"));
            return Hk3DiplomacyService.topic(player, topic);
        }
        int step = n.getInt("Step"); String doc = path.get(step);
        var preview = new Preview(UUID.randomUUID(), team, topic, n.getUUID("Attempt"), n.getInt("Version"), step,
                player.server.overworld().getGameTime() + 12000);
        PREVIEWS.put(player.getUUID(), preview);
        var view = new CompoundTag(); view.putString("Mode", "diplomacy_read"); view.putString("Topic", topic);
        view.putBoolean("PersonalSupplement", true); view.putString("Token", preview.token.toString());
        view.putString("Title", "个人补谈 " + (step+1) + "/" + path.size());
        view.putString("Body", canonicalBody(diplomacy,team,doc));
        Hk3DiplomacyService.send(player, view); return 1;
    }
    static String canonicalBody(Hk3DiplomacyData diplomacy,UUID team,String doc){
        return "本队已发生的交流 · "+Hk3DiplomacyService.title(doc)+"\n\n"
                +Hk3DiplomacyService.historicalBody(diplomacy,team,doc)
                +"\n\n本次仅确认你亲自完成这一段补谈，不代表重新发送团队答复。关闭后保留已确认步骤。";
    }
    public static int advance(ServerPlayer player, String token) {
        if (!allowed(player)) return 0;
        UUID parsed; try { parsed=UUID.fromString(token); } catch (IllegalArgumentException bad) { return 0; }
        if(!com.sirin.hk3gtl.common.easter.Hk3EggReading.consumeAction(player,token)){
            player.sendSystemMessage(Component.literal("请按顺序读完当前补谈正文，再确认本步。"));return 0;
        }
        var preview=PREVIEWS.remove(player.getUUID());
        UUID team=Hk3ResearchTeams.scope(player.server,player.getUUID());
        long tick=player.server.overworld().getGameTime();
        if (preview==null || !preview.token.equals(parsed) || !preview.team.equals(team) || (tick>=preview.expires||tick<preview.expires-12000)) return invalid(player);
        Hk3DiplomacyService.refresh(player);
        var diplomacy=Hk3DiplomacyData.get(player.server);
        if(diplomacy.version(team,preview.topic)!=preview.version) return invalid(player);
        boolean ok=Hk3PersonalCommunicationData.get(player.server).advance(player.getUUID(),team,preview.topic,
                preview.attempt,preview.version,preview.step,diplomacy.personalPath(team,preview.topic),
                Hk3ResearchData.get(player).isMember(player.getUUID(),team),tick);
        return ok?open(player,preview.topic):invalid(player);
    }
    private static int invalid(ServerPlayer p) {
        p.sendSystemMessage(Component.literal("补谈页面已过期或团队路线发生变化，请重新进入；已经确认的个人记录保留。")); return Hk3DiplomacyService.home(p);
    }
    @SubscribeEvent public static void logout(PlayerEvent.PlayerLoggedOutEvent event) { PREVIEWS.remove(event.getEntity().getUUID()); }
    @SubscribeEvent public static void stop(ServerStoppedEvent event) { PREVIEWS.clear(); }
}

// 【变更记录 · 修订161】2026-10-17 14:11:55：本轮仅将活动类名、资源与工业配方引用迁移为长期业务命名；历史备注保留，不代表旧逻辑已全部按现行设计重写。
