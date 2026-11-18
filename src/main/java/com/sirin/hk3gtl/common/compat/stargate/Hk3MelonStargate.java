package com.sirin.hk3gtl.common.compat.stargate;

import com.sirin.hk3gtl.common.constants.Hk3Constants;
import com.sirin.hk3gtl.common.dimension.melon.Hk3MelonAdventure;
import com.sirin.hk3gtl.common.dimension.melon.Hk3MelonWorld;
import com.sirin.hk3gtl.common.util.Hk3SavedDataGuard;
import java.util.HashMap;
import java.util.Map;
import java.util.UUID;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.core.registries.Registries;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceKey;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.saveddata.SavedData;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.eventbus.api.EventPriority;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import net.povstalec.sgjourney.common.block_entities.stargate.AbstractStargateEntity;
import net.povstalec.sgjourney.common.blocks.stargate.AbstractStargateBlock;
import net.povstalec.sgjourney.common.blockstates.Orientation;
import net.povstalec.sgjourney.common.init.BlockInit;
import net.povstalec.sgjourney.common.events.custom.StargateEvent;
import net.povstalec.sgjourney.common.sgjourney.StargateInfo;
import net.povstalec.sgjourney.common.sgjourney.stargate.SGJourneyStargate;

@Mod.EventBusSubscriber(modid = Hk3Constants.MOD_ID, bus = Mod.EventBusSubscriber.Bus.FORGE)
public final class Hk3MelonStargate {
    public static final BlockPos DESTINATION_BASE = new BlockPos(0, 96, 8);
    private static final String DESTINATION = "hk3gtl_melon_destination";

    public record GateSource(ResourceKey<Level> dimension, BlockPos base, String address,
                             Direction facing, Orientation orientation) {}

    private Hk3MelonStargate() {}

    public static String ensureDestination(MinecraftServer server) {
        var level = server.getLevel(Hk3MelonWorld.KEY);
        Hk3MelonWorld.ensure(level);
        var ledger = ledger(server);
        if (ledger.destination.isEmpty()) {
            var gate = place(level, DESTINATION_BASE);
            gate.getPersistentData().putBoolean(DESTINATION, true);
            charge(gate);
            ledger.destination = gate.get9ChevronAddress().toString();
            ledger.setDirty();
        }
        return ledger.destination;
    }

    public static GateSource arrivalSource(ServerPlayer player) {
        return ledger(player.server).arrivals.get(player.getUUID());
    }

    public static BlockPos returnPoint(ServerPlayer player) {
        var source = arrivalSource(player);
        var point = source.base().relative(source.facing().getOpposite(), 3);
        return source.orientation() == Orientation.REGULAR ? point : point.above();
    }

    public static boolean dialReturn(ServerPlayer player) {
        if (!player.level().dimension().equals(Hk3MelonWorld.KEY)
                || !player.blockPosition().closerThan(DESTINATION_BASE, 16)) {
            player.sendSystemMessage(Component.translatable("message.hk3gtl.melon_return_nearby"));
            return false;
        }
        var source = arrivalSource(player);
        if (source == null) return false;
        var to = gateAt(player.server, source);
        if (to == null) return false;
        return dial(player, destinationGate(player.server), to);
    }

    @SubscribeEvent(priority = EventPriority.LOWEST)
    public static void arrived(StargateEvent.WormholeTravel event) {
        if (!(event.getTraveler() instanceof ServerPlayer player)
                || !event.getDestinationStargate().getDimension().equals(Hk3MelonWorld.KEY)) return;
        if (!Hk3MelonAdventure.unlocked(player)) {
            event.setCanceled(true);
            player.sendSystemMessage(Component.literal("折页尚未读完。这片海不会向未署名的旅人打开。"));
            return;
        }
        if (!(event.getStargate() instanceof SGJourneyStargate gate)
                || event.getWormholeTravel() == StargateInfo.WormholeTravel.DISABLED
                || event.getWormholeTravel() == StargateInfo.WormholeTravel.CREATIVE_ONLY && !player.isCreative()) return;
        var ledger = ledger(event.getServer());
        var source = gate.getStargateEntity(event.getServer());
        ledger.arrivals.put(player.getUUID(), new GateSource(gate.getDimension(), gate.getBlockPos(),
                gate.get9ChevronAddress().toString(), source.getDirection(), source.getOrientation()));
        ledger.setDirty();
    }

