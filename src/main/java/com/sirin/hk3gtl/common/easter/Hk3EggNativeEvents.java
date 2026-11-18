package com.sirin.hk3gtl.common.easter;

import com.sirin.hk3gtl.common.gaze.Hk3GazeManager;
import com.sirin.hk3gtl.common.research.*;
import net.minecraft.server.level.ServerPlayer;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.event.entity.player.PlayerEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import java.time.*;
import java.util.*;

@Mod.EventBusSubscriber(modid="hk3gtl")
public final class Hk3EggNativeEvents {
    private Hk3EggNativeEvents(){}
    @SubscribeEvent public static void login(PlayerEvent.PlayerLoggedInEvent e){
        if(e.getEntity() instanceof ServerPlayer p){
            var state=Hk3EggRuntime.state(p);state.putLong("sessionTicks",0);state.remove("aeMachineSequence");
            Hk3EggResearchScenes.login(p);
            if(com.sirin.hk3gtl.common.dimension.Hk3GraduationData.get(p.serverLevel()).isGraduated(p.getUUID()))
                state.putBoolean("graduatedReturnLogin",true);
            if(!state.getBoolean("loggedBefore")&&p.getStats().getValue(net.minecraft.stats.Stats.CUSTOM.get(net.minecraft.stats.Stats.LEAVE_GAME))==0)clock(p,"first_login");
            long now=System.currentTimeMillis();
            long away=state.contains("lastLogoutMillis")?now-state.getLong("lastLogoutMillis"):0;
            state.putBoolean("awayThreeDays",away>=3L*86400000L);
            if(away>=7L*86400000L)Hk3EggVanilla.caseEvent(p,492);
            state.putBoolean("loggedBefore",true);clock(p,"login");
            var data=p.server.getWorldData();
            if(data instanceof Hk3WorldOriginData origin&&origin.hk3gtl$getWorldOrigin()!=null)
                Hk3EggRuntime.observe(p,"world_anniversary_login",Map.of("anniversary_reached",
                    Boolean.toString(origin.hk3gtl$getWorldOrigin().anniversaryReached(Instant.now(),Hk3EggCalendar.zone()))));
        }
    }
    @SubscribeEvent public static void logout(PlayerEvent.PlayerLoggedOutEvent e){
        if(e.getEntity() instanceof ServerPlayer p)Hk3EggRuntime.state(p).putLong("lastLogoutMillis",System.currentTimeMillis());
    }
    @SubscribeEvent public static void tick(TickEvent.PlayerTickEvent e){
        if(e.phase!=TickEvent.Phase.END||!(e.player instanceof ServerPlayer p)||p.tickCount%20!=0)return;
        var state=Hk3EggRuntime.state(p);
        state.putLong("sessionTicks",add(state.getLong("sessionTicks"),20));
        state.putLong("onlineTicks",add(state.getLong("onlineTicks"),20));
        clock(p,"clock");
        if(com.sirin.hk3gtl.common.phone.Hk3PhoneData.get(p).installed(p.getUUID()))Hk3EggPhone.battery(p);

        // 已批准的研究数量彩蛋只读取正式完成账本，不由材料持有推断。
        if(p.tickCount%100==0){
            Hk3EggProduction.poll(p);
            var data=Hk3ResearchData.get(p);var scope=Hk3ResearchTeams.scope(p.server,p.getUUID());
            long done=Hk3ResearchPlans.all().keySet().stream().filter(id->data.completed(scope,id)).count();
            Hk3EggRuntime.observe(p,"research_count",Map.of("completed",Long.toString(done)));
        }
    }
    private static long add(long value,long increment){return value>Long.MAX_VALUE-increment?Long.MAX_VALUE:Math.max(0,value)+increment;}
    private static void clock(ServerPlayer p,String event){
        var state=Hk3EggRuntime.state(p);
        Hk3EggRuntime.observe(p,event,timeFacts(Hk3EggCalendar.now(),p.server.overworld().getDayTime(),
                state.getLong("sessionTicks"),state.getLong("onlineTicks")));
    }
    public static Map<String,String> timeFacts(LocalDateTime now,long time,long session,long total){
        return Hk3EggRuntime.fields("month",Integer.toString(now.getMonthValue()),"day",Integer.toString(now.getDayOfMonth()),
                "hour",Integer.toString(now.getHour()),"dow",Integer.toString(now.getDayOfWeek().getValue()),
                "game_day",Long.toString(Math.floorDiv(time,24000)),"game_time",Long.toString(Math.floorMod(time,24000)),
                "session_ticks",Long.toString(session),"online_ticks",Long.toString(total));
    }
}

