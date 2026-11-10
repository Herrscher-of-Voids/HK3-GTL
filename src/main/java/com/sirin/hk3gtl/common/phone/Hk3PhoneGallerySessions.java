package com.sirin.hk3gtl.common.phone;

import java.util.UUID;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;

/** 【变更记录 #1】2026-11-05（修订209）：只保存本人相册短期会话；服务端单调时钟计时，失去连续可见回执即作废。 */
public final class Hk3PhoneGallerySessions {
    public static final long READ_MS=30_000, GAP_MS=5_000;
    private final Map<UUID,Session> sessions=new ConcurrentHashMap<>();
    private static final class Session {
        final UUID token=UUID.randomUUID();
        long start,last;
        boolean visible;
        Session(long now){start=last=now;}
    }
    public UUID open(UUID owner,long now){var s=new Session(now);sessions.put(owner,s);return s.token;}
    private Session active(UUID owner,UUID token,long now){
        var s=sessions.get(owner);
        if(s==null||!s.token.equals(token))return null;
        if(now<s.last||now-s.last>GAP_MS){clear(owner);return null;}
        return s;
    }
    public boolean pulse(UUID owner,UUID token,long now){
        var s=active(owner,token,now);if(s==null)return false;
        if(!s.visible){s.visible=true;s.start=now;}
        s.last=now;return true;
    }
    public boolean close(UUID owner,UUID token,long now){
        var s=active(owner,token,now);if(s==null)return false;
        clear(owner);return s.visible&&now-s.start>=READ_MS;
    }
    public void cancel(UUID owner,UUID token){var s=sessions.get(owner);if(s!=null&&s.token.equals(token))clear(owner);}
    public void validate(UUID owner,long now,boolean available){
        var s=sessions.get(owner);if(s!=null&&(!available||now<s.last||now-s.last>GAP_MS))clear(owner);
    }
    public boolean contains(UUID owner){return sessions.containsKey(owner);}
    public void clear(UUID owner){sessions.remove(owner);}
    public void clear(){sessions.clear();}
}
