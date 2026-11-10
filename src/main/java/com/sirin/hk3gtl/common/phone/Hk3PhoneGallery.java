package com.sirin.hk3gtl.common.phone;

import com.sirin.hk3gtl.common.easter.Hk3EggPhone;
import com.sirin.hk3gtl.common.easter.Hk3EggRuntime;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.server.level.ServerPlayer;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.event.entity.player.PlayerEvent;
import net.minecraftforge.event.server.ServerStoppedEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import java.util.*;

/** 【变更记录 #1】2026-11-05（修订209）：新增带电风景相册与本人手动关闭回执；不读截图文件，不授研究、物品或截图权限。 */
@Mod.EventBusSubscriber(modid="hk3gtl")
public final class Hk3PhoneGallery {
    private static final Hk3PhoneGallerySessions SESSIONS=new Hk3PhoneGallerySessions();
    private Hk3PhoneGallery(){}
    private static long now(){return System.nanoTime()/1_000_000L;}
    private static boolean available(ServerPlayer p){return Hk3PhoneData.get(p).installed(p.getUUID())&&Hk3PhoneRuntime.powered(p);}
    private static boolean viewing(ServerPlayer p){var s=Hk3EggRuntime.state(p);return available(p)&&s.getBoolean("phoneOpen")&&s.getString("phoneMode").equals("gallery");}
    public static int open(ServerPlayer p){
        if(!available(p))return 0;
        Hk3EggPhone.opened(p,"gallery");
        var view=new CompoundTag();view.putString("Mode","gallery");view.putUUID("GalleryToken",SESSIONS.open(p.getUUID(),now()));
        Hk3PhoneService.send(p,view);return 1;
    }
    public static void view(ServerPlayer p,CompoundTag view){
        if(!Set.of("gallery","status","toast","read_complete","note_saved","app_error").contains(view.getString("Mode")))clear(p);
    }
    public static void input(ServerPlayer p,String action,String value){
        UUID token;try{token=UUID.fromString(value);}catch(IllegalArgumentException bad){return;}
        if(action.equals("gallery_cancel")){SESSIONS.cancel(p.getUUID(),token);return;}
        if(!viewing(p)){clear(p);return;}
        if(action.equals("gallery_pulse"))SESSIONS.pulse(p.getUUID(),token,now());
        else if(action.equals("gallery_close")&&SESSIONS.close(p.getUUID(),token,now()))
            Hk3EggRuntime.observe(p,"phone_gallery_closed",Map.of("thirty_seconds","true"));
    }
    public static void navigation(ServerPlayer p,String mode){if(!mode.equals("gallery"))clear(p);}
    public static void clear(ServerPlayer p){SESSIONS.clear(p.getUUID());}
    @SubscribeEvent public static void tick(TickEvent.PlayerTickEvent e){
        if(e.phase==TickEvent.Phase.END&&e.player instanceof ServerPlayer p&&SESSIONS.contains(p.getUUID()))SESSIONS.validate(p.getUUID(),now(),viewing(p));
    }
    @SubscribeEvent public static void logout(PlayerEvent.PlayerLoggedOutEvent e){SESSIONS.clear(e.getEntity().getUUID());}
    @SubscribeEvent public static void stop(ServerStoppedEvent e){SESSIONS.clear();}
}
