package com.sirin.hk3gtl.common.event;
import java.time.*;
import java.util.*;
 
public final class Hk3EasterEggClock {
    private Hk3EasterEggClock(){}
    public static List<Integer> events(LocalDateTime real,long worldTime){
        var ids=new ArrayList<Integer>();int hour=real.getHour();
        if(hour==3)ids.add(53);
        long time=Math.floorMod(worldTime,24000L),day=Math.floorDiv(worldTime,24000L);
        if(time>=6000&&time<=6100)ids.add(70);
        if(day==0)ids.add(55);else if(day==100)ids.add(56);else if(day==365)ids.add(57);
        int month=real.getMonthValue(),date=real.getDayOfMonth();
        if(month==4&&date==1)ids.add(51);if(month==12&&date==25)ids.add(52);
        if(month==2&&date==14)ids.add(58);if(month==10&&date==1)ids.add(59);
        if(real.getDayOfWeek()==DayOfWeek.SUNDAY&&hour<6)ids.add(60);
        return List.copyOf(ids);
    }
    public static boolean restDue(long sessionTicks){return sessionTicks>=6L*60*60*20;}
}
