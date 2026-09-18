package com.sirin.hk3gtl.common.badending;

import com.sirin.hk3gtl.common.constants.Hk3Constants;
import com.sirin.hk3gtl.common.dimension.Hk3Dimensions;
import com.sirin.hk3gtl.common.dimension.Hk3GraduationData;
import com.sirin.hk3gtl.common.entity.VoidQueenSirinEntity;
import com.sirin.hk3gtl.common.event.Hk3FactionEventChecker;
import com.sirin.hk3gtl.common.network.BadEndingBlackoutS2CPacket;
import com.sirin.hk3gtl.common.network.Hk3Network;
import com.sirin.hk3gtl.mixin.LevelSettingsAccessor;
import com.sirin.hk3gtl.mixin.PrimaryLevelDataAccessor;
import net.minecraft.core.BlockPos;
import net.minecraft.network.chat.Component;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.level.ServerBossEvent;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.BossEvent;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.LevelSettings;
import net.minecraft.world.level.storage.PrimaryLevelData;
import net.minecraft.world.phys.Vec3;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.event.entity.player.AttackEntityEvent;
import net.minecraftforge.event.entity.player.PlayerEvent;
import net.minecraftforge.event.server.ServerStoppedEvent;
import net.minecraftforge.network.PacketDistributor;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import org.slf4j.Logger;
import com.mojang.logging.LogUtils;

import java.util.List;
import java.util.UUID;
import java.util.concurrent.CopyOnWriteArrayList;
import java.util.concurrent.atomic.AtomicInteger;

/**
 * 西琳坏结局流程管理器 —— 攻击计数、专属 Boss 战、抓取演出、叙事层打击（踢出游戏）、
 * 重进世界的收尾（传送出生点 + 二次进入虚数维度播放终局文本并毕业）。
 *
 * <h3>完整流程</h3>
 * <ol>
 *   <li>虚数维度内玩家累计左键攻击西琳 10 次 → 启动 Boss 战（阶段 → ERASED 并持久化）</li>
 *   <li>Boss 战期间：西琳持续无敌，聊天框周期推送嘲讽文本</li>
 *   <li>60 tick 后：体型放大 10 倍 → 抓取动画（玩家被拖向西琳手部）→ 客户端黑屏</li>
 *   <li>黑屏同时：世界名改为「xxxx：已被抹除」→ 强制存盘 → 客户端关闭游戏进程</li>
 *   <li>重新登录：传送回主世界出生点（不打毕业标记）</li>
 *   <li>二次进入虚数维度：西琳正常登场，定时播放终局文本，播完打毕业标记（阶段 → COMPLETED）</li>
 * </ol>
 *
 * <p>Boss 战运行时状态（非持久化）仅存在于内存；玩家中途退出/崩溃后重进，
 * 阶段仍为 ERASED，直接走收尾流程，不会延续 Boss 战。</p>
 */
@Mod.EventBusSubscriber(modid = Hk3Constants.MOD_ID)
public final class SirinBadEndingManager {

    private static final Logger LOGGER = LogUtils.getLogger();

    /** 触发坏结局所需的累计左键攻击次数 */
    private static final int ATTACKS_TO_TRIGGER = 10;
    /** Boss 战开始后多少 tick 进入抓取阶段 */
    private static final int GRAB_START_TICK = 60;
    /** 抓取阶段的体型倍率（玩家模型的 10 倍） */
    private static final float GRAB_SCALE = 10.0F;
    /** 黑屏淡入 / 全黑保持时长（tick），客户端据此计时后退出到主标题画面 */
    private static final int BLACKOUT_FADE_TICKS = 60;
    private static final int BLACKOUT_HOLD_TICKS = 30;
    /** 嘲讽文本推送间隔（tick） */
    private static final int TAUNT_INTERVAL = 20;
    /** 嘲讽 / 终局文本行数（与语言文件键 0..N-1 保持一致） */
    private static final int TAUNT_COUNT = 6;
    private static final int FINALE_LINE_COUNT = 8;
    /** 终局文本行间隔（tick） */
    private static final int FINALE_LINE_INTERVAL = 60;
    /** 世界名抹除后缀 */
    private static final String ERASED_SUFFIX = "：已被抹除";
    /** 玩家级标记：被抹除后的首次登录已执行出生点传送 */
    private static final String RESPAWNED_TAG = "hk3gtl_be_respawned";

    // ── Boss 战运行时状态（单场，不持久化；服务器停止时重置） ──
    private static volatile boolean bossActive = false;
    private static final AtomicInteger bossTicks = new AtomicInteger();
    private static final AtomicInteger tauntIndex = new AtomicInteger();
    private static volatile ServerBossEvent bossEvent;
    private static volatile boolean kickExecuted = false;

