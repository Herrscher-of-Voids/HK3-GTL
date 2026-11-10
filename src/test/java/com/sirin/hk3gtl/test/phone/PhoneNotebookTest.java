package com.sirin.hk3gtl.test.phone;

import com.sirin.hk3gtl.common.phone.*;
import com.sirin.hk3gtl.common.easter.Hk3EggRules;
import net.minecraft.nbt.*;
import java.util.*;

/** 【变更记录 #1】2026-11-05（修订205）：覆盖真实标签、待办CAS、连续编辑、旧档及坏档拒绝；不冒充客户端实机画面。 */
public final class PhoneNotebookTest {
    private static int checks;
    private static void check(boolean result,String message){if(!result)throw new AssertionError(message);checks++;}
    private static void bad(CompoundTag root,String message){boolean rejected=false;try{Hk3PhoneNotes.load(root);}catch(RuntimeException e){rejected=true;}check(rejected,message);}
    public static void main(String[] args){
        UUID a=UUID.randomUUID(),b=UUID.randomUUID();var data=new Hk3PhoneNotes();
        var note=data.saveNote(a,"",0,"优化初稿","正文0",1,7,true);
        check(note!=null&&note.colors()==7&&note.task()&&!note.done(),"创建带三色标签的未完成任务");
        check(data.checkTask(b,note.id(),1,true,2)==null&&data.list(b).isEmpty(),"他人不能勾选");
        check(data.saveNote(a,note.id(),1,"优化改稿","正文1",2,8,true)==null,"非法颜色不提交");
        check(data.saveNote(a,note.id(),1,"优化改稿","正文1",2,-1,true)==null,"负颜色不提交");
        check(data.checkTask(a,note.id(),2,true,2)==null,"过期勾选被拒绝");
        note=data.checkTask(a,note.id(),1,true,2);check(note.done()&&note.version()==2,"本人逐条勾选更新版本");
        check(data.checkTask(a,note.id(),1,true,3)==null&&data.checkTask(a,note.id(),2,true,3)==null,"重放及重复勾选无事务");
        for(int i=1;i<=3;i++){
            note=data.saveNote(a,note.id(),note.version(),"优化第"+i+"稿","正文"+i,3+i,7,true);
            check(note.done()&&note.optimizations()==i,"已完成任务连续实质修改"+i);
        }
        var restored=Hk3PhoneNotes.load(data.save(new CompoundTag()));
        check(restored.find(a,note.id()).equals(note),"保存重载保留所有状态");
        check(restored.saveNote(a,note.id(),note.version(),"优化第3稿","正文3",9),"旧API仍可保存");
        note=restored.find(a,note.id());check(note.done()&&note.colors()==7&&note.optimizations()==0,"旧API保留标签但空改动中断连续编辑");
        note=restored.saveNote(a,note.id(),note.version(),"优化新标题","正文3",10,7,true);
        check(note.optimizations()==0,"仅改标题不计实质修改");
        note=restored.saveNote(a,note.id(),note.version(),note.title(),"另一正文",11,7,true);
        check(note.optimizations()==0,"仅改正文不计标题修改");
        note=restored.saveNote(a,note.id(),note.version(),"其他标题","正文12",12,7,true);
        check(note.optimizations()==0,"去掉优化不累计");
        note=restored.checkTask(a,note.id(),note.version(),false,13);
        check(!note.done()&&note.optimizations()==0,"取消勾选清除连续编辑");
        note=restored.saveNote(a,note.id(),note.version(),"优化未完成","正文14",14,7,true);
        check(!note.done()&&note.optimizations()==0,"未完成任务编辑不计数");
        note=restored.saveNote(a,note.id(),note.version(),"普通笔记","正文15",15,3,false);
        check(!note.task()&&!note.done()&&restored.checkTask(a,note.id(),note.version(),true,16)==null,"普通笔记不能勾选");
        var root=restored.save(new CompoundTag());var raw=root.getCompound("Users").getList(a.toString(),Tag.TAG_COMPOUND).getCompound(0);
        var original=root.copy();raw.putBoolean("Done",true);bad(root,"非任务完成状态拒绝");
        root=original.copy();raw=root.getCompound("Users").getList(a.toString(),Tag.TAG_COMPOUND).getCompound(0);raw.putInt("Colors",8);bad(root,"坏颜色拒绝");
        root=original.copy();raw=root.getCompound("Users").getList(a.toString(),Tag.TAG_COMPOUND).getCompound(0);raw.remove("Task");bad(root,"不完整新格式拒绝");
        root=original.copy();raw=root.getCompound("Users").getList(a.toString(),Tag.TAG_COMPOUND).getCompound(0);raw.putByte("Task",(byte)2);bad(root,"布尔值必须为0或1");
        root=original.copy();raw=root.getCompound("Users").getList(a.toString(),Tag.TAG_COMPOUND).getCompound(0);
        for(String field:List.of("Colors","Task","Done","Optimizations"))raw.remove(field);
        var legacy=Hk3PhoneNotes.load(root).find(a,note.id());check(legacy.colors()==0&&!legacy.task()&&!legacy.done()&&legacy.optimizations()==0,"旧笔记不丢正文且默认无标签");
        root=original.copy();raw=root.getCompound("Users").getList(a.toString(),Tag.TAG_COMPOUND).getCompound(0);
        raw.putBoolean("Task",true);raw.putInt("Version",Integer.MAX_VALUE);
        check(Hk3PhoneNotes.load(root).checkTask(a,note.id(),Integer.MAX_VALUE,true,17)==null,"勾选版本上溢拒绝");
        var buffer=new net.minecraft.network.FriendlyByteBuf(io.netty.buffer.Unpooled.buffer());
        try{var request=new Hk3PhoneNotePacket(false,note.id(),note.version(),note.title(),note.body(),7,true);Hk3PhoneNotePacket.encode(request,buffer);check(request.equals(Hk3PhoneNotePacket.decode(buffer))&&!buffer.isReadable(),"请求标签编码解码一致");}finally{buffer.release();}
        var rules=Hk3EggRules.all();
        check(rules.stream().filter(r->Set.of("E-EG-283","E-EG-339","E-EG-464").contains(r.id())).count()==3,"三条规则真实注册");
        for(var r:rules){
            if(r.id().equals("E-EG-283")){check(r.matches("notebook_saved",Map.of("colors","7")),"三色同次保存");check(!r.matches("notebook_saved",Map.of("colors","3")),"少一种标签不触发");}
            if(r.id().equals("E-EG-339")){check(r.matches("notebook_checked",Map.of("completed","3","pending","0")),"三条勾完且清零");check(!r.matches("notebook_checked",Map.of("completed","2","pending","0"))&&!r.matches("notebook_checked",Map.of("completed","3","pending","1")),"不足三条或有剩余不触发");}
            if(r.id().equals("E-EG-464")){check(r.matches("notebook_saved",Map.of("optimizations","3")),"三次实质修改");check(!r.matches("notebook_saved",Map.of("optimizations","2")),"两次不触发");}
        }
        System.out.println("Phone notebook: "+checks+" checks passed");
    }
}
