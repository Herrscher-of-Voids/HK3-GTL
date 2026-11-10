package com.sirin.hk3gtl.common.capability;

/**
 * 【文件职责】
 * - 维护按玩家 UUID 隔离的无线崩坏能 BigInteger 余额，并同步 Minecraft SavedData。
 * - 关键调用链：双能源机器/注入器 -> 原子余额 API -> HonkaiWirelessSavedData。
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
 * 【变更记录 #2】2026-07-19 19:16:14（第 2 次备注 · 内测四第 31 次更新）
 * - 删除：
 *   1) 删除 1,000,000,000 固定容量和所有 long 余额钳制，网络容量不再限制跨配方并行规模。
 *   2) 删除模拟后再部分抽取的非原子计费依赖。
 * - 新增：
 *   1) 新增 BigInteger insert/extract 与 tryExtractExact；精确扣款在单次 ConcurrentMap.compute 中全额成功或零扣除。
 *   2) 保留 long 适配重载供旧仓室能力使用，但内部立即转换为 BigInteger，不截断账户余额。
 * - 修改：
 *   1) POOLS 改为 ConcurrentMap<UUID, BigInteger>，零值删除记录，正值容量无上限。
 *   2) 所有持久化同步均写入实际 BigInteger 新余额，避免内存与 SavedData 真相源不一致。
 * - 用途：
 *   1) 支持任意规模的崩坏能积累与合并配方计费，并保证同一 UUID 多台机器并发扣费不产生负余额。
 */

import com.sirin.hk3gtl.common.constants.Hk3Constants;
import net.minecraft.server.MinecraftServer;
import net.minecraftforge.event.server.ServerStartedEvent;
import net.minecraftforge.event.server.ServerStoppingEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import net.minecraftforge.server.ServerLifecycleHooks;

import java.math.BigInteger;
import java.util.UUID;

/**
 * 【变更记录 #3】2026-10-01 17:17:43（修订137）
 * 删除：第二份静态余额、先改内存再存档及异步访问DimensionDataStorage的路径。
 * 新增：启动时绑定服务器权威账本，停止时解除；未启动或跨服务器调用拒绝真实写入。
 * 修改：全部余额操作委托同一SavedData，保留模拟、long适配和全额扣款接口。
 * 用途：避免余额与存盘不同步或跨存档串用，不修改费用、生产配方及个人归属。
 */
@Mod.EventBusSubscriber(modid = Hk3Constants.MOD_ID, bus = Mod.EventBusSubscriber.Bus.FORGE)
/**
 * 【变更记录 #4】2026-10-01 17:41:38（修订139）
 * 删除：无；新增：工作票据预留HW并捕获原账本、原玩家的退款操作。
 * 修改：预留限定当前服务器主线程，失败全额退回原SavedData，不重新选择活动存档。
 * 用途：配方后续未推进时退还HW，保留其他机器的同时充值及扣款。
 */
public final class HonkaiWirelessNetwork {

    public static final String UNLIMITED_CAPACITY_TEXT = "∞";
    private record Binding(MinecraftServer server, HonkaiWirelessSavedData data) {}
    private static Binding active;

    private HonkaiWirelessNetwork() {}

    public static synchronized BigInteger getStoredAmount(UUID playerId) {
        var data = current();
        return data == null ? BigInteger.ZERO : data.getAmount(playerId);
    }

    public static synchronized void putStoredAmount(UUID playerId, BigInteger amount) {
        if (playerId == null) return;
        requireData().setAmount(playerId, amount);
    }

    /** 旧入口保留，但不再允许绕过权威账本写入。 */
    @Deprecated
    public static void putStoredAmountInternal(UUID playerId, BigInteger amount) {
        putStoredAmount(playerId, amount);
    }

    public static synchronized BigInteger insert(UUID playerId, BigInteger amount, boolean simulate) {
        BigInteger requested = normalize(amount);
        if (playerId == null || requested.signum() == 0) return BigInteger.ZERO;
        if (simulate && current() == null) return BigInteger.ZERO;
        return requireData().insert(playerId, requested, simulate);
    }

    public static synchronized BigInteger extract(UUID playerId, BigInteger amount, boolean simulate) {
        BigInteger requested = normalize(amount);
        if (playerId == null || requested.signum() == 0) return BigInteger.ZERO;
        if (simulate && current() == null) return BigInteger.ZERO;
        return requireData().extract(playerId, requested, simulate);
    }

    /** 单键原子全额扣款：余额不足时不修改余额。 */
    public static synchronized boolean tryExtractExact(UUID playerId, BigInteger amount) {
        BigInteger requested = normalize(amount);
        if (requested.signum() == 0) return true;
        if (playerId == null) return false;

        var data = current();
        return data != null && data.tryExtractExact(playerId, requested);
    }

    public static synchronized boolean reserve(UUID playerId, BigInteger amount, Hk3EnergyTick tick) {
        tick.requireOpen();
        if (amount == null || amount.signum() < 0) throw new IllegalArgumentException("无效HW费用");
        if (amount.signum() == 0) return true;
        Binding binding = active;
        if (playerId == null || binding == null || current() == null || !binding.server().isSameThread()) return false;
        return binding.data().reserve(playerId, amount, tick);
    }

    public static long insert(UUID playerId, long amount, boolean simulate) {
        if (amount <= 0) return 0L;
        return insert(playerId, BigInteger.valueOf(amount), simulate).longValueExact();
    }

    public static long extract(UUID playerId, long amount, boolean simulate) {
        if (amount <= 0) return 0L;
        return extract(playerId, BigInteger.valueOf(amount), simulate).longValueExact();
    }

    private static BigInteger normalize(BigInteger amount) {
        return amount == null || amount.signum() <= 0 ? BigInteger.ZERO : amount;
    }

    private static HonkaiWirelessSavedData current() {
        return active != null && active.server() == ServerLifecycleHooks.getCurrentServer() ? active.data() : null;
    }

    private static HonkaiWirelessSavedData requireData() {
        var data = current();
        if (data == null) throw new IllegalStateException("无线HW账户未就绪，拒绝无存档写入");
        return data;
    }

    @SubscribeEvent
    public static synchronized void onServerStarted(ServerStartedEvent event) {
        active = null;
        HonkaiWirelessSavedData data = HonkaiWirelessSavedData.get(event.getServer());
        if (data != null) active = new Binding(event.getServer(), data);
    }

    @SubscribeEvent
    public static synchronized void onServerStopping(ServerStoppingEvent event) {
        if (active != null && active.server() == event.getServer()) active = null;
    }
}
