package com.sirin.hk3gtl.common.overview;

import com.gregtechceu.gtceu.api.machine.IMachineBlockEntity;
import com.gregtechceu.gtceu.api.machine.MetaMachine;
import com.sirin.hk3gtl.common.research.Hk3ResearchTeams;
import net.minecraft.core.BlockPos;
import net.minecraft.core.registries.Registries;
import net.minecraft.resources.ResourceKey;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import net.minecraftforge.server.ServerLifecycleHooks;

import java.util.UUID;

 






 






 





@Mod.EventBusSubscriber(modid = "hk3gtl")
public final class Hk3MachineOverviewService {
    private Hk3MachineOverviewService() {}
    public static void register(MetaMachine machine, UUID team) {
        ServerLevel level = serverLevel(machine);
        if (level == null || team == null) return;
        Hk3MachineOverviewData.get(level.getServer()).register(team, dimension(level), machine.getPos().asLong(),
                Hk3MachineOverviewAdapter.describe(machine), Hk3MachineOverviewAdapter.sample(machine), tick(level), true);
    }
    /** 服务再次核验玩家现场访问权限，并拒绝覆盖账本中其他团队的既有归属。 */
    public static boolean bind(ServerPlayer actor, MetaMachine machine) {
        ServerLevel level = serverLevel(machine);
        if (level == null || Hk3MachineOverviewHooks.isPending(level, machine.getPos())
                || !Hk3MachineOverviewAdapter.canBind(actor, machine))
            return false;
        UUID team = Hk3ResearchTeams.scope(actor.server, actor.getUUID());
        return Hk3MachineOverviewData.get(actor.server).register(team, dimension(level), machine.getPos().asLong(),
                Hk3MachineOverviewAdapter.describe(machine), Hk3MachineOverviewAdapter.sample(machine), tick(level), false);
    }
    public static void observe(MetaMachine machine) {
        ServerLevel level = serverLevel(machine);
        if (level == null || Hk3MachineOverviewHooks.isPending(level, machine.getPos())) return;
        Hk3MachineOverviewData data = Hk3MachineOverviewData.get(level.getServer());
        if (Hk3MachineOverviewHooks.needsLoadVerification(data.entry(dimension(level), machine.getPos().asLong()),
                machine instanceof com.sirin.hk3gtl.common.machine.Hk3WorkableMultiblockMachine)) {
            Hk3MachineOverviewHooks.loaded(machine);
            return;
        }
        data.observe(dimension(level), machine.getPos().asLong(),
                Hk3MachineOverviewAdapter.describe(machine), Hk3MachineOverviewAdapter.sample(machine), tick(level));
    }
    public static void invalidated(MetaMachine machine) { observe(machine); }
    public static void unloaded(MetaMachine machine) {
        ServerLevel level = serverLevel(machine); if (level != null)
            Hk3MachineOverviewData.get(level.getServer()).unloaded(dimension(level), machine.getPos().asLong());
    }
    public static void removed(MetaMachine machine) {
        ServerLevel level = serverLevel(machine); if (level != null)
            Hk3MachineOverviewData.get(level.getServer()).remove(dimension(level), machine.getPos().asLong());
    }
    public static Hk3MachineOverviewData.Page page(ServerPlayer actor, int page, String filter) {
        return Hk3MachineOverviewData.get(actor.server).page(Hk3ResearchTeams.scope(actor.server, actor.getUUID()), page, 4, filter);
    }
    public static Hk3MachineOverviewData.Entry detail(ServerPlayer actor, UUID id) {
        return Hk3MachineOverviewData.get(actor.server).visible(Hk3ResearchTeams.scope(actor.server, actor.getUUID()), id);
    }
    public static java.util.List<String> sources(ServerPlayer actor) {
        return Hk3MachineOverviewData.get(actor.server).sources(Hk3ResearchTeams.scope(actor.server, actor.getUUID()));
    }
    @SubscribeEvent public static void tick(TickEvent.ServerTickEvent event) {
        if (event.phase != TickEvent.Phase.END) return;
        MinecraftServer server = ServerLifecycleHooks.getCurrentServer();
        if (server == null || server.getTickCount() % 20 != 0) return;
        Hk3MachineOverviewData data = Hk3MachineOverviewData.get(server);
        for (var entry : data.refreshBatch(64)) refresh(server, data, entry);
    }
    /** 第三方控制器的读接口异常只影响该快照；不能中断服务端tick或据异常删除归属。 */
    private static void refresh(MinecraftServer server, Hk3MachineOverviewData data, Hk3MachineOverviewData.Entry entry) {
        boolean loaded = false;
        try {
            ServerLevel level = server.getLevel(ResourceKey.create(Registries.DIMENSION, new ResourceLocation(entry.dimension())));
            BlockPos pos = BlockPos.of(entry.position());
            if (level != null && Hk3MachineOverviewHooks.isPending(level, pos)) return;
            if (level == null || !level.hasChunkAt(pos)) { data.unloaded(entry.dimension(), entry.position()); return; }
            loaded = true;
            if (!(level.getBlockEntity(pos) instanceof IMachineBlockEntity holder)) { data.remove(entry.dimension(), entry.position()); return; }
            MetaMachine machine = holder.getMetaMachine();
            if (machine == null || !machine.getDefinition().getId().toString().equals(entry.descriptor().registryId())) {
                data.remove(entry.dimension(), entry.position()); return;
            }
            observe(machine);
        } catch (RuntimeException | LinkageError failure) {
            if (recordObservationFailure(data, entry, loaded, server.overworld().getGameTime()))
                com.mojang.logging.LogUtils.getLogger().warn("[HK3-OVERVIEW] 轮转观察首次失败：{}@{}", entry.dimension(), entry.position(), failure);
        }
    }
    /** 返回是否首次转入此故障；区块存在不等于机器加载和持久归属已通过后继复核。 */
    static boolean recordObservationFailure(Hk3MachineOverviewData data, Hk3MachineOverviewData.Entry entry,
                                            boolean positionLoaded, long tick) {
        if (!positionLoaded || !entry.loaded()) {
            data.unloaded(entry.dimension(), entry.position());
            return entry.loaded();
        }
        var failed = new Hk3MachineOverviewData.Observation(Hk3MachineOverviewData.State.UNKNOWN,
                "已加载位置的控制器观察失败；保留原归属和注册信息");
        data.observe(entry.dimension(), entry.position(), entry.descriptor(), failed, tick);
        return !entry.observation().equals(failed);
    }
    private static ServerLevel serverLevel(MetaMachine machine) {
        return machine != null && machine.getLevel() instanceof ServerLevel level ? level : null;
    }
    private static String dimension(ServerLevel level) { return level.dimension().location().toString(); }
    private static long tick(ServerLevel level) { return level.getServer().overworld().getGameTime(); }
}
