package com.sirin.hk3gtl.common.research;

/** 【变更记录 #3】2026-09-30 23:58:50（修订121）：删除旧个人答复自动代表新队的生产路径；新增/修改：读取FTB真实队长，换队即时撤外交授权，队长变更刷新；用途：团队外交、阅读与个人经历分账，不发研究或物品奖励。 */
/** 【变更记录 #4】2026-10-31 03:33:10（修订187）：修正FTB个人队继承NIL owner导致本人无法答复；个人队以自身ID为队长，党团仍只认FTB实际owner，未知队拒绝授权。 */



/**
 * 【文件职责／本轮边界】可选FTB团队事件触发重新对账；共享已完成知识与来源，原队待研任务不跟随付款人迁移。
 * 【变更记录 #1】2026-09-29 21:06:40（第 1 次编号备注 · 内测5修订100）
 * 删除：取消已被批准规则替代的研究个人独占、旧数值或在线限定分支；历史备注与其他系统保留。
 * 新增／修改：可选FTB团队事件触发重新对账；共享已完成知识与来源，原队待研任务不跟随付款人迁移。
 * 用途：接通实际证据→付款→研究完成与权限检查；不授予缺真实证据的课题。
 * 边界：编译和账本测试不代表游戏验收；S02至S05正式结构及未接线课题仍未完成。
 * 追溯：logs/research-mainline-r100；R100_FINAL_RECORD。
 */

import com.sirin.hk3gtl.common.constants.Hk3Constants;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.level.ServerPlayer;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.event.server.ServerStartedEvent;
import net.minecraftforge.event.server.ServerStoppedEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.ModList;
import net.minecraftforge.fml.common.Mod;
import java.util.UUID;

/** 修订100 · 2026-09-29：FTB可选桥接；事件变更才重新对账，不在机器tick扫描所有团队。 */
/** 【变更记录 #4】2026-10-01 00:59:10（修订124）：删除无；新增/修改：离队事件清除首信/外交/补谈临时预览，离队后立即回队也不得复用旧令牌；用途：按五方交流系统整链收口，真实权限和本人经历不混用。 */
@Mod.EventBusSubscriber(modid=Hk3Constants.MOD_ID)
/**
 * 【变更记录 #2】2026-09-29 23:37:35（内测5修订101）
 * 删除：本轮被替代的单前置或旧提示分支；其余历史保留。
 * 新增／修改：换队重新核验本人已完成交流，原生产批次仍留原队。
 * 用途：补足研究接线并如实保留未接物理执行器及结构审批边界。
 * 追溯：logs/research-mainline-r101；R101_FINAL_RECORD。
 */
