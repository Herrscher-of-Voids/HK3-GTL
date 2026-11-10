package com.sirin.hk3gtl.common.machine.research;


/**
 * 【文件职责】
 * - 定义 Hk3ResearchMatrixMachine 机器行为与结构逻辑。
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
 * 【变更记录 #2】2026-06-28 02:45:00（第 2 次备注 · 内测三第 23 次更新）
 * - 删除：无。
 * - 新增：重写 enableMultiRecipe() 返回 false。
 * - 修改：无业务逻辑改动。
 * - 用途：研究矩阵由 onServerTick 全局驱动、不跑标准配方，需排除基类新增的“多配方同时运行”逻辑，
 *   避免挂载无意义/可能干扰研究扣电的 RecipeLogic。
 *
 * 【段内说明】
 * - 复杂方法补充“干什么 / 边界 / 线程侧”精简中文注释。
 */
import com.gregtechceu.gtceu.api.machine.IMachineBlockEntity;
import com.sirin.hk3gtl.common.constants.Hk3Constants;
import com.sirin.hk3gtl.common.machine.Hk3WorkableMultiblockMachine;
import com.sirin.hk3gtl.common.gaze.Hk3GazeManager;
import com.sirin.hk3gtl.common.research.Hk3ResearchFailureTracker;
import com.sirin.hk3gtl.common.research.Hk3ResearchManager;
import com.sirin.hk3gtl.common.research.Hk3ResearchNode;
import com.sirin.hk3gtl.common.research.Hk3ResearchNodes;
import net.minecraft.core.BlockPos;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.entity.player.Inventory;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.entity.BlockEntity;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import org.slf4j.Logger;
import com.mojang.logging.LogUtils;

import javax.annotation.Nullable;
import java.util.Collections;
import java.util.List;
import java.util.Set;
import java.util.UUID;
import java.util.WeakHashMap;

/** 中文说明：该处说明已按当前代码行为整理。*/
@Mod.EventBusSubscriber(modid = Hk3Constants.MOD_ID, bus = Mod.EventBusSubscriber.Bus.FORGE)
/**
 * 【变更记录 #3】2026-09-30 15:50:54（内测5修订109）
 * 删除：旧线性压力与旁置设施加速。新增：机器位置的同队真实锚查询。
 * 修改：旧课题仍是原个人归属，采用非S01复合压力；用途：不以旧入口绕过新公式。
 */
public class Hk3ResearchMatrixMachine extends Hk3WorkableMultiblockMachine {

    private static final Logger LOGGER = LogUtils.getLogger();

    /**
     * 全局活跃实例注册表。用 WeakHashMap 的 key-set，机器被 GC 时自动移除，
     * 不需要手动管理 onUnload 生命周期。synchronizedSet 兜底防止构造期并发修改。
     * <p>为什么不 override GT 的 serverTick：GTCEu 在 1.4.x 内 serverTick 签名在子类继承链
     * 中偶有变化，使用外部 tick 分发可以彻底解耦 GT 内部 tick 时序。</p>
     */
    private static final Set<Hk3ResearchMatrixMachine> INSTANCES =
            Collections.synchronizedSet(Collections.newSetFromMap(new WeakHashMap<>()));

    /** 当前正在研究的任务；null = 机器空闲（仅待机扣电） */
    @Nullable
    private ActiveResearch activeResearch;

    public Hk3ResearchMatrixMachine(IMachineBlockEntity holder) {
        super(holder);
        INSTANCES.add(this);
    }

    /**
     * 研究矩阵不走标准配方逻辑（由 onServerTick 全局驱动扣电与研究推进），
     * 必须排除“多配方同时运行”，避免挂载无意义的 RecipeLogic。
     */
    @Override
    protected boolean enableMultiRecipe() {
        return false;
    }

    /**
     * Forge {@link TickEvent.ServerTickEvent} 入口：每 tick 分发给所有活跃矩阵实例。
     * 注意：phase END 保证本 tick 内方块实体已完成自身 tick，扣电顺序稳定。
     */
    @SubscribeEvent
    public static void onServerTick(TickEvent.ServerTickEvent event) {
        if (event.phase != TickEvent.Phase.END) return;
        synchronized (INSTANCES) {
            for (Hk3ResearchMatrixMachine m : INSTANCES) {
                try {
                    m.tickLogic();
                } catch (Throwable t) {
                    LOGGER.error("[HK3GTL] 研究矩阵 tick 异常", t);
                }
            }
        }
    }

