package com.sirin.hk3gtl.common.compat.stargate;

import com.sirin.hk3gtl.common.integration.Hk3QuestEvents;
import java.util.Map;
import java.util.UUID;
import java.util.concurrent.ConcurrentHashMap;
import net.minecraft.core.BlockPos;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.stats.Stats;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.phys.Vec3;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.event.entity.player.PlayerEvent;
import net.povstalec.sgjourney.common.events.custom.StargateEvent;
import net.povstalec.sgjourney.common.sgjourney.StargateInfo;
import net.minecraftforge.event.server.ServerStoppedEvent;
import net.minecraftforge.eventbus.api.EventPriority;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import net.povstalec.sgjourney.common.block_entities.dhd.AbstractDHDEntity;
import net.povstalec.sgjourney.common.block_entities.stargate.ClassicStargateEntity;
import net.povstalec.sgjourney.common.data.StargateNetwork;
import net.povstalec.sgjourney.common.init.StatisticsInit;
import net.povstalec.sgjourney.common.sgjourney.StargateConnection;
import net.povstalec.sgjourney.common.sgjourney.stargate.Stargate;

@Mod.EventBusSubscriber(modid = "hk3gtl")
public final class Hk3StargateQuestEvents {
    private static final String TRIP = "hk3gtl_quest_stargate_trip";
    private static final ThreadLocal<Press> DHD_OPERATOR = new ThreadLocal<>();
    private static final Map<UUID, Dial> DIALS = new ConcurrentHashMap<>();

    private static final Map<UUID, Transit> TRANSITS = new ConcurrentHashMap<>();
    private record Transit(Stargate from, Stargate to, int travels, int tick) {}

    private record Press(ServerPlayer player, AbstractDHDEntity dhd) {}
    private record Dial(UUID player, StargateConnection connection) {}
    private static String gateIdentity(MinecraftServer server, Stargate gate) {
        return gate.getDimension().location() + "|" + gate.get9ChevronAddress()
                + "|" + BlockPos.containing(Hk3StargateApi.position(server, gate)).asLong();
    }

    private Hk3StargateQuestEvents() {}

    public static void activated(ServerPlayer player, BlockPos pos) {
        if (player.isCreative() || player.isSpectator()
                || !(player.serverLevel().getBlockEntity(pos) instanceof ClassicStargateEntity gate)) return;
        var registered = StargateNetwork.get(player.serverLevel()).getStargate(gate.get9ChevronAddress());
        if (registered != null && Hk3StargateApi.registered(player.server, registered))
            Hk3QuestEvents.recordPlayer(player.server, player.getUUID(), "stargate-classic-activation");
    }

    public static void press(ServerPlayer player, AbstractDHDEntity dhd, Runnable invoke) {
        DHD_OPERATOR.set(new Press(player, dhd));
        try {
            invoke.run();
        } finally {
            DHD_OPERATOR.remove();
        }
    }

    static void connected(StargateConnection connection) {
        var press = DHD_OPERATOR.get();
        if (press == null) return;
        var player = press.player();
        if (player.isCreative() || player.isSpectator()
                || !Hk3StargateApi.isDhdMenu(player.containerMenu)
                || player.level() != press.dhd().getLevel()
                || player.distanceToSqr(Vec3.atCenterOf(press.dhd().getBlockPos())) > 64
                || !(Hk3StargateApi.blockEntity(player.server, connection.getDialingStargate())
                instanceof ClassicStargateEntity)) return;
        DIALS.put(connection.getID(), new Dial(player.getUUID(), connection));
    }

    static void terminated(StargateConnection connection) {
        DIALS.remove(connection.getID());
    }

    @SubscribeEvent(priority = EventPriority.LOWEST)
    public static void requested(StargateEvent.WormholeTravel event) {
        if (event.getTraveler() instanceof ServerPlayer player && !player.isCreative() && !player.isSpectator()
                && event.getWormholeTravel() == StargateInfo.WormholeTravel.ENABLED)
            TRANSITS.put(player.getUUID(), new Transit(event.getStargate(), event.getDestinationStargate(),
                    travels(player), event.getServer().getTickCount()));
    }

    @SubscribeEvent
    public static void tick(TickEvent.ServerTickEvent event) {
        if (event.phase != TickEvent.Phase.END) return;
        var server = event.getServer();
        var dials = DIALS.entrySet().iterator();
        while (dials.hasNext()) {
            var dial = dials.next().getValue();
            if (dial.connection().getOpenTime() <= 0) continue;
            dials.remove();
            Hk3QuestEvents.recordPlayer(server, dial.player(), "stargate-outgoing-connection");
        }
        var transits = TRANSITS.entrySet().iterator();
        while (transits.hasNext()) {
            var entry = transits.next();
            var transit = entry.getValue();
            var player = server.getPlayerList().getPlayer(entry.getKey());
            if (player == null || server.getTickCount() - transit.tick() > 100) { transits.remove(); continue; }
            if (travels(player) <= transit.travels()) continue;
            var destination = transit.to();
            double radius = destination.getInnerRadius() + 6;
            if (player.level().dimension().equals(destination.getDimension())
                    && player.position().distanceToSqr(Hk3StargateApi.position(server, destination)) <= radius * radius) {
                transits.remove();
                completed(player, transit.from(), destination);
            }
        }
    }

    public static void completed(ServerPlayer player, Stargate origin, Stargate destination) {
        TRANSITS.remove(player.getUUID());
        if (player.isCreative() || player.isSpectator() || !player.isAlive()) return;
        String from = gateIdentity(player.server, origin), to = gateIdentity(player.server, destination);
        if (from.equals(to)) return;
        var data = player.getPersistentData();
        var persisted = data.getCompound(Player.PERSISTED_NBT_TAG);
        var trip = persisted.getCompound(TRIP);
        if (!trip.getString("Current").equals(from))
            trip.putString("Origin", from);
        if (trip.getString("Origin").equals(to))
            Hk3QuestEvents.recordPlayer(player.server, player.getUUID(), "stargate-round-trip");
        trip.putString("Current", to);
        persisted.put(TRIP, trip);
        data.put(Player.PERSISTED_NBT_TAG, persisted);
    }

    public static int travels(ServerPlayer player) {
        return player.getStats().getValue(Stats.CUSTOM.get(StatisticsInit.TIMES_USED_WORMHOLE.get()));
    }

    @SubscribeEvent
    public static void logout(PlayerEvent.PlayerLoggedOutEvent event) { TRANSITS.remove(event.getEntity().getUUID()); }

    @SubscribeEvent
    public static void stopped(ServerStoppedEvent event) {
        DIALS.clear();
        TRANSITS.clear();
        DHD_OPERATOR.remove();
    }
}
