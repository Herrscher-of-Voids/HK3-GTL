package com.sirin.hk3gtl.common.integration.ae.exact;

import appeng.api.stacks.AEKey;
import com.sirin.hk3gtl.common.research.Hk3ResearchPaymentJournal;
import com.sirin.hk3gtl.common.util.Hk3SavedDataGuard;
import net.minecraft.SharedConstants;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.nbt.ListTag;
import net.minecraft.nbt.Tag;
import net.minecraft.server.MinecraftServer;
import net.minecraft.world.level.saveddata.SavedData;
import net.minecraft.world.level.storage.LevelResource;

import java.io.IOException;
import java.math.BigInteger;
import java.util.HashMap;
import java.util.LinkedHashMap;
import java.util.Map;
import java.util.UUID;

/** 父订单保存精确整数；提交CPU前强制持久化在途令牌，重启不能盲目重发。 */
public final class Hk3ExactOrderData extends SavedData {
    private static final String NAME = "hk3gtl_ae_exact_orders_v1";
    static final int MAX_ORDERS = 256;
    final Map<UUID, Entry> entries = new LinkedHashMap<>();
    final Map<UUID, Entry> activeTokens = new HashMap<>();

    static final class Entry {
        final Hk3ExactOrder order;
        final AEKey target;
        final BigInteger plannedBytes;
        UUID parent;
        Map<AEKey, BigInteger> missingSupply = Map.of();
        String note;

        Entry(Hk3ExactOrder order, AEKey target, BigInteger plannedBytes, String note) {
            this.order = order;
            this.target = target;
            this.plannedBytes = plannedBytes;
            this.note = note;
        }
    }

    static Hk3ExactOrderData get(MinecraftServer server) {
        return Hk3SavedDataGuard.get(server, NAME, Hk3ExactOrderData::load, Hk3ExactOrderData::new);
    }

    static Hk3ExactOrderData load(CompoundTag tag) {
        return load(tag, AEKey::fromTagGeneric);
    }

    static Hk3ExactOrderData load(CompoundTag tag, java.util.function.Function<CompoundTag, AEKey> keyReader) {
        if (tag.getInt("Version") != 1 || !tag.contains("Orders", Tag.TAG_LIST))
            throw new IllegalArgumentException("大数订单账本版本或结构损坏");
        ListTag list = (ListTag) tag.get("Orders");
        if (!list.isEmpty() && list.getElementType() != Tag.TAG_COMPOUND)
            throw new IllegalArgumentException("大数订单列表元素损坏");
        if (list.size() > MAX_ORDERS) throw new IllegalArgumentException("大数订单账本超过容量");
        Hk3ExactOrderData data = new Hk3ExactOrderData();
        var tokens = new java.util.HashSet<UUID>();
        for (Tag element : list) {
            CompoundTag row = (CompoundTag) element;
            if (!row.hasUUID("Id") || !row.hasUUID("Owner") || !row.contains("State", Tag.TAG_STRING))
                throw new IllegalArgumentException("大数订单身份缺失");
            UUID token = row.hasUUID("ActiveToken") ? row.getUUID("ActiveToken") : null;
            if (row.contains("ActiveToken") && token == null) throw new IllegalArgumentException("大数批次令牌损坏");
            if (token != null && !tokens.add(token)) throw new IllegalArgumentException("大数批次令牌重复");
            var snapshot = new Hk3ExactOrder.Snapshot(row.getUUID("Id"), row.getUUID("Owner"),
                    integer(row, "Total"), integer(row, "Completed"), integer(row, "ActiveAmount"),
                    token, Hk3ExactOrder.State.valueOf(row.getString("State")));
            if (!row.contains("Target", Tag.TAG_COMPOUND)) throw new IllegalArgumentException("大数订单目标缺失");
            AEKey target = keyReader.apply(row.getCompound("Target"));
            if (target == null) throw new IllegalArgumentException("大数订单资源无法解析");
            Entry entry = new Entry(Hk3ExactOrder.restore(snapshot), target, integer(row, "Bytes"),
                    "重启后已暂停；在途批次只等待原CPU回执，不重新投料");
            if (row.hasUUID("Parent")) entry.parent = row.getUUID("Parent");
            if (data.entries.put(snapshot.orderId(), entry) != null)
                throw new IllegalArgumentException("大数订单编号重复");
            if (token != null) data.activeTokens.put(token, entry);
        }
        return data;
    }

    @Override
    public CompoundTag save(CompoundTag tag) {
        tag.putInt("Version", 1);
        ListTag list = new ListTag();
        for (Entry entry : entries.values()) {
            var state = entry.order.snapshot();
            CompoundTag row = new CompoundTag();
            row.putUUID("Id", state.orderId());
            row.putUUID("Owner", state.owner());
            if (entry.parent != null) row.putUUID("Parent", entry.parent);
            row.putByteArray("Total", state.total().toByteArray());
            row.putByteArray("Completed", state.completed().toByteArray());
            row.putByteArray("ActiveAmount", state.activeAmount().toByteArray());
            if (state.activeToken() != null) row.putUUID("ActiveToken", state.activeToken());
            row.putString("State", state.state().name());
            row.put("Target", entry.target.toTagGeneric());
            row.putByteArray("Bytes", entry.plannedBytes.toByteArray());
            list.add(row);
        }
        tag.put("Orders", list);
        return tag;
    }

    /** 复用已有强制写盘和原子替换实现；写失败时调用方禁止提交CPU。 */
    void checkpoint(MinecraftServer server) throws IOException {
        setDirty();
        CompoundTag envelope = new CompoundTag();
        envelope.put("data", save(new CompoundTag()));
        envelope.putInt("DataVersion", SharedConstants.getCurrentVersion().getDataVersion().getVersion());
        Hk3ResearchPaymentJournal.write(server.getWorldPath(LevelResource.ROOT).resolve("data")
                .resolve(NAME + ".dat"), envelope);
    }

    private static BigInteger integer(CompoundTag row, String key) {
        if (!row.contains(key, Tag.TAG_BYTE_ARRAY)) throw new IllegalArgumentException("大数订单数字缺失：" + key);
        byte[] bytes = row.getByteArray(key);
        if (bytes.length == 0 || bytes.length > 65536) throw new IllegalArgumentException("大数订单数字长度无效");
        BigInteger number = new BigInteger(bytes);
        if (number.signum() < 0) throw new IllegalArgumentException("大数订单数量不能为负数");
        return number;
    }
}
