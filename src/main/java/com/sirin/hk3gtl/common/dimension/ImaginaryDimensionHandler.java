package com.sirin.hk3gtl.common.dimension;


/**
 * 【文件职责】
 * - 维护 ImaginaryDimensionHandler 的核心功能实现。
 * - 关键调用链：由上层系统入口调用 -> 本文件核心方法 -> 下游模块。
 *
 * 【变更记录】2026-05-19
 * - 删除：
 *   1) 初始归档备注：自 v0.3 基线梳理，无本次 diff。
 * - 新增：
 *   1) 新增统一变更备注块，便于后续维护与审计追踪。
 * - 修改：
 *   1) 未改动业务逻辑，仅补充文件级职责与维护注释模板。
 * - 用途：
 *   1) 帮助维护者快速理解文件职责、变更背景与风险点。
 *
 * 【段内说明】
 * - 复杂方法补充“干什么 / 边界 / 线程侧”精简中文注释。
 */
import com.sirin.hk3gtl.common.constants.Hk3Constants;
import com.sirin.hk3gtl.common.dialogue.DialogueSessionManager;
import com.sirin.hk3gtl.common.entity.VoidQueenSirinEntity;
import com.sirin.hk3gtl.common.network.ResearchStateSyncRequestC2SPacket;
import net.minecraft.core.BlockPos;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.level.Level;
import net.minecraftforge.event.entity.EntityTravelToDimensionEvent;
import net.minecraftforge.event.entity.player.PlayerEvent;
import net.minecraftforge.event.entity.living.MobSpawnEvent;
import net.minecraftforge.event.level.BlockEvent;
import net.minecraftforge.event.level.LevelEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;

@Mod.EventBusSubscriber(modid = Hk3Constants.MOD_ID)
/** 【变更记录 #1】2026-09-30 23:34:26（修订119）：删除：世界级结果对所有玩家的隐式授权；新增/修改：毕业/传送/彩蛋/调试改为查询当前玩家，实体避免在已有坏结局演出时开启新会面；用途：个人结算不覆盖其他玩家，未完成的资格采集仍单独接入。 */
/**
 * 【变更记录 #2】2026-10-17 14:44:46（第2次备注 · 内测5修订162）
 * 删除：退役虚数锚扫描缓存专用的维度卸载回调和依赖。
 * 新增：无。修改：保留维度加载、实体、玩家登录/离线和毕业传送处理。
 * 用途：解绑无设备消费者的旧约束，不改变现行维度与终局行为。
 */
public class ImaginaryDimensionHandler {

    private static final String DIALOGUE_DONE_TAG = "hk3gtl_dialogue_done";

    /** 登录时：已完成对话的玩家若仍在虚数维度，强制回主世界 */
    @SubscribeEvent
    public static void onPlayerLoggedIn(PlayerEvent.PlayerLoggedInEvent event) {
        if (!(event.getEntity() instanceof ServerPlayer player)) return;
        if (player.level().dimension() != Hk3Dimensions.IMAGINARY) {
            if (com.sirin.hk3gtl.common.finale.Hk3FinalePlayerMode.hasSavedMode(player))
                com.sirin.hk3gtl.common.finale.Hk3FinalePlayerMode.leave(player);
            return;
        }
        boolean graduated = Hk3GraduationData.get(player.serverLevel()).isGraduated(player.getUUID());
        boolean mustLeave = graduated || player.getPersistentData().getBoolean(DIALOGUE_DONE_TAG);
        if (!mustLeave) {
            com.sirin.hk3gtl.common.finale.Hk3FinalePlayerMode.enter(player);
            return;
        }

        ServerLevel dest = player.server.getLevel(Level.OVERWORLD);
        if (dest == null) return;
        BlockPos spawn = dest.getSharedSpawnPos();
        player.teleportTo(dest, spawn.getX() + 0.5, spawn.getY(), spawn.getZ() + 0.5,
                player.getYRot(), player.getXRot());
        if (player.level().dimension() != Hk3Dimensions.IMAGINARY)
            com.sirin.hk3gtl.common.finale.Hk3FinalePlayerMode.leave(player);
    }

