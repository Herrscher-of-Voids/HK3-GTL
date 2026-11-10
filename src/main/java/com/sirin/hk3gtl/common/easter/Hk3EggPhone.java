package com.sirin.hk3gtl.common.easter;
import com.sirin.hk3gtl.common.phone.*;
import com.sirin.hk3gtl.common.item.Hk3PhoneItem;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.nbt.CompoundTag;
import java.util.*;
/** 【变更记录 #1】2026-10-01 04:27:32（修订128）：删除无；新增手机既有界面操作的事实适配；修改无；用途：仅接受安装且有电的本人操作，状态时间由服务器读取，不将客户端分数或正文当权限。 */
/** 【变更记录 #2】2026-10-01 04:43:52（修订128）：删除：旧固定上限或被替代的分支；新增/修改：儿童节打开既有小游戏时只读服务器日历，不接受分数报告；用途：已审核彩蛋独立执行，不授研究或审查资格。 */
/** 【变更记录 #3】2026-10-01 04:47:12（修订128）：删除：旧固定上限或被替代的分支；新增/修改：下次再做使用审核名称；即死年等待真正手机日期页，不再用文明总览替代；用途：已审核彩蛋独立执行，不授研究或审查资格。 */
/** 【变更记录 #4】2026-10-01 04:48:51（修订128）：删除：旧固定上限或被替代的分支；新增/修改：小游戏操作在手机安装且供电校验后重放，回主页只核对本人本局已结束状态；用途：已审核彩蛋独立执行，不授研究或审查资格。 */
/** 【变更记录 #5】2026-10-01 05:11:58（修订128）：删除：旧固定上限或被替代的分支；新增/修改：机械降神的三项备份清单使用已保存笔记，再打开文明总览；不执行备份或重置；用途：已审核彩蛋独立执行，不授研究或审查资格。 */
/** 【变更记录 #6】2026-10-01 05:36:00（修订128）：删除：旧固定上限或被替代的分支；新增/修改：079笔记打开须先由本人把命名纸实际存入工作台旁箱子；用途：已审核彩蛋独立执行，不授研究或审查资格。 */
/** 【变更记录 #7】2026-10-01 05:56:06（修订128）：删除：无；新增/修改：只在真开关手机时通知环境检测，回到主页不冒充重新打开；用途：已审核彩蛋独立执行，不授研究或审查资格。 */
/** 【变更记录 #8】2026-10-01 06:19:47（修订128）：删除：无；新增/修改：文明总览核对真实传送落点后的连续14至15格步行；用途：已审核彩蛋独立执行，不授研究或审查资格。 */
public final class Hk3EggPhone {
    /** 【变更记录 #9】2026-11-05（修订206）：开机与有效关闭通知个人待办日历会话；重复关闭不观察，导航不冒充新会话。 */
    private static final Set<String> LOCAL=Set.of("home","settings","notification_settings","gaze_settings","about","trade","tiles2048","snake","note","draft_exit","social_ai");
    private Hk3EggPhone(){}
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