    /** 终局文本播放会话（服务端 tick 驱动，CopyOnWriteArrayList 保证并发遍历安全） */
    private static final CopyOnWriteArrayList<FinaleSession> FINALE_SESSIONS = new CopyOnWriteArrayList<>();

    private SirinBadEndingManager() {}

    /** 查询坏结局是否已激活（供对话系统屏蔽常规终局对话）。 */
    public static boolean isBadEndingActive(ServerLevel level) {
        return Hk3BadEndingData.get(level).getStage() != Hk3BadEndingData.STAGE_NONE;
    }

    // ══════════════════════════════════════
    //  一、攻击计数 → 触发 Boss 战
    // ══════════════════════════════════════

    /** 左键攻击检测：AttackEntityEvent 在伤害结算前触发，即使西琳 hurt() 恒 false 也能计数。 */
    @SubscribeEvent
    public static void onAttackEntity(AttackEntityEvent event) {
        if (!(event.getEntity() instanceof ServerPlayer player)) return;
        if (!(event.getTarget() instanceof VoidQueenSirinEntity sirin)) return;
        if (player.level().dimension() != Hk3Dimensions.IMAGINARY) return;
        if (bossActive) return;

        ServerLevel level = player.serverLevel();
        Hk3BadEndingData data = Hk3BadEndingData.get(level);
        if (data.getStage() != Hk3BadEndingData.STAGE_NONE) return;
        if (Hk3GraduationData.get(level).isGraduated()) return;

        int count = data.incrementAttackCount();
        LOGGER.info("[HK3GTL] 玩家 {} 攻击西琳，累计 {}/{}", player.getName().getString(), count, ATTACKS_TO_TRIGGER);
        if (count >= ATTACKS_TO_TRIGGER) {
            startBossFight(sirin, level);
        }
    }

    /** 启动坏结局 Boss 战：立即持久化 ERASED 阶段（中途崩溃/退出也不会重打 Boss 战）。 */
    private static void startBossFight(VoidQueenSirinEntity sirin, ServerLevel level) {
        bossActive = true;
        bossTicks.set(0);
        tauntIndex.set(0);
        kickExecuted = false;
        Hk3BadEndingData.get(level).setStage(Hk3BadEndingData.STAGE_ERASED);

        bossEvent = new ServerBossEvent(
                Component.translatable("hk3gtl.badending.bossbar"),
                BossEvent.BossBarColor.PINK,
                BossEvent.BossBarOverlay.PROGRESS);
        bossEvent.setProgress(1.0F);
        for (ServerPlayer player : level.players()) {
            bossEvent.addPlayer(player);
            player.sendSystemMessage(Component.translatable("hk3gtl.badending.start"));
        }
        LOGGER.info("[HK3GTL] 坏结局 Boss 战启动");
    }

    // ══════════════════════════════════════
    //  二、Boss 战 tick（由西琳 aiStep 驱动，仅服务端）
    // ══════════════════════════════════════

    public static void tickBossFight(VoidQueenSirinEntity sirin, ServerLevel level) {
        if (!bossActive) return;

        List<ServerPlayer> players = level.players();
        if (players.isEmpty()) {
            // 玩家全部离开（退出游戏等）：中止运行时演出；阶段已持久化为 ERASED，重进走收尾
            abortBossRuntime(sirin);
            return;
        }

        int t = bossTicks.incrementAndGet();

        // 持续推送嘲讽文本
        if (t % TAUNT_INTERVAL == 0 && !kickExecuted) {
            int idx = tauntIndex.getAndIncrement() % TAUNT_COUNT;
            Component taunt = Component.translatable("hk3gtl.badending.taunt." + idx);
            players.forEach(p -> p.sendSystemMessage(taunt));
        }

        if (t == GRAB_START_TICK) {
            beginGrabPhase(sirin, level, players);
        }

        if (t > GRAB_START_TICK) {
            dragPlayersTowardsHand(sirin, players);
        }

        // 兜底：黑屏结束后客户端应已自行退回主标题；若仍在线（如专用服务器），强制断开连接
        if (t > GRAB_START_TICK + BLACKOUT_FADE_TICKS + BLACKOUT_HOLD_TICKS + 40) {
            for (ServerPlayer player : players) {
                player.connection.disconnect(Component.translatable("hk3gtl.badending.kicked"));
            }
            abortBossRuntime(sirin);
        }
    }

