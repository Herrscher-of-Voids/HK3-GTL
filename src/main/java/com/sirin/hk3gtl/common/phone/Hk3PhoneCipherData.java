package com.sirin.hk3gtl.common.phone;

import com.sirin.hk3gtl.common.util.Hk3SavedDataGuard;
import java.util.HashMap;
import java.util.Map;
import java.util.UUID;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.level.saveddata.SavedData;

public final class Hk3PhoneCipherData extends SavedData {
    public record Progress(int stage, int hints) {}

    private final Map<UUID, Progress> users = new HashMap<>();

    public static Hk3PhoneCipherData get(ServerPlayer player) {
        return Hk3SavedDataGuard.get(player.server, "hk3gtl_phone_cipher",
                Hk3PhoneCipherData::load, Hk3PhoneCipherData::new);
    }

    public Progress progress(UUID player) {
        return users.getOrDefault(player, new Progress(0, 0));
    }

    public void advance(UUID player) {
        var old = progress(player);
        users.put(player, new Progress(old.stage() + 1, old.hints()));
        setDirty();
    }

    public void hint(UUID player) {
        var old = progress(player);
        users.put(player, new Progress(old.stage(), old.hints() | 1 << old.stage()));
        setDirty();
    }

    public static Hk3PhoneCipherData load(CompoundTag tag) {
        var data = new Hk3PhoneCipherData();
        var users = tag.getCompound("Users");
        for (String id : users.getAllKeys()) {
            var row = users.getCompound(id);
            data.users.put(UUID.fromString(id), new Progress(row.getInt("Stage"), row.getInt("Hints")));
        }
        return data;
    }

    @Override
    public CompoundTag save(CompoundTag tag) {
        var rows = new CompoundTag();
        users.forEach((id, progress) -> {
            var row = new CompoundTag();
            row.putInt("Stage", progress.stage());
            row.putInt("Hints", progress.hints());
            rows.put(id.toString(), row);
        });
        tag.put("Users", rows);
        return tag;
    }
}
