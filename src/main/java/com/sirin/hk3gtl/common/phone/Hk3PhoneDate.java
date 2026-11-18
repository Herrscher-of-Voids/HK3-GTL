package com.sirin.hk3gtl.common.phone;

import java.util.Locale;





public final class Hk3PhoneDate {
    private Hk3PhoneDate() {}
    public record Snapshot(long day, long tick, String clock) {}
    public static Snapshot from(long dayTime) {
        long tick=Math.floorMod(dayTime,24000);
        long minutes=((tick+6000)%24000)*1440/24000;
        return new Snapshot(Math.floorDiv(dayTime,24000)+1,tick,String.format(Locale.ROOT,"%02d:%02d",minutes/60,minutes%60));
    }
}
