package com.sirin.hk3gtl.test.narrative;

import com.sirin.hk3gtl.common.easter.*;
import com.sirin.hk3gtl.common.phone.Hk3SocialBuiltinTopics;
import com.sirin.hk3gtl.common.phone.Hk3SocialCatalog;
import java.io.*;
import java.time.*;
import java.util.*;

/** 【变更记录 #1】2026-11-05（修订211）：新增年度农历表、闰月排除、坏表/时区/动作隔离及内置话题一致性检验；这些纯逻辑断言不冒充自然日期或真人触发。 */
public final class LunarCalendarTest {
    private static int checks;
    private static void check(boolean ok,String label){checks++;if(!ok)throw new AssertionError(label);}
    private static void rejected(String json){try{Hk3LunarCalendar.parse(new StringReader(json));throw new AssertionError("坏农历表未拒绝");}catch(RuntimeException expected){checks++;}}
    public static void main(String[] args)throws Exception{
        String json;
        try(var in=LunarCalendarTest.class.getResourceAsStream("/data/hk3gtl/calendar/lunar_festivals.json")){if(in==null)throw new AssertionError("缺农历表");json=new String(in.readAllBytes(),java.nio.charset.StandardCharsets.UTF_8);}
        var hk=ZoneId.of("Asia/Hong_Kong");var calendar=Hk3LunarCalendar.parse(new StringReader(json));
        check(calendar.years().size()==12,"12个逐年来源");
        for(var row:calendar.years().entrySet()){
            check(row.getValue().size()==6,"每年六节日");
            for(var entry:row.getValue().entrySet())check(entry.getKey().equals(calendar.facts(entry.getValue(),hk).get("lunar_festival")),"年度节日事实");
        }
        check(calendar.years().get(2026).get("spring_festival").equals(LocalDate.of(2026,2,17)),"2026春节");
        check(calendar.years().get(2026).get("mid_autumn").equals(LocalDate.of(2026,9,25)),"2026中秋");
        check(calendar.years().get(2028).get("dragon_boat").isBefore(LocalDate.of(2028,6,15)),"闰五月不重复端午");
        check(calendar.facts(LocalDate.of(2036,2,1),hk).isEmpty(),"缺年休眠");
        check(calendar.facts(LocalDate.of(2026,2,17),ZoneId.of("UTC")).isEmpty(),"民用日区间不同时拒绝");
        check(calendar.facts(LocalDate.of(2026,2,17),ZoneId.of("Asia/Shanghai")).get("lunar_festival").equals("spring_festival"),"同区间可用");
        rejected(json.replace("2026-02-17","2025-02-17"));rejected(json.replace("2026-09-25","2026-02-17"));rejected(json.replace("Asia/Hong_Kong","Unknown/Zone"));rejected("{}");
        var rule=Hk3EggRules.all().stream().filter(r->r.id().equals("E-EG-370")).findFirst().orElseThrow();
        check(!rule.matches("block_placed",calendar.facts(LocalDate.of(2026,2,17),hk)),"日期不能代替放灯笼");
        check(!rule.matches("food_finished",Map.of("lunar_festival","spring_festival","lantern","true")),"动作不能串用");
        var ids=new HashSet<Integer>();
        for(var topic:Hk3SocialBuiltinTopics.TOPICS){
            check(ids.add(topic.egg()),"话题ID不重复");check(Hk3SocialCatalog.get(topic.contact())!=null,"真实联系人");
            check(Hk3SocialBuiltinTopics.topic(topic.contact(),topic.text()).equals(topic),"固定话题可查");
            check(Hk3SocialBuiltinTopics.topic(topic.contact(),topic.text()+"自由补充")==null,"自由输入不能冒充");
        }
        check(Hk3EggCatalog.all().size()==500,"固定500正文分母");
        System.out.println("LunarCalendarTest: "+checks+" checks passed; calendar/topic logic only, not 500 natural triggers.");
    }
}
