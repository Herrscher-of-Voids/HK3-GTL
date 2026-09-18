package com.sirin.hk3gtl.common.gaze;

import com.sirin.hk3gtl.common.constants.Hk3Constants;
import net.minecraft.core.BlockPos;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.entity.BlockEntity;


public final class Hk3GazeManager {

    public static final String TAG_GAZE_LEVEL = "hk3gtl_gaze_level";
    public static final String TAG_GAZE_BUFFER_UNTIL = "hk3gtl_gaze_buffer_until";
    private static final int BUFFER_OFFSET = 50;

    private static final ResourceLocation FINALITY_BUFFER_ID =
            new ResourceLocation(Hk3Constants.MOD_ID, "finality_pressure_buffer_array");
    private static final ResourceLocation QUANTUM_COMPUTER_ID =
            new ResourceLocation(Hk3Constants.MOD_ID, "quantum_entanglement_computer");
    private static final ResourceLocation SHIPBOARD_RESEARCH_ID =
            new ResourceLocation(Hk3Constants.MOD_ID, "shipboard_finality_observation");
    private static final ResourceLocation DIVINE_KEY_GALLERY_ID =
            new ResourceLocation(Hk3Constants.MOD_ID, "divine_key_gallery");
    private static final ResourceLocation SHIPBOARD_DIVINE_KEY_ID =
            new ResourceLocation(Hk3Constants.MOD_ID, "shipboard_divine_key_shrine");
    private static final ResourceLocation SUPPRESSION_ID =
            new ResourceLocation(Hk3Constants.MOD_ID, "honkai_phase_purification_plant");

    private Hk3GazeManager() {}

    public static int getGaze(Player player) {
        return player.getPersistentData().getInt(TAG_GAZE_LEVEL);
    }

    public static void setGaze(ServerPlayer player, int level) {
        int old = getGaze(player);
        int clamped = Math.max(Hk3Constants.GAZE_MIN, Math.min(Hk3Constants.GAZE_MAX, level));
        player.getPersistentData().putInt(TAG_GAZE_LEVEL, clamped);
        Hk3GazeThresholdWatcher.onGazeChanged(player, old, clamped);
        syncToClient(player);
    }

    /**
     * 下发注视度快照到客户端 HUD。所有注视/缓冲变化后统一调用，保证 HUD 实时性。
     * <p>用 try/catch 兜底：同步失败不得影响服务端注视业务主流程。</p>
     */
    public static void syncToClient(ServerPlayer player) {
        try {
            com.sirin.hk3gtl.common.network.Hk3Network.CHANNEL.send(
                    net.minecraftforge.network.PacketDistributor.PLAYER.with(() -> player),
                    new com.sirin.hk3gtl.common.network.GazeSyncS2CPacket(
                            getGaze(player), Hk3Constants.GAZE_MAX, isBufferActive(player)));
        } catch (Throwable ignored) {
            // HUD 同步失败不影响服务端注视逻辑
        }
    }

    public static int addGaze(ServerPlayer player, int amount) {
        return addGaze(player, amount, "generic");
    }

    public static int addGaze(ServerPlayer player, int amount, String reason) {
        int delta = Hk3GazeGrowth.adjustGrowth(player, amount, reason);
        int next = getGaze(player) + delta;
        setGaze(player, next);
        return getGaze(player);
    }

    /** 有效注视值：缓冲状态期间按 offset 抵消，用于研究/机器效率计算。 */
    public static int getEffectiveGaze(Player player) {
        int raw = getGaze(player);
        if (player instanceof ServerPlayer serverPlayer && isBufferActive(serverPlayer)) {
            return Math.max(Hk3Constants.GAZE_MIN, raw - BUFFER_OFFSET);
        }
        return raw;
    }

