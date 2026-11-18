package com.sirin.hk3gtl.common.machine.energy;

import com.sirin.hk3gtl.common.util.Hk3SavedDataGuard;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.nbt.ListTag;
import net.minecraft.nbt.Tag;
import net.minecraft.server.MinecraftServer;
import net.minecraft.world.level.saveddata.SavedData;

import java.util.HashSet;
import java.util.Map;
import java.util.UUID;
import java.util.concurrent.ConcurrentHashMap;

/**
 * I19-I22 批次游标的世界级持久账本。
 */
public final class Hk3ReactorEnergyData extends SavedData {
    public static final String DATA_NAME = "hk3gtl_reactor_energy";
    private static final int SCHEMA = 1;
    private static final int MAX_BATCHES = 4096;
    private static final String SCHEMA_KEY = "schema";
    private static final String BATCHES_KEY = "batches";

    private final Map<UUID, Hk3ReactorEnergyExecutor.Batch> batches = new ConcurrentHashMap<>();

    public static Hk3ReactorEnergyData load(CompoundTag tag) {
        if (tag == null || !tag.getAllKeys().equals(SetHolder.ROOT_KEYS)
                || !tag.contains(SCHEMA_KEY, Tag.TAG_INT) || tag.getInt(SCHEMA_KEY) != SCHEMA
                || !tag.contains(BATCHES_KEY, Tag.TAG_LIST)) {
            throw new IllegalArgumentException("反应堆能源账本字段或版本损坏");
        }
        ListTag list = (ListTag) tag.get(BATCHES_KEY);
        // getList会把错误元素类型转换为空列表，必须先检查原始列表，避免清空坏账本。
        if (!list.isEmpty() && list.getElementType() != Tag.TAG_COMPOUND)
            throw new IllegalArgumentException("反应堆能源账本批次列表类型损坏");
        if (list.size() > MAX_BATCHES) throw new IllegalArgumentException("反应堆能源账本批次数超限");
        Hk3ReactorEnergyData data = new Hk3ReactorEnergyData();
        SetHolder.ids(list, data);
        return data;
    }

    @Override
    public synchronized CompoundTag save(CompoundTag tag) {
        ListTag list = new ListTag();
        for (Hk3ReactorEnergyExecutor.Batch batch : batches.values()) list.add(batch.toNbt());
        tag.putInt(SCHEMA_KEY, SCHEMA);
        tag.put(BATCHES_KEY, list);
        return tag;
    }

    public static Hk3ReactorEnergyData get(MinecraftServer server) {
        if (server == null) return null;
        return Hk3SavedDataGuard.get(server, DATA_NAME, Hk3ReactorEnergyData::load, Hk3ReactorEnergyData::new);
    }

    public synchronized Hk3ReactorEnergyExecutor.Batch get(UUID batchId) {
        return batches.get(batchId);
    }

    public synchronized void put(Hk3ReactorEnergyExecutor.Batch batch) {
        if (batch == null) throw new IllegalArgumentException("反应堆批次不能为空");
        Hk3ReactorEnergyExecutor.Batch previous = batches.get(batch.batchId());
        if (previous == null && batches.size() >= MAX_BATCHES)
            throw new IllegalStateException("反应堆能源账本批次数达到上限");
        if (previous != null && (!previous.owner().equals(batch.owner())
                || !previous.role().equals(batch.role()) || !previous.recipeId().equals(batch.recipeId())
                || previous.totalTicks() != batch.totalTicks()))
            throw new IllegalArgumentException("反应堆批次身份不能更换归属或工艺合同");
        if (previous != null && (batch.elapsedTicks() < previous.elapsedTicks()
                || batch.generatedEu().compareTo(previous.generatedEu()) < 0
                || previous.completed() && !batch.completed()))
            throw new IllegalArgumentException("反应堆批次累计游标不能回退");
        batches.put(batch.batchId(), batch);
        if (!batch.equals(previous)) setDirty();
    }

    public synchronized void remove(UUID batchId) {
        if (batchId == null) return;
        Hk3ReactorEnergyExecutor.Batch batch = batches.get(batchId);
        if (batch == null) return;
        if (!batch.completed()) throw new IllegalStateException("不能清理尚未完成的反应堆批次");
        if (batches.remove(batchId, batch)) setDirty();
    }

    public synchronized int size() {
        return batches.size();
    }

    private static final class SetHolder {
        private static final java.util.Set<String> ROOT_KEYS = java.util.Set.of(SCHEMA_KEY, BATCHES_KEY);

        private static void ids(ListTag list, Hk3ReactorEnergyData data) {
            HashSet<UUID> seen = new HashSet<>();
            for (int i = 0; i < list.size(); i++) {
                Hk3ReactorEnergyExecutor.Batch batch = Hk3ReactorEnergyExecutor.Batch.fromNbt(list.getCompound(i));
                if (!seen.add(batch.batchId())) throw new IllegalArgumentException("反应堆能源账本包含重复批次身份");
                data.batches.put(batch.batchId(), batch);
            }
        }
    }
}
