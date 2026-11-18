package com.sirin.hk3gtl.common.communication;

 





import net.minecraft.nbt.CompoundTag;
import net.minecraft.nbt.Tag;
import net.minecraft.server.MinecraftServer;
import net.minecraft.world.level.saveddata.SavedData;

import java.util.UUID;

public final class Hk3ProgressCorrespondenceData extends SavedData {
    private CompoundTag teams = new CompoundTag();

    public static Hk3ProgressCorrespondenceData get(MinecraftServer server) {
        return com.sirin.hk3gtl.common.util.Hk3SavedDataGuard.get(server, "hk3gtl_progress_correspondence_v1",
                Hk3ProgressCorrespondenceData::load, Hk3ProgressCorrespondenceData::new);
    }

    public static Hk3ProgressCorrespondenceData load(CompoundTag tag) {
        if (!tag.contains("Teams", Tag.TAG_COMPOUND) || (tag.contains("Version") && tag.getInt("Version") != 1))
            throw new IllegalArgumentException("持续通信账本异常，拒绝重置");
        var data = new Hk3ProgressCorrespondenceData();
        data.teams = tag.getCompound("Teams").copy();
        return data;
    }

    @Override public CompoundTag save(CompoundTag tag) {
        tag.putInt("Version", 1);
        tag.put("Teams", teams.copy());
        return tag;
    }

    private CompoundTag team(UUID id) { return teams.getCompound(id.toString()).copy(); }

    public boolean delivered(UUID team, String stage) {
        return team(team).getCompound(stage).contains("DeliveredAt", Tag.TAG_LONG);
    }

    public String route(UUID team, String stage) { return team(team).getCompound(stage).getString("Route"); }

    public boolean deliver(UUID team, String stage, String route, long time) {
        if (delivered(team, stage)) return false;
        var row = team(team);
        var letter = row.getCompound(stage).copy();
        letter.putLong("DeliveredAt", time);
        letter.putString("Route", route);
        row.put(stage, letter);
        teams.put(team.toString(), row);
        setDirty();
        return true;
    }

    public CompoundTag reply(UUID team, String stage) { return team(team).getCompound(stage).getCompound("Reply").copy(); }

    public boolean answer(UUID team, String stage, UUID actor, int choice, long time) {
        if (!delivered(team, stage) || choice < 0 || choice > 1 || !reply(team, stage).isEmpty()) return false;
        var row = team(team);
        var letter = row.getCompound(stage).copy();
        var answer = new CompoundTag();
        answer.putUUID("Actor", actor);
        answer.putInt("Choice", choice);
        answer.putLong("Time", time);
        letter.put("Reply", answer);
        row.put(stage, letter);
        teams.put(team.toString(), row);
        setDirty();
        return true;
    }
}