    /**
     * 激活注视缓冲单元：立即降低 50 注视，并附加 10 分钟缓冲状态。
     */
    public static void activateBufferUnit(ServerPlayer player, int durationTicks) {
        long now = getGameTime(player);
        long until = Math.max(now + durationTicks, player.getPersistentData().getLong(TAG_GAZE_BUFFER_UNTIL));
        player.getPersistentData().putLong(TAG_GAZE_BUFFER_UNTIL, until);
        setGaze(player, getGaze(player) - BUFFER_OFFSET);
    }

    public static boolean isBufferActive(ServerPlayer player) {
        long until = player.getPersistentData().getLong(TAG_GAZE_BUFFER_UNTIL);
        long now = getGameTime(player);
        if (until <= now) {
            if (until != 0L) {
                player.getPersistentData().remove(TAG_GAZE_BUFFER_UNTIL);
            }
            return false;
        }
        return true;
    }

    /**
     * 研究速度衰减：max(floor, 1 - gaze / divisor)。
     * 若玩家附近有终焉压力缓冲阵，floor 至少提升到 0.4。
     */
    public static double getResearchSpeedFactor(Player player) {
        double floor = Hk3Constants.RESEARCH_SPEED_FLOOR;
        if (player instanceof ServerPlayer serverPlayer && hasControllerNearby(serverPlayer, FINALITY_BUFFER_ID, 16)) {
            floor = Math.max(floor, 0.4D);
        }
        double base = 1.0D - getEffectiveGaze(player) / Hk3Constants.GAZE_DECAY_DIVISOR;
        return Math.max(floor, base);
    }

    /**
     * 研究设施协作加成：
     * - 量子纠缠计算机：1.5x
     * - 舰载终焉观测：2.0x（覆盖前者）
     * - 神之键展示设施：每台 +0.1，最多 +0.3
     */
    public static double getFacilityFactor(ServerPlayer player) {
        double factor = 1.0D;
        if (hasControllerNearby(player, QUANTUM_COMPUTER_ID, 16)) {
            factor = Math.max(factor, 1.5D);
        }
        if (hasControllerNearby(player, SHIPBOARD_RESEARCH_ID, 16)) {
            factor = Math.max(factor, 2.0D);
        }

        int divineKeyDisplays = countControllersNearby(player, 16, DIVINE_KEY_GALLERY_ID, SHIPBOARD_DIVINE_KEY_ID);
        if (divineKeyDisplays > 0) {
            factor *= 1.0D + Math.min(0.3D, divineKeyDisplays * 0.1D);
        }
        return factor;
    }

    static boolean hasSuppressionNearby(ServerPlayer player) {
        return hasControllerNearby(player, SUPPRESSION_ID, 16);
    }

    private static boolean hasControllerNearby(ServerPlayer player, ResourceLocation blockId, int radius) {
        return countControllersNearby(player, radius, blockId) > 0;
    }

    private static int countControllersNearby(ServerPlayer player, int radius, ResourceLocation... blockIds) {
        Level level = player.level();
        BlockPos center = player.blockPosition();
        int chunkRadius = (radius >> 4) + 1;
        int chunkX = center.getX() >> 4;
        int chunkZ = center.getZ() >> 4;
        long radiusSq = (long) radius * radius;
        int count = 0;
        for (int dx = -chunkRadius; dx <= chunkRadius; dx++) {
            for (int dz = -chunkRadius; dz <= chunkRadius; dz++) {
                var chunk = level.getChunkSource().getChunkNow(chunkX + dx, chunkZ + dz);
                if (chunk == null) continue;
                for (BlockEntity blockEntity : chunk.getBlockEntities().values()) {
                    BlockPos pos = blockEntity.getBlockPos();
                    if (pos.distSqr(center) > radiusSq) continue;
                    ResourceLocation currentId = BuiltInRegistries.BLOCK.getKey(blockEntity.getBlockState().getBlock());
                    for (ResourceLocation blockId : blockIds) {
                        if (blockId.equals(currentId)) {
                            count++;
                        }
                    }
                }
            }
        }
        return count;
    }

    private static long getGameTime(ServerPlayer player) {
        return player.level() instanceof ServerLevel level ? level.getGameTime() : 0L;
    }
}
