package com.sirin.hk3gtl.common.integration.ae;

import com.mojang.logging.LogUtils;
import com.sirin.hk3gtl.common.constants.Hk3Constants;
import net.minecraft.server.MinecraftServer;
import net.minecraftforge.event.server.ServerAboutToStartEvent;
import net.minecraftforge.event.server.ServerStoppingEvent;
import net.minecraftforge.event.server.ServerStoppedEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import net.minecraftforge.fml.ModList;

import java.util.concurrent.Callable;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.Future;
import java.util.concurrent.FutureTask;

/** 每台服务器独立持有规划池，关服后的请求不得复活旧线程池。 */
@Mod.EventBusSubscriber(modid = Hk3Constants.MOD_ID)
public final class Hk3AePlanningService {
    private static final ConcurrentHashMap<MinecraftServer, Hk3AePlanningQueue> POOLS = new ConcurrentHashMap<>();

    private Hk3AePlanningService() {}

    @SubscribeEvent
    public static void starting(ServerAboutToStartEvent event) {
        if (!ModList.get().isLoaded("ae2")) return;
        var limits = Hk3AePlanningQueue.limits(Runtime.getRuntime().availableProcessors(), Runtime.getRuntime().maxMemory());
        var previous = POOLS.put(event.getServer(), new Hk3AePlanningQueue(limits.workers(), limits.queued()));
        if (previous != null) previous.close();
        LogUtils.getLogger().info("HK3 AE规划调度：最多{}个并行规划、{}个等待请求；内存按启发式准入，非总堆硬限",
                limits.workers(), limits.queued());
    }

    public static <T> Future<T> submit(MinecraftServer server, Callable<T> calculation) {
        var pool = POOLS.get(server);
        if (pool != null) return pool.submit(calculation);
        FutureTask<T> stopped = new FutureTask<>(calculation);
        stopped.cancel(false);
        return stopped;
    }

    public static boolean hasCapacity(MinecraftServer server) {
        return hasCapacity(server, 0);
    }

    public static boolean hasCapacity(MinecraftServer server, int collecting) {
        var pool = POOLS.get(server);
        return pool != null && pool.hasCapacity(collecting);
    }

    @SubscribeEvent
    public static void stopping(ServerStoppingEvent event) {
        close(event.getServer());
    }

    @SubscribeEvent
    public static void stopped(ServerStoppedEvent event) {
        close(event.getServer());
        if (ModList.get().isLoaded("ae2"))
            com.sirin.hk3gtl.common.integration.ae.exact.Hk3ExactOrderService.stopped(event);
    }

    @SubscribeEvent
    public static void tick(net.minecraftforge.event.TickEvent.ServerTickEvent event) {
        if (ModList.get().isLoaded("ae2"))
            com.sirin.hk3gtl.common.integration.ae.exact.Hk3ExactOrderService.tick(event);
    }

    @SubscribeEvent
    public static void loggedOut(net.minecraftforge.event.entity.player.PlayerEvent.PlayerLoggedOutEvent event) {
        if (ModList.get().isLoaded("ae2") && event.getEntity() instanceof net.minecraft.server.level.ServerPlayer player)
            com.sirin.hk3gtl.common.integration.ae.exact.Hk3ExactOrderService.loggedOut(player);
    }

    private static void close(MinecraftServer server) {
        var pool = POOLS.remove(server);
        if (pool != null) pool.close();
    }
}
