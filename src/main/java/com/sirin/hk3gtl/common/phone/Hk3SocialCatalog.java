package com.sirin.hk3gtl.common.phone;

import com.google.gson.Gson;
import java.io.InputStreamReader;
import java.nio.charset.StandardCharsets;
import java.util.*;

/** 【变更记录 #1】2026-09-30 19:56:03（修订116）：删除无；新增角色正文目录、话题选择与阶段判定；修改家园语境为远程通信；用途：离线对话与AI示例共用，不产生游戏事实。 */
public final class Hk3SocialCatalog {
    public record Line(String source,String topic,String text){}
    public record Contact(String id,String name,String voice,String suffix,int minimum,int maximum,List<Line> lines,List<String> moments){
        public boolean available(int stage){return stage>=minimum&&stage<maximum;}
        public String finish(String text){
            text=text.replace("§","").strip();
            if(suffix.equals("☆"))text=text.replace("。☆","☆").replace("。","☆");
            if(text.length()>1800)text=text.substring(0,1800);
            return suffix.isEmpty()||text.endsWith(suffix)?text:text+suffix;
        }
        public Line reply(String input,long dayTime,boolean raining,int sequence){
            String topic=topic(input,dayTime,raining);
            var options=lines.stream().filter(l->l.topic.equals(topic)).toList();
            if(options.isEmpty())options=lines.stream().filter(l->l.topic.equals("unknown")).toList();
            return options.get(Math.floorMod(sequence,options.size()));
        }
    }
    private record Catalog(List<Contact> contacts){}
    private static final List<Contact> CONTACTS=load();
    private Hk3SocialCatalog(){}
    private static List<Contact> load(){
        try(var stream=Hk3SocialCatalog.class.getResourceAsStream("/assets/hk3gtl/narrative/social_dialogues.json")){
            if(stream==null)throw new IllegalStateException("微讯息正文缺失");
            var rows=new Gson().fromJson(new InputStreamReader(stream,StandardCharsets.UTF_8),Catalog.class).contacts;
            var ids=new HashSet<String>();
            for(var c:rows)if(!ids.add(c.id)||c.lines.size()<24||c.lines.stream().noneMatch(l->l.topic.equals("unknown")))throw new IllegalStateException("微讯息目录不完整");
            return List.copyOf(rows);
        }catch(java.io.IOException ex){throw new IllegalStateException("微讯息资源读取失败",ex);}
    }
    public static List<Contact> all(){return CONTACTS;}
    public static Contact get(String id){return CONTACTS.stream().filter(c->c.id.equals(id)).findFirst().orElse(null);}
    public static boolean validInput(String text){return text!=null&&!text.isBlank()&&text.length()<=512&&text.chars().noneMatch(c->Character.isISOControl(c)||c=='§');}
    private static boolean has(String s,String... words){return Arrays.stream(words).anyMatch(s::contains);}
    public static String topic(String text,long time,boolean raining){
        String s=text.toLowerCase(Locale.ROOT).strip();long t=Math.floorMod(time,24000);
        if(has(s,"配方","多少","怎么做","怎么合成","解锁","奖励","指令","几安","电压","审查","api","key","密码"))return "mechanics";
        if(has(s,"早安","早上好"))return t<6000?"morning":"time";
        if(has(s,"下雨","雨天"))return raining?"rain":"weather";
        if(has(s,"晚安","晚上好","夜晚"))return t>=12000?"night":"time";
        if(has(s,"你好","您好","hello","嗨"))return "greeting";
        if(has(s,"再见","拜拜","下次聊"))return "goodbye";
        if(has(s,"失败","实验","研究","记录"))return "research";
        if(has(s,"累","休息","熬夜","难过","不开心","挫折"))return "care";
        if(has(s,"目标","选择","决定","未来"))return "choice";
        if(has(s,"家园","房子","基地","建筑"))return "home";
        if(has(s,"吃饭","今天","日常","闲聊","聊聊"))return "daily";
        if(has(s,"忙","稍后","等会"))return "busy";
        if(has(s,"安静","陪我","听我"))return "quiet";
        if(has(s,"又来","还记得","好久"))return "reunion";
        return "unknown";
    }
}
