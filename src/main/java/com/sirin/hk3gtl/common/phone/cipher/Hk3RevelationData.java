package com.sirin.hk3gtl.common.phone.cipher;

import com.sirin.hk3gtl.common.util.Hk3SavedDataGuard;
import java.util.ArrayList;
import java.util.Collections;
import java.util.HashMap;
import java.util.Map;
import java.util.Random;
import java.util.UUID;
import java.util.stream.IntStream;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.server.MinecraftServer;
import net.minecraft.world.level.saveddata.SavedData;

public final class Hk3RevelationData extends SavedData {
    private final UUID edition;
    private final int[] entries;
    private final int[] order;
    private final int circuit;
    private final Map<UUID, CompoundTag> readers = new HashMap<>();

    private Hk3RevelationData(UUID edition, int[] entries, int[] order, int circuit) {
        this.edition = edition;
        this.entries = entries;
        this.order = order;
        this.circuit = circuit;
    }

    public static Hk3RevelationData get(MinecraftServer server) {
        return Hk3SavedDataGuard.get(server, "hk3gtl_seed_revelation", Hk3RevelationData::load, Hk3RevelationData::create);
    }

    private static Hk3RevelationData create() {
        UUID edition = UUID.randomUUID();
        var random = new Random(edition.getMostSignificantBits() ^ edition.getLeastSignificantBits());
        var pool = new ArrayList<>(IntStream.range(0, Hk3RevelationItems.size()).boxed().toList());
        do {
            Collections.shuffle(pool, random);
        } while (pool.subList(0, 4).stream().map(Hk3RevelationItems::namespace).distinct().count() < 2);
        var order = new ArrayList<>(java.util.List.of(0, 1, 2, 3));
        Collections.shuffle(order, random);
        var data = new Hk3RevelationData(edition, pool.subList(0, 4).stream().mapToInt(Integer::intValue).toArray(),
                order.stream().mapToInt(Integer::intValue).toArray(), random.nextInt(32) + 1);
        data.setDirty();
        return data;
    }

    public int entry(int page) { return entries[page]; }
    public int order(int page) { return order[page]; }
    public int circuit() { return circuit; }

    public CompoundTag reader(UUID player) {
        return readers.computeIfAbsent(player, id -> new CompoundTag());
    }

    public void select(UUID player, int page) {
        reader(player).putInt("Page", page);
        setDirty();
    }

    public void verify(UUID player, int page) {
        var reader = reader(player);
        reader.putInt("Mask", reader.getInt("Mask") | 1 << page);
        setDirty();
    }

    public void hint(UUID player, int page) {
        var reader = reader(player);
        reader.putInt("Hints", reader.getInt("Hints") | 1 << page);
        setDirty();
    }

    private static Hk3RevelationData load(CompoundTag tag) {
        var data = new Hk3RevelationData(tag.getUUID("Edition"), tag.getIntArray("Entries"),
                tag.getIntArray("Order"), tag.getInt("Circuit"));
        var readers = tag.getCompound("Readers");
        for (String id : readers.getAllKeys()) data.readers.put(UUID.fromString(id), readers.getCompound(id));
        return data;
    }

    @Override public CompoundTag save(CompoundTag tag) {
        tag.putUUID("Edition", edition);
        tag.putIntArray("Entries", entries);
        tag.putIntArray("Order", order);
        tag.putInt("Circuit", circuit);
        var rows = new CompoundTag();
        readers.forEach((id, reader) -> rows.put(id.toString(), reader));
        tag.put("Readers", rows);
        return tag;
    }
}
