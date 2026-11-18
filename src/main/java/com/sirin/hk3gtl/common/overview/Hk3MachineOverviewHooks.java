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
        Hk3MachineOverviewService.register(machine, team);
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
        if (action == 1) Hk3MachineOverviewService.unloaded(machine);
        else if (!isPending(machine)) Hk3MachineOverviewService.observe(machine);
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
