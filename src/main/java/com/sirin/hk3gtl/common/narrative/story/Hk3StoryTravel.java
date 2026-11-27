package com.sirin.hk3gtl.common.narrative.story;

import com.sirin.hk3gtl.common.dimension.Hk3Dimensions;
import com.sirin.hk3gtl.common.dimension.melon.Hk3MelonWorld;
import java.util.HashMap;
import java.util.Map;
import java.util.UUID;
import net.minecraft.core.BlockPos;
import net.minecraft.resources.ResourceKey;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.stats.Stats;
import net.minecraft.world.level.Level;
import net.minecraft.world.phys.Vec3;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.event.entity.player.PlayerEvent;
import net.minecraftforge.event.server.ServerStoppedEvent;
import net.minecraftforge.eventbus.api.EventPriority;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import com.sirin.hk3gtl.common.compat.stargate.Hk3StargateApi;
import net.povstalec.sgjourney.common.events.custom.StargateEvent;
import net.povstalec.sgjourney.common.init.StatisticsInit;
import net.povstalec.sgjourney.common.sgjourney.StargateInfo;
import net.povstalec.sgjourney.common.sgjourney.stargate.Stargate;

@Mod.EventBusSubscriber(modid = "hk3gtl")
public final class Hk3StoryTravel {
    private static final Map<UUID, Transit> TRANSITS = new HashMap<>();
    private static final int ARRIVAL_TIMEOUT_TICKS = 100;

    private record Gate(ResourceKey<Level> dimension, Vec3 position, String address, double radius) {
        static Gate of(MinecraftServer server, Stargate gate) {
            return new Gate(gate.getDimension(), Hk3StargateApi.position(server, gate),
                    gate.get9ChevronAddress().toString(), gate.getInnerRadius());
        }
    }

    private record Transit(Gate source, Gate target, int traveledBefore, int tick) {}

    private Hk3StoryTravel() {}

    @SubscribeEvent(priority = EventPriority.LOWEST)
    public static void requested(StargateEvent.WormholeTravel event) {
        if (!(event.getTraveler() instanceof ServerPlayer player) || player.isCreative() || player.isSpectator()
                || event.getWormholeTravel() != StargateInfo.WormholeTravel.ENABLED) return;
        var from = event.getStargate();
        var to = event.getDestinationStargate();
        if (from.getDimension().equals(to.getDimension()) || special(from.getDimension()) || special(to.getDimension())) return;
        TRANSITS.put(player.getUUID(), new Transit(Gate.of(player.server, from), Gate.of(player.server, to),
                travels(player), player.server.getTickCount()));
    }

    @SubscribeEvent
    public static void tick(TickEvent.ServerTickEvent event) {
        if (event.phase != TickEvent.Phase.END || TRANSITS.isEmpty()) return;
        var server = event.getServer();
        var entries = TRANSITS.entrySet().iterator();
        while (entries.hasNext()) {
            var entry = entries.next();
            var transit = entry.getValue();
            var player = server.getPlayerList().getPlayer(entry.getKey());
            if (player == null || server.getTickCount() - transit.tick() > ARRIVAL_TIMEOUT_TICKS) {
                entries.remove();
                continue;
            }
            // 原生通行统计在实际传送后递增，取消请求与护盾阻挡不会递增。
            if (travels(player) <= transit.traveledBefore()) continue;
            double radius = transit.target().radius() + 6;
            if (player.isCreative() || player.isSpectator() || !player.isAlive()
                    || !player.level().dimension().equals(transit.target().dimension())
                    || player.position().distanceToSqr(transit.target().position()) > radius * radius) continue;
            entries.remove();
            arrived(player, transit);
        }
    }

    private static void arrived(ServerPlayer player, Transit transit) {
        var evidence = player.getPersistentData().getCompound(Hk3StoryNativeEvents.EVIDENCE);
        if (!evidence.contains("origin_dimension")) {
            evidence.putString("origin_dimension", transit.source().dimension().location().toString());
            evidence.putString("origin_gate", transit.source().address());
            evidence.putLong("origin_position", BlockPos.containing(transit.source().position()).asLong());
            evidence.putString("first_target_dimension", transit.target().dimension().location().toString());
            evidence.putString("first_target_gate", transit.target().address());
            evidence.putLong("first_target_position", BlockPos.containing(transit.target().position()).asLong());
            player.getPersistentData().put(Hk3StoryNativeEvents.EVIDENCE, evidence);
            Hk3StoryService.fact(player, "stargate_departed");
        } else if (evidence.getString("origin_dimension").equals(transit.target().dimension().location().toString())
                && evidence.getString("origin_gate").equals(transit.target().address())) {
            Hk3StoryService.fact(player, "stargate_returned");
        }
    }

    private static int travels(ServerPlayer player) {
        return player.getStats().getValue(Stats.CUSTOM.get(StatisticsInit.TIMES_USED_WORMHOLE.get()));
    }

    private static boolean special(ResourceKey<Level> dimension) {
        return dimension.equals(Hk3Dimensions.IMAGINARY) || dimension.equals(Hk3MelonWorld.KEY);
    }

    @SubscribeEvent
    public static void logout(PlayerEvent.PlayerLoggedOutEvent event) {
        TRANSITS.remove(event.getEntity().getUUID());
    }

    @SubscribeEvent
    public static void stopped(ServerStoppedEvent event) {
        TRANSITS.clear();
    }
}
