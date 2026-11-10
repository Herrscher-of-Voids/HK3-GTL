package com.sirin.hk3gtl.common.dialogue;

import com.sirin.hk3gtl.common.util.Hk3SavedDataGuard;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.nbt.Tag;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.level.saveddata.SavedData;

import java.util.HashMap;
import java.util.Map;
import java.util.UUID;

/** 终审IF首次选读记录，按世界存档中的玩家UUID保存。指令阅览不访问写入口。 */
public final class Hk3FinaleIfData extends SavedData {
    public static final int BRANCH_COUNT = 26;
    public static final int MAX_CHOICES = 5;
    private static final String NAME = "hk3gtl_finale_if_v5";
    private static final int VALID_MASK = (1 << BRANCH_COUNT) - 1;
    private final Map<UUID, Integer> selected = new HashMap<>();

    public static Hk3FinaleIfData get(ServerPlayer player) {
        return Hk3SavedDataGuard.get(player.server, NAME, Hk3FinaleIfData::load, Hk3FinaleIfData::new);
    }

    public static Hk3FinaleIfData load(CompoundTag tag) {
        Hk3FinaleIfData data = new Hk3FinaleIfData();
        if (!tag.contains("Selected", Tag.TAG_COMPOUND))
            throw new IllegalStateException("IF账本缺少有效的Selected字段");
        CompoundTag entries = tag.getCompound("Selected");
        for (String key : entries.getAllKeys()) {
            if (!entries.contains(key, Tag.TAG_INT)) throw new IllegalStateException("IF账本条目类型错误：" + key);
            UUID id;
            try {
                id = UUID.fromString(key);
            } catch (IllegalArgumentException e) {
                throw new IllegalStateException("IF账本玩家标识错误：" + key, e);
            }
            int mask = entries.getInt(key);
            if ((mask & ~VALID_MASK) != 0 || Integer.bitCount(mask) > MAX_CHOICES)
                throw new IllegalStateException("IF账本条目范围错误：" + key);
            data.selected.put(id, mask);
        }
        return data;
    }

    @Override
    public CompoundTag save(CompoundTag tag) {
        CompoundTag entries = new CompoundTag();
        selected.forEach((id, mask) -> entries.putInt(id.toString(), mask));
        tag.put("Selected", entries);
        return tag;
    }

    public int selectedMask(UUID player) {
        return selected.getOrDefault(player, 0);
    }

    public int selectedCount(UUID player) {
        return Integer.bitCount(selectedMask(player));
    }

    /** 仅由服务端已核验的终审选择调用；重复选择原条目不另扣名额。 */
    public boolean select(UUID player, int index) {
        if (index < 0 || index >= BRANCH_COUNT) return false;
        int mask = selectedMask(player);
        int bit = 1 << index;
        if ((mask & bit) != 0) return true;
        if (Integer.bitCount(mask) >= MAX_CHOICES) return false;
        selected.put(player, mask | bit);
        setDirty();
        return true;
    }
}
