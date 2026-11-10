package com.sirin.hk3gtl.common.multiblock.build;

import com.gregtechceu.gtceu.api.machine.MetaMachine;
import com.sirin.hk3gtl.common.machine.Hk3W01HallMachine;
import com.sirin.hk3gtl.common.multiblock.pattern.Hk3W01HallLayout;
import com.sirin.hk3gtl.common.multiblock.pattern.Hk3W01HallPattern;
import com.mojang.logging.LogUtils;
import it.unimi.dsi.fastutil.longs.LongOpenHashSet;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.network.chat.Component;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.server.level.TicketType;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.ChunkPos;
import net.minecraft.world.level.block.*;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraftforge.common.util.BlockSnapshot;
import net.minecraftforge.event.ForgeEventFactory;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.event.entity.player.PlayerEvent;
import net.minecraftforge.event.level.ChunkEvent;
import net.minecraftforge.event.server.ServerStoppingEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import org.gtlcore.gtlcore.common.item.UltimateTerminalBehavior;
import org.slf4j.Logger;

import java.util.Comparator;
import java.util.Map;
import java.util.UUID;
import java.util.concurrent.ConcurrentHashMap;

/** W01创造模式真实终极终端适配；不提供免费生存取料，不直接写成型标志。 */
/**
 * 【文件职责】真实终极终端入口的W01创造分tick搭建；校验权限、冲突、物理放置及最终GT成型。
 * 【变更记录 #1】2026-10-29 23:48:50（第1次备注 · 内测5修订183）
 * - 删除：BUILD阶段三遍全体跳读、已加载区块新票强制空等一tick及正常到点收尾的警告刷屏。
 * - 新增：2至12毫秒自适应预算，准备阶段65536步、放置阶段8192步双重上限，始终按原生区块加载状态等待。
 * - 修改：阶段与高度索引直接单遍消费；保留Forge放置事件、回滚、逐格状态与取消清理。
 * - 用途：提高空闲服务器搭建吞吐；不热部署、不改存档、不冻结重力/珊瑚，生存取料仍明确拒绝。
 * 【变更记录 #2】2026-10-30 00:08:31（第2次备注 · 内测5修订183）
 * 删除：独立的朝北零转映射；新增：无；修改：调用Pattern共用的西入口朝向映射。
 * 用途：新主控的四向搭建位置、真实状态和成型检测保持一致。
 */
@Mod.EventBusSubscriber(modid = "hk3gtl", bus = Mod.EventBusSubscriber.Bus.FORGE)
public final class Hk3W01TerminalBuilder {
    private static final Logger LOGGER = LogUtils.getLogger();
    private static final TicketType<Long> TICKET = TicketType.create("hk3gtl_w01_terminal", Comparator.<Long>naturalOrder());
    // 本轮专用验收仅允许每个服务器一项任务，避免多项巨构叠加主线程预算。
    private static final Map<MinecraftServer, Job> JOBS = new ConcurrentHashMap<>();
    private Hk3W01TerminalBuilder() {}

    public static void use(Player player, Hk3W01HallMachine hall,
            UltimateTerminalBehavior.AutoBuildSetting settings) {
        if (!(player instanceof ServerPlayer owner) || !(hall.getLevel() instanceof ServerLevel level)) return;
        if (!owner.isCreative()) { tell(owner, "survival"); return; }
        if (settings.isFlipped() || hall.getFrontFacing().getAxis().isVertical() || hall.getUpwardsFacing() != Direction.NORTH) {
            tell(owner, "orientation"); return;
        }
        Job previous = JOBS.get(level.getServer());
        if (previous != null) {
            if (previous.hall != hall || !previous.owner.equals(owner.getUUID())) { tell(owner, "busy"); return; }
            if (previous.stage == Stage.WAIT || previous.stage == Stage.COMPLETE) { previous.report(); return; }
            previous.paused = !previous.paused;
            tell(owner, previous.paused ? "paused" : "resumed");
            return;
        }
        if (!(hall.getPattern() instanceof Hk3W01HallPattern pattern)) return;
        Job job = new Job(owner, hall, pattern, level);
        if (!job.inBounds()) { tell(owner, "bounds"); return; }
        JOBS.put(level.getServer(), job);
        hall.setTerminalBuilding(true);
        tell(owner, "started");
    }

    public static void cancel(Player player, Hk3W01HallMachine hall) {
        if (!(player instanceof ServerPlayer owner)) return;
        Job job = JOBS.get(owner.server);
        if (job == null || job.hall != hall) { tell(owner, "nothing"); return; }
        if (!job.owner.equals(owner.getUUID())) { tell(owner, "busy"); return; }
        release(owner.server, "cancelled");
    }