    /** 抓取阶段：体型放大 10 倍 + 黑屏包 + 世界名抹除 + 强制存盘。 */
    private static void beginGrabPhase(VoidQueenSirinEntity sirin, ServerLevel level, List<ServerPlayer> players) {
        kickExecuted = true;
        sirin.setBadEndingScale(GRAB_SCALE);

        Component grabLine = Component.translatable("hk3gtl.badending.grab");
        for (ServerPlayer player : players) {
            player.sendSystemMessage(grabLine);
            Hk3Network.CHANNEL.send(PacketDistributor.PLAYER.with(() -> player),
                    new BadEndingBlackoutS2CPacket(BLACKOUT_FADE_TICKS, BLACKOUT_HOLD_TICKS, true));
        }

        MinecraftServer server = level.getServer();
        renameWorldErased(server);
        // 客户端即将关闭游戏进程，先把改名与坏结局阶段落盘
        server.saveEverything(true, true, true);
        LOGGER.info("[HK3GTL] 叙事层打击：世界已抹除并存盘，等待客户端关闭进程");
    }

    /** 抓取动画：每 tick 将玩家向西琳手部位置（胸口高度前方）拉近 15%。 */
    private static void dragPlayersTowardsHand(VoidQueenSirinEntity sirin, List<ServerPlayer> players) {
        Vec3 look = sirin.getLookAngle().normalize();
        Vec3 hand = sirin.position()
                .add(look.scale(sirin.getBbWidth() * 1.2))
                .add(0, sirin.getBbHeight() * 0.72, 0);
        for (ServerPlayer player : players) {
            Vec3 pos = player.position();
            Vec3 next = pos.add(hand.subtract(pos).scale(0.15));
            player.teleportTo(next.x, next.y, next.z);
            player.setDeltaMovement(Vec3.ZERO);
        }
    }

    /** 中止 Boss 战运行时演出（不回滚已持久化的 ERASED 阶段）。 */
    private static void abortBossRuntime(VoidQueenSirinEntity sirin) {
        bossActive = false;
        bossTicks.set(0);
        if (bossEvent != null) {
            bossEvent.removeAllPlayers();
            bossEvent = null;
        }
        sirin.setBadEndingScale(1.0F);
    }

    /** 世界名追加「：已被抹除」后缀（level.dat 的 Data.LevelName，存盘后世界选择页面即生效）。 */
    private static void renameWorldErased(MinecraftServer server) {
        if (!(server.getWorldData() instanceof PrimaryLevelData primaryData)) return;
        LevelSettings settings = ((PrimaryLevelDataAccessor) primaryData).hk3gtl$getSettings();
        String name = settings.levelName();
        if (!name.endsWith(ERASED_SUFFIX)) {
            ((LevelSettingsAccessor) (Object) settings).hk3gtl$setLevelName(name + ERASED_SUFFIX);
            LOGGER.info("[HK3GTL] 世界名称已改写为: {}{}", name, ERASED_SUFFIX);
        }
    }

    // ══════════════════════════════════════
    //  三、重进游戏的后续效果
    // ══════════════════════════════════════

    /** 被抹除后的首次登录：传送回主世界初始出生点（仅一次，不打毕业标记）。 */
    @SubscribeEvent
    public static void onPlayerLoggedIn(PlayerEvent.PlayerLoggedInEvent event) {
        if (!(event.getEntity() instanceof ServerPlayer player)) return;
        Hk3BadEndingData data = Hk3BadEndingData.get(player.serverLevel());
        if (data.getStage() != Hk3BadEndingData.STAGE_ERASED) return;

        resetSirinRuntime(player.server.getLevel(Hk3Dimensions.IMAGINARY));

        if (!player.getPersistentData().getBoolean(RESPAWNED_TAG)) {
            player.getPersistentData().putBoolean(RESPAWNED_TAG, true);
            ServerLevel overworld = player.server.getLevel(Level.OVERWORLD);
            if (overworld != null) {
                BlockPos spawn = overworld.getSharedSpawnPos();
                player.teleportTo(overworld, spawn.getX() + 0.5, spawn.getY(), spawn.getZ() + 0.5,
                        player.getYRot(), player.getXRot());
            }
        } else if (player.level().dimension() == Hk3Dimensions.IMAGINARY) {
            // 已完成首次回城，又直接登录在虚数维度内：直接开启收尾
            startFinaleSequence(player);
        }
    }