    // ═══════════════════════════════════════
    //  生命周期：结构成型/无效化时清理状态
    // ═══════════════════════════════════════

    @Override
    public void onStructureInvalid() {
        super.onStructureInvalid();
        if (activeResearch != null) {
            LOGGER.info("[HK3GTL] 研究矩阵结构解散，中止研究 {}", activeResearch.researchId);
            activeResearch = null;
            markDirtyToPersist();
        }
    }

    // ═══════════════════════════════════════
    //  NBT 持久化（让研究状态在区块卸载/服务器重启后不丢失）
    // ═══════════════════════════════════════

    private static final String TAG_ACTIVE = "hk3gtl_active_research";

    private void saveActiveResearch(CompoundTag tag) {
        if (activeResearch != null) {
            tag.put(TAG_ACTIVE, activeResearch.toNbt());
        }
    }

    private void loadActiveResearch(CompoundTag tag) {
        if (tag.contains(TAG_ACTIVE)) {
            this.activeResearch = ActiveResearch.fromNbt(tag.getCompound(TAG_ACTIVE));
        } else {
            this.activeResearch = null;
        }
    }

    public CompoundTag saveCustomData(CompoundTag tag) {
        saveActiveResearch(tag);
        return tag;
    }

    public void loadCustomData(CompoundTag tag) {
        loadActiveResearch(tag);
    }

    public CompoundTag writeAdditional(CompoundTag tag) {
        saveActiveResearch(tag);
        return tag;
    }

    public void readAdditional(CompoundTag tag) {
        loadActiveResearch(tag);
    }

    private void markDirtyToPersist() {
        if (getHolder() instanceof BlockEntity be) {
            be.setChanged();
        }
    }

    // ═══════════════════════════════════════
    //  每 tick 推进逻辑
    // ═══════════════════════════════════════

    /**
     * 每 tick 核心流程（由 GT 通过 {@code MetaMachine#serverTick} 回调驱动）。
     * 注意：只在服务端执行，客户端无需扣电。
     *
     * <p>{@code super.serverTick()} 保留以让 GT 的能源仓 accept-from-network 与 RecipeLogic
     * 基础 tick 继续工作；本机器虽然不跑 RecipeType，但 super tick 里的能源容器聚合/同步
     * 逻辑仍必须跑，否则 {@link #consumeEnergy} 拿不到新进来的电能。</p>
     */
    @Override
    public void onStructureFormed() {
        super.onStructureFormed();
        // 结构成型时清空可能残留的 activeResearch（比如旧存档里留下的无效 UUID）
        if (activeResearch != null && Hk3ResearchNodes.get(activeResearch.researchId) == null) {
            activeResearch = null;
        }
    }

    /**
     * 研究矩阵自定义 tick 逻辑：扣待机电 → 推进进度 → 条件满足则完成研究。
     * 由 {@link #onServerTick} 统一驱动，不依赖 GT 内部 tick 机制。
     */
    public void tickLogic() {
        if (!isStructureReady()) return;
        Level lvl = getLevelSafe();
        if (!(lvl instanceof ServerLevel serverLevel)) return;

        if (activeResearch == null) {
            // 纯待机：只扣 IDLE
            consumeEnergy(Hk3Constants.RESEARCH_MATRIX_IDLE_EUT_PER_TICK);
            return;
        }

        ServerPlayer starter = serverLevel.getServer().getPlayerList().getPlayer(activeResearch.playerUuid);
        if (starter == null) {
            // 启动研究的玩家离线 → 整机暂停：不扣电、不推进
            return;
        }

        long needed = Hk3Constants.RESEARCH_MATRIX_IDLE_EUT_PER_TICK + activeResearch.extraEutPerTick;
        if (!consumeEnergy(needed)) {
            // 电不够：推进暂停，但不中断研究（等玩家补电后继续）
            // 注意：IDLE 部分也没扣到，这是合理的，因为"电不够 = 机器实际没运行"
            return;
        }

        var team = com.sirin.hk3gtl.common.research.Hk3ResearchTeams.scope(starter.server, starter.getUUID());
        double gaze = com.sirin.hk3gtl.common.research.Hk3ResearchTeams.gaze(starter.server, team);
        double suppression = com.sirin.hk3gtl.common.gaze.Hk3ResearchSuppression.at(serverLevel, getPos(), team);
        double speedFactor = com.sirin.hk3gtl.common.research.Hk3ResearchMath.speed(2, gaze, suppression, false, false);

        activeResearch = activeResearch.withSpeedFactor(speedFactor).advance(speedFactor);
        if (activeResearch.progress >= activeResearch.totalTicks) {
            finish(starter);
        } else {
            if (serverLevel.getGameTime() % 20L == 0L) {
                // 研究中每秒同步一次，保证客户端倒计时连续更新。
                Hk3ResearchManager.syncClientResearchState(starter);
            }
            if (serverLevel.getGameTime() % 100L == 0L) {
                // 每 5 秒持久化一次，避免每 tick 都 setChanged 造成 IO 压力。
                markDirtyToPersist();
            }
        }
    }

