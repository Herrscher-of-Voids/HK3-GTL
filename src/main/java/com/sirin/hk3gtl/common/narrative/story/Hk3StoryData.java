package com.sirin.hk3gtl.common.narrative.story;

import net.minecraft.nbt.CompoundTag;
import net.minecraft.nbt.Tag;
import net.minecraft.server.MinecraftServer;
import net.minecraft.world.level.saveddata.SavedData;
import java.util.UUID;

public final class Hk3StoryData extends SavedData {
    private final CompoundTag people;
    private final CompoundTag teams;

    public Hk3StoryData() { this(new CompoundTag(), new CompoundTag()); }
    private Hk3StoryData(CompoundTag people, CompoundTag teams) { this.people = people; this.teams = teams; }

    public static Hk3StoryData get(MinecraftServer server) {
        return com.sirin.hk3gtl.common.util.Hk3SavedDataGuard.get(server, "hk3gtl_story_v1", Hk3StoryData::load, Hk3StoryData::new);
    }

    private static Hk3StoryData load(CompoundTag tag) {
        if (tag.getInt("Version") != 1 || !tag.contains("People", Tag.TAG_COMPOUND) || !tag.contains("Teams", Tag.TAG_COMPOUND))
            throw new IllegalStateException("文明剧情存档格式异常");
        return new Hk3StoryData(tag.getCompound("People"), tag.getCompound("Teams"));
    }

    private CompoundTag child(CompoundTag parent, String key) {
        if (!parent.contains(key)) parent.put(key, new CompoundTag());
        return parent.getCompound(key);
    }

    private CompoundTag person(UUID actor) { return child(people, actor.toString()); }
    private CompoundTag chapters(UUID actor, UUID team) { return child(child(person(actor), "Chapters"), team.toString()); }
    private CompoundTag stored(UUID actor, UUID team) { return people.getCompound(actor.toString()).getCompound("Chapters").getCompound(team.toString()); }

    private boolean record(CompoundTag facts, String id, long tick) {
        if (facts.contains(id)) return false;
        facts.putLong(id, tick); setDirty(); return true;
    }

    public boolean fact(UUID actor, String id, long tick) { return record(child(person(actor), "Facts"), id, tick); }
    public boolean teamFact(UUID team, String id, long tick) { return record(child(teams, team.toString()), id, tick); }
    public boolean teamHas(UUID team, String id) { return teams.getCompound(team.toString()).contains(id); }

    public boolean has(UUID actor, UUID team, String id) {
        if (id.startsWith("story_")) return completed(actor, team, id.substring(6));
        return people.getCompound(actor.toString()).getCompound("Facts").contains(id)
                || teams.getCompound(team.toString()).contains(id);
    }

    public boolean remembers(UUID actor, UUID team, String id) {
        if (!id.startsWith("story_")) return has(actor, team, id);
        var chapters = history(actor);
        for (String origin : chapters.getAllKeys())
            if (chapters.getCompound(origin).getCompound(id.substring(6)).contains("Completed")) return true;
        return false;
    }

    public boolean delivered(UUID actor, UUID team, String id) { return stored(actor, team).getCompound(id).contains("Delivered"); }
    public boolean completed(UUID actor, UUID team, String id) { return stored(actor, team).getCompound(id).contains("Completed"); }
    public void deliver(UUID actor, UUID team, String id, long tick) { record(child(chapters(actor, team), id), "Delivered", tick); }
    public void complete(UUID actor, UUID team, String id, String choice, String reply, long tick) {
        var node = child(chapters(actor, team), id);
        node.putLong("Completed", tick); node.putString("Choice", choice); node.putString("Reply", reply); setDirty();
    }
    public void defer(UUID actor, UUID team, String id, String choice, String reply, long tick) {
        var node = child(chapters(actor, team), id);
        node.putLong("Deferred", tick); node.putString("Choice", choice); node.putString("Reply", reply); setDirty();
    }
    public String answer(UUID actor, UUID team, String id) { return stored(actor, team).getCompound(id).getString("Choice"); }
    public String reply(UUID actor, UUID team, String id) { return stored(actor, team).getCompound(id).getString("Reply"); }
    public void choice(UUID actor, UUID team, String key, String value) {
        var choices = child(child(person(actor), "Choices"), team.toString());
        if (choices.getString(key).equals(value)) return;
        choices.putString(key, value); setDirty();
    }
    public CompoundTag history(UUID actor) { return people.getCompound(actor.toString()).getCompound("Chapters"); }

    @Override public CompoundTag save(CompoundTag tag) {
        tag.putInt("Version", 1); tag.put("People", people.copy()); tag.put("Teams", teams.copy()); return tag;
    }
}
