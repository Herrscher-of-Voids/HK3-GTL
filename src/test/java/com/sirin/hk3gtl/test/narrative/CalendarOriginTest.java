package com.sirin.hk3gtl.test.narrative;

import com.sirin.hk3gtl.common.easter.*;
import java.io.*;
import java.time.*;
import java.util.*;

/**
 * 【文件职责】检验节气年度变化、时区/缺库休眠、真实创建时间序列化与公历周年边界。
 * 【变更记录 #1】2026-11-05 19:08:32（修订210）：删除无；新增正反例与闰年/夏令时边界；修改无；用途：固定日期测试不冒充自然节气或真人入睡。
 */
public final class CalendarOriginTest {
    private static int checks;
    private static void check(boolean ok,String label){checks++;if(!ok)throw new AssertionError(label);}
    private static Hk3EggRules.Rule rule(int id){return Hk3EggRules.all().stream().filter(r->r.id().equals("E-EG-"+id)).findFirst().orElseThrow();}
    public static void main(String[] args)throws Exception{
        var hk=ZoneId.of("Asia/Hong_Kong");
        Hk3SolarCalendar.Library library;
        try(var in=CalendarOriginTest.class.getResourceAsStream("/data/hk3gtl/calendar/solar_terms.json")){
            if(in==null)throw new AssertionError("年度日历必须随包分发");
            library=Hk3SolarCalendar.parse(new InputStreamReader(in,java.nio.charset.StandardCharsets.UTF_8));
        }
        check(library.years().size()==12,"2024至2035逐年配置");
        for(var entry:library.years().entrySet()){
            var t=entry.getValue();
            check(library.facts(t.qingming(),hk).get("qingming").equals("true"),"逐年清明");
            check(library.facts(t.winterSolstice(),hk).get("winter_solstice").equals("true"),"逐年冬至");
            check(library.facts(t.qingming().minusDays(1),hk).get("qingming").equals("false"),"前日非清明");
            check(library.facts(t.winterSolstice().plusDays(1),hk).get("winter_solstice").equals("false"),"次日非冬至");
        }
        check(library.years().get(2024).qingming().getDayOfMonth()==4&&library.years().get(2026).qingming().getDayOfMonth()==5,"不固定4月4或5日");
        check(library.facts(LocalDate.of(2036,4,4),hk).isEmpty(),"无来源年份休眠");
        check(library.facts(LocalDate.of(2026,4,5),ZoneId.of("America/New_York")).isEmpty(),"不猜其他时区的交节日");
        check(library.facts(LocalDate.of(2026,4,5),ZoneId.of("Asia/Shanghai")).get("qingming").equals("true"),"同民用日区间接受");
        check(new Hk3SolarCalendar.Library(hk,Map.of()).facts(LocalDate.of(2026,4,5),hk).isEmpty(),"空库休眠");
        for(String bad:List.of("{}","{\"schema\":2}","{\"schema\":1,\"source\":\"\",\"sourceZone\":\"Asia/Hong_Kong\",\"years\":{}}",
                "{\"schema\":1,\"source\":\"x\",\"sourceZone\":\"UTC\",\"years\":{\"2026\":{\"qingming\":\"2025-04-05\",\"winter_solstice\":\"2026-12-22\"}}}")){
            boolean rejected=false;try{Hk3SolarCalendar.parse(new StringReader(bad));}catch(RuntimeException expected){rejected=true;}check(rejected,"损坏库不能补猜");
        }
        var q=new HashMap<>(library.facts(LocalDate.of(2026,4,5),hk));q.put("flower","true");q.put("ordinary_ground","true");
        check(rule(372).matches("block_placed",q),"清明普通地面种花");q.put("ordinary_ground","false");check(!rule(372).matches("block_placed",q),"石台和盆栽不能替代");
        check(rule(377).matches("slept",library.facts(LocalDate.of(2026,12,22),hk)),"冬至入睡条件");
        check(!rule(377).matches("clock",library.facts(LocalDate.of(2026,12,22),hk)),"仅到日期不能入睡");
        check(!rule(380).matches("login",Map.of("anniversary_reached","true")),"普通登录不冒充可信周年入口");
        var birth=Instant.parse("2024-02-29T08:30:15.123456Z");var origin=new Hk3WorldOrigin(birth);
        check(origin.createdAt().equals(Instant.parse("2024-02-29T08:30:15.123Z")),"记录毫秒精度与原生NBT一致");
        check(Hk3WorldOrigin.read(origin.save()).orElseThrow().equals(origin),"创建记录保存重载不漂移");
        var anniversary=Instant.parse("2025-02-28T08:30:15.123Z");
        check(!origin.anniversaryReached(anniversary.minusMillis(1),hk),"未满一年拒绝");
        check(origin.anniversaryReached(anniversary,hk),"闰日按公历plusYears规则");
        check(!origin.anniversaryReached(birth.minusSeconds(1),hk),"未来创建时间不触发");
        var leapSpan=new Hk3WorldOrigin(Instant.parse("2023-03-01T00:00:00Z"));
        check(!leapSpan.anniversaryReached(leapSpan.createdAt().plusSeconds(365L*86400),ZoneId.of("UTC")),"跨闰年365天不等于满公历年");
        var ny=ZoneId.of("America/New_York");var dst=new Hk3WorldOrigin(Instant.parse("2025-03-08T07:30:00Z"));
        var dstAnniversary=dst.createdAt().atZone(ny).plusYears(1).toInstant();
        check(!dst.anniversaryReached(dstAnniversary.minusMillis(1),ny)&&dst.anniversaryReached(dstAnniversary,ny),"按服务端时区跨夏令时周年");
        var saved=origin.save();saved.remove("CreatedAt");check(Hk3WorldOrigin.read(saved).isEmpty(),"缺时间不拿首次加入补填");
        saved=origin.save();saved.putString("CreatedAt","2024-02-29");check(Hk3WorldOrigin.read(saved).isEmpty(),"错误类型不转换");
        saved=origin.save();saved.putLong("CreatedAt",0);check(Hk3WorldOrigin.read(saved).isEmpty(),"零时间不猜测");
        saved=origin.save();saved.putString("Source","LastPlayed");check(Hk3WorldOrigin.read(saved).isEmpty(),"LastPlayed不可替代创建时间");
        saved=origin.save();saved.putInt("Schema",2);check(Hk3WorldOrigin.read(saved).isEmpty(),"未知版本不解读");
        System.out.println("Calendar origin: "+checks+" checks passed; explicit fixed-date tests, not natural-date player acceptance.");
    }
}
