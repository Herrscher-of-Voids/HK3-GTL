package com.sirin.hk3gtl.common.easter;

import java.util.*;

public final class Hk3EggNoteFacts {
    private Hk3EggNoteFacts(){}
    public static boolean hasValidDate(String body){
        var dates=java.util.regex.Pattern.compile("(?<![0-9])([0-9]{4})(?:-([0-9]{1,2})-([0-9]{1,2})|年([0-9]{1,2})月([0-9]{1,2})日)(?![0-9])").matcher(body);
        while(dates.find())try{
            java.time.LocalDate.of(Integer.parseInt(dates.group(1)),Integer.parseInt(dates.group(dates.group(2)!=null?2:4)),Integer.parseInt(dates.group(dates.group(3)!=null?3:5)));
            return true;
        }catch(java.time.DateTimeException invalid){}
        return false;
    }
    public static Map<String,String> saved(String title,String body){
        if(title.length()>64||body.length()>4096)throw new IllegalArgumentException("超出笔记服务约定的长度");
        String upper=body.toUpperCase(Locale.ROOT);
        boolean alphabet=true;for(char c='A';c<='Z';c++)if(upper.indexOf(c)<0){alphabet=false;break;}
        return Map.of("title",title,"body",body,"characters",Integer.toString(body.codePointCount(0,body.length())),
                "paragraphs",Long.toString(body.lines().filter(s->!s.isBlank()).count()),"alphabet",Boolean.toString(alphabet));
    }
}
