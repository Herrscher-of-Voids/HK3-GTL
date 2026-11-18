package com.sirin.hk3gtl.common.communication;

import net.minecraft.nbt.*;
import net.minecraft.server.MinecraftServer;
import net.minecraft.world.level.saveddata.SavedData;
import java.util.*;









public final class Hk3PersonalCommunicationData extends SavedData {
    private CompoundTag players = new CompoundTag();
    public static Hk3PersonalCommunicationData get(MinecraftServer server) {
        return com.sirin.hk3gtl.common.util.Hk3SavedDataGuard.get(server,
                "hk3gtl_personal_communication_v5", Hk3PersonalCommunicationData::load, Hk3PersonalCommunicationData::new);
    }
    public static Hk3PersonalCommunicationData load(CompoundTag root) {
        if (!root.contains("Version", Tag.TAG_INT) || root.getInt("Version") != 1 || !root.contains("Players", Tag.TAG_COMPOUND))
            throw new IllegalArgumentException("个人交流账本格式异常，拒绝重置");
        var data = new Hk3PersonalCommunicationData(); data.players = root.getCompound("Players").copy(); return data;
    }
    @Override public CompoundTag save(CompoundTag root) {
        root.putInt("Version", 1); root.put("Players", players.copy()); return root;
    }
    private CompoundTag person(UUID actor) { return players.getCompound(actor.toString()).copy(); }
    private static String key(UUID team, String topic) { return team + "/" + topic; }
    public CompoundTag snapshot(UUID actor, UUID team, String topic) {
        return person(actor).getCompound("Active").getCompound(key(team, topic)).copy();
    }
    private void put(UUID actor, UUID team, String topic, CompoundTag snapshot) {
        var person = person(actor); var active = person.getCompound("Active").copy();
        active.put(key(team, topic), snapshot.copy()); person.put("Active", active);
        if (complete(snapshot)) {
            var history = person.getCompound("Completed").copy();
            if (!history.contains(topic)) history.put(topic, snapshot.copy());
            person.put("Completed", history);
        }
        players.put(actor.toString(), person); setDirty();
    }
    public static List<String> documents(CompoundTag snapshot) {
        var docs = snapshot.getList("Documents", Tag.TAG_STRING);
        return docs.stream().map(Tag::getAsString).toList();
    }
    private static boolean validPath(String topic, List<String> path) {
        var t = Hk3DiplomacyData.topic(topic);
        if (t == null || path.isEmpty() || path.size() > 16) return false;
        var allowed = new HashSet<>(List.of(t.first(), t.yes(), t.no(), t.agreed(), t.refused(), t.submit(), t.feedback(), t.retry(), t.resumed(), "N20"));
        if (topic.equals("schicksal")) allowed.add("A06");
        return path.stream().allMatch(s -> !s.isBlank() && allowed.contains(s));
    }
    public static boolean valid(CompoundTag n) {
        return n.hasUUID("Attempt") && n.hasUUID("Team") && n.hasUUID("Actor")
                && n.contains("Version", Tag.TAG_INT) && n.getInt("Version") > 0
                && n.contains("Step", Tag.TAG_INT) && n.getInt("Step") >= 0
                && n.getInt("Step") <= documents(n).size()
                && (n.getInt("Step") == documents(n).size()
                    ? n.contains("CompletedAt", Tag.TAG_LONG) && n.getLong("CompletedAt") >= 0
                    : !n.contains("CompletedAt"))
                && validPath(n.getString("Topic"), documents(n));
    }
    public static boolean complete(CompoundTag n) {
        return valid(n) && n.getInt("Step") == documents(n).size()
                && n.contains("CompletedAt", Tag.TAG_LONG) && n.getLong("CompletedAt") >= 0;
    }
    /** 同一路线恢复原检查点；主题有新决定时新建快照，已完成历史不删除。损坏记录拒绝覆盖。 */
    public boolean begin(UUID actor, UUID team, String topic, int version, List<String> path, boolean member) {
        if (!member || version < 1 || !validPath(topic, path)) return false;
        var person = person(actor);
        if ((players.contains(actor.toString()) && !players.contains(actor.toString(), Tag.TAG_COMPOUND))
                || (person.contains("Active") && !person.contains("Active", Tag.TAG_COMPOUND))
                || (person.contains("Completed") && !person.contains("Completed", Tag.TAG_COMPOUND))) return false;
        var active = person.getCompound("Active"); var existing = snapshot(actor, team, topic);
        if (active.contains(key(team, topic)) && (!valid(existing) || !actor.equals(existing.getUUID("Actor")) || !team.equals(existing.getUUID("Team")) || !topic.equals(existing.getString("Topic")))) return false;
        if (valid(existing) && existing.getInt("Version") == version && documents(existing).equals(path)) return true;
        var n = new CompoundTag(); n.putUUID("Attempt", UUID.randomUUID()); n.putUUID("Team", team); n.putUUID("Actor", actor);
        n.putString("Topic", topic); n.putInt("Version", version); n.putInt("Step", 0);
        var docs = new ListTag(); path.forEach(s -> docs.add(StringTag.valueOf(s))); n.put("Documents", docs);
        put(actor, team, topic, n); return true;
    }
    /** 单次令牌之外再校验持久化快照，旧页面、离队及重复包不能推进。 */
    public boolean advance(UUID actor, UUID team, String topic, UUID attempt, int version, int step,
                           List<String> currentPath, boolean member, long tick) {
        var n = snapshot(actor, team, topic);
        if (!member || tick < 0 || !valid(n) || complete(n) || !n.getUUID("Actor").equals(actor)
                || !n.getUUID("Team").equals(team) || !n.getString("Topic").equals(topic)
                || !n.getUUID("Attempt").equals(attempt) || n.getInt("Version") != version
                || n.getInt("Step") != step || step >= documents(n).size() || !documents(n).equals(currentPath)) return false;
        n.putInt("Step", step + 1);
        if (step + 1 == documents(n).size()) n.putLong("CompletedAt", tick);
        put(actor, team, topic, n); return true;
    }
    public boolean experienced(UUID actor, String topic) {
        var n = person(actor).getCompound("Completed").getCompound(topic);
        return complete(n) && n.getUUID("Actor").equals(actor) && n.getString("Topic").equals(topic);
    }
    public boolean completedCurrent(UUID actor, UUID team, String topic, int version, List<String> path) {
        var n = snapshot(actor, team, topic);
        return complete(n) && n.getUUID("Actor").equals(actor) && n.getUUID("Team").equals(team)
                && n.getString("Topic").equals(topic) && n.getInt("Version") == version && documents(n).equals(path);
    }
}
