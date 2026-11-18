package com.sirin.hk3gtl.common.easter;
import net.minecraftforge.common.ForgeConfigSpec;
import java.time.*;
import java.util.*;
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
