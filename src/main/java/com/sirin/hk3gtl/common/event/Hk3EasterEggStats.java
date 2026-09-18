package com.sirin.hk3gtl.common.event;



import net.minecraft.nbt.CompoundTag;
import net.minecraft.nbt.ListTag;
import net.minecraft.nbt.StringTag;
import net.minecraft.server.level.ServerPlayer;

import java.util.HashSet;
import java.util.Set;

/**
 * 彩蛋统计：玩家 persistentData 中的计数与集合。
 */
public final class Hk3EasterEggStats {

    public static final String ROOT = "hk3gtl_egg_stats";

    private Hk3EasterEggStats() {}

    public static CompoundTag root(ServerPlayer player) {
        CompoundTag data = player.getPersistentData();
        if (!data.contains(ROOT)) {
            data.put(ROOT, new CompoundTag());
        }
        return data.getCompound(ROOT);
    }

    public static long getLong(ServerPlayer player, String key) {
        return root(player).getLong(key);
    }

    public static void addLong(ServerPlayer player, String key, long delta) {
        CompoundTag tag = root(player);
        tag.putLong(key, tag.getLong(key) + delta);
    }

    public static int getInt(ServerPlayer player, String key) {
        return root(player).getInt(key);
    }

    public static void putInt(ServerPlayer player, String key, int value) {
        root(player).putInt(key, value);
    }

    public static void addInt(ServerPlayer player, String key, int delta) {
        putInt(player, key, getInt(player, key) + delta);
    }

    public static boolean getFlag(ServerPlayer player, String key) {
        return root(player).getBoolean(key);
    }

    public static void setFlag(ServerPlayer player, String key, boolean value) {
        root(player).putBoolean(key, value);
    }

    public static Set<String> getBuiltMachines(ServerPlayer player) {
        Set<String> set = new HashSet<>();
        ListTag list = root(player).getList("built_machines", 8);
        for (int i = 0; i < list.size(); i++) {
            set.add(list.getString(i));
        }
        return set;
    }

    public static void markMachineBuilt(ServerPlayer player, String machineId) {
        addInt(player, "multiblock_formed_total", 1);
        Set<String> built = getBuiltMachines(player);
        if (built.add(machineId)) {
            ListTag list = new ListTag();
            for (String id : built) {
                list.add(StringTag.valueOf(id));
            }
            root(player).put("built_machines", list);
        }
    }

    public static int getMultiblockFormedTotal(ServerPlayer player) {
        return getInt(player, "multiblock_formed_total");
    }

    public static int countBuiltMachines(ServerPlayer player) {
        return getBuiltMachines(player).size();
    }

    public static boolean hasBuiltAll(ServerPlayer player, String... machineIds) {
        Set<String> built = getBuiltMachines(player);
        for (String id : machineIds) {
            if (!built.contains(id)) {
                return false;
            }
        }
        return true;
    }
}