    /** 玩家断线时释放仅在当前登录会话有效的临时状态。 */
    @SubscribeEvent
    public static void onPlayerLoggedOut(PlayerEvent.PlayerLoggedOutEvent event) {
        if (!(event.getEntity() instanceof ServerPlayer player)) return;
        DialogueSessionManager.onPlayerDisconnect(player.getUUID());
        ResearchStateSyncRequestC2SPacket.clearRateLimit(player.getUUID());
    }

    /** 修订198：成功入场才保存个人模式；未毕业离开恢复原模式，毕业仍创造。 */
    @SubscribeEvent
    public static void onPlayerChangedDimension(PlayerEvent.PlayerChangedDimensionEvent event) {
        if (!(event.getEntity() instanceof ServerPlayer player)) return;
        if (event.getTo() == Hk3Dimensions.IMAGINARY)
            com.sirin.hk3gtl.common.finale.Hk3FinalePlayerMode.enter(player);
        else if (event.getFrom() == Hk3Dimensions.IMAGINARY)
            com.sirin.hk3gtl.common.finale.Hk3FinalePlayerMode.leave(player);
    }

    @SubscribeEvent
    public static void onPlayerRespawned(PlayerEvent.PlayerRespawnEvent event) {
        if (!(event.getEntity() instanceof ServerPlayer player)) return;
        if (player.level().dimension() == Hk3Dimensions.IMAGINARY)
            com.sirin.hk3gtl.common.finale.Hk3FinalePlayerMode.enter(player);
        else if (com.sirin.hk3gtl.common.finale.Hk3FinalePlayerMode.hasSavedMode(player))
            com.sirin.hk3gtl.common.finale.Hk3FinalePlayerMode.leave(player);
    }

    @SubscribeEvent
    public static void onLevelLoad(LevelEvent.Load event) {
        if (event.getLevel() instanceof ServerLevel serverLevel
                && serverLevel.dimension() == Hk3Dimensions.IMAGINARY) {
            VoidQueenSirinEntity.ensurePlatformAndEntity(serverLevel);
        }
    }

    /** 已完成对话的玩家禁止再次进入虚数维度；模式仅在传送成功后变更。 */
    @SubscribeEvent
    public static void onDimensionTravel(EntityTravelToDimensionEvent event) {
        if (event.getDimension() == Hk3Dimensions.IMAGINARY
                && event.getEntity() instanceof ServerPlayer player) {
            if (Hk3GraduationData.get(player.serverLevel()).isGraduated(player.getUUID())) {
                event.setCanceled(true);
                player.sendSystemMessage(Component.translatable("hk3gtl.imaginary.block.graduated"));
                return;
            }
            if (player.getPersistentData().getBoolean(DIALOGUE_DONE_TAG)) {
                event.setCanceled(true);
                player.sendSystemMessage(Component.translatable("hk3gtl.imaginary.block.dialogue_done"));
                return;
            }
            player.sendSystemMessage(Component.translatable("hk3gtl.imaginary.rift.hint"));
        }
    }

    @SubscribeEvent
    public static void onBlockPlace(BlockEvent.EntityPlaceEvent event) {
        if (event.getLevel() instanceof ServerLevel serverLevel
                && serverLevel.dimension() == Hk3Dimensions.IMAGINARY) {
            event.setCanceled(true);
        }
    }

    @SubscribeEvent
    public static void onBlockBreak(BlockEvent.BreakEvent event) {
        if (event.getLevel() instanceof ServerLevel serverLevel
                && serverLevel.dimension() == Hk3Dimensions.IMAGINARY) {
            event.setCanceled(true);
        }
    }

    @SubscribeEvent
    public static void onMobSpawn(MobSpawnEvent.FinalizeSpawn event) {
        if (event.getLevel() instanceof ServerLevel serverLevel
                && serverLevel.dimension() == Hk3Dimensions.IMAGINARY
                && !(event.getEntity() instanceof VoidQueenSirinEntity)) {
            event.setSpawnCancelled(true);
        }
    }
}
