package com.sirin.hk3gtl.common.gaze;

import com.sirin.hk3gtl.common.constants.Hk3Constants;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.entity.player.Player;

/**
 * 
 * - 注视度统一入口：负责注视读写、增长修正、缓冲单元、研究速度与设施加成。
 * - 调用链：事件系统/研究系统 -> Hk3GazeManager -> Hk3GazeThresholdWatcher。
 *
 */
public final class Hk3GazeManager {

    public static final String TAG_GAZE_LEVEL = "hk3gtl_gaze_level";
    public static final String TAG_GAZE_BUFFER_UNTIL = "hk3gtl_gaze_buffer_until";
    private static final int BUFFER_OFFSET = 50;

    private Hk3GazeManager() {}

    public static int getGaze(Player player) {
        return player.getPersistentData().getInt(TAG_GAZE_LEVEL);
    }

    public static void setGaze(ServerPlayer player, int level) {
        setGaze(player, level, "manual");
    }

    private static void setGaze(ServerPlayer player, int level, String source) {
        int old = getGaze(player);
        int clamped = Math.max(Hk3Constants.GAZE_MIN, Math.min(Hk3Constants.GAZE_MAX, level));
        player.getPersistentData().putInt(TAG_GAZE_LEVEL, clamped);
        Hk3GazeJournal.record(player.getPersistentData(), source, old, clamped, getGameTime(player));
        Hk3GazeThresholdWatcher.onGazeChanged(player, old, clamped);
        if(!source.equals("manual")) com.sirin.hk3gtl.common.easter.Hk3EggRuntime.observe(player,"gaze",
            com.sirin.hk3gtl.common.easter.Hk3EggRuntime.fields("gaze",Integer.toString(clamped),"old",Integer.toString(old),"source",source));
        if(source.equals("buffer-unit")&&clamped<old){
            long uses=com.sirin.hk3gtl.common.easter.Hk3EggVanilla.increment(player,"effectiveBuffers",20);
            com.sirin.hk3gtl.common.easter.Hk3EggRuntime.observe(player,"effective_buffer",java.util.Map.of("count",Long.toString(uses)));
        }
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
                            getGaze(player), Hk3Constants.GAZE_MAX, isBufferActive(player), getEffectiveGaze(player),
                            (int) com.sirin.hk3gtl.common.research.Hk3ResearchTeams.gaze(player.server,
                                    com.sirin.hk3gtl.common.research.Hk3ResearchTeams.scope(player.server,player.getUUID()))));
        } catch (Throwable ignored) {
            // HUD 同步失败不影响服务端注视逻辑
        }
    }

    public static int addGaze(ServerPlayer player, int amount) {
        return addGaze(player, amount, "generic");
    }

    public static int addGaze(ServerPlayer player, int amount, String reason) {
        int delta = Hk3GazeGrowth.adjustGrowth(player, amount, reason);
        int next = Hk3GazeRules.add(getGaze(player), delta, Hk3Constants.GAZE_MAX);
        setGaze(player, next, reason);
        return getGaze(player);
    }

    /** 一次性来源先登记再增长，阈值回调重入也不会重复收费；不追补旧事件。 */
    public static int addGazeOnce(ServerPlayer player, int amount, String source) {
        if (Hk3GazeJournal.claim(player.getPersistentData(), source)) return addGaze(player, amount, source);
        return getGaze(player);
    }

    /** 有效注视值：缓冲状态期间按 offset 抵消，用于研究/机器效率计算。 */
    public static int getEffectiveGaze(Player player) {
        return Hk3GazeRules.effective(getGaze(player),
                player instanceof ServerPlayer sp && isBufferActive(sp));
    }

    /**
     * 激活注视缓冲单元：立即降低 50 注视，并附加 10 分钟缓冲状态。
     */
    public static void activateBufferUnit(ServerPlayer player, int durationTicks) {
        long now = getGameTime(player);
        long until = Math.max(now + durationTicks, player.getPersistentData().getLong(TAG_GAZE_BUFFER_UNTIL));
        player.getPersistentData().putLong(TAG_GAZE_BUFFER_UNTIL, until);
        setGaze(player, getGaze(player) - BUFFER_OFFSET, "buffer-unit");
    }

    public static boolean isBufferActive(ServerPlayer player) {
        long until = player.getPersistentData().getLong(TAG_GAZE_BUFFER_UNTIL);
        long now = getGameTime(player);
        if (!Hk3GazeRules.bufferActive(until, now)) {
            if (until != 0L) {
                player.getPersistentData().remove(TAG_GAZE_BUFFER_UNTIL);
            }
            return false;
        }
        return true;
    }

    /** 兼容旧研究入口：使用在线团队最高有效值与已批准复合压力，不扫描控制器加速。 */
    public static double getResearchSpeedFactor(Player player) {
        double gaze = getEffectiveGaze(player);
        if (player instanceof ServerPlayer sp) {
            gaze = com.sirin.hk3gtl.common.research.Hk3ResearchTeams.gaze(sp.server,
                    com.sirin.hk3gtl.common.research.Hk3ResearchTeams.scope(sp.server, sp.getUUID()));
        }
        return com.sirin.hk3gtl.common.research.Hk3ResearchMath.speed(2, gaze, 0, false, false);
    }

    /** 旧设施旁置加成已停用；ERM/W13须走实际供能与授权路径。 */
    public static double getFacilityFactor(ServerPlayer player) { return 1.0D; }

    private static long getGameTime(ServerPlayer player) {
        return player.server.overworld().getGameTime();
    }
}
