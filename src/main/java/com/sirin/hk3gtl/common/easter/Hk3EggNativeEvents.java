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

/** 【变更记录 #1】2026-10-01 04:08:14（修订128）：删除无；新增服务器每秒时间/真实课题/注视事实；用途：不依赖客户端报完成，不强制加载区块，连续在线与累计在线分开保存。 */
@Mod.EventBusSubscriber(modid="hk3gtl")
/** 【变更记录 #2】2026-10-01 04:09:54（修订128）：删除：旧固定上限或被替代的分支；新增/修改：移除轮询注视授予，服务器日历改为明确配置时区；用途：已审核彩蛋独立执行，不授研究或审查资格。 */
/** 【变更记录 #3】2026-10-01 04:24:23（修订128）：删除：旧固定上限或被替代的分支；新增/修改：定期投递本人真实生产账本，包括本人离线时完成的已归属输出；用途：已审核彩蛋独立执行，不授研究或审查资格。 */
/** 【变更记录 #4】2026-10-01 04:25:20（修订128）：删除：旧固定上限或被替代的分支；新增/修改：世界第0天彩蛋只检查首次加入，不允许以后改dayTime补触发；用途：已审核彩蛋独立执行，不授研究或审查资格。 */
/** 【变更记录 #5】2026-10-01 04:27:55（修订128）：删除：旧固定上限或被替代的分支；新增/修改：跟踪同一实体手机电量，不用不同手机替换来伪装充电；用途：已审核彩蛋独立执行，不授研究或审查资格。 */
/** 【变更记录 #6】2026-10-01 04:43:52（修订128）：删除：旧固定上限或被替代的分支；新增/修改：真实登出时间戳用于7日回归及3日离线阅读；缺历史数据不猜测；用途：已审核彩蛋独立执行，不授研究或审查资格。 */
/** 【变更记录 #7】2026-10-01 05:11:58（修订128）：删除：旧固定上限或被替代的分支；新增/修改：AE与机器访问的三步顺序每次登录重置，不能跨连接拼接；用途：已审核彩蛋独立执行，不授研究或审查资格。 */
/** 【变更记录 #8】2026-11-05 19:08:32（修订210）：删除无；新增登录时只读世界创建记录并接通380；修改无旧触发；用途：只有满公历一年后本人首次成功投递，不猜旧档生日。 */
public final class Hk3EggNativeEvents {
    private Hk3EggNativeEvents(){}
    @SubscribeEvent public static void login(PlayerEvent.PlayerLoggedInEvent e){
        if(e.getEntity() instanceof ServerPlayer p){
            var state=Hk3EggRuntime.state(p);state.putLong("sessionTicks",0);state.remove("aeMachineSequence");
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

// 【变更记录 · 修订161】2026-10-17 14:11:55：本轮仅将活动类名、资源与工业配方引用迁移为长期业务命名；历史备注保留，不代表旧逻辑已全部按现行设计重写。
