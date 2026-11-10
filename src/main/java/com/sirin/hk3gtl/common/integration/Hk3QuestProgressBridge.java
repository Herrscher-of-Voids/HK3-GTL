package com.sirin.hk3gtl.common.integration;

import com.sirin.hk3gtl.common.research.*;
import com.sirin.hk3gtl.common.review.*;
import com.sirin.hk3gtl.common.civ.Hk3CivilizationData;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.level.ServerPlayer;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.event.server.ServerStoppedEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.ModList;
import net.minecraftforge.fml.common.Mod;
import java.util.*;

/** 每100刻按在线研究队伍去重投影；FTB类隔离到内部桥，不读取库存、不付费、不修改研究。 */
@Mod.EventBusSubscriber(modid="hk3gtl")
/** 【变更记录 #1】2026-10-01 14:10:35（修订129）：删除：无；新增/修改：服务端每五秒按在线队伍投影真实成果，检查FTB个人队伍与研究scope差异；用途：任务和进度只投影真实账本，不授研究、物品或审查资格。 */
public final class Hk3QuestProgressBridge {
    private static long lastWarning=Long.MIN_VALUE;
    private Hk3QuestProgressBridge(){}
    public static Hk3QuestCatalog.Facts facts(MinecraftServer server,UUID scope){
        var data=Hk3ResearchData.get(server);var completed=new LinkedHashSet<String>();
        for(String id:Hk3ResearchCatalog.bundled().topics().keySet())if(data.completed(scope,id))completed.add(id);
        var reviews=Hk3ReviewData.get(server);
        return new Hk3QuestCatalog.Facts(completed,Hk3CivilizationData.get(server).highest(scope),reviews.settled(scope,Hk3ReviewLedger.Kind.FIRST),reviews.settled(scope,Hk3ReviewLedger.Kind.SECOND));
    }
    @SubscribeEvent public static void tick(TickEvent.ServerTickEvent event){
        if(event.phase!=TickEvent.Phase.END)return;var server=event.getServer();
        if(server.getTickCount()%100!=0)return;
        var snapshots=new HashMap<UUID,Hk3QuestCatalog.Facts>();var ftbTeams=new HashSet<UUID>();
        for(var player:server.getPlayerList().getPlayers())try{
            var scope=Hk3ResearchTeams.scope(server,player.getUUID());
            var f=snapshots.computeIfAbsent(scope,id->facts(server,id));
            Hk3GuideAdvancements.sync(player,f);
            if(ModList.get().isLoaded("ftbquests"))Ftb.sync(player,scope,f,ftbTeams);
        }catch(RuntimeException ex){
            long now=server.getTickCount();if(lastWarning==Long.MIN_VALUE||now<lastWarning||now-lastWarning>=1200){lastWarning=now;com.mojang.logging.LogUtils.getLogger().error("[HK3GTL] 教程进度同步失败，保留原研究和任务数据，稍后重试",ex);}
        }
    }
    @SubscribeEvent public static void stopped(ServerStoppedEvent event){lastWarning=Long.MIN_VALUE;}
    private static final class Ftb {
        static void sync(ServerPlayer player,UUID scope,Hk3QuestCatalog.Facts f,Set<UUID> seen){
            var file=dev.ftb.mods.ftbquests.quest.ServerQuestFile.INSTANCE;
            if(file==null||file.server!=player.server)return;
            var api=dev.ftb.mods.ftbteams.api.FTBTeamsAPI.api();if(!api.isManagerLoaded())return;
            var team=api.getManager().getTeamForPlayerID(player.getUUID()).orElse(null);if(team==null)return;
            // FTB个人队伍ID不必等于玩家UUID；党团才以teamId作为研究scope。
            if(!(team.isPlayerTeam()?player.getUUID():team.getTeamId()).equals(scope)||!seen.add(team.getTeamId()))return;
            var data=file.getNullableTeamData(team.getTeamId());if(data==null||!file.isPlayerOnTeam(player,data))return;
            file.withPlayerContext(player,()->{
                for(var e:Hk3QuestCatalog.all()){
                    if(!Hk3QuestCatalog.satisfied(e,f))continue;
                    var task=file.getTask(e.taskId());
                    if(!(task instanceof dev.ftb.mods.ftbquests.quest.task.CustomTask)||task.getQuest().id!=e.questId()||!task.hasTag(e.tag()))continue;
                    if(data.getProgress(task)<1&&data.canStartTasks(task.getQuest()))data.setProgress(task,1);
                }
            });
        }
    }
}

// 【变更记录 · 修订161】2026-10-17 14:11:55：本轮仅将活动类名、资源与工业配方引用迁移为长期业务命名；历史备注保留，不代表旧逻辑已全部按现行设计重写。
