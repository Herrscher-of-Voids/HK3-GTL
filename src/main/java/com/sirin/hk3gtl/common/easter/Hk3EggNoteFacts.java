package com.sirin.hk3gtl.common.easter;

import java.util.*;

/** 【变更记录 #1】2026-10-01 04:08:14（修订128）：删除无；新增成功保存后笔记内容的有界事实提取；用途：只读本人的本次已确认文本，不读取其他文件或AI回复。 */
/** 【变更记录 #2】2026-10-01 04:41:04（修订128）：删除：旧固定上限或被替代的分支；新增/修改：备份笔记日期以LocalDate严格验证，不接受越界月份、日期或非闰年2月29日；用途：已审核彩蛋独立执行，不授研究或审查资格。 */
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
        Objects.requireNonNull(title);Objects.requireNonNull(body);
        if(title.length()>64||body.length()>4096)throw new IllegalArgumentException("超出笔记服务约定的长度");
        String upper=body.toUpperCase(Locale.ROOT);
        boolean alphabet=true;for(char c='A';c<='Z';c++)if(upper.indexOf(c)<0){alphabet=false;break;}
        return Map.of("title",title,"body",body,"characters",Integer.toString(body.codePointCount(0,body.length())),
                "paragraphs",Long.toString(body.lines().filter(s->!s.isBlank()).count()),"alphabet",Boolean.toString(alphabet));
    }
}
