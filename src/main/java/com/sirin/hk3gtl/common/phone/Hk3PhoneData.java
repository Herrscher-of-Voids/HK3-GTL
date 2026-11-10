package com.sirin.hk3gtl.common.phone;

/** 【变更记录 #6】2026-10-01 00:20:13（修订122）：删除无；新增/修改：重谈更新原主题待处理，阅读不清业务状态；离队旧通知仅留历史；用途：服务端主题状态与阅读权限一致。 */

/** 【变更记录 #1】2026-09-29 18:57:18（内测5修订95）：新增个人持久通知账本；限制每人128条，重复事件不重复入账。 */
/** 【变更记录 #2】2026-09-29 19:19:27（内测5修订96）：删除免费手机资格；新增已安装UUID持久集合；安装物品后才可打开手机，重进存档保持资格。 */

import java.util.*;
import net.minecraft.nbt.*;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.level.saveddata.SavedData;
import static com.sirin.hk3gtl.common.util.Hk3LedgerValidation.*;

/**
 * 【变更记录 #3】2026-09-30 16:16:37（内测5修订110）
 * 删除：被新版通知读取流程替代的旧分支，历史备注保留。
 * 新增／修改：取消128条自动删除；永久消息以接收人＋事件去重；八条分页、全部/未读/待处理、独立阅读与处理状态，兼容旧账本。
 * 用途：通知与业务结果分离，服务端授权和个人持久化；不改结构、贴图和贸易。
 */
/**
 * 【变更记录 #4】2026-09-30 18:44:46（内测5修订113）
 * 删除：无；新增：旧消耗式安装迁移待补发集合。
 * 修改：仅旧格式已安装玩家可补发一次；用途：实体手机改为充电物品后不丢失原安装权益。
 */
/**
 * 【变更记录 #5】2026-09-30 19:08:08（内测5修订114）
 * 删除：无；新增仅本人标题/正文搜索；修改筛选沿用未读和待处理事实。
 * 用途：手机应用集成，保留既有电量和阅读权限；交易只展示不结算。
 */
