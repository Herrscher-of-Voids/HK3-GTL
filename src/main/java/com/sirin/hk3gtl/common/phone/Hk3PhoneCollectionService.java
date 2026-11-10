package com.sirin.hk3gtl.common.phone;


import com.sirin.hk3gtl.common.easter.*;
import com.sirin.hk3gtl.common.narrative.*;
import net.minecraft.nbt.*;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerPlayer;
import java.util.*;

/** 【变更记录 #1】2026-11-05 01:59:54（第1次备注 · 内测5修订204）：删除无；新增本人收藏搜索、保存版本的分段只读笔记及第五百页说明的主动收藏；修改通过既有手机与连续阅读回执提交324、385、500事实；用途：本人供电、原文、版本、动作令牌共同核验，不授研究或阶段。 */
/** 【变更记录 #2】2026-11-05 02:06:11（第2次备注 · 内测5修订204）：删除动作拒绝后保留无效会话的路径；新增翻段和收藏入口在供电、资格或版本失效时立即清除阅读与个人上下文；修改不再依赖下一游戏刻清理；用途：同刻恢复电量不能复用失效前的完整阅读动作。 */
/** 【变更记录 #3】2026-11-05 22:19:02（修订211）：删除无；新增自写冒险计划末段完整阅读的本人回执；修改不影响2747或收藏动作；用途：接通418前置并保留逐段、版本和供电校验。 */
public final class Hk3PhoneCollectionService {
    private record Open(String id,String action,Hk3PhoneNotes.Note note,int page) {}
    private static final Map<UUID,Open> OPEN=new java.util.concurrent.ConcurrentHashMap<>();
    private Hk3PhoneCollectionService() {}
    private static boolean allowed(ServerPlayer p){return Hk3PhoneData.get(p).installed(p.getUUID())&&Hk3PhoneRuntime.powered(p);}
    private static String tr(String key){return Component.translatable(key).getString();}
    public static List<String> notePages(String body){return body.lines().filter(s->!s.isBlank()).toList();}
    public static boolean sameNote(Hk3PhoneNotes.Note opened,Hk3PhoneNotes.Note latest){return opened!=null&&opened.equals(latest);}
    public static boolean sevenParagraphs(Hk3PhoneNotes.Note note){return note!=null&&note.title().equals("2747")&&notePages(note.body()).size()==7;}
    public static boolean matches(String query,String title,String body){return (title+"\n"+body).toLowerCase(Locale.ROOT).contains(query.toLowerCase(Locale.ROOT));}
    public static boolean discovered(CompoundTag state){return Hk3EggCatalog.all().stream().anyMatch(e->Hk3NarrativeLog.isUnlocked(state,e.id()));}
    public static List<Hk3NarrativeNode> searchOwned(CompoundTag state,String query,java.util.function.Function<String,String> translate){
        return Hk3CollectionRecords.unlocked(state,"all").stream()
            .filter(n->matches(query,n.id()+"\n"+Hk3CollectionRecords.title(n,translate),Hk3CollectionRecords.body(n,translate))).toList();
    }
    public static int search(ServerPlayer p,int page,String query){
        if(!allowed(p)||query==null||query.length()>64||query.isBlank())return 0;
        var all=searchOwned(p.getPersistentData(),query,Hk3PhoneCollectionService::tr);
        page=Math.max(0,Math.min(page,Math.max(0,(all.size()-1)/8)));
        var v=new CompoundTag();v.putString("Mode","archive");v.putString("Filter","all");v.putString("Query",query);
        v.putInt("Page",page);v.putInt("Total",all.size());v.putInt("Available",(int)Hk3CollectionRecords.total("all"));
        v.putBoolean("CollectionExplanation",discovered(p.getPersistentData()));var rows=new ListTag();
        all.stream().skip(page*8L).limit(8).forEach(n->{var row=new CompoundTag();row.putString("Id",n.id());row.putString("Title",Hk3CollectionRecords.title(n,Hk3PhoneCollectionService::tr));rows.add(row);});
        v.put("Rows",rows);Hk3PhoneService.send(p,v);
        Hk3EggRuntime.observe(p,"collection_search",Hk3EggRuntime.fields("query",query,"results",Integer.toString(all.size())));return 1;
    }
    public static int readNote(ServerPlayer p,String id){
        if(!allowed(p))return 0;var note=Hk3PhoneNotes.get(p).find(p.getUUID(),id);
        if(note==null||notePages(note.body()).isEmpty())return 0;
        return showNote(p,note,0);
    }
    private static int showNote(ServerPlayer p,Hk3PhoneNotes.Note note,int page){
        var pages=notePages(note.body());var open=new Open("note_read_"+note.id()+"_"+note.version()+"_"+page,UUID.randomUUID().toString(),note,page);
        OPEN.put(p.getUUID(),open);var v=detail(open,note.title(),pages.get(page));
        v.putBoolean("NoteRead",true);v.putString("NoteId",note.id());v.putInt("NotePage",page);v.putInt("NoteTotal",pages.size());
        Hk3PhoneService.send(p,v);return 1;
    }
    public static int nextNote(ServerPlayer p,String action){
        var open=OPEN.get(p.getUUID());
        if(open!=null&&!valid(p,open)){Hk3EggReading.clear(p.getUUID());return 0;}
        if(open==null||open.note()==null||!open.action().equals(action)||open.page()+1>=notePages(open.note().body()).size()
                ||!Hk3EggReading.consumeAction(p,action))return 0;
        return showNote(p,open.note(),open.page()+1);
    }
    public static int explanation(ServerPlayer p){
        if(!allowed(p)||!discovered(p.getPersistentData()))return 0;
        var egg=Hk3EggCatalog.get("E-EG-500");var open=new Open("collection_explanation_500",UUID.randomUUID().toString(),null,0);
        OPEN.put(p.getUUID(),open);var v=detail(open,egg.title(),egg.body()+"\n\n收藏说明\n"+egg.condition());v.putBoolean("CollectionExplanation",true);
        Hk3PhoneService.send(p,v);return 1;
    }
    private static CompoundTag detail(Open open,String title,String body){
        var v=new CompoundTag();v.putString("Mode","archive_detail");v.putString("Id",open.id());v.putString("Token",open.action());v.putString("Title",title);v.putString("Body",body);return v;
    }
    public static int collect(ServerPlayer p,String action){
        var open=OPEN.get(p.getUUID());
        if(open!=null&&!valid(p,open)){Hk3EggReading.clear(p.getUUID());return 0;}
        if(open==null||open.note()!=null||!open.action().equals(action)||!Hk3EggReading.consumeAction(p,action))return 0;
        OPEN.remove(p.getUUID());Hk3EggRuntime.observe(p,"collection_collect",Hk3EggRuntime.fields("id","E-EG-500","discovered","true","complete","true","active","true"));
        if(!Hk3NarrativeLog.isUnlocked(p,"E-EG-500"))return 0;
        var done=new CompoundTag();done.putString("Mode","archive_detail");done.putString("Title","第五百页之后 · 已收藏");done.putString("Body",Hk3EggCatalog.get("E-EG-500").body());Hk3PhoneService.send(p,done);return 1;
    }
    private static boolean valid(ServerPlayer p,Open open){
        return allowed(p)&&(open.note()==null?discovered(p.getPersistentData()):sameNote(open.note(),Hk3PhoneNotes.get(p).find(p.getUUID(),open.note().id())));
    }
    public static boolean managed(String id){return id.startsWith("note_read_")||id.equals("collection_explanation_500");}
    /** 阅读期间逐片重验供电和保存版本；失效会话即使恢复供电也不能续用。 */
    public static boolean authorize(ServerPlayer p,String id){
        var open=OPEN.get(p.getUUID());return open!=null&&open.id().equals(id)&&valid(p,open);
    }
    public static void viewChanged(ServerPlayer p,CompoundTag view){
        var open=OPEN.get(p.getUUID());if(open!=null&&!open.id().equals(view.getString("Id")))OPEN.remove(p.getUUID());
    }
    public static void readCompleted(ServerPlayer p,Hk3ReadingSessions.Session session){
        var open=OPEN.get(p.getUUID());if(open==null||!session.cursor().done()||!open.action().equals(session.action())||!authorize(p,session.id())||open.note()==null)return;
        if(open.page()==notePages(open.note().body()).size()-1&&open.note().title().contains("冒险计划"))Hk3EggRuntime.state(p).putBoolean("adventurePlanRead",true);
        if(open.page()==6&&sevenParagraphs(open.note()))Hk3EggRuntime.observe(p,"note_read_last",Hk3EggRuntime.fields("title","2747","paragraphs","7","complete","true","manual","true"));
    }
    public static boolean invalid(ServerPlayer p){var open=OPEN.get(p.getUUID());return open!=null&&!valid(p,open);}
    public static void clear(UUID player){OPEN.remove(player);}
    public static void clear(){OPEN.clear();}
}
