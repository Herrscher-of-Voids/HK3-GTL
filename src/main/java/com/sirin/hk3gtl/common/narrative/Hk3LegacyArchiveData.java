package com.sirin.hk3gtl.common.narrative;

import net.minecraft.nbt.*;
import net.minecraft.server.MinecraftServer;
import net.minecraft.world.level.saveddata.SavedData;
import java.util.*;








public final class Hk3LegacyArchiveData extends SavedData {
    private CompoundTag players=new CompoundTag();
    public static Hk3LegacyArchiveData get(MinecraftServer server) {
        return com.sirin.hk3gtl.common.util.Hk3SavedDataGuard.get(server,"hk3gtl_legacy_archive_v5",
            Hk3LegacyArchiveData::load,Hk3LegacyArchiveData::new);
    }
    public static Hk3LegacyArchiveData load(CompoundTag root) {
        if(!root.contains("Version",Tag.TAG_INT)||root.getInt("Version")!=2||!root.contains("Players",Tag.TAG_COMPOUND))
            throw new IllegalArgumentException("正式档案回执格式异常，拒绝重置");
        var data=new Hk3LegacyArchiveData();data.players=root.getCompound("Players").copy();
        for(String actorKey:data.players.getAllKeys()) {
            UUID actor=UUID.fromString(actorKey);
            if(!data.players.contains(actorKey,Tag.TAG_COMPOUND))throw new IllegalArgumentException("本人档案历史类型错误");
            var events=data.players.getCompound(actorKey);
            for(String event:events.getAllKeys()) {
                if(!events.contains(event,Tag.TAG_COMPOUND)||!valid(events.getCompound(event),actor,event))
                    throw new IllegalArgumentException("正式档案完成回执损坏："+event);
            }
        }
        return data;
    }
    private static boolean valid(CompoundTag n,UUID actor,String event) {
        var rule=Hk3LegacyArchiveMigration.all().get(event);
        return rule!=null&&n.getString("Kind").equals("RESEARCH")
            &&com.sirin.hk3gtl.common.research.Hk3ResearchPlans.get(n.getString("Source"))!=null
            &&n.contains("MigrationVersion",Tag.TAG_INT)&&n.getInt("MigrationVersion")==2
            &&n.hasUUID("Actor")&&n.getUUID("Actor").equals(actor)&&n.hasUUID("Scope")&&n.hasUUID("ReadToken")
            &&n.getString("Event").equals(event)&&n.getString("RuleHash").matches("[0-9a-f]{64}")
            &&(!n.getString("RuleHash").equals(rule.fingerprint())
                ||(rule.kind()==Hk3LegacyArchiveMigration.SourceKind.RESEARCH&&n.getString("Source").equals(rule.source())))
            &&researchProof(n)
            &&n.contains("CompletedAt",Tag.TAG_LONG)&&n.getLong("CompletedAt")>=0
            &&n.contains("BodyLength",Tag.TAG_INT)&&n.getInt("BodyLength")>0
            &&n.contains("ReadLength",Tag.TAG_INT)&&n.getInt("ReadLength")==n.getInt("BodyLength")
            &&(!n.getString("RuleHash").equals(rule.fingerprint())||n.getInt("BodyLength")==bodyLength(rule))
            &&n.contains("Pieces",Tag.TAG_INT)&&n.getInt("Pieces")>0&&n.getInt("Pieces")<=n.getInt("ReadLength");
    }
    private static boolean researchProof(CompoundTag n) {
        if(!n.contains("ResearchProof",Tag.TAG_COMPOUND))return false;
        var proof=n.getCompound("ResearchProof");
        if(!proof.hasUUID("Scope")||!proof.getUUID("Scope").equals(n.getUUID("Scope"))
                ||!proof.getString("Research").equals(n.getString("Source"))||!proof.contains("Completed",Tag.TAG_LIST))return false;
        var raw=(ListTag)proof.get("Completed");var actual=new HashSet<String>();
        for(Tag entry:raw)if(!(entry instanceof StringTag)||!actual.add(entry.getAsString()))return false;
        var expected=new HashSet<String>();
        return ancestors(n.getString("Source"),expected)&&actual.equals(expected);
    }
    private static boolean ancestors(String id,Set<String> result) {
        var topic=com.sirin.hk3gtl.common.research.Hk3ResearchCatalog.bundled().get(id);
        if(topic==null)return false;
        if(!result.add(id))return true;
        for(String parent:topic.prerequisites())if(!ancestors(parent,result))return false;
        return true;
    }
    private static int bodyLength(Hk3LegacyArchiveMigration.Rule rule) {
        return com.sirin.hk3gtl.common.easter.Hk3EggReadingCursor.normalize(rule.body()).length();
    }
    @Override public CompoundTag save(CompoundTag root) {
        root.putInt("Version",2);root.put("Players",players.copy());return root;
    }
    public CompoundTag receipt(UUID actor,Hk3LegacyArchiveMigration.Rule rule) {
        if(rule==null||!rule.equals(Hk3LegacyArchiveMigration.all().get(rule.eventId())))return new CompoundTag();
        var n=players.getCompound(actor.toString()).getCompound(rule.eventId());
        return valid(n,actor,rule.eventId())&&rule.kind()==Hk3LegacyArchiveMigration.SourceKind.RESEARCH
            &&n.getString("Source").equals(rule.source())&&n.getString("RuleHash").equals(rule.fingerprint())?n.copy():new CompoundTag();
    }
    public boolean experienced(UUID actor,Hk3LegacyArchiveMigration.Rule rule) {return !receipt(actor,rule).isEmpty();}

    /** 只由已核验全文的服务提交；再核来源快照、当前规则及准确原队，重复结算不写入。 */
    public boolean record(UUID actor,UUID scope,Hk3LegacyArchiveMigration.Rule rule,UUID token,
                         long tick,int pieces,CompoundTag verifiedSource) {
        if(rule==null||actor==null||scope==null||token==null||tick<0||pieces<=0||verifiedSource==null
                ||!rule.equals(Hk3LegacyArchiveMigration.all().get(rule.eventId()))
                ||rule.kind()!=Hk3LegacyArchiveMigration.SourceKind.RESEARCH||experienced(actor,rule))return false;
        var n=verifiedSource.copy();
        n.putUUID("ReadToken",token);n.putLong("CompletedAt",tick);n.putInt("Pieces",pieces);
        n.putInt("BodyLength",bodyLength(rule));n.putInt("ReadLength",bodyLength(rule));
        if(!valid(n,actor,rule.eventId())||!n.getUUID("Scope").equals(scope)||!n.getString("RuleHash").equals(rule.fingerprint()))return false;
        var events=players.getCompound(actor.toString()).copy();events.put(rule.eventId(),n);
        players.put(actor.toString(),events);setDirty();return true;
    }
}
