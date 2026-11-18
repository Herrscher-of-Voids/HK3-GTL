package com.sirin.hk3gtl.common.compat.stargate;

import com.sirin.hk3gtl.common.integration.Hk3QuestEvents;
import java.util.Map;
import java.util.UUID;
import java.util.concurrent.ConcurrentHashMap;
import net.minecraft.core.BlockPos;
import net.minecraft.resources.ResourceKey;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.stats.Stats;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.Level;
import net.minecraft.world.phys.Vec3;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.event.entity.player.PlayerEvent;
import net.minecraftforge.event.server.ServerStoppedEvent;
import net.minecraftforge.eventbus.api.EventPriority;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import net.povstalec.sgjourney.common.block_entities.dhd.AbstractDHDEntity;
import net.povstalec.sgjourney.common.block_entities.stargate.ClassicStargateEntity;
import net.povstalec.sgjourney.common.data.StargateNetwork;
import net.povstalec.sgjourney.common.events.custom.ConnectionEvent;
import net.povstalec.sgjourney.common.events.custom.StargateEvent;
import net.povstalec.sgjourney.common.init.StatisticsInit;
import net.povstalec.sgjourney.common.menu.AbstractDHDMenu;
import net.povstalec.sgjourney.common.sgjourney.StargateConnection;
import net.povstalec.sgjourney.common.sgjourney.StargateInfo;
import net.povstalec.sgjourney.common.sgjourney.stargate.SGJourneyStargate;
import net.povstalec.sgjourney.common.sgjourney.stargate.Stargate;

@Mod.EventBusSubscriber(modid = "hk3gtl")
public final class Hk3StargateQuestEvents {
    private static final String TRIP = "hk3gtl_quest_stargate_trip";
    private static final ThreadLocal<Press> DHD_OPERATOR = new ThreadLocal<>();
    private static final Map<UUID, Dial> DIALS = new ConcurrentHashMap<>();
    private static final Map<UUID, Transit> TRANSITS = new ConcurrentHashMap<>();

    private record Press(ServerPlayer player, AbstractDHDEntity dhd) {}
    private record Dial(UUID player, StargateConnection connection) {}
    private record Gate(String identity, ResourceKey<Level> dimension, Vec3 position, double radius) {
        static Gate of(MinecraftServer server, Stargate gate) {
            var position = gate.getPosition(server);
            String identity = gate.getDimension().location() + "|" + gate.get9ChevronAddress()
                    + "|" + BlockPos.containing(position).asLong();
            return new Gate(identity, gate.getDimension(), position, gate.getInnerRadius());
        }
    }
    private record Transit(Gate from, Gate to, int travels, int tick) {}

    private Hk3StargateQuestEvents() {}

    public static void activated(ServerPlayer player, BlockPos pos) {
        if (player.isCreative() || player.isSpectator()
                || !(player.serverLevel().getBlockEntity(pos) instanceof ClassicStargateEntity gate)) return;
        var registered = StargateNetwork.get(player.serverLevel()).getStargate(gate.get9ChevronAddress());
        if (registered != null && registered.isValid(player.server))
            Hk3QuestEvents.recordPlayer(player.server, player.getUUID(), "stargate-classic-activation");
    }

    public static void press(ServerPlayer player, AbstractDHDEntity dhd, int symbol) {
        DHD_OPERATOR.set(new Press(player, dhd));
        try {
            dhd.engageChevron(symbol);
        } finally {
            DHD_OPERATOR.remove();
        }
    }

    @SubscribeEvent(priority = EventPriority.LOWEST)
    public static void connected(ConnectionEvent.Establish event) {
        var press = DHD_OPERATOR.get();
        if (press == null) return;
        var player = press.player();
        var connection = event.getStargateConnection();
        if (player.isCreative() || player.isSpectator()
                || !(player.containerMenu instanceof AbstractDHDMenu)
                || player.level() != press.dhd().getLevel()
                || player.distanceToSqr(Vec3.atCenterOf(press.dhd().getBlockPos())) > 64
                || !(connection.getDialingStargate() instanceof SGJourneyStargate gate)
                || !(gate.getStargateEntity(event.getServer()) instanceof ClassicStargateEntity)) return;
        DIALS.put(connection.getID(), new Dial(player.getUUID(), connection));
    }

    @SubscribeEvent
    public static void terminated(ConnectionEvent.Terminate event) {
        DIALS.remove(event.getStargateConnection().getID());
    }

    @SubscribeEvent(priority = EventPriority.LOWEST)
    public static void requested(StargateEvent.WormholeTravel event) {
        if (!(event.getTraveler() instanceof ServerPlayer player) || player.isCreative() || player.isSpectator()
                || event.getWormholeTravel() != StargateInfo.WormholeTravel.ENABLED) return;
        var server = event.getServer();
        var from = Gate.of(server, event.getStargate());
        var to = Gate.of(server, event.getDestinationStargate());
        if (from.identity().equals(to.identity())) return;
        TRANSITS.put(player.getUUID(), new Transit(from, to, travels(player), server.getTickCount()));
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
            if (player == null || server.getTickCount() > transit.tick() + 1) {
                transits.remove();
                continue;
            }
            // 原生统计在传送完成后递增，取消请求与护盾阻挡不构成通行。
            if (travels(player) <= transit.travels()) continue;
            transits.remove();
            double radius = transit.to().radius() + 6;
            if (player.isCreative() || player.isSpectator() || !player.isAlive()
                    || !player.level().dimension().equals(transit.to().dimension())
                    || player.position().distanceToSqr(transit.to().position()) > radius * radius) continue;
            arrived(player, transit);
        }
    }

    private static void arrived(ServerPlayer player, Transit transit) {
        var data = player.getPersistentData();
        var persisted = data.getCompound(Player.PERSISTED_NBT_TAG);
        var trip = persisted.getCompound(TRIP);
        if (!trip.getString("Current").equals(transit.from().identity()))
            trip.putString("Origin", transit.from().identity());
        if (trip.getString("Origin").equals(transit.to().identity()))
            Hk3QuestEvents.recordPlayer(player.server, player.getUUID(), "stargate-round-trip");
        trip.putString("Current", transit.to().identity());
        persisted.put(TRIP, trip);
        data.put(Player.PERSISTED_NBT_TAG, persisted);
    }

    private static int travels(ServerPlayer player) {
        return player.getStats().getValue(Stats.CUSTOM.get(StatisticsInit.TIMES_USED_WORMHOLE.get()));
    }

    @SubscribeEvent
    public static void logout(PlayerEvent.PlayerLoggedOutEvent event) {
        TRANSITS.remove(event.getEntity().getUUID());
    }

    @SubscribeEvent
    public static void stopped(ServerStoppedEvent event) {
        DIALS.clear();
        TRANSITS.clear();
        DHD_OPERATOR.remove();
    }
}