    /**
     * 研究完成：物品检查 → 1/100 失败掷骰 → 消耗物品 → 标记完成 → 清空状态。
     *
     * <h4>失败设计</h4>
     * <ul>
     *   <li>掷骰发生在物品消耗之前，失败时不消耗任何物品</li>
     *   <li>失败概率由 {@link Hk3ResearchFailureTracker#getFailChance(Player)} 决定（默认 1%，触发非酋彩蛋后 0.5%）</li>
     *   <li>失败后玩家可以立即重新提交（材料还在背包，进度归零）</li>
     *   <li>累计失败次数由 {@link Hk3ResearchFailureTracker#onResearchFailed} 维护，
     *       达到阈值会一次性触发非酋彩蛋（独立流程，不影响本机器逻辑）</li>
     * </ul>
     *
     * <p>若玩家背包在进度到达时已经不足（可能把材料给别人了），则<b>白跑一场电</b>但
     * 仍标记失败以免研究线卡死。</p>
     */
    private void finish(ServerPlayer starter) {
        Hk3ResearchNode node = Hk3ResearchNodes.get(activeResearch.researchId);
        if (node == null) {
            LOGGER.warn("[HK3GTL] activeResearch 关联的节点不存在: {}", activeResearch.researchId);
            activeResearch = null;
            markDirtyToPersist();
            return;
        }

        Inventory inv = starter.getInventory();
        if (!Hk3ResearchManager.hasRequirements(inv, node)) {
            starter.sendSystemMessage(Component.translatable("hk3gtl.research.matrix.finish_missing_items",
                    Component.translatable(node.nameKey())));
            activeResearch = null;
            markDirtyToPersist();
            return;
        }

        // 1/100 失败判定（可由非酋彩蛋永久减半）
        double chance = Hk3ResearchFailureTracker.getFailChance(starter);
        if (starter.getRandom().nextDouble() < chance) {
            // 失败：不消耗物品，进度清零，玩家可立即重试
            Hk3ResearchFailureTracker.onResearchFailed(starter, node.nameKey());
            activeResearch = null;
            markDirtyToPersist();
            return;
        }

        Hk3ResearchManager.consumeRequirements(inv, node);
        Hk3ResearchManager.forceCompleteResearch(starter, node.id());
        Hk3ResearchManager.syncClientResearchState(starter);

        starter.sendSystemMessage(Component.translatable("hk3gtl.research.matrix.finish_ok",
                Component.translatable(node.nameKey())));

        activeResearch = null;
        markDirtyToPersist();
    }

    // ═══════════════════════════════════════
    //  对外公开入口：由 Hk3ResearchManager 调用
    // ═══════════════════════════════════════

    /**
     * 尝试在当前矩阵上启动一个研究节点。调用前 Manager 已经做过前置/物品校验。
     *
     * @return true 表示启动成功；false 表示机器正忙或未成型
     */
    public boolean tryStart(ServerPlayer player, Hk3ResearchNode node) {
        if (!isStructureReady()) {
            player.sendSystemMessage(Component.translatable("hk3gtl.research.matrix.not_formed"));
            return false;
        }
        if (activeResearch != null) {
            Hk3ResearchNode activeNode = Hk3ResearchNodes.get(activeResearch.researchId);
            Component activeName = activeNode == null
                    ? Component.literal(activeResearch.researchId)
                    : Component.translatable(activeNode.nameKey());
            player.sendSystemMessage(Component.translatable("hk3gtl.research.matrix.busy",
                    activeName));
            return false;
        }
        int total = ResearchDifficulty.durationTicks(node);
        long extra = ResearchDifficulty.extraEutPerTick(node);
        this.activeResearch = new ActiveResearch(player.getUUID(), node.id(), 0, 0.0D, total, extra, 1.0D);
        markDirtyToPersist();

        player.sendSystemMessage(Component.translatable("hk3gtl.research.matrix.started",
                Component.translatable(node.nameKey()),
                formatSeconds(total),
                String.format("%.1f", (Hk3Constants.RESEARCH_MATRIX_IDLE_EUT_PER_TICK + extra) / 1_000_000.0)));
        return true;
    }

