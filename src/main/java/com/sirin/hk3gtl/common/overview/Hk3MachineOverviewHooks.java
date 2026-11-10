package com.sirin.hk3gtl.common.overview;

import com.gregtechceu.gtceu.api.machine.MetaMachine;
import com.gregtechceu.gtceu.api.machine.IMachineBlockEntity;
import com.sirin.hk3gtl.common.machine.Hk3WorkableMultiblockMachine;
import com.sirin.hk3gtl.common.research.Hk3ResearchTeams;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.server.MinecraftServer;
import net.minecraft.core.BlockPos;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.event.server.ServerStoppedEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;

import java.lang.ref.WeakReference;
import java.util.ArrayDeque;
import java.util.HashMap;
import java.util.Map;
import java.util.UUID;

/**
 * 【文件职责】隔离GT生命周期旁路观察；只在真实服务端主线程向总览账本提交。
 * 【变更记录 #1】2026-10-19 02:07:23（第1次备注 · 修订171）
 * 删除：无。新增：放置者权威归属、加载观察、卸载快照、方块移除与结构变化入口。
 * 修改：无；预览世界和异步结构回调不写账本，后者由有预算的已登记位置补查收敛。
 * 用途：不改GT原回调结果；观察异常被隔离且仅输出调试日志，不使机器操作失败。
 */
/**
 * 【变更记录 #2】2026-10-19 02:16:00（第2次备注 · 修订171）
 * 删除：放置事务尚可被Forge取消时立即修改总览的路径。
 * 新增：下一tick最多64候选的FIFO提交队列、过渡位置屏蔽、4096上限及停服清理。
 * 修改：放置重验同一真实BE；拆除后恢复原BE则保留归属；弱引用不留存世界、机器或服务器。
 * 用途：避免取消/回滚被当成功或吞掉旧归属；无法安全重验及过载时仅撤销索引，不授权他人。
 */
/**
 * 【变更记录 #3】2026-10-19 02:19:26（第3次备注 · 修订171）
 * 删除：HK加载时提前恢复归属、普通加载候选遇卸载时删除目录的过渡分支。
 * 新增：持久归属加载候选；修改：同一BE确认后才恢复，正常卸载保留快照，逐候选隔离第三方读异常。
 * 用途：回滚窗口不抢占归属，坏控制器不打断服务器；账本保护在循环外先初始化，不把损坏账本当普通观察失败。
 */
/**
 * 【变更记录 #4】2026-10-19 02:25:53（第4次备注 · 修订171）
 * 删除：持久归属加载候选在4096项队列饱和时删除已有有效索引的分支。
 * 新增：过载加载只保留未加载快照；Service通过原有64项轮转重新提交同BE、后继tick和持久归属复核。
 * 修改：普通放置/拆除过载仍撤销不确定索引；不增加重试集合、不扫描世界、不从历史条目猜测新归属。
 * 用途：已有大基地加载峰值不会永久丢目录；未登记且超过候选限额的机器仍须现场登记，不冒充全覆盖。
 */
@Mod.EventBusSubscriber(modid = "hk3gtl")
public final class Hk3MachineOverviewHooks {
    private enum Action { PLACED, REMOVED, OWNED_LOAD }
    private record Position(int server, String dimension, long position) {}
    private record Pending(WeakReference<MinecraftServer> server, WeakReference<MetaMachine> machine,
                           UUID actor, Action action, Position position, long eligible, long expires) {}
    private static final ArrayDeque<Pending> PENDING = new ArrayDeque<>();
    private static final Map<Position, Integer> TRANSITIONS = new HashMap<>();
    private Hk3MachineOverviewHooks() {}

    public static void placed(MetaMachine machine, ServerPlayer actor) {
        if (!available(machine) || actor.level() != machine.getLevel()) return;
        enqueue(machine, actor.getUUID(), Action.PLACED);
    }

    public static boolean isPending(ServerLevel level, BlockPos pos) {
        return TRANSITIONS.containsKey(position(level, pos));
    }
    public static boolean isPending(MetaMachine machine) {
        return machine.getLevel() instanceof ServerLevel level && isPending(level, machine.getPos());
    }
    private static Position position(ServerLevel level, BlockPos pos) {
        return new Position(System.identityHashCode(level.getServer()), level.dimension().location().toString(), pos.asLong());
    }
    private static void enqueue(MetaMachine machine, UUID actor, Action action) {
        ServerLevel level = (ServerLevel) machine.getLevel();
        if (PENDING.size() >= 4096) {
            overflow(Hk3MachineOverviewData.get(level.getServer()), level.dimension().location().toString(),
                    machine.getPos().asLong(), action == Action.OWNED_LOAD);
            return;
        }
        Position key = position(level, machine.getPos());
        long now = level.getServer().getTickCount();
        PENDING.addLast(new Pending(new WeakReference<>(level.getServer()), new WeakReference<>(machine), actor, action, key, now + 1, now + 201));
        TRANSITIONS.merge(key, 1, Integer::sum);
    }

