package com.sirin.hk3gtl.common.phone;
import java.util.*;










public final class Hk3PhoneDesktopOrder {
    public static final List<String> APPS=List.of("inbox","letters","ae","updates","settings","quiet","notes","trade","tiles2048","snake","civilization","social","cipher");
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
