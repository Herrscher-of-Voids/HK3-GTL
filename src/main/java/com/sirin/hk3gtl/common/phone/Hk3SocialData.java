package com.sirin.hk3gtl.common.phone;

import net.minecraft.nbt.*;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.level.saveddata.SavedData;
import java.util.*;

/** 【变更记录 #1】2026-09-30 19:56:03（修订116）：删除无；新增按玩家保存会话、阶段和朋友圈；修改无；用途：服务端主线程账本，每角色保留最近200条、朋友圈120条，AI和Key不写入。 */
/** 【变更记录 #2】2026-10-01 17:04:49（修订136）：删除聊天数据损坏时的默认空根读取；新增防覆盖加载及已知字段完整性核验；修改合法内容深拷贝保留，未知扩展字段不静默删除；用途：保护私聊、朋友圈、阶段及轮换记录，不保存AI或Key。 */
public final class Hk3SocialData extends SavedData {
    private CompoundTag users=new CompoundTag();
    public static Hk3SocialData get(ServerPlayer p){return com.sirin.hk3gtl.common.util.Hk3SavedDataGuard.get(p.server,"hk3gtl_social",Hk3SocialData::load,Hk3SocialData::new);}
    public static Hk3SocialData load(CompoundTag tag){
        com.sirin.hk3gtl.common.util.Hk3LedgerValidation.type(tag,"Users",Tag.TAG_COMPOUND);
        var root=tag.getCompound("Users");var identities=new HashSet<UUID>();
        for(String key:root.getAllKeys()){
            var id=com.sirin.hk3gtl.common.util.Hk3LedgerValidation.uuid(key);
            com.sirin.hk3gtl.common.util.Hk3LedgerValidation.require(identities.add(id),"重复微讯息用户");
            com.sirin.hk3gtl.common.util.Hk3LedgerValidation.type(root,key,Tag.TAG_COMPOUND);var u=root.getCompound(key);
            com.sirin.hk3gtl.common.util.Hk3LedgerValidation.optionalType(u,"Stage",Tag.TAG_INT);
            com.sirin.hk3gtl.common.util.Hk3LedgerValidation.require(u.getInt("Stage")>=0&&u.getInt("Stage")<=4,"联系人阶段");
            com.sirin.hk3gtl.common.util.Hk3LedgerValidation.optionalType(u,"FeedDay",Tag.TAG_LONG);
            for(var contact:Hk3SocialCatalog.all()){
                String c=contact.id();String count="Count_"+c,rotation="Rotation_"+c;
                com.sirin.hk3gtl.common.util.Hk3LedgerValidation.optionalType(u,count,Tag.TAG_INT);
                com.sirin.hk3gtl.common.util.Hk3LedgerValidation.require(u.getInt(count)>=0,"聊天计数");
                if(u.contains(rotation)){
                    com.sirin.hk3gtl.common.util.Hk3LedgerValidation.type(u,rotation,Tag.TAG_COMPOUND);
                    var values=u.getCompound(rotation);for(String topic:values.getAllKeys()){
                        com.sirin.hk3gtl.common.util.Hk3LedgerValidation.type(values,topic,Tag.TAG_INT);
                        com.sirin.hk3gtl.common.util.Hk3LedgerValidation.require(values.getInt(topic)>=0,"话题轮换");
                    }
                }
                if(u.contains(c))validateRows(u,c,200,false);
            }
            if(u.contains("Feed"))validateRows(u,"Feed",120,true);
        }
        var d=new Hk3SocialData();d.users=root.copy();return d;
    }
    private static void validateRows(CompoundTag user,String key,int max,boolean feed){
        var rows=com.sirin.hk3gtl.common.util.Hk3LedgerValidation.list(user,key,Tag.TAG_COMPOUND);
        com.sirin.hk3gtl.common.util.Hk3LedgerValidation.require(rows.size()<=max,key);var ids=new HashSet<String>();
        for(Tag raw:rows){var n=(CompoundTag)raw;
            for(String field:feed?List.of("Id","Contact","Body"):List.of("Who","Body","Source"))com.sirin.hk3gtl.common.util.Hk3LedgerValidation.type(n,field,Tag.TAG_STRING);
            com.sirin.hk3gtl.common.util.Hk3LedgerValidation.type(n,feed?"Day":"Time",Tag.TAG_LONG);
            if(feed){
                com.sirin.hk3gtl.common.util.Hk3LedgerValidation.require(!n.getString("Id").isBlank()&&ids.add(n.getString("Id")),"朋友圈身份");
                com.sirin.hk3gtl.common.util.Hk3LedgerValidation.flag(n,"Liked",false);
            }
        }
    }
    @Override public CompoundTag save(CompoundTag tag){tag.put("Users",users.copy());return tag;}
    private CompoundTag user(UUID id){String k=id.toString();if(!users.contains(k))users.put(k,new CompoundTag());return users.getCompound(k);}
    public int stage(UUID id){return Math.max(0,Math.min(4,user(id).getInt("Stage")));}
    /** 仅由真实审查结算端调用；不提供客户端写入或预览授予接口。 */
    public void advance(UUID id,int stage){if(stage>stage(id)&&stage<=4){user(id).putInt("Stage",stage);setDirty();}}
    public ListTag history(UUID id,String contact){return user(id).getList(contact,Tag.TAG_COMPOUND).copy();}
    public int count(UUID id,String contact){return user(id).getInt("Count_"+contact);}
    public int nextReply(UUID id,String contact,String topic){
        var u=user(id);String key="Rotation_"+contact;var rotation=u.getCompound(key);int index=rotation.getInt(topic)&0x7fffffff;
        rotation.putInt(topic,(index+1)&0x7fffffff);u.put(key,rotation);setDirty();return index;
    }
    public void append(UUID id,String contact,String who,String body,String source,long time){
        var u=user(id);var rows=u.getList(contact,Tag.TAG_COMPOUND);var n=new CompoundTag();
        n.putString("Who",who);n.putString("Body",body);n.putString("Source",source);n.putLong("Time",time);rows.add(n);
        while(rows.size()>200)rows.remove(0);u.put(contact,rows);u.putInt("Count_"+contact,(u.getInt("Count_"+contact)+1)&0x7fffffff);setDirty();
    }
    /** 使用总游戏tick计算发布间隔，时间指令不回拨；离线天数不批量补发。 */
    public boolean publish(UUID id,int stage,long ticks){
        var u=user(id);long day=Math.floorDiv(ticks,24000);
        if(u.contains("FeedDay")&&day<=u.getLong("FeedDay"))return false;
        var pool=Hk3SocialCatalog.all().stream().filter(c->c.available(stage)).toList();if(pool.isEmpty())return false;
        var feed=u.getList("Feed",Tag.TAG_COMPOUND);
        for(int i=0;i<Math.min(2,pool.size());i++){
            var c=pool.get(Math.floorMod(day*2+i+id.hashCode(),pool.size()));var n=new CompoundTag();
            n.putString("Id",day+"_"+c.id());n.putString("Contact",c.id());n.putString("Body",c.moments().get(Math.floorMod(day,c.moments().size())));n.putLong("Day",day+1);feed.add(n);
        }
        while(feed.size()>120)feed.remove(0);u.put("Feed",feed);u.putLong("FeedDay",day);setDirty();return true;
    }
    public ListTag feed(UUID id){return user(id).getList("Feed",Tag.TAG_COMPOUND).copy();}
    public void like(UUID id,String post){var u=user(id);var rows=u.getList("Feed",Tag.TAG_COMPOUND);for(Tag raw:rows){var n=(CompoundTag)raw;if(n.getString("Id").equals(post)){n.putBoolean("Liked",!n.getBoolean("Liked"));setDirty();return;}}}
}
