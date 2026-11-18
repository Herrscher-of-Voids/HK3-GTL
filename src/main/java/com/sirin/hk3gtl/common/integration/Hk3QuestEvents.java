package com.sirin.hk3gtl.common.integration;

import com.sirin.hk3gtl.common.util.Hk3SavedDataGuard;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.nbt.ListTag;
import net.minecraft.nbt.StringTag;
import net.minecraft.nbt.Tag;
import net.minecraft.server.MinecraftServer;
import net.minecraft.world.level.saveddata.SavedData;

import java.util.HashMap;
import java.util.HashSet;
import java.util.Map;
import java.util.Set;
import java.util.UUID;

public final class Hk3QuestEvents extends SavedData {
    private final Map<UUID, Set<String>> processes = new HashMap<>();
    private final Map<UUID, Set<String>> playerEvents = new HashMap<>();

    private Hk3QuestEvents() {}

    private static Hk3QuestEvents get(MinecraftServer server) {
        return Hk3SavedDataGuard.get(server, "hk3gtl_quest_events", Hk3QuestEvents::load, Hk3QuestEvents::new);
    }

    public static void recordProcess(MinecraftServer server, UUID team, String planId) {
        var data = get(server);
        if (data.processes.computeIfAbsent(team, key -> new HashSet<>()).add(planId)) data.setDirty();
    }

    public static void recordPlayer(MinecraftServer server, UUID player, String eventKey) {
        var data = get(server);
        if (data.playerEvents.computeIfAbsent(player, key -> new HashSet<>()).add(eventKey)) data.setDirty();
    }

    static Set<String> processes(MinecraftServer server, UUID team) {
        return get(server).processes.getOrDefault(team, Set.of());
    }

    static Set<String> playerEvents(MinecraftServer server, UUID player) {
        return get(server).playerEvents.getOrDefault(player, Set.of());
    }

    private static Hk3QuestEvents load(CompoundTag root) {
        var data = new Hk3QuestEvents();
        read(root.getList("Teams", Tag.TAG_COMPOUND), data.processes);
        read(root.getList("Players", Tag.TAG_COMPOUND), data.playerEvents);
        return data;
    }

    private static void read(ListTag rows, Map<UUID, Set<String>> target) {
        for (var raw : rows) {
            var row = (CompoundTag) raw;
            var events = new HashSet<String>();
            for (var event : row.getList("Events", Tag.TAG_STRING)) events.add(event.getAsString());
            target.put(row.getUUID("Id"), events);
        }
    }

    @Override
    public CompoundTag save(CompoundTag root) {
        root.put("Teams", rows(processes));
        root.put("Players", rows(playerEvents));
        return root;
    }

    private static ListTag rows(Map<UUID, Set<String>> source) {
        var rows = new ListTag();
        source.forEach((id, events) -> {
            var row = new CompoundTag();
            row.putUUID("Id", id);
            var values = new ListTag();
            events.forEach(event -> values.add(StringTag.valueOf(event)));
            row.put("Events", values);
            rows.add(row);
        });
        return rows;
    }
}
