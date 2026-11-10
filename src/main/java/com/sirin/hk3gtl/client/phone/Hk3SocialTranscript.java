package com.sirin.hk3gtl.client.phone;
import java.util.*;
/** 【变更记录 #1】2026-09-30 20:01:10（修订116）：删除无；新增跨离线/AI消息的稳定时间排序；修改无；用途：显示与最近上下文共享顺序，避免分组造成旧AI覆盖新离线语境。 */
public final class Hk3SocialTranscript {
    public record Entry(String speaker,String text,boolean user,boolean ai,long tick){}
    private Hk3SocialTranscript(){}
    public static List<Entry> merge(List<Entry> offline,List<Entry> ai){var result=new ArrayList<>(offline);result.addAll(ai);result.sort(Comparator.comparingLong(Entry::tick));return result;}
    public static List<Hk3SocialAiClient.Message> context(List<Entry> ordered){return ordered.subList(Math.max(0,ordered.size()-8),ordered.size()).stream().map(e->new Hk3SocialAiClient.Message(e.user?"user":"assistant",e.text)).toList();}
}