    /** 二次进入虚数维度：西琳正常登场，开始播放坏结局终局文本。 */
    @SubscribeEvent
    public static void onPlayerChangedDimension(PlayerEvent.PlayerChangedDimensionEvent event) {
        if (!(event.getEntity() instanceof ServerPlayer player)) return;
        if (event.getTo() != Hk3Dimensions.IMAGINARY) return;
        Hk3BadEndingData data = Hk3BadEndingData.get(player.serverLevel());
        if (data.getStage() != Hk3BadEndingData.STAGE_ERASED) return;

        resetSirinRuntime(player.server.getLevel(Hk3Dimensions.IMAGINARY));
        startFinaleSequence(player);
    }

    /** 重置西琳为正常状态（体型 1.0），确保不会延续 Boss 战演出。 */
    private static void resetSirinRuntime(ServerLevel imaginary) {
        if (imaginary == null) return;
        VoidQueenSirinEntity sirin = VoidQueenSirinEntity.findSirin(imaginary);
        if (sirin != null && sirin.getBadEndingScale() != 1.0F) {
            sirin.setBadEndingScale(1.0F);
        }
    }

    /** 为玩家开启终局文本会话（去重：同一玩家不重复开启）。 */
    private static void startFinaleSequence(ServerPlayer player) {
        UUID uuid = player.getUUID();
        for (FinaleSession session : FINALE_SESSIONS) {
            if (session.playerId.equals(uuid)) return;
        }
        FINALE_SESSIONS.add(new FinaleSession(uuid));
        LOGGER.info("[HK3GTL] 坏结局终局文本开始 - 玩家: {}", player.getName().getString());
    }

    // ══════════════════════════════════════
    //  四、终局文本调度（服务端 tick 驱动）
    // ══════════════════════════════════════

    @SubscribeEvent
    public static void onServerTick(TickEvent.ServerTickEvent event) {
        if (event.phase != TickEvent.Phase.END || FINALE_SESSIONS.isEmpty()) return;
        MinecraftServer server = net.minecraftforge.server.ServerLifecycleHooks.getCurrentServer();
        if (server == null) return;

        for (FinaleSession session : FINALE_SESSIONS) {
            ServerPlayer player = server.getPlayerList().getPlayer(session.playerId);
            if (player == null || player.level().dimension() != Hk3Dimensions.IMAGINARY) {
                // 玩家离线或离开维度：移除会话，下次进入重新播放
                FINALE_SESSIONS.remove(session);
                continue;
            }
            if (--session.cooldown > 0) continue;
            session.cooldown = FINALE_LINE_INTERVAL;

            if (session.lineIndex < FINALE_LINE_COUNT) {
                player.sendSystemMessage(Component.translatable("hk3gtl.badending.finale." + session.lineIndex));
                session.lineIndex++;
            } else {
                finishBadEnding(player);
                FINALE_SESSIONS.remove(session);
            }
        }
    }

    /** 终局文本播完：打毕业标记（COMPLETED），传送回主世界出生点。 */
    private static void finishBadEnding(ServerPlayer player) {
        ServerLevel level = player.serverLevel();
        Hk3BadEndingData.get(level).setStage(Hk3BadEndingData.STAGE_COMPLETED);
        Hk3GraduationData.get(level).markGraduated();
        Hk3FactionEventChecker.triggerGraduationComplete(player);
        player.sendSystemMessage(Component.translatable("hk3gtl.badending.finale.done"));

        ServerLevel overworld = player.server.getLevel(Level.OVERWORLD);
        if (overworld != null) {
            BlockPos spawn = overworld.getSharedSpawnPos();
            player.teleportTo(overworld, spawn.getX() + 0.5, spawn.getY(), spawn.getZ() + 0.5,
                    player.getYRot(), player.getXRot());
        }
        LOGGER.info("[HK3GTL] 坏结局完成 - 玩家: {} 存档已打毕业标记", player.getName().getString());
    }

    /** 服务器停止：清空所有静态运行时状态，防止跨存档串档/内存泄漏。 */
    @SubscribeEvent
    public static void onServerStopped(ServerStoppedEvent event) {
        bossActive = false;
        bossTicks.set(0);
        tauntIndex.set(0);
        kickExecuted = false;
        if (bossEvent != null) {
            bossEvent.removeAllPlayers();
            bossEvent = null;
        }
        FINALE_SESSIONS.clear();
    }

    /** 终局文本会话：按行推进，逐行 60 tick 间隔。 */
    private static final class FinaleSession {
        final UUID playerId;
        int lineIndex = 0;
        int cooldown = FINALE_LINE_INTERVAL;

        FinaleSession(UUID playerId) {
            this.playerId = playerId;
        }
    }
}