    private static boolean dial(ServerPlayer player, AbstractStargateEntity from,
                                AbstractStargateEntity to) {
        charge(from);
        if (from.isConnected() || to.isConnected()) {
            player.sendSystemMessage(Component.literal("门内仍有潮声。等这一轮通行结束，再唤醒它。"));
            return false;
        }
        // 原生参数只关闭本次连接的开启浪涌，通行与能耗仍由星门处理。
        var feedback = from.engageStargate(to.get9ChevronAddress(), false);
        if (feedback.isError()) player.sendSystemMessage(feedback.getFeedbackMessage());
        return !feedback.isError();
    }

    private static AbstractStargateEntity place(ServerLevel level, BlockPos base) {
        var block = BlockInit.MILKY_WAY_STARGATE.get();
        var state = block.defaultBlockState().setValue(AbstractStargateBlock.FACING, Direction.NORTH)
                .setValue(AbstractStargateBlock.ORIENTATION, Orientation.REGULAR);
        level.setBlock(base, state, 3);
        block.setPlacedBy(level, base, state, null, new ItemStack(block));
        var gate = (AbstractStargateEntity) level.getBlockEntity(base);
        gate.generate();
        gate.setProtected(true);
        gate.updateStargate(true);
        return gate;
    }

    private static AbstractStargateEntity destinationGate(MinecraftServer server) {
        var level = server.getLevel(Hk3MelonWorld.KEY);
        level.getChunkAt(DESTINATION_BASE);
        return (AbstractStargateEntity) level.getBlockEntity(DESTINATION_BASE);
    }

    private static AbstractStargateEntity gateAt(MinecraftServer server, GateSource source) {
        var level = server.getLevel(source.dimension());
        level.getChunkAt(source.base());
        if (level.getBlockEntity(source.base()) instanceof AbstractStargateEntity gate
                && gate.get9ChevronAddress().toString().equals(source.address())) return gate;
        return null;
    }

    @SubscribeEvent
    public static void tick(TickEvent.ServerTickEvent event) {
        if (event.phase != TickEvent.Phase.END || event.getServer().getTickCount() % 20 != 0) return;
        var server = event.getServer();
        var ledger = ledger(server);
        if (ledger.destination.isEmpty()) return;
        var destinationLevel = server.getLevel(Hk3MelonWorld.KEY);
        if (destinationLevel.hasChunkAt(DESTINATION_BASE)
                && destinationLevel.getBlockEntity(DESTINATION_BASE) instanceof AbstractStargateEntity gate
                && gate.getPersistentData().getBoolean(DESTINATION)) charge(gate);
    }

    private static void charge(AbstractStargateEntity gate) {
        var tag = gate.getPersistentData();
        if (tag.getBoolean(DESTINATION)
                && gate.getEnergyStored() < gate.getEnergyCapacity()) {
            gate.setEnergy(gate.getEnergyCapacity());
            gate.setChanged();
        }
    }

    private static Ledger ledger(MinecraftServer server) {
        return Hk3SavedDataGuard.get(server, "hk3gtl_melon_stargates", Ledger::load, Ledger::new);
    }

    private static final class Ledger extends SavedData {
        private String destination = "";
        private final Map<UUID, GateSource> arrivals = new HashMap<>();

        private static Ledger load(CompoundTag tag) {
            var data = new Ledger();
            data.destination = tag.getString("Destination");
            read(tag.getCompound("Arrivals"), data.arrivals);
            return data;
        }

        private static void read(CompoundTag rows, Map<UUID, GateSource> target) {
            for (var id : rows.getAllKeys()) {
                var row = rows.getCompound(id);
                target.put(UUID.fromString(id), new GateSource(ResourceKey.create(Registries.DIMENSION,
                        new ResourceLocation(row.getString("Dimension"))), BlockPos.of(row.getLong("Base")),
                        row.getString("Address"), Direction.byName(row.getString("Facing")),
                        Orientation.valueOf(row.getString("Orientation"))));
            }
        }

        @Override
        public CompoundTag save(CompoundTag tag) {
            tag.putString("Destination", destination);
            tag.put("Arrivals", write(arrivals));
            return tag;
        }

        private static CompoundTag write(Map<UUID, GateSource> sources) {
            var rows = new CompoundTag();
            sources.forEach((id, source) -> {
                var row = new CompoundTag();
                row.putString("Dimension", source.dimension().location().toString());
                row.putLong("Base", source.base().asLong());
                row.putString("Address", source.address());
                row.putString("Facing", source.facing().getName());
                row.putString("Orientation", source.orientation().name());
                rows.put(id.toString(), row);
            });
            return rows;
        }
    }
}
