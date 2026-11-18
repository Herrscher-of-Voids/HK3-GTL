package com.sirin.hk3gtl.common.research;

import com.sirin.hk3gtl.common.util.Hk3SavedDataGuard;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.nbt.ListTag;
import net.minecraft.nbt.Tag;
import net.minecraft.server.MinecraftServer;
import net.minecraft.world.level.saveddata.SavedData;

import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.UUID;

/** W13的双边连接只授权服务，不迁移机器、课题或个人账户。 */
public final class Hk3W13ResearchData extends SavedData {
    public record Endpoint(UUID id, String dimension, long position, UUID owner, UUID team) {
        CompoundTag save() {
            var tag = new CompoundTag();
            tag.putUUID("Id", id); tag.putString("Dimension", dimension); tag.putLong("Position", position);
            tag.putUUID("Owner", owner); tag.putUUID("Team", team);
            return tag;
        }
        static Endpoint load(CompoundTag tag) {
            return new Endpoint(tag.getUUID("Id"), tag.getString("Dimension"), tag.getLong("Position"),
                    tag.getUUID("Owner"), tag.getUUID("Team"));
        }
    }
    public record Link(Endpoint mother, Endpoint lab, boolean supply, boolean receive,
                       UUID payerTeam, int priority, long version) {
        public boolean authorized(MinecraftServer server) {
            return supply && receive && Hk3ResearchTeams.scope(server, mother.owner()).equals(payerTeam);
        }
    }
    private final Map<String, Link> links = new LinkedHashMap<>();

    public static Hk3W13ResearchData get(MinecraftServer server) {
        return Hk3SavedDataGuard.get(server, "hk3gtl_w13_research", Hk3W13ResearchData::load, Hk3W13ResearchData::new);
    }
    private static String key(UUID mother, UUID lab) { return mother + "/" + lab; }
    public Link link(UUID mother, UUID lab) { return links.get(key(mother, lab)); }
    public List<Link> forLab(UUID lab) { return links.values().stream().filter(l -> l.lab().id().equals(lab)).toList(); }

    public boolean approve(MinecraftServer server, Endpoint mother, Endpoint lab, UUID actor) {
        if (!actor.equals(mother.owner()) && !actor.equals(lab.owner())) return false;
        var old = link(mother.id(), lab.id());
        if (old == null || !old.mother().equals(mother) || !old.lab().equals(lab))
            old = new Link(mother, lab, false, false, mother.team(), 0, 0);
        boolean payer = actor.equals(mother.owner());
        links.put(key(mother.id(), lab.id()), new Link(mother, lab, payer || old.supply(),
                actor.equals(lab.owner()) || old.receive(), payer ? Hk3ResearchTeams.scope(server, actor) : old.payerTeam(),
                old.priority(), old.version() + 1));
        setDirty();
        return true;
    }
    public boolean revoke(UUID mother, UUID lab, UUID actor) {
        var old = link(mother, lab);
        if (old == null || !actor.equals(old.mother().owner()) && !actor.equals(old.lab().owner())) return false;
        links.put(key(mother, lab), new Link(old.mother(), old.lab(), false, false,
                old.payerTeam(), old.priority(), old.version() + 1));
        setDirty();
        return true;
    }
    public boolean priority(UUID mother, UUID lab, UUID actor, int priority) {
        var old = link(mother, lab);
        if (old == null || !actor.equals(old.mother().owner())) return false;
        links.put(key(mother, lab), new Link(old.mother(), old.lab(), old.supply(), old.receive(),
                old.payerTeam(), priority, old.version() + 1));
        setDirty();
        return true;
    }
    public void departed(UUID payer) {
        boolean changed = false;
        for (var entry : links.entrySet()) {
            var old = entry.getValue();
            if (!old.mother().owner().equals(payer) || !old.supply()) continue;
            entry.setValue(new Link(old.mother(), old.lab(), false, old.receive(), old.payerTeam(),
                    old.priority(), old.version() + 1));
            changed = true;
        }
        if (changed) setDirty();
    }
    @Override public CompoundTag save(CompoundTag tag) {
        var rows = new ListTag();
        for (var link : links.values()) {
            var row = new CompoundTag();
            row.put("Mother", link.mother().save()); row.put("Lab", link.lab().save());
            row.putBoolean("Supply", link.supply()); row.putBoolean("Receive", link.receive());
            row.putUUID("PayerTeam", link.payerTeam()); row.putInt("Priority", link.priority());
            row.putLong("Version", link.version()); rows.add(row);
        }
        tag.put("Links", rows);
        return tag;
    }
    public static Hk3W13ResearchData load(CompoundTag tag) {
        var data = new Hk3W13ResearchData();
        for (var raw : tag.getList("Links", Tag.TAG_COMPOUND)) {
            var row = (CompoundTag) raw;
            var mother = Endpoint.load(row.getCompound("Mother"));
            var lab = Endpoint.load(row.getCompound("Lab"));
            data.links.put(key(mother.id(), lab.id()), new Link(mother, lab, row.getBoolean("Supply"),
                    row.getBoolean("Receive"), row.getUUID("PayerTeam"), row.getInt("Priority"), row.getLong("Version")));
        }
        return data;
    }
}
