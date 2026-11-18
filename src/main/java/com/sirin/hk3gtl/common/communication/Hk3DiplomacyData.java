package com.sirin.hk3gtl.common.communication;

 

 
import net.minecraft.nbt.*;
import net.minecraft.server.MinecraftServer;
import net.minecraft.world.level.saveddata.SavedData;
import java.util.*;

 
 
 
 
 
public final class Hk3DiplomacyData extends SavedData {
    public record Topic(String id,String name,String first,String yes,String no,String agreed,String refused,String submit,String feedback,String retry,String resumed){}
    public static final List<Topic> TOPICS=List.of(new Topic("schicksal","天命","A05","N01","N02","A05","N04","N03","A07","N05","N06"),new Topic("anti_entropy","逆熵","A08","N07","N08","N09","N10","N11","N12","N23","N24"),new Topic("world_serpent","世界蛇","A09","N13","N14","N15","N16","N17","N18","N25","N26"),new Topic("elysian_realm","往世乐土","ER01","ER02","ER03","ER04","ER05","","ER04","ER06","ER04"),new Topic("st_freya","圣芙蕾雅学园","SF01","SF02","SF03","SF04","SF05","","SF04","SF06","SF04"));
    private CompoundTag teams=new CompoundTag();
    public static Topic topic(String id){return TOPICS.stream().filter(t->t.id.equals(id)).findFirst().orElse(null);}
    public static Hk3DiplomacyData get(MinecraftServer s){return com.sirin.hk3gtl.common.util.Hk3SavedDataGuard.get(s,"hk3gtl_diplomacy_v5",Hk3DiplomacyData::load,Hk3DiplomacyData::new);}
    public static Hk3DiplomacyData load(CompoundTag n){if(!n.contains("Teams",Tag.TAG_COMPOUND)||(n.contains("Version")&&n.getInt("Version")!=1))throw new IllegalArgumentException("正式交流账本异常，拒绝重置");var d=new Hk3DiplomacyData();d.teams=n.getCompound("Teams").copy();return d;}
    @Override public CompoundTag save(CompoundTag n){n.putInt("Version",1);n.put("Teams",teams.copy());return n;}
    private CompoundTag row(UUID team){return teams.getCompound(team.toString()).copy();}
    private boolean writable(UUID team){return (!teams.contains(team.toString())||teams.contains(team.toString(),Tag.TAG_COMPOUND))&&(!row(team).contains("Documents")||row(team).contains("Documents",Tag.TAG_COMPOUND));}
    private void put(UUID team,CompoundTag r){teams.put(team.toString(),r.copy());setDirty();}
    private void document(CompoundTag r,String doc){var docs=r.getCompound("Documents").copy();docs.putBoolean(doc,true);r.put("Documents",docs);}
    public List<String> documents(UUID team){return row(team).getCompound("Documents").getAllKeys().stream().filter(k->row(team).getCompound("Documents").getBoolean(k)).sorted().toList();}
    public CompoundTag published(UUID team){var r=row(team).getCompound("Published").copy();return Hk3CommunicationEvidence.validEnvelope("public",r)?r:new CompoundTag();}
    public long publishedTick(UUID team){return row(team).getLong("PublishedTick");}
    public boolean publish(UUID team,UUID actor,boolean authorized,CompoundTag proof,long tick){
        if(!writable(team)||!authorized||!Hk3CommunicationEvidence.validEnvelope("public",proof)||tick<0||row(team).contains("Published"))return false;
        var r=row(team);r.put("Published",proof.copy());r.putUUID("PublishedBy",actor);r.putLong("PublishedTick",tick);document(r,"N19");put(team,r);return true;
    }
    public String state(UUID team,String id){var n=row(team).getCompound(id);return n.getString("State").isBlank()?"LOCKED":n.getString("State");}
    public int version(UUID team,String id){return row(team).getCompound(id).getInt("Version");}
    public void offer(UUID team,String id,boolean initiallyRefused){
        var t=topic(id);if(t==null||!writable(team)||row(team).contains(id))return;var r=row(team);var n=new CompoundTag();n.putString("State",initiallyRefused?"DECLINED":"OFFERED");n.putInt("Version",1);r.put(id,n);document(r,initiallyRefused?"A06":t.first);put(team,r);
    }
    /** 同一版本只允许一次有效迁移，重谈保留旧正文，不发放任何技术或材料。 */
    public boolean apply(UUID team,String id,String action,UUID actor,boolean authorized,int expected,CompoundTag evidence){
        var t=topic(id);if(t==null||!writable(team)||!authorized||version(team,id)!=expected||expected<1||expected==Integer.MAX_VALUE)return false;
        String state=state(team,id),next;String request,response;
        switch(action){
            case "accept"->{if(!state.equals("OFFERED"))return false;next=t.submit.isEmpty()?"COMPLETED":"ACCEPTED";request=t.yes;response=t.agreed;}
            case "decline"->{if(!state.equals("OFFERED"))return false;next="DECLINED";request=t.no;response=t.refused;}
            case "retry"->{if(!state.equals("DECLINED"))return false;next=id.equals("schicksal")?"OFFERED":t.submit.isEmpty()?"COMPLETED":"ACCEPTED";request=t.retry;response=t.resumed;}
            case "submit"->{if(t.submit.isEmpty()||!state.equals("ACCEPTED")||!Hk3CommunicationEvidence.validEnvelope(id,evidence))return false;next="COMPLETED";request=t.submit;response=t.feedback;}
            default->{return false;}
        }
        var r=row(team);var n=r.getCompound(id).copy();n.putString("State",next);n.putInt("Version",expected+1);n.putUUID("Actor",actor);if(action.equals("submit"))n.put("Submitted",evidence.copy());r.put(id,n);document(r,request);document(r,response);if(id.equals("schicksal")&&action.equals("retry"))document(r,t.first);put(team,r);return true;
    }
    public boolean pendingDocument(UUID team,String document){
        for(var t:TOPICS){String state=state(team,t.id);if(state.equals("OFFERED")&&t.first.equals(document))return true;if(state.equals("ACCEPTED")&&(t.agreed.equals(document)||t.resumed.equals(document)))return true;}return false;
    }

