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

/**
 * 【文件职责】连接机器生命周期、权限归属与总览账本，只观察真实已加载实例。
 * 【变更记录 #1】2026-10-19 02:05:22（第1次备注 · 修订171）
 * 删除：无。新增：权威归属登记、现场绑定、观察、卸载/移除区分及每秒64项轮转校验、逐项观察故障隔离。
 * 修改：无；不持有静态世界或机器引用，不加载区块，不发放研究、物品或工程成果。
 * 用途：T03后端读模型与实际机器同步；第三方归属校验由适配入口执行，已绑定其他团队不可抢占。
 */
/**
 * 【变更记录 #2】2026-10-19 02:25:53（第2次备注 · 修订171）
 * 删除：HK未加载索引一经普通观察就直接恢复实时状态的路径。
 * 新增：原账本轮转和结构观察将该条目重新交给OWNED_LOAD候选，后继tick核对同BE与持久研究团队后才恢复。
 * 修改：复用现有64项/秒轮转及4096项候选上限；过载时保留未加载快照，不无限排队、不强载区块。
 * 用途：恢复突发加载被延迟的既有目录，且不能通过观察绕开pending或归属复核。
 */
/**
 * 【变更记录 #3】2026-10-19 02:29:04（第3次备注 · 修订171）
 * 删除：已加载位置读取异常时将原未加载条目写成实时UNKNOWN的路径。
 * 新增：观察失败按原可信加载状态处理；原未加载快照保留状态和时间，仍必须等待持久归属后继复核。
 * 修改：故障发布策略独立为可测方法，连续同故障仍不重复告警；用途：异常也不能绕过OWNED_LOAD恢复门槛。
 */
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
