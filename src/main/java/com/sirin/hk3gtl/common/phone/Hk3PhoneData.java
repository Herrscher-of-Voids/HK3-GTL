package com.sirin.hk3gtl.common.phone;



import java.util.*;
import net.minecraft.nbt.*;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.level.saveddata.SavedData;
import static com.sirin.hk3gtl.common.util.Hk3LedgerValidation.*;

public final class Hk3PhoneData extends SavedData {
    private static final String NAME="hk3gtl_phone_v5";
    private final Map<UUID,LinkedHashMap<String,Entry>> users=new HashMap<>();
    private final Set<UUID> installed=new HashSet<>();
    private final Set<UUID> physicalMigration=new HashSet<>();
    public boolean needsPhysical(UUID user){return physicalMigration.contains(user);}
    public void physicalDelivered(UUID user){if(physicalMigration.remove(user))setDirty();}
    public record Entry(String id,String title,String body,long time,boolean read,String kind,String target,boolean pending) {
        public int priority(){return pending?2:kind.equals("chatter")?0:1;}
        private Entry asRead(){return new Entry(id,title,body,time,true,kind,target,pending);}
    }
    public static Hk3PhoneData get(ServerPlayer player){return get(player.server);}
    public static Hk3PhoneData get(MinecraftServer server){
        return com.sirin.hk3gtl.common.util.Hk3SavedDataGuard.get(server,NAME,Hk3PhoneData::load,Hk3PhoneData::new);
    }
    public boolean add(UUID user,String id,String title,String body,long time){
        return add(user,id,title,body,time,"notice","",false);
    }
    public boolean add(UUID user,String id,String title,String body,long time,String kind,String target,boolean pending){
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
        users.get(user).put(id,old.asRead());setDirty();
    }
    public void readAll(UUID user){
        var entries=users.get(user);
        if(entries==null)return;
        boolean changed=false;
        for(var entry:entries.entrySet()){
            var message=entry.getValue();
            if(message.read())continue;
            entry.setValue(message.asRead());
            changed=true;
        }
        if(changed)setDirty();
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
            boolean foreign=(e.kind().equals("diplomacy")||e.kind().equals("progress_letter")||e.kind().equals("story"))&&!e.target().startsWith(team+"/");
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
