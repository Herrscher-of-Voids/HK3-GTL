package com.sirin.hk3gtl.common.narrative.story;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import net.minecraft.core.BlockPos;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.event.level.BlockEvent;
import net.minecraftforge.event.server.ServerStoppedEvent;
import net.minecraftforge.eventbus.api.EventPriority;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;

@Mod.EventBusSubscriber(modid = "hk3gtl")
public final class Hk3StoryNativeEvents {
    static final String EVIDENCE = "hk3gtl_story_native";
    private static final Map<String, String> BLOCKS = Map.of(
            "expatternprovider:fishbig", "fishbig",
            "gtceu:creative_tank", "creative_tank",
            "gtceu:creative_chest", "creative_chest");
    private static final List<Placement> PLACEMENTS = new ArrayList<>();

    private record Placement(ServerPlayer player, ServerLevel level, BlockPos pos, String block) {}

    private Hk3StoryNativeEvents() {}

    @SubscribeEvent(priority = EventPriority.LOWEST)
    public static void placed(BlockEvent.EntityPlaceEvent event) {
        if (!(event.getEntity() instanceof ServerPlayer player) || player.isCreative() || player.isSpectator()) return;
        String block = BuiltInRegistries.BLOCK.getKey(event.getPlacedBlock().getBlock()).toString();
        if (BLOCKS.containsKey(block))
            PLACEMENTS.add(new Placement(player, player.serverLevel(), event.getPos().immutable(), block));
    }

    @SubscribeEvent
    public static void tick(TickEvent.ServerTickEvent event) {
        if (event.phase != TickEvent.Phase.END) return;
        var placements = List.copyOf(PLACEMENTS);
        PLACEMENTS.clear();
        for (var placed : placements) {
            if (!BuiltInRegistries.BLOCK.getKey(placed.level().getBlockState(placed.pos()).getBlock())
                    .toString().equals(placed.block())) continue;
            String key = BLOCKS.get(placed.block());
            var evidence = placed.player().getPersistentData().getCompound(EVIDENCE);
            if (!evidence.contains(key + "_dimension")) {
                evidence.putString(key + "_dimension", placed.level().dimension().location().toString());
                evidence.putLong(key + "_position", placed.pos().asLong());
                placed.player().getPersistentData().put(EVIDENCE, evidence);
            }
            if (key.equals("fishbig")) Hk3StoryService.fact(placed.player(), "fishbig_activated");
            else {
                Hk3StoryService.fact(placed.player(), key + "_placed");
                Hk3StoryService.fact(placed.player(), key + "_completed");
            }
        }
    }

    @SubscribeEvent
    public static void stopped(ServerStoppedEvent event) {
        PLACEMENTS.clear();
    }
}
