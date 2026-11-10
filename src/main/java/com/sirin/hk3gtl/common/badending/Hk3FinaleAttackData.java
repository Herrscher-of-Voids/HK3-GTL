package com.sirin.hk3gtl.common.badending;

import com.sirin.hk3gtl.common.dimension.Hk3Dimensions;
import com.sirin.hk3gtl.common.entity.VoidQueenSirinEntity;
import com.sirin.hk3gtl.common.util.Hk3SavedDataGuard;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.nbt.Tag;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.level.saveddata.SavedData;
import net.minecraftforge.event.entity.player.AttackEntityEvent;

import java.util.HashMap;
import java.util.Map;
import java.util.UUID;

/** Personal attack tally for an explicitly opened finale meeting. */
public final class Hk3FinaleAttackData extends SavedData {
    public static final int ATTACKS_TO_TRIGGER = 10;
    private static final String NAME = "hk3gtl_finale_attacks_v5";
    private final Map<UUID, Attempt> attempts = new HashMap<>();

    public static Hk3FinaleAttackData get(ServerPlayer player) {
        return Hk3SavedDataGuard.get(player.server, NAME, Hk3FinaleAttackData::load, Hk3FinaleAttackData::new);
    }

    /** Reopening the same meeting keeps its count; a new meeting starts at zero. */
    public void begin(UUID player, UUID meeting) {
        if (meeting == null) throw new IllegalArgumentException("meeting is required");
        Attempt current = attempts.get(player);
        if (current != null && current.meeting().equals(meeting)) return;
        attempts.put(player, new Attempt(meeting, 0));
        setDirty();
    }

    /** Returns -1 for a stale or absent meeting; otherwise the capped attack count. */
    public int recordDirectHit(UUID player, UUID meeting) {
        Attempt current = attempts.get(player);
        if (current == null || !current.meeting().equals(meeting)) return -1;
        if (current.hits() == ATTACKS_TO_TRIGGER) return ATTACKS_TO_TRIGGER;
        int count = current.hits() + 1;
        attempts.put(player, new Attempt(meeting, count));
        setDirty();
        return count;
    }

    public int count(UUID player, UUID meeting) {
        Attempt current = attempts.get(player);
        return current != null && current.meeting().equals(meeting) ? current.hits() : -1;
    }

    public void end(UUID player, UUID meeting) {
        Attempt current = attempts.get(player);
        if (current != null && current.meeting().equals(meeting)) {
            attempts.remove(player);
            setDirty();
        }
    }

    /** AttackEntityEvent represents the player's own left click, before hurt() is resolved. */
    public static boolean isDirectSirinAttack(AttackEntityEvent event) {
        return event.getEntity() instanceof ServerPlayer player
                && event.getTarget() instanceof VoidQueenSirinEntity
                && player.level().dimension() == Hk3Dimensions.IMAGINARY;
    }

    public static Hk3FinaleAttackData load(CompoundTag tag) {
        if (!tag.contains("Attempts", Tag.TAG_COMPOUND))
            throw new IllegalStateException("Finale attack ledger has no Attempts compound");
        Hk3FinaleAttackData data = new Hk3FinaleAttackData();
        CompoundTag entries = tag.getCompound("Attempts");
        for (String key : entries.getAllKeys()) {
            if (!entries.contains(key, Tag.TAG_COMPOUND))
                throw new IllegalStateException("Invalid finale attack entry: " + key);
            CompoundTag entry = entries.getCompound(key);
            if (!entry.hasUUID("Meeting") || !entry.contains("Hits", Tag.TAG_INT))
                throw new IllegalStateException("Incomplete finale attack entry: " + key);
            int hits = entry.getInt("Hits");
            if (hits < 0 || hits > ATTACKS_TO_TRIGGER)
                throw new IllegalStateException("Invalid finale attack count: " + key);
            try {
                data.attempts.put(UUID.fromString(key), new Attempt(entry.getUUID("Meeting"), hits));
            } catch (IllegalArgumentException e) {
                throw new IllegalStateException("Invalid finale attack player: " + key, e);
            }
        }
        return data;
    }

    @Override
    public CompoundTag save(CompoundTag tag) {
        CompoundTag entries = new CompoundTag();
        attempts.forEach((player, attempt) -> {
            CompoundTag entry = new CompoundTag();
            entry.putUUID("Meeting", attempt.meeting());
            entry.putInt("Hits", attempt.hits());
            entries.put(player.toString(), entry);
        });
        tag.put("Attempts", entries);
        return tag;
    }

    private record Attempt(UUID meeting, int hits) {}
}