    /** 强制取消当前研究（命令调试用，普通玩法不对外） */
    public void cancel() {
        activeResearch = null;
        markDirtyToPersist();
    }

    public boolean isBusy() {
        return activeResearch != null;
    }

    /** 给客户端 / GUI 读的快照，仅返回值类型字段，避免直接暴露内部可变对象 */
    @Nullable
    public Snapshot snapshot() {
        if (activeResearch == null) return null;
        return new Snapshot(activeResearch.researchId, activeResearch.progress,
                activeResearch.totalTicks, activeResearch.extraEutPerTick, activeResearch.speedFactor);
    }

    // ═══════════════════════════════════════
    //  辅助工具
    // ═══════════════════════════════════════

    /** 通过反射/字段路径兜底读取 machine 是否成型。失败默认返回 false（不扣电） */
    private boolean isStructureReady() {
        try {
            Object v = this.getClass().getMethod("isFormed").invoke(this);
            if (v instanceof Boolean b) return b;
        } catch (NoSuchMethodError | Exception ignored) {}
        // 无 isFormed 时：看 holder/parts 是否初始化过，保守判定
        try {
            Object parts = this.getClass().getMethod("getParts").invoke(this);
            return parts != null;
        } catch (NoSuchMethodError | Exception ignored) {}
        return false;
    }

    /** 通过 holder 拿到 Level；失败返回 null */
    @Nullable
    private Level getLevelSafe() {
        Object holder = getHolder();
        if (holder instanceof BlockEntity be) return be.getLevel();
        return null;
    }

    /** 中文说明：该处说明已按当前代码行为整理。*/
    private boolean consumeEnergy(long amount) {
        // 只使用 GT 原生能源仓；本模组不再注册自定义 EU/激光/并行仓。
        try {
            Object container = this.getClass().getMethod("getEnergyContainer").invoke(this);
            if (container == null) return false;

            long stored = ((Number) container.getClass().getMethod("getEnergyStored").invoke(container)).longValue();
            if (stored < amount) return false;

            container.getClass().getMethod("removeEnergy", long.class).invoke(container, amount);
            return true;
        } catch (NoSuchMethodError | Exception e) {
            // 签名不匹配 / 未能源仓：不推进研究，避免无能源仓也能完成。
            if (activeResearch != null) {
                LOGGER.warn("[HK3GTL] 研究矩阵能量接口不可用，研究暂停：{}", e.toString());
            }
            return false;
        }
    }

    private static String formatSeconds(int ticks) {
        int totalSec = ticks / 20;
        int min = totalSec / 60;
        int sec = totalSec % 60;
        return min > 0 ? (min + "m" + sec + "s") : (sec + "s");
    }

    // ═══════════════════════════════════════
    //  静态工具：在玩家周围查找已成型的研究矩阵
    // ═══════════════════════════════════════

    /**
     * 在玩家所在维度、以玩家为中心 {@link Hk3Constants#RESEARCH_MATRIX_SEARCH_RADIUS} 半径范围内，
     * 查找最近的已成型且空闲的研究矩阵。
     *
     * <p>实现策略：遍历区域内 BlockEntity，按距离排序优先返回空闲矩阵，
     * 没有空闲时返回最近的忙碌矩阵（用于给出"机器正忙"错误信息）。</p>
     *
     * @return 最近的研究矩阵机器，或 null
     */
    @Nullable
    public static Hk3ResearchMatrixMachine findNearest(Player player) {
        Level level = player.level();
        BlockPos playerPos = player.blockPosition();
        int r = Hk3Constants.RESEARCH_MATRIX_SEARCH_RADIUS;

        Hk3ResearchMatrixMachine nearestFree = null;
        Hk3ResearchMatrixMachine nearestAny = null;
        double bestFreeDist = Double.MAX_VALUE;
        double bestAnyDist = Double.MAX_VALUE;

        // 按区块遍历 BlockEntity，避免 r^3 次 getBlockState 的 O(256^3) 代价
        List<BlockEntity> entities = collectNearbyEntities(level, playerPos, r);

        for (BlockEntity be : entities) {
            BlockPos pos = be.getBlockPos();
            if (pos.distSqr(playerPos) > (long) r * r) continue;
            Hk3ResearchMatrixMachine m = extractMachine(be);
            if (m == null || !m.isStructureReady()) continue;

            double d = pos.distSqr(playerPos);
            if (d < bestAnyDist) {
                bestAnyDist = d;
                nearestAny = m;
            }
            if (!m.isBusy() && d < bestFreeDist) {
                bestFreeDist = d;
                nearestFree = m;
            }
        }
        return nearestFree != null ? nearestFree : nearestAny;
    }

