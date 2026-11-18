package com.sirin.hk3gtl.common.easter;
import com.sirin.hk3gtl.common.phone.*;
import com.sirin.hk3gtl.common.item.Hk3PhoneItem;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.nbt.CompoundTag;
import java.util.*;








public final class Hk3EggPhone {

    private static final Set<String> LOCAL=Set.of("home","settings","notification_settings","gaze_settings","about","trade","tiles2048","snake","note","draft_exit","social_ai");
    private Hk3EggPhone(){}
    public static void finaleInspection(ServerPlayer p){
        if(p.getMainHandItem().is(net.minecraft.world.item.Items.DIAMOND)||p.getOffhandItem().is(net.minecraft.world.item.Items.DIAMOND))Hk3EggVanilla.caseEvent(p,99);
    }
    public static void opened(ServerPlayer p,String mode){
        Hk3PhoneGallery.navigation(p,mode);
        Hk3PhoneAppHints.opened(p,mode);
        Hk3PhoneTodoCalendar.phoneOpened(p);
        var state=Hk3EggRuntime.state(p);long tick=p.server.overworld().getGameTime();
        if(!state.getBoolean("phoneOpen"))Hk3EggPhoneWeather.opened(p);
        if(mode.equals("home")||!state.getBoolean("phoneOpen")){state.putBoolean("phoneOpen",true);state.putLong("phoneOpenedTick",tick);}
        if(mode.equals("home"))Hk3EggGames.home(p);
        state.putString("phoneMode",mode);if(mode.equals("notes")&&!state.contains("notesOpenedTick"))state.putLong("notesOpenedTick",tick);
        var f=new LinkedHashMap<>(Hk3EggVanilla.withTime(p,"mode",mode));
        f.put("daylight",Boolean.toString(p.level().isDay()));
        f.put("raining",Boolean.toString(p.level().isRaining()));
        long day=Math.floorMod(p.server.overworld().getDayTime(),24000);f.put("palindrome_time",Boolean.toString(day>=6350&&day<6367));
        if(mode.equals("tiles2048")||mode.equals("snake")){
            var calendarDay=Hk3EggCalendar.now();if(calendarDay.getMonthValue()==6&&calendarDay.getDayOfMonth()==1)Hk3EggVanilla.caseEvent(p,354);
        }
        if(mode.equals("notes")&&state.getBoolean("079StoredAtWorkbench"))Hk3EggVanilla.caseEvent(p,392);
        if(mode.equals("home")){battery(p);f.put("recharged",Boolean.toString(state.getBoolean("phoneRecharged")));}
        if(mode.equals("civilization"))Hk3EggPersonalScenes.civilization(p);
        if(mode.equals("civilization")&&state.getString("lastNoteTitle").equals("机械降神")&&state.getString("lastNoteBody").lines().filter(line->line.strip().matches("[1-9][.、)）].{3,}")).count()>=3)Hk3EggVanilla.caseEvent(p,399);
        Hk3EggRuntime.observe(p,"phone_open",f);
    }
    public static void input(ServerPlayer p,String action,String value){
        if(action.startsWith("gallery_")){Hk3PhoneGallery.input(p,action,value);return;}
        if(action.startsWith("app_hint_")){Hk3PhoneAppHints.input(p,action,value);return;}
        if(!Hk3PhoneData.get(p).installed(p.getUUID()))return;
        var s=Hk3EggRuntime.state(p);
        if(action.equals("close")){
            Hk3PhoneGallery.clear(p);
            Hk3PhoneAppHints.clear(p);
            if(!s.getBoolean("phoneOpen"))return;s.putBoolean("phoneOpen",false);Hk3EggPhoneWeather.closed(p);
            Hk3PhoneTodoCalendar.phoneClosed(p);
            var f=new LinkedHashMap<>(Hk3EggVanilla.withTime(p,"mode",s.getString("phoneMode")));
            boolean saved=s.getLong("lastNoteTick")>=s.getLong("phoneOpenedTick");
            f.put("infinity_note",Boolean.toString(saved&&s.getString("lastNoteBody").contains("∞")));
            f.put("later_note",Boolean.toString(saved&&s.getString("lastNoteTitle").equals("下次再做")));
            f.put("notes_elapsed",Long.toString(s.contains("notesOpenedTick")?Math.max(0,p.server.overworld().getGameTime()-s.getLong("notesOpenedTick")):0));
            Hk3EggRuntime.observe(p,"phone_closed",f);s.remove("notesOpenedTick");return;
        }
        if(!Hk3PhoneRuntime.powered(p))return;
        if(action.startsWith("tiles_")||action.startsWith("snake_")){Hk3EggGames.input(p,action,value);return;}
        if(action.equals("open")&&LOCAL.contains(value)){opened(p,value);return;}
        if(action.equals("layout")){
            var order=List.of(value.split(",",-1));
            if(order.size()!=Hk3PhoneDesktopOrder.APPS.size()||!new HashSet<>(order).equals(new HashSet<>(Hk3PhoneDesktopOrder.APPS))||order.equals(Hk3PhoneDesktopOrder.APPS))return;
            s.putBoolean("desktopMoved",true);Hk3EggRuntime.observe(p,"phone_layout",Map.of("valid","true"));
        }else if(action.equals("notification_position")){
            String[] parts=value.split(",",-1);if(parts.length!=2)return;
            try{double x=Double.parseDouble(parts[0]),y=Double.parseDouble(parts[1]);if(!Double.isFinite(x)||!Double.isFinite(y)||x<0||x>1||y<0||y>1)return;
                Hk3EggRuntime.observe(p,"phone_position",Map.of("valid","true"));
            }catch(NumberFormatException bad){return;}
        }
    }
    public static void battery(ServerPlayer p){
        var phone=Hk3PhoneRuntime.phone(p);if(phone.isEmpty())return;
        var tag=phone.getOrCreateTag();if(!tag.hasUUID("Hk3EggBatteryId"))tag.putUUID("Hk3EggBatteryId",UUID.randomUUID());
        var state=Hk3EggRuntime.state(p);UUID id=tag.getUUID("Hk3EggBatteryId");long charge=Hk3PhoneItem.charge(phone);
        if(charge<Hk3PhoneItem.CAPACITY/10){state.putUUID("lowPhone",id);state.putBoolean("phoneRecharged",false);}
        if(state.hasUUID("lowPhone")&&state.getUUID("lowPhone").equals(id)&&charge>=Hk3PhoneItem.CAPACITY*8/10)state.putBoolean("phoneRecharged",true);
        if(state.hasUUID("lastPhone")&&state.getUUID("lastPhone").equals(id)&&state.getLong("lastCharge")<Hk3PhoneItem.CAPACITY&&charge==Hk3PhoneItem.CAPACITY)Hk3EggRuntime.observe(p,"phone_charged",Map.of("full","true"));
        state.putUUID("lastPhone",id);state.putLong("lastCharge",charge);
    }
}
