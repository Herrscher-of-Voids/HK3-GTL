package com.sirin.hk3gtl.common.phone;

import java.util.Locale;

/**
 * 手机日期页的只读游戏日历，输入为服务器主世界dayTime，不读取现实日期。
 */
public final class Hk3PhoneDate {
    private Hk3PhoneDate() {}
    public record Snapshot(long day, long tick, String clock) {}
    public static Snapshot from(long dayTime) {
        long tick=Math.floorMod(dayTime,24000);
        long minutes=((tick+6000)%24000)*1440/24000;
        return new Snapshot(Math.floorDiv(dayTime,24000)+1,tick,String.format(Locale.ROOT,"%02d:%02d",minutes/60,minutes%60));
    }
}
