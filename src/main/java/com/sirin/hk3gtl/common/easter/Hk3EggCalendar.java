package com.sirin.hk3gtl.common.easter;
import net.minecraftforge.common.ForgeConfigSpec;
import java.time.*;
import java.util.*;
/** 【变更记录 #1】2026-10-01 04:12:10（修订128）：删除无；新增可配置服务器时区与纯公历事实；修改无；用途：单人及专服同源日历，不猜农历。 */
public final class Hk3EggCalendar {
    public static final ForgeConfigSpec SPEC;
    public static final ForgeConfigSpec.ConfigValue<String> TIME_ZONE;
    static {
        var b=new ForgeConfigSpec.Builder();
        TIME_ZONE=b.comment("彩蛋日历时区；使用 IANA 时区名称，不跟随玩家电脑。")
            .define("timeZone","Asia/Hong_Kong",v->{try{ZoneId.of(String.valueOf(v));return true;}catch(DateTimeException e){return false;}});
        SPEC=b.build();
    }
    private Hk3EggCalendar(){}
    /** 【变更记录 #2】2026-11-05 19:08:32（修订210）：删除无；新增逐年节气事实；修改统一时区读取；用途：缺来源不推算清明和冬至。 */
    /** 【变更记录 #3】2026-11-05 21:56:28（修订211）：删除无；新增有来源农历节日事实；修改既有事件合并年度库；用途：不猜农历、不新增手机或配置。 */
    public static ZoneId zone(){return ZoneId.of(TIME_ZONE.get());}
    public static LocalDateTime now(){return LocalDateTime.now(zone());}
    public static Map<String,String> facts(LocalDateTime t,long gameTime){
        var f=new LinkedHashMap<>(Hk3EggNativeEvents.timeFacts(t,gameTime,0,0));
        f.put("week",Integer.toString((t.getDayOfMonth()-1)/7+1));
        f.put("night",Boolean.toString(Math.floorMod(gameTime,24000)>=13000));
        f.putAll(Hk3SolarCalendar.facts(t.toLocalDate(),zone()));
        f.putAll(Hk3LunarCalendar.facts(t.toLocalDate(),zone()));
        return f;
    }
}
