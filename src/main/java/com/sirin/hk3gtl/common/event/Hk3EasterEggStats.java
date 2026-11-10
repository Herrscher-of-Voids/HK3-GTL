package com.sirin.hk3gtl.common.event;


/**
 * 【文件职责】
 * - 处理 Hk3EasterEggStats 相关事件分发与触发。
 * - 关键调用链：由上层系统入口调用 -> 本文件核心方法 -> 下游模块。
 *
 * 【变更记录】2026-05-19
 * - 删除：
 *   1) 初始归档备注：自 v0.3 基线梳理，无本次 diff。
 * - 新增：
 *   1) 新增统一变更备注块，便于后续维护与审计追踪。
 * - 修改：
 *   1) 未改动业务逻辑，仅补充文件级职责与维护注释模板。
 * - 用途：
 *   1) 帮助维护者快速理解文件职责、变更背景与风险点。
 *
 * 【段内说明】
 * - 复杂方法补充“干什么 / 边界 / 线程侧”精简中文注释。
 */
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
