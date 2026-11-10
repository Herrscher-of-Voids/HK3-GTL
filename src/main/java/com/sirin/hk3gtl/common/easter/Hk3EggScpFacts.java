package com.sirin.hk3gtl.common.easter;

import com.sirin.hk3gtl.common.phone.Hk3PhoneNotes;
import net.minecraft.core.BlockPos;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.world.phys.Vec3;
import java.text.Normalizer;
import java.util.List;
import java.util.UUID;

/**
 * 三条SCP场景的可测试边界；只判断服务端已经获得的事实。
 * 【变更记录 #1】2026-10-01 16:30:04（修订134）：删除无；新增日出区间、连续观察、穿玻璃几何、本人完整盔甲和已保存笔记判断。
 * 修改：无；用途：移除审核条件没有的抬头30度和笔记顺序限制，不改正文、不授主线资格。
 */
public final class Hk3EggScpFacts {
    public static final List<String> ARMOR_SLOTS = List.of("head", "chest", "legs", "feet");
    private Hk3EggScpFacts() {}
    private static String title(String text) { return Normalizer.normalize(text.strip(), Normalizer.Form.NFKC); }
    public static boolean whyNote(String heading, String body) { return title(heading).equals("为什么?") && body.contains("5000"); }
    public static boolean emergencyNote(String heading, String body) {
        if (!title(heading).equals("即死年")) return false;
        return java.util.Arrays.stream(body.split("[\\r\\n;；]+"))
                .map(s -> s.strip().replaceFirst("^(?:[-*•·]|[0-9０-９]+[.．、:：)）]|[一二三四五六七八九十]+[、.：:])\\s*", "").strip())
                .filter(s -> !s.isEmpty()).distinct().count() >= 3;
    }
    public static boolean hasWhyNote(List<Hk3PhoneNotes.Note> notes) { return notes.stream().anyMatch(n -> whyNote(n.title(), n.body())); }
    public static boolean hasEmergencyNote(List<Hk3PhoneNotes.Note> notes) { return notes.stream().anyMatch(n -> emergencyNote(n.title(), n.body())); }
    public static boolean ownsArmor(CompoundTag owners, UUID player, boolean[] armor) {
        if (armor.length != 4) return false;
        for (int i = 0; i < 4; i++) {
            String key = "hk3_egg_armorer_" + ARMOR_SLOTS.get(i);
            if (!armor[i] || !owners.hasUUID(key) || !owners.getUUID(key).equals(player)) return false;
        }
        return true;
    }
    public static boolean dawn(boolean overworld, long dayTime, double lookY) {
        long day = Math.floorMod(dayTime, 24000);
        return overworld && day >= 23000 && day < 24000 && Double.isFinite(lookY) && lookY >= 0;
    }
    public static int nextObservation(int previous, boolean continuous, boolean valid) {
        return valid ? Math.min(100, (continuous ? Math.max(0, previous) : 0) + 1) : 0;
    }
    /** 射线穿出完整玻璃方块的出口，越过边界后继续检查真正的遮挡。 */
    public static double exitDistance(Vec3 origin, Vec3 direction, BlockPos block) {
        double result = Double.POSITIVE_INFINITY;
        double[] start = {origin.x, origin.y, origin.z}, dir = {direction.x, direction.y, direction.z};
        int[] pos = {block.getX(), block.getY(), block.getZ()};
        for (int i = 0; i < 3; i++) if (Math.abs(dir[i]) > 1e-12) {
            double t = (pos[i] + (dir[i] > 0 ? 1 : 0) - start[i]) / dir[i];
            result = Math.min(result, t);
        }
        return result;
    }
}
