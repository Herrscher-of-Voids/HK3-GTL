package com.sirin.hk3gtl.common.communication;











/** 修订100 · 2026-09-29：接通团队研究归属、个人付款及真实实验来源。 */

import net.minecraft.nbt.CompoundTag;
import net.minecraft.nbt.Tag;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.level.saveddata.SavedData;
import java.util.LinkedHashMap;
import java.util.Map;
import java.util.UUID;


public final class Hk3CommunicationData extends SavedData {
    private static final String NAME = "hk3gtl_communication_v5";
    private final Map<UUID, Hk3FirstContactState> contacts = new LinkedHashMap<>();
    // 未识别条目原样保留且不允许改写，避免损坏/未来版本状态被重置后重复答复。
    private CompoundTag unrecognized = new CompoundTag();

    public static Hk3CommunicationData get(ServerPlayer player) {
        return get(player.server);
    }
    public static Hk3CommunicationData get(net.minecraft.server.MinecraftServer server) {
        return com.sirin.hk3gtl.common.util.Hk3SavedDataGuard.get(server,NAME,Hk3CommunicationData::load,Hk3CommunicationData::new);
    }

    /** NBT采用枚举名字而非序号；未知条目保留，避免未来枚举插入改变旧值。 / Name-based NBT avoids ordinal drift; unknown values are retained. */
    public static Hk3CommunicationData load(CompoundTag tag) {
        if(!tag.contains("Contacts",Tag.TAG_COMPOUND))throw new IllegalArgumentException("首信来源账本异常，拒绝重置");
        Hk3CommunicationData data = new Hk3CommunicationData();
        data.unrecognized = tag.getCompound("Contacts").copy();
        for (String id : data.unrecognized.getAllKeys().toArray(String[]::new)) {
            try {
                UUID uuid = UUID.fromString(id);
                if (!data.unrecognized.contains(id, Tag.TAG_STRING)) continue;
                data.contacts.put(uuid, Hk3FirstContactState.valueOf(data.unrecognized.getString(id)));
                data.unrecognized.remove(id);
            } catch (IllegalArgumentException ignored) {
            }
        }
        return data;
    }

    /** 序列化当前档案及未知条目，无客户端数据作为输入。 / Serialize known states plus retained entries, never client-supplied state. */
    @Override public CompoundTag save(CompoundTag tag) {
        CompoundTag values = unrecognized.copy();
        contacts.forEach((id, state) -> values.putString(id.toString(), state.name()));
        tag.put("Contacts", values);
        return tag;
    }

    /** 未建档视为LOCKED，异常存档拒绝操作而非重置。 / Absent entries are locked; malformed entries fail closed. */
    public Hk3FirstContactState state(UUID player) {
        if (unrecognized.contains(player.toString())) throw new IllegalStateException("Unknown communication state for " + player);
        return contacts.getOrDefault(player, Hk3FirstContactState.LOCKED);
    }

    public boolean hasFact(UUID player, String fact) {
        Hk3FirstContactState state = state(player);
        if (Hk3FirstContactState.LETTER_FACT.equals(fact)) return state.hasObservationData();
        return !state.replyFact().isEmpty() && state.replyFact().equals(fact);
    }

    public boolean discover(UUID player) { return update(player, state(player).discover()); }
    /** 已读状态只前进一次。 / Mark read at most once. */
    public boolean read(UUID player) { return update(player, state(player).read()); }
    public boolean reply(UUID player, boolean accept) { return update(player, state(player).reply(accept)); }
    /** 私有写入口，无变化时不触发存盘。 / Private update avoids marking unchanged state dirty. */
    private boolean update(UUID player, Hk3FirstContactState next) {
        if (state(player) == next) return false;
        contacts.put(player, next);
        setDirty();
        return true;
    }
}
