package com.sirin.hk3gtl.common.capability;



import com.sirin.hk3gtl.common.constants.Hk3Constants;
import net.minecraft.server.MinecraftServer;
import net.minecraftforge.event.server.ServerStartedEvent;
import net.minecraftforge.event.server.ServerStoppingEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import net.minecraftforge.server.ServerLifecycleHooks;

import java.math.BigInteger;
import java.util.UUID;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.ConcurrentMap;
import java.util.concurrent.atomic.AtomicReference;

@Mod.EventBusSubscriber(modid = Hk3Constants.MOD_ID, bus = Mod.EventBusSubscriber.Bus.FORGE)
public final class HonkaiWirelessNetwork {

    public static final String UNLIMITED_CAPACITY_TEXT = "∞";
    private static final ConcurrentMap<UUID, BigInteger> POOLS = new ConcurrentHashMap<>();

    private HonkaiWirelessNetwork() {}

    public static BigInteger getStoredAmount(UUID playerId) {
        return playerId == null ? BigInteger.ZERO : POOLS.getOrDefault(playerId, BigInteger.ZERO);
    }

    public static void putStoredAmount(UUID playerId, BigInteger amount) {
        if (playerId == null) return;
        BigInteger normalized = normalize(amount);
        putStoredAmountInternal(playerId, normalized);
        syncSavedData(playerId, normalized);
    }

    /** 启动镜像专用：只更新内存，不回写 SavedData。 */
    public static void putStoredAmountInternal(UUID playerId, BigInteger amount) {
        if (playerId == null) return;
        BigInteger normalized = normalize(amount);
        if (normalized.signum() == 0) {
            POOLS.remove(playerId);
        } else {
            POOLS.put(playerId, normalized);
        }
    }

    public static BigInteger insert(UUID playerId, BigInteger amount, boolean simulate) {
        BigInteger requested = normalize(amount);
        if (playerId == null || requested.signum() == 0) return BigInteger.ZERO;
        if (simulate) return requested;

        AtomicReference<BigInteger> accepted = new AtomicReference<>(BigInteger.ZERO);
        POOLS.compute(playerId, (id, stored) -> {
            BigInteger updated = (stored == null ? BigInteger.ZERO : stored).add(requested);
            accepted.set(requested);
            syncSavedData(id, updated);
            return updated;
        });
        return accepted.get();
    }

    public static BigInteger extract(UUID playerId, BigInteger amount, boolean simulate) {
        BigInteger requested = normalize(amount);
        if (playerId == null || requested.signum() == 0) return BigInteger.ZERO;
        if (simulate) return getStoredAmount(playerId).min(requested);

        AtomicReference<BigInteger> extracted = new AtomicReference<>(BigInteger.ZERO);
        POOLS.computeIfPresent(playerId, (id, stored) -> {
            BigInteger drawn = stored.min(requested);
            extracted.set(drawn);
            BigInteger remaining = stored.subtract(drawn);
            if (drawn.signum() > 0) syncSavedData(id, remaining);
            return remaining.signum() == 0 ? null : remaining;
        });
        return extracted.get();
    }

    /** 单键原子全额扣款：余额不足时不修改余额。 */
    public static boolean tryExtractExact(UUID playerId, BigInteger amount) {
        BigInteger requested = normalize(amount);
        if (requested.signum() == 0) return true;
        if (playerId == null) return false;

        AtomicReference<Boolean> success = new AtomicReference<>(false);
        POOLS.computeIfPresent(playerId, (id, stored) -> {
            if (stored.compareTo(requested) < 0) return stored;
            BigInteger remaining = stored.subtract(requested);
            success.set(true);
            syncSavedData(id, remaining);
            return remaining.signum() == 0 ? null : remaining;
        });
        return success.get();
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

    private static void syncSavedData(UUID playerId, BigInteger amount) {
        MinecraftServer server = ServerLifecycleHooks.getCurrentServer();
        if (server == null) return;
        HonkaiWirelessSavedData data = HonkaiWirelessSavedData.get(server);
        if (data != null) data.setAmount(playerId, amount);
    }

    @SubscribeEvent
    public static void onServerStarted(ServerStartedEvent event) {
        POOLS.clear();
        HonkaiWirelessSavedData data = HonkaiWirelessSavedData.get(event.getServer());
        if (data != null) data.mirrorToMemory();
    }

    @SubscribeEvent
    public static void onServerStopping(ServerStoppingEvent event) {
        POOLS.clear();
    }
}