/** 【变更记录 #5】2026-10-01 01:30:10（修订125）：删除无；新增离队事件中止未完成个人二审、按原规则暂停一审；修改保留原队资格与个人历史；用途：不得携旧队准入续谈，亦不永久锁住新队补行入口。 */
public final class Hk3ResearchTeams {
    private static boolean dirty = true;
    private static boolean refreshing;
    private Hk3ResearchTeams() {}
    public static void init() { if (ModList.get().isLoaded("ftbteams")) Ftb.register(); }
    public static UUID scope(MinecraftServer server, UUID player) {
        refresh(server); return Hk3ResearchData.get(server).scope(player);
    }
    public static void refresh(MinecraftServer server) {
        if (!dirty || refreshing) return;
        if (!ModList.get().isLoaded("ftbteams")) { dirty=false; return; }
        refreshing=true;
        try { if (Ftb.refresh(server)) dirty=false; } finally { refreshing=false; }
    }
    /** 外交只认实际队长，不把官员权限等同于明确授权。 */
    public static UUID owner(MinecraftServer server,UUID scope) {
        refresh(server);return ModList.get().isLoaded("ftbteams")?Ftb.owner(scope):scope;
    }
    public static boolean canManage(MinecraftServer server, UUID scope, UUID player) {
        refresh(server);
        if (!Hk3ResearchData.get(server).isMember(player, scope)) return false;
        return scope.equals(player) || (ModList.get().isLoaded("ftbteams") && Ftb.officer(scope, player));
    }
    public static java.util.List<ServerPlayer> online(MinecraftServer server, UUID scope) {
        refresh(server);
        var data=Hk3ResearchData.get(server);
        return server.getPlayerList().getPlayers().stream().filter(p -> data.isMember(p.getUUID(),scope)).toList();
    }
    public static double gaze(MinecraftServer server, UUID scope) {
        return online(server,scope).stream().mapToDouble(com.sirin.hk3gtl.common.gaze.Hk3GazeManager::getEffectiveGaze)
                .map(v -> Math.max(0,v)).max().orElse(0);
    }
    @SubscribeEvent public static void started(ServerStartedEvent event) { dirty=true; refresh(event.getServer()); }
    @SubscribeEvent public static void stopped(ServerStoppedEvent event) { dirty=true; }
    @SubscribeEvent public static void tick(TickEvent.ServerTickEvent event) {
        if (event.phase==TickEvent.Phase.END && dirty) refresh(event.getServer());
    }
    private static final class Ftb {
        static void register() {
            dev.ftb.mods.ftbteams.api.event.TeamEvent.PLAYER_CHANGED.register(e -> {dirty=true;departed(e.getPlayerId());});
            dev.ftb.mods.ftbteams.api.event.TeamEvent.CREATED.register(e -> dirty=true);
            dev.ftb.mods.ftbteams.api.event.TeamEvent.DELETED.register(e -> dirty=true);
            dev.ftb.mods.ftbteams.api.event.TeamEvent.PLAYER_LOGGED_IN.register(e -> dirty=true);
            dev.ftb.mods.ftbteams.api.event.TeamEvent.PLAYER_JOINED_PARTY.register(e -> dirty=true);
            dev.ftb.mods.ftbteams.api.event.TeamEvent.PLAYER_LEFT_PARTY.register(e -> {dirty=true;departed(e.getPlayerId());});
            dev.ftb.mods.ftbteams.api.event.TeamEvent.OWNERSHIP_TRANSFERRED.register(e -> dirty=true);
        }
        static boolean refresh(MinecraftServer server) {
            var api=dev.ftb.mods.ftbteams.api.FTBTeamsAPI.api();
            if (!api.isManagerLoaded() || api.getManager().getServer()!=server) return false;
            var manager=api.getManager();
            var membership=new java.util.HashMap<UUID,UUID>();
            var teams=new java.util.HashSet<UUID>();
            // 个人队伍的getMembers可能包含已加入party者，故使用当前玩家映射，不能互相覆盖。
            for (UUID player:manager.getKnownPlayerTeams().keySet()) {
                var team=manager.getTeamForPlayerID(player).orElse(null);
                membership.put(player,team==null || team.isPlayerTeam()?player:team.getTeamId());
            }
            for (var team:manager.getTeams()) if (team.isValid() && !team.isPlayerTeam()) {
                teams.add(team.getTeamId());
                for (UUID member:team.getMembers()) membership.put(member,team.getTeamId());
            }
            Hk3ResearchData.get(server).reconcileTeams(membership,teams);
            for (var player:server.getPlayerList().getPlayers()) {
                Hk3CommunicationResearchProof.reconcile(player);
                Hk3ResearchManager.syncClientResearchState(player);
            }
            return true;
        }
        static UUID owner(UUID scope) {
            var api=dev.ftb.mods.ftbteams.api.FTBTeamsAPI.api();
            return api.isManagerLoaded()?owner(api.getManager().getTeamByID(scope).orElse(null)):null;
        }
        private static UUID owner(dev.ftb.mods.ftbteams.api.Team team) {
            // PlayerTeam未覆写getOwner，继承实现固定返回NIL；getId才是其真实玩家身份。
            return team==null?null:team.isPlayerTeam()?team.getId():team.getOwner();
        }
        static void departed(UUID player) {
            var server=net.minecraftforge.server.ServerLifecycleHooks.getCurrentServer();
            if(server!=null){
                com.sirin.hk3gtl.common.communication.Hk3TeamContactData.get(server).revokeDeparted(player);
                com.sirin.hk3gtl.common.communication.Hk3TeamContactService.clearPreview(player);
                com.sirin.hk3gtl.common.communication.Hk3DiplomacyService.clearPreview(player);
                com.sirin.hk3gtl.common.communication.Hk3PersonalCommunicationService.clearPreview(player);
                com.sirin.hk3gtl.common.review.Hk3ReviewData.get(server).change(ledger->{ledger.leaveTeam(player);return null;});
            }
        }
        static boolean officer(UUID scope, UUID player) {
            var api=dev.ftb.mods.ftbteams.api.FTBTeamsAPI.api();
            return api.isManagerLoaded() && api.getManager().getTeamByID(scope)
                    .map(team -> team.getRankForPlayer(player).isOfficerOrBetter()).orElse(false);
        }
    }
}

// 【变更记录 · 修订161】2026-10-17 14:11:55：本轮仅将活动类名、资源与工业配方引用迁移为长期业务命名；历史备注保留，不代表旧逻辑已全部按现行设计重写。
