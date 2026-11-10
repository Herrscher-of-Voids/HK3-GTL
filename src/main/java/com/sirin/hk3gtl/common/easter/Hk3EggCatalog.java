package com.sirin.hk3gtl.common.easter;

import com.google.gson.*;
import java.io.*;
import java.nio.charset.StandardCharsets;
import java.util.*;

/** 【变更记录 #1】2026-10-01 04:08:14（修订128）：删除无；新增已审核彩蛋资源目录与严格结构校验；用途：稳定ID注册不再写死100或500，正文与触发来源可追溯。 */
public final class Hk3EggCatalog {
    public record Egg(String id,String title,String body,String condition,String category,List<String> sources) {
        public Egg { sources=List.copyOf(sources); }
        public String bodyKey(){return "hk3gtl.event.eg"+id.substring(5);}
        public String titleKey(){return "hk3gtl.narrative."+id.toLowerCase(Locale.ROOT).replace('-','_')+".title";}
    }
    private static final Map<String,Egg> ENTRIES=load();
    private Hk3EggCatalog(){}
    public static Collection<Egg> all(){return ENTRIES.values();}
    public static Egg get(String id){return ENTRIES.get(id);}
    public static boolean contains(String id){return ENTRIES.containsKey(id);}
    private static Map<String,Egg> load(){
        try(var in=Hk3EggCatalog.class.getResourceAsStream("/assets/hk3gtl/narrative/easter_eggs.json")){
            if(in==null)throw new IllegalStateException("彩蛋正式目录缺失");
            return parse(new InputStreamReader(in,StandardCharsets.UTF_8));
        }catch(IOException e){throw new IllegalStateException("读取彩蛋目录失败",e);}
    }
    public static Map<String,Egg> parse(Reader input){
        var root=JsonParser.parseReader(input).getAsJsonObject();
        if(root.get("schema").getAsInt()!=1)throw new IllegalArgumentException("未知彩蛋目录格式");
        var entries=new LinkedHashMap<String,Egg>();
        for(var value:root.getAsJsonArray("entries")){
            var r=value.getAsJsonObject();String id=text(r,"id",32);
            if(!id.matches("E-EG-[0-9]{3,}"))throw new IllegalArgumentException("非法彩蛋ID："+id);
            var sources=new ArrayList<String>();
            if(r.has("sources"))for(var s:r.getAsJsonArray("sources"))sources.add(s.getAsString());
            var egg=new Egg(id,text(r,"title",180),text(r,"body",8192),text(r,"condition",4096),text(r,"category",80),sources);
            if(entries.putIfAbsent(id,egg)!=null)throw new IllegalArgumentException("彩蛋ID重复："+id);
        }
        if(entries.isEmpty())throw new IllegalArgumentException("彩蛋目录为空");
        return Collections.unmodifiableMap(entries);
    }
    private static String text(JsonObject row,String key,int max){
        if(!row.has(key)||!row.get(key).isJsonPrimitive()||!row.getAsJsonPrimitive(key).isString())throw new IllegalArgumentException("彩蛋缺少文本字段："+key);
        String value=row.get(key).getAsString();
        if(value.isBlank()||value.length()>max)throw new IllegalArgumentException("彩蛋文本字段长度非法："+key);
        return value;
    }
}
