package com.sirin.hk3gtl.common.gaze;

import net.minecraft.nbt.CompoundTag;
import net.minecraft.nbt.ListTag;
import net.minecraft.nbt.Tag;

/**
 * 【文件职责】保存个人注视来源、去重键和历史峰值；仅由服务端业务调用，随玩家数据存盘与重生复制。
 * 【变更记录 #1】2026-09-30 15:50:54（内测5修订109）
 * 删除：无。新增：永久里程碑去重与最近64条变更记录。
 * 修改：来源日志与去重集合分离，裁剪日志不会允许重复增长；用途：提供可查询的注视来源与迁移基线。
 */
public final class Hk3GazeJournal {
    public static final String KEY = "hk3gtl_gaze_journal";
    private Hk3GazeJournal() {}
    private static CompoundTag journal(CompoundTag player) {
        if (!player.contains(KEY, Tag.TAG_COMPOUND)) player.put(KEY, new CompoundTag());
        return player.getCompound(KEY);
    }
    public static boolean claim(CompoundTag player, String key) {
        if (key == null || key.isBlank() || key.length() > 200) throw new IllegalArgumentException("无效注视来源键");
        var root = journal(player);
        var seen = root.getCompound("Seen");
        if (seen.getBoolean(key)) return false;
        seen.putBoolean(key, true); root.put("Seen", seen); return true;
    }
    public static void record(CompoundTag player, String source, int before, int after, long tick) {
        var root = journal(player);
        root.putInt("Peak", Math.max(root.getInt("Peak"), Math.max(before, after)));
        if (before == after) return;
        var list = root.getList("Recent", Tag.TAG_COMPOUND);
        var entry = new CompoundTag(); entry.putString("Source", source);
        entry.putInt("Before", before); entry.putInt("After", after); entry.putLong("Tick", tick);
        list.add(entry); while (list.size() > 64) list.remove(0);
        root.put("Recent", list);
    }
    public static ListTag recent(CompoundTag player) {
        return journal(player).getList("Recent", Tag.TAG_COMPOUND).copy();
    }
}
