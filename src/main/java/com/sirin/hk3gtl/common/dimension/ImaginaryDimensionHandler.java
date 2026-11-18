package com.sirin.hk3gtl.common.dimension;

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
