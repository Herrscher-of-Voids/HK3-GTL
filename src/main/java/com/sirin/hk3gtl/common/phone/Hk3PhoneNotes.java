package com.sirin.hk3gtl.common.phone;
import java.util.*;
import net.minecraft.nbt.*;
import net.minecraft.world.level.saveddata.SavedData;
import net.minecraft.server.level.ServerPlayer;
/**
 * 【变更记录 #1】2026-09-30 18:58:24（内测5修订114）
 * 删除：无；新增：按玩家隔离的个人笔记账本；修改：无。
 * 用途：存档持久化、64条上限、标题64字/正文4096字、版本冲突保护，客户端不指定他人UUID。
 */
/** 【变更记录 #2】2026-10-01 17:04:49（修订136）：删除坏条目静默跳过与空账本回退；新增完整类型/身份/重复项/数量检查及防覆盖加载；修改读取须全部合法才返回；用途：避免下一次保存覆盖玩家笔记，正常旧格式保持可读。 */
public final class Hk3PhoneNotes extends SavedData {
    /** 【变更记录 #3】2026-11-05（修订205）：新增本人颜色标签、待办勾选与已完成任务的连续实质修改；旧笔记默认无标签，状态和版本一起提交。 */
    public record Note(String id,String title,String body,int version,long time,int colors,boolean task,boolean done,int optimizations){
        public Note(String id,String title,String body,int version,long time){this(id,title,body,version,time,0,false,false,0);}
    }
    private final Map<UUID,LinkedHashMap<String,Note>> users=new HashMap<>();
    public static Hk3PhoneNotes get(ServerPlayer p){return com.sirin.hk3gtl.common.util.Hk3SavedDataGuard.get(p.server,"hk3gtl_phone_notes",Hk3PhoneNotes::load,Hk3PhoneNotes::new);}
    public List<Note> list(UUID id){var result=new ArrayList<>(users.getOrDefault(id,new LinkedHashMap<>()).values());result.sort(Comparator.comparingLong(Note::time).reversed().thenComparing(Note::id));return result;}
    public Note find(UUID user,String id){return users.getOrDefault(user,new LinkedHashMap<>()).get(id);}
    public boolean saveNote(UUID user,String id,int expected,String title,String body,long time){
        var old=find(user,id);
        return saveNote(user,id,expected,title,body,time,old==null?0:old.colors(),old!=null&&old.task())!=null;
    }
    public Note saveNote(UUID user,String id,int expected,String title,String body,long time,int colors,boolean task){
        if(id==null||colors<0||colors>7||title==null||body==null||title.length()>64||body.length()>4096||body.indexOf('\0')>=0||title.isBlank()||title.chars().anyMatch(Character::isISOControl))return null;
        var notes=users.computeIfAbsent(user,k->new LinkedHashMap<>());
        Note old=notes.get(id);
        if(id.isEmpty()){
            if(expected!=0||notes.size()>=64)return null;id=UUID.randomUUID().toString();
        }else{
            if(old==null||old.version()!=expected||expected==Integer.MAX_VALUE)return null;
        }
        boolean done=task&&old!=null&&old.done();
        int edits=done&&old.title().contains("优化")&&title.contains("优化")&&!old.title().equals(title)&&!old.body().equals(body)?Math.min(3,old.optimizations()+1):0;
        var saved=new Note(id,title,body,expected+1,time,colors,task,done,edits);
        notes.put(id,saved);setDirty();return saved;
    }
    public Note checkTask(UUID user,String id,int expected,boolean done,long time){
        var old=find(user,id);
        if(old==null||!old.task()||old.done()==done||old.version()!=expected||expected==Integer.MAX_VALUE)return null;
        var saved=new Note(id,old.title(),old.body(),expected+1,time,old.colors(),true,done,0);
        users.get(user).put(id,saved);setDirty();return saved;
    }
    public boolean delete(UUID user,String id,int expected){
        var note=find(user,id);if(note==null||note.version()!=expected)return false;
        users.get(user).remove(id);setDirty();return true;
    }
    public static Hk3PhoneNotes load(CompoundTag tag){
        com.sirin.hk3gtl.common.util.Hk3LedgerValidation.type(tag,"Users",Tag.TAG_COMPOUND);
        var data=new Hk3PhoneNotes();var root=tag.getCompound("Users");
        for(String key:root.getAllKeys()){
            UUID user=com.sirin.hk3gtl.common.util.Hk3LedgerValidation.uuid(key);var rows=new LinkedHashMap<String,Note>();
            var list=com.sirin.hk3gtl.common.util.Hk3LedgerValidation.list(root,key,Tag.TAG_COMPOUND);
            com.sirin.hk3gtl.common.util.Hk3LedgerValidation.require(list.size()<=64&&!data.users.containsKey(user),"笔记用户或数量");
            for(Tag raw:list){
                var n=(CompoundTag)raw;String id=n.getString("Id"),title=n.getString("Title"),body=n.getString("Body");
                for(String field:List.of("Id","Title","Body"))com.sirin.hk3gtl.common.util.Hk3LedgerValidation.type(n,field,Tag.TAG_STRING);
                com.sirin.hk3gtl.common.util.Hk3LedgerValidation.uuid(id);
                com.sirin.hk3gtl.common.util.Hk3LedgerValidation.type(n,"Version",Tag.TAG_INT);
                com.sirin.hk3gtl.common.util.Hk3LedgerValidation.type(n,"Time",Tag.TAG_LONG);
                com.sirin.hk3gtl.common.util.Hk3LedgerValidation.require(!title.isBlank()&&title.length()<=64&&body.length()<=4096
                    &&body.indexOf('\0')<0&&title.chars().noneMatch(Character::isISOControl)&&n.getInt("Version")>=1&&!rows.containsKey(id),"笔记条目");
                int colors=0,edits=0;boolean task=false,done=false;
                if(List.of("Colors","Task","Done","Optimizations").stream().anyMatch(n::contains)){
                    for(String field:List.of("Colors","Optimizations"))com.sirin.hk3gtl.common.util.Hk3LedgerValidation.type(n,field,Tag.TAG_INT);
                    for(String field:List.of("Task","Done"))com.sirin.hk3gtl.common.util.Hk3LedgerValidation.type(n,field,Tag.TAG_BYTE);
                    colors=n.getInt("Colors");edits=n.getInt("Optimizations");task=n.getBoolean("Task");done=n.getBoolean("Done");
                    com.sirin.hk3gtl.common.util.Hk3LedgerValidation.require(colors>=0&&colors<=7&&edits>=0&&edits<=3
                        &&n.getByte("Task")>=0&&n.getByte("Task")<=1&&n.getByte("Done")>=0&&n.getByte("Done")<=1
                        &&(!done||task)&&(edits==0||done&&title.contains("优化"))&&edits<n.getInt("Version"),"笔记标签或待办状态");
                }
                rows.put(id,new Note(id,title,body,n.getInt("Version"),n.getLong("Time"),colors,task,done,edits));
            }data.users.put(user,rows);
        }
        return data;
    }
    @Override public CompoundTag save(CompoundTag tag){
        var root=new CompoundTag();users.forEach((id,notes)->{
            var rows=new ListTag();notes.values().forEach(note->{
                var n=new CompoundTag();n.putString("Id",note.id());n.putString("Title",note.title());n.putString("Body",note.body());n.putInt("Version",note.version());n.putLong("Time",note.time());rows.add(n);
                n.putInt("Colors",note.colors());n.putBoolean("Task",note.task());n.putBoolean("Done",note.done());n.putInt("Optimizations",note.optimizations());
            });root.put(id.toString(),rows);
        });tag.put("Users",root);return tag;
    }
}
