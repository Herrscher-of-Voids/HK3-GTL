package com.sirin.hk3gtl.common.phone;

import com.sirin.hk3gtl.common.easter.Hk3EggCalendar;
import com.sirin.hk3gtl.common.easter.Hk3EggRuntime;
import net.minecraft.server.level.ServerPlayer;
import net.minecraftforge.event.entity.player.PlayerEvent;
import net.minecraftforge.event.server.ServerStoppedEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;

/** 【变更记录 #1】2026-11-05（修订206）：日历只读服务器配置时区；真实待办页、成功勾选和手机关闭回调接入378/379，客户端不能申报日期或完成事实。 */
@Mod.EventBusSubscriber(modid="hk3gtl")
public final class Hk3PhoneTodoCalendar {
    private static final Hk3TodoCalendarSessions SESSIONS=new Hk3TodoCalendarSessions();
    private Hk3PhoneTodoCalendar(){}
    public static void phoneOpened(ServerPlayer p){
        if(Hk3PhoneData.get(p).installed(p.getUUID())&&Hk3PhoneRuntime.powered(p))SESSIONS.opened(p.getUUID(),Hk3EggCalendar.now());
    }
    static void todoOpened(ServerPlayer p){
        boolean monday=SESSIONS.todoOpened(p.getUUID(),Hk3EggCalendar.now());
        Hk3EggRuntime.observe(p,"notebook_calendar_open",Hk3EggRuntime.fields("monday",Boolean.toString(monday)));
    }
    static void completed(ServerPlayer p){
        if(Hk3EggRuntime.state(p).getBoolean("phoneOpen"))SESSIONS.completed(p.getUUID(),Hk3EggCalendar.now());
    }
    public static void phoneClosed(ServerPlayer p){
        boolean friday=SESSIONS.closed(p.getUUID(),Hk3EggCalendar.now());
        Hk3EggRuntime.observe(p,"notebook_calendar_close",Hk3EggRuntime.fields("friday_completed",Boolean.toString(friday)));
    }
    @SubscribeEvent public static void logout(PlayerEvent.PlayerLoggedOutEvent event){SESSIONS.clear(event.getEntity().getUUID());}
    @SubscribeEvent public static void stop(ServerStoppedEvent event){SESSIONS.clear();}
}
