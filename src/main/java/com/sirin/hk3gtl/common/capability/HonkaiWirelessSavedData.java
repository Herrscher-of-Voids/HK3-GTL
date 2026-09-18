package com.sirin.hk3gtl.common.capability;



import net.minecraft.nbt.CompoundTag;
import net.minecraft.nbt.ListTag;
import net.minecraft.nbt.Tag;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.level.saveddata.SavedData;

import javax.annotation.Nullable;
import java.math.BigInteger;
import java.util.Map;
import java.util.UUID;
import java.util.concurrent.ConcurrentHashMap;

public final class HonkaiWirelessSavedData extends SavedData {

    public static final String DATA_NAME = "hk3gtl_wireless_pool";
    private static final String POOLS_KEY = "pools";
    private static final String ID_KEY = "id";
    private static final String AMOUNT_KEY = "amt";

    private final Map<UUID, BigInteger> pools = new ConcurrentHashMap<>();

    public HonkaiWirelessSavedData() {}

    public static HonkaiWirelessSavedData load(CompoundTag tag) {
        HonkaiWirelessSavedData data = new HonkaiWirelessSavedData();
        if (!tag.contains(POOLS_KEY, Tag.TAG_LIST)) return data;

        ListTag list = tag.getList(POOLS_KEY, Tag.TAG_COMPOUND);
        for (int index = 0; index < list.size(); index++) {
            CompoundTag entry = list.getCompound(index);
            if (!entry.hasUUID(ID_KEY) || !entry.contains(AMOUNT_KEY, Tag.TAG_STRING)) continue;
            try {
                BigInteger amount = new BigInteger(entry.getString(AMOUNT_KEY));
                if (amount.signum() > 0) data.pools.put(entry.getUUID(ID_KEY), amount);
            } catch (NumberFormatException ignored) {
                // 单条损坏记录不应阻止世界加载。
            }
        }
        return data;
    }

    @Override
    public CompoundTag save(CompoundTag tag) {
        ListTag list = new ListTag();
        for (Map.Entry<UUID, BigInteger> entryValue : pools.entrySet()) {
            BigInteger amount = entryValue.getValue();
            if (amount == null || amount.signum() <= 0) continue;
            CompoundTag entry = new CompoundTag();
            entry.putUUID(ID_KEY, entryValue.getKey());
            entry.putString(AMOUNT_KEY, amount.toString());
            list.add(entry);
        }
        tag.put(POOLS_KEY, list);
        return tag;
    }

    public static HonkaiWirelessSavedData get(MinecraftServer server) {
        if (server == null) return null;
        ServerLevel overworld = server.overworld();
        return overworld.getDataStorage().computeIfAbsent(
                HonkaiWirelessSavedData::load,
                HonkaiWirelessSavedData::new,
                DATA_NAME);
    }

    public BigInteger getAmount(UUID playerId) {
        return pools.getOrDefault(playerId, BigInteger.ZERO);
    }

    public void setAmount(UUID playerId, BigInteger amount) {
        BigInteger normalized = amount == null || amount.signum() <= 0 ? BigInteger.ZERO : amount;
        if (normalized.signum() == 0) {
            if (pools.remove(playerId) != null) setDirty();
            return;
        }
        BigInteger previous = pools.put(playerId, normalized);
        if (!normalized.equals(previous)) setDirty();
    }

    public void mirrorToMemory() {
        for (Map.Entry<UUID, BigInteger> entry : pools.entrySet()) {
            HonkaiWirelessNetwork.putStoredAmountInternal(entry.getKey(), entry.getValue());
        }
    }

    public boolean hasPool(@Nullable UUID playerId) {
        return playerId != null && pools.containsKey(playerId);
    }
}
