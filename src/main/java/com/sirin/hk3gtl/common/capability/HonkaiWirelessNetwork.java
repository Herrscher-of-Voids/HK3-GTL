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








@Mod.EventBusSubscriber(modid = Hk3Constants.MOD_ID, bus = Mod.EventBusSubscriber.Bus.FORGE)






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

    static synchronized HonkaiWirelessSavedData journalData(MinecraftServer server) {
        if (active == null || active.server() != server || current() == null || !server.isSameThread())
            throw new IllegalStateException("退款账本未绑定当前服务器主线程");
        return active.data();
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
