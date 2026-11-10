package com.sirin.hk3gtl.common.communication;

/** 【变更记录 #2】2026-10-01 00:17:25（修订122）：删除无；新增/修改：公开具名发信人供抬头、通知和历史共同读取；用途：五方首信与团队限定交流保持一致。 */
import com.google.gson.Gson;
import java.io.InputStreamReader;
import java.nio.charset.StandardCharsets;
import java.util.*;

/** 【变更记录 #1】2026-10-01 00:14:30（修订122）：删除无；新增往世乐土/圣芙蕾雅首信正文目录；修改无；用途：按本轮五方范围提供新增正文，原三方已审稿保持不变。 */
public final class Hk3FactionLetters {
    public record Entry(String id,String title,String speaker,List<String> lines){}
    private record Catalog(int schema,List<Entry> entries){}
    private static final Map<String,Entry> ALL=load();
    private Hk3FactionLetters(){}
    private static Map<String,Entry> load(){
        try(var in=Hk3FactionLetters.class.getResourceAsStream("/assets/hk3gtl/narrative/faction_first_contacts.json")){
            if(in==null)throw new IllegalStateException("五方首信目录缺失");var c=new Gson().fromJson(new InputStreamReader(in,StandardCharsets.UTF_8),Catalog.class);
            if(c.schema!=1)throw new IllegalStateException("首信版本无效");var out=new LinkedHashMap<String,Entry>();
            for(var e:c.entries)if(e.lines==null||e.lines.isEmpty()||out.put(e.id,new Entry(e.id,e.title,e.speaker,List.copyOf(e.lines)))!=null)throw new IllegalStateException("首信条目无效");return Map.copyOf(out);
        }catch(java.io.IOException e){throw new IllegalStateException("首信目录读取失败",e);}
    }
    public static String speaker(String id){var e=ALL.get(id);return e==null?"":e.speaker;}
    public static String title(String id){var e=ALL.get(id);return e==null?id:e.title;}
    public static String body(String id){var e=ALL.get(id);return e==null?"":String.join("\n\n",e.lines);}
    public static Collection<Entry> all(){return ALL.values();}
}
