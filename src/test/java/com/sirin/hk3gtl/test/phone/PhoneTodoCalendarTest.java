package com.sirin.hk3gtl.test.phone;

import com.sirin.hk3gtl.common.easter.Hk3EggRules;
import com.sirin.hk3gtl.common.phone.Hk3TodoCalendarSessions;
import java.time.*;
import java.util.*;

/** 【变更记录 #1】2026-11-05（修订206）：用明确日期验证全星期、跨日、倒退、本人隔离及清理；固定日期是测试输入，不改服务器或系统时钟。 */
public final class PhoneTodoCalendarTest {
    private static int checks;
    private static void check(boolean result,String message){if(!result)throw new AssertionError(message);checks++;}
    public static void main(String[] args){
        UUID a=UUID.randomUUID(),b=UUID.randomUUID();var sessions=new Hk3TodoCalendarSessions();
        var monday=LocalDateTime.of(2026,11,2,12,0);var friday=monday.plusDays(4);
        for(int i=0;i<7;i++){
            var now=monday.plusDays(i);sessions.clear();
            check(sessions.todoOpened(a,now)==(i==0),"待办周一事实："+now.getDayOfWeek());
            sessions.completed(a,now.plusSeconds(1));
            check(sessions.closed(a,now.plusSeconds(2))==(i==4),"只有周五实际完成后关闭："+now.getDayOfWeek());
            check(!sessions.closed(a,now.plusSeconds(3)),"重复关闭无事实");
        }
        sessions.completed(a,friday);sessions.opened(a,friday.plusSeconds(1));
        check(!sessions.closed(a,friday.plusSeconds(2)),"开机前完成不跨会话");
        sessions.opened(a,friday);check(!sessions.closed(a,friday.plusSeconds(1)),"仅打开关闭不算完成");
        sessions.opened(a,friday);sessions.completed(a,friday.plusSeconds(1));sessions.opened(b,friday);
        check(!sessions.closed(b,friday.plusSeconds(2)),"其他玩家不能沿用完成事实");
        sessions.opened(a,friday.plusSeconds(2));sessions.todoOpened(a,friday.plusSeconds(3));
        check(sessions.closed(a,friday.plusSeconds(4)),"导航与待办刷新不丢本会话完成");
        sessions.opened(a,friday);sessions.completed(a,friday.plusSeconds(1));sessions.clear(a);
        check(!sessions.closed(a,friday.plusSeconds(2)),"断线清理后不沿用");
        for(UUID owner:List.of(a,b)){sessions.opened(owner,friday);sessions.completed(owner,friday.plusSeconds(1));}
        sessions.clear();for(UUID owner:List.of(a,b))check(!sessions.closed(owner,friday.plusSeconds(2)),"停服清空全部会话");
        var late=friday.withHour(23).withMinute(59).withSecond(59);
        sessions.opened(a,late.minusSeconds(1));sessions.completed(a,late);
        check(!sessions.closed(a,late.plusSeconds(1)),"跨到周六不发收工彩蛋");
        sessions.opened(a,friday);sessions.completed(a,friday.plusSeconds(1));
        check(!sessions.closed(a,friday.plusWeeks(1)),"不能留到下周五使用");
        sessions.opened(a,friday);sessions.completed(a,friday.plusSeconds(1));
        check(!sessions.closed(a,friday.minusSeconds(1)),"关闭时钟倒退拒绝");
        sessions.opened(a,friday);sessions.completed(a,friday.plusMinutes(1));sessions.opened(a,friday.minusMinutes(1));
        check(!sessions.closed(a,friday.plusMinutes(2)),"导航发现倒退即清完成标记");
        sessions.opened(a,friday.minusDays(1));sessions.completed(a,friday.minusDays(1).plusSeconds(1));
        check(!sessions.closed(a,friday),"周四完成周五关闭不满足");
        sessions.opened(a,friday.minusDays(1));sessions.completed(a,friday);
        check(sessions.closed(a,friday.plusSeconds(1)),"前一日开机、周五完成并关闭有效");
        var instant=Instant.parse("2026-11-05T16:30:00Z");
        check(instant.atZone(ZoneId.of("Asia/Hong_Kong")).getDayOfWeek()==DayOfWeek.FRIDAY
            &&instant.atZone(ZoneId.of("UTC")).getDayOfWeek()==DayOfWeek.THURSDAY,"服务器配置时区决定星期而非客户端日期");
        for(var rule:Hk3EggRules.all()){
            if(rule.id().equals("E-EG-378")){check(rule.matches("notebook_calendar_open",Map.of("monday","true")),"378周一真实事实");check(!rule.matches("notebook_calendar_open",Map.of("monday","false")),"378非周一拒绝");}
            if(rule.id().equals("E-EG-379")){check(rule.matches("notebook_calendar_close",Map.of("friday_completed","true")),"379周五完成关闭事实");check(!rule.matches("notebook_calendar_close",Map.of("friday_completed","false")),"379缺完成事实拒绝");}
        }
        check(Hk3EggRules.all().stream().filter(r->Set.of("E-EG-378","E-EG-379").contains(r.id())).count()==2,"两条日历规则真实注册");
        System.out.println("Phone todo calendar: "+checks+" checks passed");
    }
}