    @SubscribeEvent public static void tick(TickEvent.ServerTickEvent event) {
        if (event.phase != TickEvent.Phase.END) return;
        Job job = JOBS.get(event.getServer());
        if (job == null) return;
        long begin = System.nanoTime();
        long timeBudget = Hk3W01BuildBudget.nanos(event.getServer().getAverageTickTime());
        try {
            if (!job.valid()) { release(event.getServer(), "stopped"); return; }
            job.tick(begin + timeBudget);
            if (!job.paused && job.stage != Stage.COMPLETE && job.level.getGameTime() - job.reportTick >= 40) job.report();
        } catch (RuntimeException failure) {
            LOGGER.error("W01终极终端建造失败；保留已放实体并释放临时区块票据", failure);
            release(event.getServer(), "failed");
        } finally {
            long elapsed = System.nanoTime() - begin;
            job.maxBatchNanos = Math.max(job.maxBatchNanos, elapsed);
            if (elapsed > timeBudget + 1_000_000L) {
                job.slowBatches++;
                if (job.slowBatches == 1 || job.slowBatches % 100 == 0)
                    LOGGER.warn("W01终端批次超预算：{}ms，区块{}，累计{}批；下一批继续限时",
                            elapsed / 1_000_000.0, job.lastChunk, job.slowBatches);
            }
        }
    }

    @SubscribeEvent public static void logout(PlayerEvent.PlayerLoggedOutEvent event) {
        if (event.getEntity() instanceof ServerPlayer player) {
            Job job = JOBS.get(player.server);
            if (job != null && job.owner.equals(player.getUUID())) release(player.server, "stopped");
        }
    }
    @SubscribeEvent public static void chunkUnload(ChunkEvent.Unload event) {
        if (event.getLevel() instanceof ServerLevel level) {
            Job job = JOBS.get(level.getServer());
            if (job != null && job.level == level && new ChunkPos(job.center).equals(event.getChunk().getPos()))
                release(level.getServer(), "stopped");
        }
    }
    @SubscribeEvent public static void stopping(ServerStoppingEvent event) { release(event.getServer(), "stopped"); }

    private static void release(MinecraftServer server, String reason) {
        Job job = JOBS.remove(server);
        if (job == null) return;
        job.hall.setTerminalBuilding(false);
        for (long chunk : job.tickets) job.level.getChunkSource().removeRegionTicket(TICKET,
                new ChunkPos(chunk), 2, job.center.asLong());
        job.tickets.clear();
        ServerPlayer owner = server.getPlayerList().getPlayer(job.owner);
        if (owner != null) tell(owner, reason);
        LOGGER.info("W01终端任务结束：{}，已放{}格，超预算{}批，峰值{}ms；不拆实体",
                reason, job.placed, job.slowBatches, job.maxBatchNanos / 1_000_000.0);
    }

    private static void tell(Player player, String key, Object... args) {
        player.sendSystemMessage(Component.translatable("hk3gtl.w01.terminal." + key, args));
    }
    private enum Stage { COUNT, ORDER, BUILD, WAIT, COMPLETE }

    private static final class Job {
        private final UUID owner;
        private final Hk3W01HallMachine hall;
        private final Hk3W01HallPattern pattern;
        private final ServerLevel level;
        private final BlockPos center;
        private final Direction facing;
        private final int turn;
        private final Hk3W01HallLayout data = Hk3W01HallPattern.layout();
        private Hk3W01BuildOrder order;
        private final byte[] phases;
        private final LongOpenHashSet tickets = new LongOpenHashSet();
        private final BlockPos.MutableBlockPos pos = new BlockPos.MutableBlockPos();
        private Stage stage = Stage.COUNT;
        private int preparation, cursor, checked, placed;
        private boolean paused;
        private long reportTick, slowBatches, maxBatchNanos;
        private long lastChunk = Long.MIN_VALUE;

        private Job(ServerPlayer owner, Hk3W01HallMachine hall, Hk3W01HallPattern pattern, ServerLevel level) {
            this.owner = owner.getUUID(); this.hall = hall; this.pattern = pattern; this.level = level;
            center = hall.getPos().immutable(); facing = hall.getFrontFacing();
            turn = Hk3W01HallPattern.turnForFront(facing);
            phases = new byte[data.palette().size()];
            for (int i = 0; i < phases.length; i++) {
                Block block = pattern.expectedState(i, turn).getBlock();
                phases[i] = (byte) (block instanceof FallingBlock ? 1
                        : block instanceof BushBlock || block instanceof SignBlock
                        || block instanceof BaseCoralPlantTypeBlock || block instanceof AmethystClusterBlock ? 2 : 0);
            }
            order = new Hk3W01BuildOrder(data.cells(), data.height(), phases);
        }

        private boolean inBounds() {
            Hk3W01HallPattern.position(pos, center, 0, 0, 0, turn);
            if (level.isOutsideBuildHeight(pos) || !level.getWorldBorder().isWithinBounds(pos)) return false;
            Hk3W01HallPattern.position(pos, center, data.width() - 1, data.height() - 1, data.depth() - 1, turn);
            return !level.isOutsideBuildHeight(pos) && level.getWorldBorder().isWithinBounds(pos);
        }
        private boolean valid() {
            ServerPlayer player = level.getServer().getPlayerList().getPlayer(owner);
            return player != null && player.isCreative() && player.level() == level
                    && hall.getFrontFacing() == facing && hall.getUpwardsFacing() == Direction.NORTH
                    && level.getChunkSource().getChunkNow(center.getX() >> 4, center.getZ() >> 4) != null
                    && MetaMachine.getMachine(level, center) == hall;
        }
        private ServerPlayer player() { return level.getServer().getPlayerList().getPlayer(owner); }

