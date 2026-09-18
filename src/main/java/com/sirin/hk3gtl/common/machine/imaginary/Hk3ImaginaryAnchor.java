package com.sirin.hk3gtl.common.machine.imaginary;



import com.gregtechceu.gtceu.api.machine.IMachineBlockEntity;
import com.gregtechceu.gtceu.api.machine.MetaMachine;
import com.gregtechceu.gtceu.api.machine.multiblock.WorkableElectricMultiblockMachine;
import com.sirin.hk3gtl.common.constants.Hk3Constants;
import net.minecraft.core.BlockPos;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.entity.BlockEntity;
import net.minecraft.world.level.chunk.LevelChunk;

import java.util.Map;
import java.util.Set;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.ConcurrentLinkedQueue;
import java.util.concurrent.ConcurrentMap;
import java.util.concurrent.atomic.AtomicInteger;

/**
 * 虚数锚定装置（imaginary_anchor_device）的环境依赖扫描器。
 *
 * <h3>职责</h3>
 * 提供两件事：
 * <ol>
 *   <li>判断"指定虚数 RecipeType"是否归本系统约束</li>
 *   <li>扫描指定半径内是否存在已成型且正在工作的虚数锚定装置</li>
 * </ol>
 *
 * <h3>性能策略</h3>
 * <ul>
 *   <li>扫描结果按 {@code level + 控制器 pos} 缓存 {@value #CACHE_TTL_TICKS} tick (~1.5 秒)，
 *       避免每 tick 都做 5×5 chunk 扫描造成 TPS 损失</li>
 *   <li>缓存按维度键索引；维度卸载时调用 {@link #invalidate(Level)} 清空</li>
 *   <li>{@link Level#getGameTime()} 单调递增，可直接用作时间戳</li>
 * </ul>
 */
public final class Hk3ImaginaryAnchor {

    /** 锚定装置的注册路径（不含命名空间）。 */
    public static final String ANCHOR_MACHINE_PATH = "imaginary_anchor_device";

    /** 受锚定约束的虚数 RecipeType 路径集合（不含 {@code gtceu:} 前缀）。
     * <p>注意：刻意不把 {@code imaginary_anchoring}（锚定装置自身）放进来，避免循环依赖。</p>
     */
    public static final Set<String> CONSTRAINED_RECIPE_TYPES = Set.of(
            "imaginary_circuit_computation",
            "soulium_superstructure_forging",
            "civilization_exchange",
            "precivilization_database_decoding",
            "honkai_phase_purification",
            "imaginary_matter_weaving",
            "imaginary_dream_melting",
            "dual_energy_stable_supply",
            "imaginary_tree_observation"
    );

    /** 锚定影响半径（方块） */
    public static final int ANCHOR_RADIUS = 64;

    /** 扫描缓存有效期（tick），1.5 秒 */
    private static final long CACHE_TTL_TICKS = 30L;

    /** 缓存条目：以"控制器 pos 的 long 值"为键，避免重复扫描同一台机器邻域。 */
    private record Entry(long gameTime, boolean hasAnchor) {}

    /** 到期清理票据；保留 Entry 身份以防并发刷新后误删新值。 */
    private record ExpiryTicket(long key, Entry entry) {}

    /** 单次读取最多处理的到期票据数，避免清理成本随缓存规模线性增长。 */
    private static final int CLEANUP_BATCH_SIZE = 8;

    /** 按维度保存缓存条目与有界清理队列（多机器并发推进时需要线程安全）。 */
    private static final class DimensionCache {
        private final ConcurrentMap<Long, Entry> entries = new ConcurrentHashMap<>();
        private final ConcurrentLinkedQueue<ExpiryTicket> expiryQueue = new ConcurrentLinkedQueue<>();
        private final AtomicInteger queuedTickets = new AtomicInteger();

        private Entry get(long key) {
            return entries.get(key);
        }

        private void put(long key, Entry entry) {
            entries.put(key, entry);
            expiryQueue.offer(new ExpiryTicket(key, entry));
            queuedTickets.incrementAndGet();
        }

