package com.sirin.hk3gtl.common.phone;

import java.time.DayOfWeek;
import java.time.LocalDateTime;
import java.util.HashMap;
import java.util.Map;
import java.util.UUID;

 
public final class Hk3TodoCalendarSessions {
    private static final class Session {
        LocalDateTime last,completed;
        Session(LocalDateTime now){last=now;}
        void advance(LocalDateTime now){
            if(now.isBefore(last)||!now.toLocalDate().equals(last.toLocalDate()))completed=null;
            last=now;
        }
    }
    private final Map<UUID,Session> sessions=new HashMap<>();
    public void opened(UUID owner,LocalDateTime now){sessions.computeIfAbsent(owner,id->new Session(now)).advance(now);}
    public boolean todoOpened(UUID owner,LocalDateTime now){opened(owner,now);return now.getDayOfWeek()==DayOfWeek.MONDAY;}
    public void completed(UUID owner,LocalDateTime now){
        var session=sessions.get(owner);if(session==null)return;
        session.advance(now);session.completed=now.getDayOfWeek()==DayOfWeek.FRIDAY?now:null;
    }
    public boolean closed(UUID owner,LocalDateTime now){
        var session=sessions.remove(owner);
        return session!=null&&session.completed!=null&&!now.isBefore(session.last)
            &&now.getDayOfWeek()==DayOfWeek.FRIDAY&&now.toLocalDate().equals(session.completed.toLocalDate());
    }
    public void clear(UUID owner){sessions.remove(owner);}
    public void clear(){sessions.clear();}
}
