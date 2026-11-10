package com.sirin.hk3gtl.common.phone;

import java.util.*;
import java.util.concurrent.ConcurrentHashMap;

/** 【变更记录 #1】2026-11-05（修订208）：按本人桌面会话记录连续悬停与实际打开，关闭后不保留临时阅读记录。 */
public final class Hk3PhoneAppHintSessions {
    public static final long READ_TICKS=20, EXPIRE_TICKS=6000, LAUNCH_TICKS=40;
    private final Map<UUID,Session> sessions=new ConcurrentHashMap<>();
    private static final Set<String> APPS=new HashSet<>(Hk3PhoneDesktopOrder.APPS);
    static { APPS.remove("quiet"); }
    private static final class Session {
        final UUID token=UUID.randomUUID();
        final Set<String> read=new HashSet<>();
        final long opened;
        long last, hoverAt, launchAt;
        String hover="", launch="";
        Session(long now){opened=last=now;}
    }
    public UUID open(UUID owner,long now){var s=new Session(now);sessions.put(owner,s);return s.token;}
    private Session active(UUID owner,UUID token,long now){
        var s=sessions.get(owner);
        if(s==null||!s.token.equals(token))return null;
        if(now<s.last||now-s.opened>EXPIRE_TICKS){clear(owner);return null;}
        s.last=now;return s;
    }
    public boolean hover(UUID owner,UUID token,String app,long now){
        var s=active(owner,token,now);if(s==null)return false;
        s.hover="";s.launch="";
        if(app.isEmpty())return true;
        if(!APPS.contains(app))return false;
        s.hover=app;s.hoverAt=now;return true;
    }
    public boolean read(UUID owner,UUID token,String app,long now){
        var s=active(owner,token,now);
        return s!=null&&APPS.contains(app)&&s.hover.equals(app)&&now-s.hoverAt>=READ_TICKS&&s.read.add(app);
    }
    public boolean launch(UUID owner,UUID token,String app,long now){
        var s=active(owner,token,now);if(s==null)return false;
        s.launch="";
        if(s.read.size()<3||!s.read.contains(app))return false;
        s.launch=app;s.launchAt=now;return true;
    }
    public boolean opened(UUID owner,String app,long now){
        var s=sessions.remove(owner);
        return s!=null&&!app.isEmpty()&&s.launch.equals(app)&&now>=s.last&&now-s.opened<=EXPIRE_TICKS&&now-s.launchAt<=LAUNCH_TICKS;
    }
    public void validate(UUID owner,long now,boolean allowed){
        var s=sessions.get(owner);if(s!=null&&(!allowed||now<s.last||now-s.opened>EXPIRE_TICKS))clear(owner);
    }
    public boolean contains(UUID owner){return sessions.containsKey(owner);}
    public void cancel(UUID owner,UUID token,long now){if(active(owner,token,now)!=null)clear(owner);}
    public void clear(UUID owner){sessions.remove(owner);}
    public void clear(){sessions.clear();}
}
