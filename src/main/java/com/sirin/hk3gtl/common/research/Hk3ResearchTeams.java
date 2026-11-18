package com.sirin.hk3gtl.common.research;
















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

@Mod.EventBusSubscriber(modid=Hk3Constants.MOD_ID)








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
                Hk3W13ResearchData.get(server).departed(player);
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


