package com.sirin.hk3gtl.common.gaze;

import net.minecraft.nbt.CompoundTag;
import net.minecraft.nbt.ListTag;
import net.minecraft.nbt.Tag;

 





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
