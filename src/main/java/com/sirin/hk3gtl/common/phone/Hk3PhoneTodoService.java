package com.sirin.hk3gtl.common.phone;

import com.sirin.hk3gtl.common.easter.Hk3EggRuntime;
import net.minecraft.nbt.*;
import net.minecraft.server.level.ServerPlayer;

 
public final class Hk3PhoneTodoService {
     
    private Hk3PhoneTodoService(){}
    private static boolean allowed(ServerPlayer p){return Hk3PhoneData.get(p).installed(p.getUUID())&&Hk3PhoneRuntime.requirePower(p);}
    static void saved(ServerPlayer p,Hk3PhoneNotes.Note note){
        Hk3EggRuntime.observe(p,"notebook_saved",Hk3EggRuntime.fields("colors",Integer.toString(note.colors()),
            "optimizations",Integer.toString(note.optimizations())));
    }
    public static int open(ServerPlayer p,int page){
        if(!allowed(p))return 0;
        com.sirin.hk3gtl.common.easter.Hk3EggPhone.opened(p,"todos");
        var all=Hk3PhoneNotes.get(p).list(p.getUUID()).stream().filter(Hk3PhoneNotes.Note::task).toList();
        page=Math.min(Math.max(0,page),Math.max(0,(all.size()-1)/6));
        var rows=new ListTag();all.stream().skip(page*6L).limit(6).forEach(n->{var row=Hk3PhoneAppService.row(n);row.remove("Body");rows.add(row);});
        var v=new CompoundTag();v.putString("Mode","todos");v.putInt("Page",page);v.putInt("Total",all.size());
        v.putInt("Done",(int)all.stream().filter(Hk3PhoneNotes.Note::done).count());v.put("Rows",rows);
        Hk3PhoneService.send(p,v);Hk3PhoneTodoCalendar.todoOpened(p);return 1;
    }
    public static int check(ServerPlayer p,String id,int version,boolean done){
        if(!allowed(p))return 0;
        var data=Hk3PhoneNotes.get(p);var saved=data.checkTask(p.getUUID(),id,version,done,p.server.overworld().getGameTime());
        if(saved==null){
            var v=new CompoundTag();v.putString("Mode","app_error");v.putString("Error","未更改：待办已更新或不存在，请返回列表刷新。");Hk3PhoneService.send(p,v);return 0;
        }
        if(done){
            Hk3PhoneTodoCalendar.completed(p);
            var tasks=data.list(p.getUUID()).stream().filter(Hk3PhoneNotes.Note::task).toList();
            long completed=tasks.stream().filter(Hk3PhoneNotes.Note::done).count();
            Hk3EggRuntime.observe(p,"notebook_checked",Hk3EggRuntime.fields("completed",Long.toString(completed),"pending",Long.toString(tasks.size()-completed)));
        }
        return open(p,0);
    }
}