        private void tick(long deadline) {
            if (paused) return;
            if (stage == Stage.COMPLETE) {
                if (!hall.isFormed()) release(level.getServer(), "invalidated");
                return;
            }
            long controllerChunk = ChunkPos.asLong(center.getX() >> 4, center.getZ() >> 4);
            if (tickets.add(controllerChunk)) {
                level.getChunkSource().addRegionTicket(TICKET, new ChunkPos(controllerChunk), 2, center.asLong());
            }
            if (stage == Stage.WAIT) {
                if (hall.isFormed()) {
                    stage = Stage.COMPLETE;
                    tell(player(), "complete", placed, tickets.size());
                    LOGGER.info("W01终端实体搭建并通过真实GT成型；已放{}格，跳过{}格，临时票{}块",
                            placed, checked - placed, tickets.size());
                } else if (level.getGameTime() - reportTick >= 100) { report(); }
                return;
            }
            int steps = stage == Stage.COUNT || stage == Stage.ORDER
                    ? Hk3W01BuildBudget.PREPARATION_STEPS : Hk3W01BuildBudget.BUILD_STEPS;
            for (int n = 0; n < steps && System.nanoTime() < deadline; n++) {
                if (stage == Stage.COUNT || stage == Stage.ORDER) {
                    boolean done = order.step();
                    if (++preparation == data.cells().length) stage = Stage.ORDER;
                    if (done) { stage = Stage.BUILD; return; }
                    continue;
                }
                if (cursor == data.cells().length) {
                    stage = Stage.WAIT; order = null; hall.setTerminalBuilding(false);
                    tell(player(), "verifying"); return;
                }
                long cell = order.cell(cursor);
                Hk3W01HallPattern.position(pos, center, Hk3W01HallLayout.x(cell),
                        Hk3W01HallLayout.y(cell), Hk3W01HallLayout.z(cell), turn);
                if (pos.equals(center)) { cursor++; checked++; continue; }
                lastChunk = ChunkPos.asLong(pos.getX() >> 4, pos.getZ() >> 4);
                if (tickets.add(lastChunk)) {
                    level.getChunkSource().addRegionTicket(TICKET, new ChunkPos(lastChunk), 2, center.asLong());
                }
                // 只投递一张新票，等待原生区块加载；禁止getChunk同步生成卡住服务器。
                if (level.getChunkSource().getChunkNow(pos.getX() >> 4, pos.getZ() >> 4) == null) return;
                BlockState expected = pattern.expectedState(cell, turn);
                BlockState present = level.getBlockState(pos);
                if (present != expected) {
                    if (!present.canBeReplaced()) { pause("conflict", pos.toShortString(), BuiltInRegistries.BLOCK.getKey(present.getBlock()).toString()); return; }
                    ServerPlayer player = player();
                    if (!level.mayInteract(player, pos) || !player.mayUseItemAt(pos, Direction.UP, player.getMainHandItem())) {
                        pause("permission", pos.toShortString()); return;
                    }
                    BlockSnapshot before = BlockSnapshot.create(level.dimension(), level, pos.immutable());
                    // 精确蓝图状态使用局部放置标志，不全局关闭流体、重力、随机tick或其他机器检测。
                    try {
                        if (!level.setBlock(pos, expected, Block.UPDATE_CLIENTS | Block.UPDATE_KNOWN_SHAPE)) {
                            pause("placement", pos.toShortString()); return;
                        }
                        if (ForgeEventFactory.onBlockPlace(player, before, Direction.UP)) {
                            before.restore(true, false); pause("permission", pos.toShortString()); return;
                        }
                    } catch (RuntimeException failure) {
                        before.restore(true, false); throw failure;
                    }
                    if (level.getBlockState(pos) != expected) { pause("placement", pos.toShortString()); return; }
                    placed++;
                }
                cursor++; checked++;
            }
        }

        private void pause(String key, Object... args) { paused = true; tell(player(), key, args); }
        private void report() {
            reportTick = level.getGameTime();
            if (stage == Stage.WAIT) { tell(player(), "waiting"); return; }
            if (stage == Stage.COMPLETE) {
                if (hall.isFormed()) tell(player(), "complete", placed, tickets.size());
                else release(level.getServer(), "invalidated");
                return;
            }
            if (stage == Stage.COUNT || stage == Stage.ORDER) tell(player(), "preparing", preparation, data.cells().length * 2);
            else tell(player(), "progress", checked, data.cells().length, placed, tickets.size());
        }
    }
}
