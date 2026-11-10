package com.sirin.hk3gtl.common.communication;
import net.minecraft.nbt.*;
import net.minecraft.server.MinecraftServer;
import net.minecraft.world.level.saveddata.SavedData;
import java.util.*;

/** 【变更记录 #1】2026-09-30 23:58:50（修订121）：删除旧个人答复自动代表新队的生产路径；新增/修改：以团队UUID保存唯一回信、队长授权、个人阅读和三步补谈；真实来源回执可恢复；用途：团队外交、阅读与个人经历分账，不发研究或物品奖励。 */
/** 【变更记录 #2】2026-10-01 00:03:22（修订121）：删除损坏步数钳制为已完成的处理；新增/修改：结算态必须有真实答复人和时间，异常个人步数拒绝继续；用途：损坏数据不授予个人经历。 */
/** 【变更记录 #3】2026-10-01 00:44:06（修订123）：删除无；新增/修改：从真实三步完成记录读取本人跨队历史，未参加者不继承；用途：个人交流、团队决定及额外收藏分开，保留真实记录。 */
/** 【变更记录 #4】2026-10-01 00:59:10（修订124）：删除无；新增/修改：首信补谈增加批准的观察资料附件；旧三步进度保留，补附件后完成；账本加载失败拒绝空白重置；用途：按五方交流系统整链收口，真实权限和本人经历不混用。 */
public final class Hk3TeamContactData extends SavedData {
    public static final int PERSONAL_STEPS=4;
    private CompoundTag teams=new CompoundTag();
    public static Hk3TeamContactData get(MinecraftServer server){return com.sirin.hk3gtl.common.util.Hk3SavedDataGuard.get(server,"hk3gtl_team_contact_v5",Hk3TeamContactData::load,Hk3TeamContactData::new);}
    public static Hk3TeamContactData load(CompoundTag root){if(!root.contains("Teams",Tag.TAG_COMPOUND)||(root.contains("Version")&&root.getInt("Version")!=1))throw new IllegalArgumentException("团队首信账本异常，拒绝重置");var d=new Hk3TeamContactData();d.teams=root.getCompound("Teams").copy();return d;}
    @Override public CompoundTag save(CompoundTag root){root.putInt("Version",1);root.put("Teams",teams.copy());return root;}
    private CompoundTag row(UUID team){return teams.getCompound(team.toString()).copy();}
    private void put(UUID team,CompoundTag row){teams.put(team.toString(),row.copy());setDirty();}
    public boolean available(UUID team){var r=row(team);return r.hasUUID("Event")&&r.hasUUID("Owner")&&r.contains("DiscoveredAt",Tag.TAG_LONG)&&r.getLong("DiscoveredAt")>=0&&Set.of("PENDING","ACCEPTED","DECLINED").contains(r.getString("State"))&&(r.getString("State").equals("PENDING")||(r.hasUUID("Actor")&&r.contains("DecidedAt",Tag.TAG_LONG)&&r.getLong("DecidedAt")>=0));}
    public UUID event(UUID team){return available(team)?row(team).getUUID("Event"):null;}
    public String state(UUID team){return available(team)?row(team).getString("State"):"LOCKED";}
    public boolean settled(UUID team){return state(team).equals("ACCEPTED")||state(team).equals("DECLINED");}
    /** 存在损坏或未来状态时拒绝重置；发现来源仅由服务器实际首信资格调用。 */
    public boolean discover(UUID team,UUID owner,long tick){
        if(owner==null||tick<0||teams.contains(team.toString()))return false;
        var r=new CompoundTag();r.putUUID("Event",UUID.randomUUID());r.putUUID("Owner",owner);r.putLong("DiscoveredAt",tick);r.putString("State","PENDING");put(team,r);return true;
    }
    /** 队长变更清空旧授权；离队者授权失效，回队须再次授权。 */
    public void reconcile(UUID team,UUID owner,Set<UUID> members){
        if(!available(team)||owner==null)return;var r=row(team);var grants=r.getCompound("Delegates").copy();boolean changed=false;
        if(!r.getUUID("Owner").equals(owner)){r.putUUID("Owner",owner);grants=new CompoundTag();changed=true;}
        for(String id:List.copyOf(grants.getAllKeys())){try{if(members.contains(UUID.fromString(id)))continue;}catch(IllegalArgumentException ignored){}grants.remove(id);changed=true;}
        if(changed){r.put("Delegates",grants);put(team,r);}
    }
    public void revokeDeparted(UUID player){for(String id:List.copyOf(teams.getAllKeys())){var r=teams.getCompound(id).copy();var g=r.getCompound("Delegates").copy();if(g.contains(player.toString())){g.remove(player.toString());r.put("Delegates",g);teams.put(id,r);setDirty();}}}
    public boolean canDecide(UUID team,UUID actor,UUID owner,boolean member){
        if(!member||owner==null||!available(team))return false;var r=row(team);
        return actor.equals(owner)||(r.getUUID("Owner").equals(owner)&&r.getCompound("Delegates").getBoolean(actor.toString()));
    }
    public boolean delegate(UUID team,UUID actor,UUID owner,UUID target,boolean targetMember,boolean grant){
        if(!available(team)||owner==null||!actor.equals(owner)||!targetMember||target.equals(owner))return false;
        var r=row(team);if(!r.getUUID("Owner").equals(owner))return false;var g=r.getCompound("Delegates").copy();
        if(g.getBoolean(target.toString())==grant)return false;if(grant)g.putBoolean(target.toString(),true);else g.remove(target.toString());r.put("Delegates",g);put(team,r);return true;
    }
    public void read(UUID team,UUID actor){if(!available(team))return;var r=row(team);var read=r.getCompound("Readers").copy();if(read.getBoolean(actor.toString()))return;read.putBoolean(actor.toString(),true);r.put("Readers",read);put(team,r);}
    public boolean hasRead(UUID team,UUID actor){return available(team)&&row(team).getCompound("Readers").getBoolean(actor.toString());}
    /** 提交时再核成员、队长/授权、事件身份与当前状态，不信任客户端按钮。 */
    public boolean decide(UUID team,UUID actor,UUID owner,boolean member,UUID expectedEvent,boolean accepted,long tick){
        if(!canDecide(team,actor,owner,member)||!hasRead(team,actor)||!state(team).equals("PENDING")||!Objects.equals(event(team),expectedEvent)||tick<0)return false;
        var r=row(team);r.putString("State",accepted?"ACCEPTED":"DECLINED");r.putUUID("Actor",actor);r.putLong("DecidedAt",tick);put(team,r);return true;
    }
    public CompoundTag receipt(UUID team){
        if(!settled(team))return new CompoundTag();var r=row(team);if(!r.hasUUID("Actor")||!r.contains("DecidedAt",Tag.TAG_LONG))return new CompoundTag();
        var proof=com.sirin.hk3gtl.common.research.Hk3CommunicationResearchProof.receipt(r.getUUID("Actor"),team,state(team).equals("ACCEPTED"),r.getLong("DecidedAt"));
        proof.putUUID("Batch",r.getUUID("Event"));proof.putString("Authority","team_owner_or_explicit_delegate");return proof;
    }
    /** 补谈四步单调推进，第四步补齐观察资料附件；旧三步保留为已确认前三步；普通历史阅读从不调用。完成仍不改团队答复或任何奖励。 */
    public int personalStep(UUID team,UUID actor){if(!settled(team))return 0;var p=row(team).getCompound("Personal");String id=actor.toString();if(!p.contains(id))return 0;if(!p.contains(id,Tag.TAG_INT)||p.getInt(id)<0||p.getInt(id)>PERSONAL_STEPS)return -1;return p.getInt(id);}
    public boolean experienced(UUID actor){
        for(String key:teams.getAllKeys())try{UUID team=UUID.fromString(key);if(personalStep(team,actor)==PERSONAL_STEPS)return true;}catch(IllegalArgumentException ignored){}
        return false;
    }
    public boolean advancePersonal(UUID team,UUID actor,UUID expectedEvent,int expectedStep,boolean member){
        if(!member||!settled(team)||!Objects.equals(event(team),expectedEvent)||expectedStep<0||expectedStep>=PERSONAL_STEPS||personalStep(team,actor)!=expectedStep)return false;
        var r=row(team);var p=r.getCompound("Personal").copy();p.putInt(actor.toString(),expectedStep+1);r.put("Personal",p);put(team,r);return true;
    }
}