    /** 只对已有加载快照延迟恢复；替换事务不能据旧条目继续授权。 */
    static void overflow(Hk3MachineOverviewData data, String dimension, long position, boolean ownedLoad) {
        if (ownedLoad) data.unloaded(dimension, position);
        else data.remove(dimension, position);
    }

    static boolean needsLoadVerification(Hk3MachineOverviewData.Entry entry, boolean persistentOwner) {
        return persistentOwner && entry != null && !entry.loaded();
    }

    private static void commitPlacement(MetaMachine machine, ServerPlayer actor) {
        Hk3MachineOverviewData.get(actor.server);
        var team = machine instanceof Hk3WorkableMultiblockMachine local ? local.getResearchTeamUUID()
                : Hk3ResearchTeams.scope(actor.server, actor.getUUID());
        try {
            Hk3MachineOverviewService.register(machine, team);
        } catch (RuntimeException | LinkageError failure) { report(machine, failure); }
    }

    public static void loaded(MetaMachine machine) {
        if (!available(machine)) return;
        if (machine instanceof Hk3WorkableMultiblockMachine) enqueue(machine, null, Action.OWNED_LOAD);
        else update(machine, 0);
    }
    public static void unloaded(MetaMachine machine) { update(machine, 1); }
    public static void removed(MetaMachine machine) { if (available(machine)) enqueue(machine, null, Action.REMOVED); }
    public static void changed(MetaMachine machine) { update(machine, 0); }

    private static void update(MetaMachine machine, int action) {
        if (!available(machine)) return;
        Hk3MachineOverviewData.get(((ServerLevel) machine.getLevel()).getServer());
        try {
            if (action == 1) Hk3MachineOverviewService.unloaded(machine);
            else if (action == 2) Hk3MachineOverviewService.removed(machine);
            else if (!isPending(machine)) Hk3MachineOverviewService.observe(machine);
        } catch (RuntimeException | LinkageError failure) { report(machine, failure); }
    }
    private static boolean available(MetaMachine machine) {
        return machine != null && machine.getLevel() instanceof ServerLevel level && level.getServer().isSameThread();
    }
    private static void report(MetaMachine machine, Throwable failure) {
        com.mojang.logging.LogUtils.getLogger().debug("[HK3-OVERVIEW] 机器总览观察失败：{}", machine.getClass().getName(), failure);
    }

    @SubscribeEvent public static void tick(TickEvent.ServerTickEvent event) {
        if (event.phase != TickEvent.Phase.END || PENDING.isEmpty()) return;
        MinecraftServer server = event.getServer();
        Hk3MachineOverviewData data = Hk3MachineOverviewData.get(server);
        int budget = Math.min(64, PENDING.size());
        while (budget-- > 0) {
            Pending next = PENDING.removeFirst();
            if (next.server().get() == server && server.getTickCount() < next.eligible()) {
                PENDING.addLast(next);
                continue;
            }
            TRANSITIONS.computeIfPresent(next.position(), (key, count) -> count > 1 ? count - 1 : null);
            if (next.server().get() != server) continue;
            MetaMachine machine = next.machine().get();
            try {
                if (!available(machine)) {
                    if (next.action() == Action.REMOVED)
                        data.remove(next.position().dimension(), next.position().position());
                    continue;
                }
                ServerLevel level = (ServerLevel) machine.getLevel();
                if (!level.hasChunkAt(machine.getPos()) || server.getTickCount() > next.expires()) {
                    update(machine, next.action() == Action.REMOVED ? 2 : 1);
                    continue;
                }
                boolean same = level.getBlockEntity(machine.getPos()) instanceof IMachineBlockEntity holder && holder.getMetaMachine() == machine;
                if (next.action() == Action.REMOVED) {
                    if (!same) update(machine, 2);
                    else update(machine, 0);
                } else if (next.action() == Action.OWNED_LOAD && same && !machine.isInValid()) {
                    Hk3MachineOverviewService.register(machine, ((Hk3WorkableMultiblockMachine) machine).getResearchTeamUUID());
                } else if (same && !machine.isInValid()) {
                    ServerPlayer actor = server.getPlayerList().getPlayer(next.actor());
                    if (actor != null) commitPlacement(machine, actor);
                }
            } catch (RuntimeException | LinkageError failure) {
                if (machine != null) report(machine, failure);
                data.remove(next.position().dimension(), next.position().position());
            }
        }
    }
    @SubscribeEvent public static void stopped(ServerStoppedEvent event) {
        PENDING.clear();
        TRANSITIONS.clear();
    }
}
