package com.sirin.hk3gtl.common.easter;
import net.minecraft.server.level.ServerPlayer;
import java.util.*;
import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
 
 
 
 
 
 
 
 
 
 
 
 
public final class Hk3EggNotes {
    private Hk3EggNotes(){}
    public static String digest(String text){
        try{return HexFormat.of().formatHex(MessageDigest.getInstance("SHA-256").digest(text.getBytes(StandardCharsets.UTF_8)));}
        catch(java.security.NoSuchAlgorithmException impossible){throw new IllegalStateException(impossible);}
    }
    public static void saved(ServerPlayer p,String title,String body){
        var n=Hk3EggRuntime.state(p);var seen=n.getCompound("noteHashes");
        if(!body.isBlank()&&seen.size()<19)seen.putBoolean(digest(body),true);
        n.put("noteHashes",seen);
        var f=new LinkedHashMap<>(Hk3EggCalendar.facts(Hk3EggCalendar.now(),p.server.overworld().getDayTime()));
        f.putAll(Hk3EggNoteFacts.saved(title,body));
        f.put("different_saves",Integer.toString(seen.size()));
        f.put("green",Boolean.toString(body.contains("绿")));f.put("blue",Boolean.toString(body.contains("蓝")));
        f.put("thanks",Boolean.toString((title+body).contains("感谢")||(title+body).contains("谢谢")));
        f.put("recipe_note",Boolean.toString((title+body).contains("配方")&&!body.isBlank()));
        f.put("celebrate",Boolean.toString(body.contains("庆典")));f.put("constant",Boolean.toString(body.contains("永恒领域")));
        f.put("stars",Long.toString(body.codePoints().filter(c->c=='☆'||c=='★'||c=='*').count()));
        var urls=java.util.regex.Pattern.compile("https?://[^\\s]+",java.util.regex.Pattern.UNICODE_CHARACTER_CLASS).matcher(body);
        var sources=new HashSet<String>();while(urls.find())sources.add(urls.group());
        f.put("sources",Integer.toString(sources.size()));
        int modification=body.indexOf("改动");f.put("modification",Boolean.toString(modification>=0&&body.substring(modification+2).strip().codePointCount(0,body.substring(modification+2).strip().length())>=20));
        f.put("backup",Boolean.toString((title+body).contains("备份")));
        f.put("has_date",Boolean.toString(Hk3EggNoteFacts.hasValidDate(body)));
        f.put("acceptance",Boolean.toString((title+body).contains("验收")));
        f.put("gravity_plan",Boolean.toString(body.contains("如果重力倒过来")&&!body.replace("如果重力倒过来","").strip().isEmpty()));
        f.put("power_plan",Boolean.toString(body.contains("戴森球")&&body.replace("戴森球","").strip().codePointCount(0,body.replace("戴森球","").strip().length())>=20));
        f.put("reference",Boolean.toString(!sources.isEmpty()||java.util.regex.Pattern.compile("(?:来源|参考|作者)[：:]\\s*[^\\s：:]+",java.util.regex.Pattern.UNICODE_CHARACTER_CLASS).matcher(body).find()));
        f.put("steps",Long.toString(body.lines().map(String::strip).filter(s->s.matches("[1-9][.、)）].{3,}")).count()));
        n.putString("lastNoteBody",body);n.putString("lastNoteTitle",title);n.putLong("lastNoteTick",p.server.overworld().getGameTime());
        if(body.codePointCount(0,body.length())>=20)n.putBoolean("note20",true);
        if(title.equals("3125")&&body.lines().filter(line->line.strip().matches("[1-5][.、)）].{1,}")).count()==5)n.putString("saved3125",digest(body));
        if(n.getBoolean("fishedAndReeled")&&p.fishing==null&&!body.isBlank()){Hk3EggVanilla.caseEvent(p,456);n.remove("fishedAndReeled");}
        if(title.equals("3819")&&!body.isBlank()&&n.getBoolean("mountainSpied"))Hk3EggVanilla.caseEvent(p,402);
        if(n.getBoolean("floor1610")&&body.contains("1.618"))Hk3EggVanilla.caseEvent(p,330);
        Hk3EggExploration.note(p,title,body);
        Hk3EggLifeEvents.note(p,title,body);
        Hk3EggPersonalScenes.note(p,title,body);
        Hk3EggPaintingScenes.note(p,title);
        Hk3EggRuntime.observe(p,"note_saved",f);
    }
    public static void opened(ServerPlayer p,String title,String body){
        Hk3EggTravel.note(p,body);
        Hk3EggPersonalScenes.openedNote(p,body);
        if(title.equals("3125")&&Hk3EggRuntime.state(p).getString("saved3125").equals(digest(body)))Hk3EggVanilla.caseEvent(p,384);
        Hk3EggRuntime.observe(p,"note_open",Hk3EggRuntime.fields("title",title,"body",body));
    }
}
