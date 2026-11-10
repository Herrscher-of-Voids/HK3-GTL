package com.sirin.hk3gtl.common.phone;
import java.util.*;
/**
 * 【变更记录 #1】2026-09-30 18:44:46（内测5修订113）
 * 删除：无；新增：应用白名单、排列清理与交换；修改：无；用途：拖动不会丢App或引入任意命令。
 */
/**
 * 【变更记录 #2】2026-09-30 19:08:08（内测5修订114）
 * 删除：无；新增笔记、交易、2048、贪吃蛇、文明总览白名单；修改排列容量为11项。
 * 用途：手机应用集成，保留既有电量和阅读权限；交易只展示不结算。
 */
/** 【变更记录 #3】2026-09-30 19:49:34（修订116）：删除无；新增微讯息接入；修改：自动补全新应用而不重置排序；用途：保留原手机布局与权限，AI不进入服务器业务。 */
public final class Hk3PhoneDesktopOrder {
    public static final List<String> APPS=List.of("inbox","letters","ae","updates","settings","quiet","notes","trade","tiles2048","snake","civilization","social");
    private Hk3PhoneDesktopOrder(){}
    public static List<String> normalize(List<? extends String> input){
        var result=new ArrayList<String>();
        for(String id:input)if(id!=null&&APPS.contains(id)&&!result.contains(id))result.add(id);
        for(String id:APPS)if(!result.contains(id))result.add(id);
        return result;
    }
    public static List<String> move(List<? extends String> input,int from,int to){
        var result=normalize(input);
        if(from>=0&&from<result.size()&&to>=0&&to<result.size())Collections.swap(result,from,to);
        return result;
    }
}