    /** 只从本队确已发生的当前分支整理补谈正文；不要求互斥分支全做，也不凭旧版本号补造经历。 */
    public List<String> personalPath(UUID team,String id){
        var t=topic(id);if(t==null)return List.of();String state=state(team,id);
        var record=row(team).getCompound(id);
        if(id.equals("schicksal")&&state.equals("DECLINED")&&version(team,id)==1&&documents(team).contains("A06"))return List.of("N20","A06");
        if(!Set.of("COMPLETED","DECLINED").contains(state)||version(team,id)<2||!record.hasUUID("Actor"))return List.of();
        if(state.equals("COMPLETED")&&!t.submit.isEmpty()&&!Hk3CommunicationEvidence.validEnvelope(id,submitted(team,id)))return List.of();
        var known=new HashSet<>(documents(team));var route=new ArrayList<String>();route.add("N20");
        if(!known.contains(t.first))return List.of();route.add(t.first);
        if(state.equals("DECLINED")){route.add(t.no);route.add(t.refused);}
        else{
            if(known.contains(t.retry)){route.add(t.retry);route.add(t.resumed);}
            if(known.contains(t.yes)){route.add(t.yes);route.add(t.agreed);}
            else if(!known.contains(t.retry))return List.of();
            if(!t.submit.isEmpty()){route.add(t.submit);route.add(t.feedback);}
        }
        if(route.stream().anyMatch(s->!s.equals("N20")&&!known.contains(s)))return List.of();
        var result=new ArrayList<String>();for(String doc:route)if(result.isEmpty()||!result.get(result.size()-1).equals(doc))result.add(doc);
        return List.copyOf(result);
    }
    public CompoundTag submitted(UUID team,String id){return row(team).getCompound(id).getCompound("Submitted").copy();}
}
