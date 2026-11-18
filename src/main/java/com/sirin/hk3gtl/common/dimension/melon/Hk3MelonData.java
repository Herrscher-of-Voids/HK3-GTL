package com.sirin.hk3gtl.common.dimension.melon;

import com.sirin.hk3gtl.common.util.Hk3SavedDataGuard;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.server.MinecraftServer;
import net.minecraft.world.level.saveddata.SavedData;
import java.util.HashMap;
import java.util.Map;
import java.util.UUID;

public final class Hk3MelonData extends SavedData {
    private final Map<UUID, CompoundTag> players = new HashMap<>();

    public static Hk3MelonData get(MinecraftServer server) {
        return Hk3SavedDataGuard.get(server, "hk3gtl_melon_adventure", Hk3MelonData::load, Hk3MelonData::new);
    }

    public CompoundTag player(UUID id) {
        return players.computeIfAbsent(id, key -> new CompoundTag());
    }

    public void arrived(UUID id) {
        player(id).putBoolean("Visited", true);
        setDirty();
    }

    public void clue(UUID id, int index) {
        var state = player(id);
        state.putInt("Clues", state.getInt("Clues") | 1 << index);
        setDirty();
    }

    public boolean finish(UUID id) {
        var state = player(id);
        if (state.getBoolean("GiftFound")) return false;
        state.putBoolean("GiftFound", true);
        setDirty();
        return true;
    }

    public static Hk3MelonData load(CompoundTag tag) {
        var data = new Hk3MelonData();
        var players = tag.getCompound("Players");
        for (String id : players.getAllKeys()) data.players.put(UUID.fromString(id), players.getCompound(id));
        return data;
    }

    @Override public CompoundTag save(CompoundTag tag) {
        var rows = new CompoundTag();
        players.forEach((id, state) -> rows.put(id.toString(), state));
        tag.put("Players", rows);
        return tag;
    }
}
