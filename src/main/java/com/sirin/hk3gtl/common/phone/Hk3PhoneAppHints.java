package com.sirin.hk3gtl.common.phone;

import com.sirin.hk3gtl.common.easter.Hk3EggRuntime;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.server.level.ServerPlayer;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.event.entity.player.PlayerEvent;
import net.minecraftforge.event.server.ServerStoppedEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import java.util.*;

/** 【变更记录 #1】2026-11-05（修订208）：手机说明回执仅使用本人带电桌面的短期令牌；实际入口成功后才观察490，不授研究或工业资格。 */
@Mod.EventBusSubscriber(modid="hk3gtl")
public final class Hk3PhoneAppHints {
    private static final Hk3PhoneAppHintSessions SESSIONS=new Hk3PhoneAppHintSessions();
    private Hk3PhoneAppHints(){}
    private static long now(ServerPlayer p){return p.server.overworld().getGameTime();}
    private static boolean available(ServerPlayer p){return Hk3PhoneData.get(p).installed(p.getUUID())&&Hk3PhoneRuntime.powered(p);}
    private static boolean desktop(ServerPlayer p){var s=Hk3EggRuntime.state(p);return available(p)&&s.getBoolean("phoneOpen")&&s.getString("phoneMode").equals("home");}
    public static void view(ServerPlayer p,CompoundTag view){
        String mode=view.getString("Mode");
        if(mode.equals("home")){
            if(available(p))view.putUUID("AppHintToken",SESSIONS.open(p.getUUID(),now(p)));else clear(p);
        }else if(!Set.of("status","toast","read_complete","note_saved","app_error").contains(mode))opened(p,mode);
    }
    public static void input(ServerPlayer p,String action,String value){
        if(!desktop(p)){clear(p);return;}
        String[] parts=value.split(",",-1);if(parts.length!=2)return;
        UUID token;try{token=UUID.fromString(parts[0]);}catch(IllegalArgumentException bad){return;}
        switch(action){
            case "app_hint_hover"->SESSIONS.hover(p.getUUID(),token,parts[1],now(p));
            case "app_hint_read"->SESSIONS.read(p.getUUID(),token,parts[1],now(p));
            case "app_hint_launch"->SESSIONS.launch(p.getUUID(),token,parts[1],now(p));
            case "app_hint_cancel"->SESSIONS.cancel(p.getUUID(),token,now(p));
            default->{ }
        }
    }
    public static void opened(ServerPlayer p,String mode){
        if(mode.equals("home"))return;
        String app=switch(mode){
            case "notifications"->"inbox";case "diplomacy"->"letters";case "ae_terminals","ae"->"ae";
            case "social"->"social";case "notes","civilization","settings","trade","tiles2048","snake","updates"->mode;
            default->"";
        };
        if(available(p)&&SESSIONS.opened(p.getUUID(),app,now(p)))Hk3EggRuntime.observe(p,"phone_app_hints_open",Map.of("three_read","true"));
        else clear(p);
    }
    public static void clear(ServerPlayer p){SESSIONS.clear(p.getUUID());}
    @SubscribeEvent public static void tick(TickEvent.PlayerTickEvent e){
        if(e.phase==TickEvent.Phase.END&&e.player instanceof ServerPlayer p&&SESSIONS.contains(p.getUUID()))SESSIONS.validate(p.getUUID(),now(p),desktop(p));
    }
    @SubscribeEvent public static void logout(PlayerEvent.PlayerLoggedOutEvent e){SESSIONS.clear(e.getEntity().getUUID());}
    @SubscribeEvent public static void stop(ServerStoppedEvent e){SESSIONS.clear();}
}