/** 【变更记录 #7】2026-10-01 00:59:10（修订124）：删除无；新增/修改：离队首信与五方主题统一降为历史，回队可恢复本队待处理；根数据损坏不清空信箱；用途：按五方交流系统整链收口，真实权限和本人经历不混用。 */
/** 【变更记录 #8】2026-10-01 17:04:49（修订136）：删除损坏安装记录/通知条目静默跳过；新增类型、UUID、重复通知及迁移集合校验；修改旧首信缺省字段仍按原规则迁移；用途：读取失败保留原文件，避免丢信或重复补发实体手机。 */
/** 【变更记录 #9】2026-10-01 22:50:14（第9次备注 · 内测5修订155）：删除玩家展示中的旧电压及开发说明；新增现行正文投影或对应回归；修改仅限呈现与检索，不改变进度、回执、触发条件或权限；用途：统一发布版玩家文案，历史备注保留。 */
public final class Hk3PhoneData extends SavedData {
    private static final String NAME="hk3gtl_phone_v5";
    private final Map<UUID,LinkedHashMap<String,Entry>> users=new HashMap<>();
    private final Set<UUID> installed=new HashSet<>();
    private final Set<UUID> physicalMigration=new HashSet<>();
    public boolean needsPhysical(UUID user){return physicalMigration.contains(user);}
    public void physicalDelivered(UUID user){if(physicalMigration.remove(user))setDirty();}
    public record Entry(String id,String title,String body,long time,boolean read,String kind,String target,boolean pending) {
        public int priority(){return pending?2:kind.equals("chatter")?0:1;}
    }
    public static Hk3PhoneData get(ServerPlayer player){return get(player.server);}
    public static Hk3PhoneData get(MinecraftServer server){
        return com.sirin.hk3gtl.common.util.Hk3SavedDataGuard.get(server,NAME,Hk3PhoneData::load,Hk3PhoneData::new);
    }
    public boolean add(UUID user,String id,String title,String body,long time){
        return add(user,id,title,body,time,"notice","",false);
    }
    public boolean add(UUID user,String id,String title,String body,long time,String kind,String target,boolean pending){
        Objects.requireNonNull(user);
        if(!valid(id,title,body,kind,target))throw new IllegalArgumentException("无效通知内容");
        var entries=users.computeIfAbsent(user,k->new LinkedHashMap<>());
        if(entries.containsKey(id))return false;
        entries.put(id,new Entry(id,title,body,time,false,kind,target,pending));
        setDirty();return true;
    }
    private static boolean valid(String id,String title,String body,String kind,String target){
        return id!=null&&id.matches("[A-Za-z0-9_.-]{1,160}")&&title!=null&&title.length()<=256
                &&body!=null&&body.length()<=16384&&kind!=null&&kind.length()<=24&&target!=null&&target.length()<=160;
    }
    public boolean installed(UUID user){return installed.contains(user);}
    public boolean install(UUID user){if(!installed.add(user))return false;setDirty();return true;}
    public Entry entry(UUID user,String id){var entries=users.get(user);return entries==null?null:entries.get(id);}
    public void read(UUID user,String id){
        var old=entry(user,id);if(old==null||old.read())return;
        users.get(user).put(id,new Entry(old.id(),old.title(),old.body(),old.time(),true,old.kind(),old.target(),old.pending()));setDirty();
    }
    /** 待处理仅由真实业务提交结果清除，阅读和通知淡出不清除。 */
    public void resolve(UUID user,String id){
        var old=entry(user,id);if(old==null||!old.pending())return;
        users.get(user).put(id,new Entry(old.id(),old.title(),old.body(),old.time(),old.read(),old.kind(),old.target(),false));setDirty();
    }
    /** 只有业务服务调用；重谈可恢复同一主题的待处理状态，不伪造未读或新增消息。 */
    public void pending(UUID user,String id,boolean pending){
        var old=entry(user,id);if(old==null||old.pending()==pending)return;
        users.get(user).put(id,new Entry(old.id(),old.title(),old.body(),old.time(),old.read(),old.kind(),old.target(),pending));setDirty();
    }
    public void resolveForeignDiplomacy(UUID user,UUID team){
        var entries=users.get(user);if(entries==null)return;
        for(var e:List.copyOf(entries.values())){
            boolean foreign=e.kind().equals("diplomacy")&&!e.target().startsWith(team+"/");
            if(e.kind().equals("letter")&&e.id().startsWith("contact_"))foreign=!e.id().equals("contact_"+team)&&!e.id().equals("contact_reply_"+team);
            if(foreign)pending(user,e.id(),false);
        }
    }
    private boolean matches(Entry e,String filter){return switch(filter){case "unread" -> !e.read();case "pending" -> e.pending();default -> true;};}
    public List<Entry> page(UUID user,int page){return page(user,page,"all");}
    public List<Entry> page(UUID user,int page,String filter){
        var values=new ArrayList<>(users.getOrDefault(user,new LinkedHashMap<>()).values());Collections.reverse(values);
        return values.stream().filter(e->matches(e,filter)).skip((long)Math.max(0,page)*8).limit(8).toList();
    }
    public List<Entry> search(UUID user,String filter,String query){return search(user,filter,query,java.util.function.Function.identity());}
    public List<Entry> search(UUID user,String filter,String query,java.util.function.Function<Entry,Entry> presentation){
        String q=query.toLowerCase(java.util.Locale.ROOT);var values=new ArrayList<>(users.getOrDefault(user,new LinkedHashMap<>()).values());Collections.reverse(values);
        return values.stream().map(presentation).filter(e->matches(e,filter)&&(e.title().toLowerCase(java.util.Locale.ROOT).contains(q)||e.body().toLowerCase(java.util.Locale.ROOT).contains(q))).toList();
    }
    public int count(UUID user){return count(user,"all");}
    public int count(UUID user,String filter){return (int)users.getOrDefault(user,new LinkedHashMap<>()).values().stream().filter(e->matches(e,filter)).count();}
    public int unread(UUID user){return count(user,"unread");}
    public static Hk3PhoneData load(CompoundTag tag){
        if(!tag.contains("Users",Tag.TAG_COMPOUND))throw new IllegalArgumentException("收件箱根数据异常，拒绝重置");
        var data=new Hk3PhoneData();var root=tag.getCompound("Users");
        if(tag.contains("Installed"))for(Tag raw:list(tag,"Installed",Tag.TAG_INT_ARRAY))require(data.installed.add(NbtUtils.loadUUID(raw)),"重复安装记录");
        if(!tag.contains("PhysicalMigration"))data.physicalMigration.addAll(data.installed);
        else for(Tag raw:list(tag,"PhysicalMigration",Tag.TAG_INT_ARRAY))require(data.physicalMigration.add(NbtUtils.loadUUID(raw)),"重复迁移记录");
        require(data.installed.containsAll(data.physicalMigration),"待补发者缺安装记录");
        for(String key:root.getAllKeys()){
            UUID user=uuid(key);var entries=new LinkedHashMap<String,Entry>();
            require(!data.users.containsKey(user),"重复通知用户");
            for(Tag raw:list(root,key,Tag.TAG_COMPOUND)){
                var n=(CompoundTag)raw;String id=n.getString("Id"),kind=n.getString("Kind"),target=n.getString("Target");
                for(String field:List.of("Id","Title","Body"))type(n,field,Tag.TAG_STRING);
                optionalType(n,"Kind",Tag.TAG_STRING);optionalType(n,"Target",Tag.TAG_STRING);optionalType(n,"Time",Tag.TAG_LONG);
                flag(n,"Read",false);flag(n,"Pending",false);
                boolean pending=n.getBoolean("Pending");
                if(kind.isEmpty()){
                    kind="notice";
                    if(id.equals("first_contact_letter")){kind="letter";target="0";pending=true;}
                    else if(id.equals("letter_reply_accepted")){kind="letter";target="4";}
                    else if(id.equals("letter_reply_declined")){kind="letter";target="5";}
                }
                require(valid(id,n.getString("Title"),n.getString("Body"),kind,target)&&!entries.containsKey(id),"通知条目");
                entries.put(id,new Entry(id,n.getString("Title"),n.getString("Body"),n.getLong("Time"),n.getBoolean("Read"),kind,target,pending));
            }
            if(entries.containsKey("letter_reply_accepted")||entries.containsKey("letter_reply_declined")){
                var e=entries.get("first_contact_letter");if(e!=null)entries.put(e.id(),new Entry(e.id(),e.title(),e.body(),e.time(),e.read(),e.kind(),e.target(),false));
            }
            data.users.put(user,entries);
        }
        return data;
    }
    @Override public CompoundTag save(CompoundTag tag){
        var migration=new ListTag();physicalMigration.forEach(id->migration.add(NbtUtils.createUUID(id)));tag.put("PhysicalMigration",migration);
        var root=new CompoundTag();var phones=new ListTag();installed.forEach(id->phones.add(NbtUtils.createUUID(id)));tag.put("Installed",phones);
        users.forEach((user,entries)->{var list=new ListTag();entries.values().forEach(e->{var n=new CompoundTag();
            n.putString("Id",e.id());n.putString("Title",e.title());n.putString("Body",e.body());n.putLong("Time",e.time());
            n.putBoolean("Read",e.read());n.putString("Kind",e.kind());n.putString("Target",e.target());n.putBoolean("Pending",e.pending());list.add(n);
        });root.put(user.toString(),list);});tag.put("Users",root);return tag;
    }
}