    /**
     * 收集玩家周围 r 格立方体内的所有 BlockEntity。
     * 使用 Level.blockEntityList 效率最好，但会扫整个维度 —— 折中使用区块遍历。
     */
    private static List<BlockEntity> collectNearbyEntities(Level level, BlockPos center, int r) {
        java.util.List<BlockEntity> out = new java.util.ArrayList<>();
        int chunkR = (r >> 4) + 1;
        int cx = center.getX() >> 4;
        int cz = center.getZ() >> 4;
        for (int dx = -chunkR; dx <= chunkR; dx++) {
            for (int dz = -chunkR; dz <= chunkR; dz++) {
                var chunk = level.getChunkSource().getChunkNow(cx + dx, cz + dz);
                if (chunk == null) continue;
                out.addAll(chunk.getBlockEntities().values());
            }
        }
        return out;
    }

    /** 从 BlockEntity 上取 MetaMachine 实例并判定是否为 ResearchMatrixMachine */
    @Nullable
    private static Hk3ResearchMatrixMachine extractMachine(BlockEntity be) {
        if (!(be instanceof IMachineBlockEntity mbe)) return null;
        Object machine = mbe.getMetaMachine();
        if (machine instanceof Hk3ResearchMatrixMachine m) return m;
        return null;
    }

    // ═══════════════════════════════════════
    //  内部数据类
    // ═══════════════════════════════════════

    /**
     * 机器内部维护的活跃研究任务。
     *
     * @param playerUuid 启动研究的玩家 UUID；玩家离线时暂停推进
     * @param researchId 研究节点 ID（如 "R-AB-004"）
     * @param progress 已推进 tick 数（0..totalTicks）
     * @param totalTicks 研究完成所需 tick 数
     * @param extraEutPerTick 该研究每 tick 叠加在 IDLE 之上的额外能耗
     */
    public record ActiveResearch(UUID playerUuid, String researchId,
                                 int progress, double progressRemainder,
                                 int totalTicks, long extraEutPerTick, double speedFactor) {

        ActiveResearch advance(double speed) {
            double totalProgress = progressRemainder + speed;
            int step = (int) Math.floor(totalProgress);
            double remainder = totalProgress - step;
            return new ActiveResearch(playerUuid, researchId, progress + step, remainder, totalTicks, extraEutPerTick, speedFactor);
        }

        ActiveResearch withSpeedFactor(double factor) {
            return new ActiveResearch(playerUuid, researchId, progress, progressRemainder, totalTicks, extraEutPerTick, factor);
        }

        CompoundTag toNbt() {
            CompoundTag tag = new CompoundTag();
            tag.putUUID("player", playerUuid);
            tag.putString("research", researchId);
            tag.putInt("progress", progress);
            tag.putDouble("progressRemainder", progressRemainder);
            tag.putInt("total", totalTicks);
            tag.putLong("extra", extraEutPerTick);
            tag.putDouble("speedFactor", speedFactor);
            return tag;
        }

        static ActiveResearch fromNbt(CompoundTag tag) {
            return new ActiveResearch(
                    tag.getUUID("player"),
                    tag.getString("research"),
                    tag.getInt("progress"),
                    tag.contains("progressRemainder") ? tag.getDouble("progressRemainder") : 0.0D,
                    tag.getInt("total"),
                    tag.getLong("extra"),
                    tag.contains("speedFactor") ? tag.getDouble("speedFactor") : 1.0D);
        }
    }

    /** 对外暴露给 GUI 的只读快照 */
    public record Snapshot(String researchId, int progress, int totalTicks, long extraEutPerTick, double speedFactor) {
        public double ratio() {
            return totalTicks <= 0 ? 0.0 : (double) progress / totalTicks;
        }
    }
}