        private void cleanup(long now) {
            int processed = 0;
            while (processed++ < CLEANUP_BATCH_SIZE) {
                ExpiryTicket ticket = expiryQueue.poll();
                if (ticket == null) return;
                queuedTickets.decrementAndGet();
                if (now - ticket.entry().gameTime() >= CACHE_TTL_TICKS) {
                    entries.remove(ticket.key(), ticket.entry());
                } else {
                    expiryQueue.offer(ticket);
                    queuedTickets.incrementAndGet();
                    return;
                }
            }
        }
    }

    /** 按维度 key 存储缓存表（多机器并发推进时需要线程安全）。 */
    private static final Map<ResourceLocation, DimensionCache> CACHE = new ConcurrentHashMap<>();

    private Hk3ImaginaryAnchor() {}

    /**
     * 判断给定 RecipeType ID 是否归本系统约束。
     * @param recipeTypeId 形如 {@code gtceu:imaginary_circuit_computation} 或仅路径
     */
    public static boolean appliesTo(String recipeTypeId) {
        if (recipeTypeId == null || recipeTypeId.isEmpty()) return false;
        int colon = recipeTypeId.indexOf(':');
        String path = colon >= 0 ? recipeTypeId.substring(colon + 1) : recipeTypeId;
        return CONSTRAINED_RECIPE_TYPES.contains(path);
    }

    /**
     * 检查 {@code center} 周围 {@link #ANCHOR_RADIUS} 格内是否存在已成型的虚数锚定装置。
     * 使用按维度 + 中心点的 tick 缓存。
     *
     * @return true 表示锚定生效；false 表示没锚定（机器应进入"半速"模式）
     */
    public static boolean hasActiveAnchorNearby(Level level, BlockPos center) {
        if (level == null || level.isClientSide()) return false;
        ResourceLocation dim = level.dimension().location();
        long key = center.asLong();
        long now = level.getGameTime();

        DimensionCache dimCache = CACHE.computeIfAbsent(dim, k -> new DimensionCache());
        dimCache.cleanup(now);
        Entry cached = dimCache.get(key);
        if (cached != null && now - cached.gameTime < CACHE_TTL_TICKS) {
            return cached.hasAnchor;
        }

        boolean found = scan(level, center);
        dimCache.put(key, new Entry(now, found));
        return found;
    }

    /** 维度卸载时清缓存；服务器停止可调本方法防内存累积。 */
    public static void invalidate(Level level) {
        if (level == null) return;
        CACHE.remove(level.dimension().location());
    }

    private static boolean scan(Level level, BlockPos center) {
        int chunkRadius = (ANCHOR_RADIUS >> 4) + 1;
        int cx = center.getX() >> 4;
        int cz = center.getZ() >> 4;
        double radiusSq = (double) ANCHOR_RADIUS * ANCHOR_RADIUS;

        for (int dx = -chunkRadius; dx <= chunkRadius; dx++) {
            for (int dz = -chunkRadius; dz <= chunkRadius; dz++) {
                LevelChunk chunk = level.getChunkSource().getChunkNow(cx + dx, cz + dz);
                if (chunk == null) continue;
                for (BlockEntity be : chunk.getBlockEntities().values()) {
                    if (!(be instanceof IMachineBlockEntity mbe)) continue;
                    MetaMachine machine = mbe.getMetaMachine();
                    if (!(machine instanceof WorkableElectricMultiblockMachine wm)) continue;
                    ResourceLocation id = wm.getDefinition().getId();
                    if (id == null) continue;
                    if (!Hk3Constants.MOD_ID.equals(id.getNamespace())) continue;
                    if (!ANCHOR_MACHINE_PATH.equals(id.getPath())) continue;
                    if (!wm.isFormed()) continue;
                    double distSq = be.getBlockPos().distSqr(center);
                    if (distSq <= radiusSq) return true;
                }
            }
        }
        return false;
    }
}
