package com.sirin.hk3gtl.common.communication;

 
import java.util.*;

 
public final class Hk3ContactSessions {
    public record Preview(UUID token,UUID team,UUID event,String action,int step,long expires){}
    private final Map<UUID,Preview> pending=new HashMap<>();
    public Preview issue(UUID actor,UUID team,UUID event,String action,int step,long now){var p=new Preview(UUID.randomUUID(),team,event,action,step,now+2400);pending.put(actor,p);return p;}
    public Preview consume(UUID actor,UUID token,UUID team,String action,long now){
        var p=pending.get(actor);if(p==null||!p.token.equals(token)||!p.team.equals(team)||!p.action.equals(action)||(now>=p.expires||now<p.expires-2400))return null;
        pending.remove(actor);return p;
    }
    public void clear(UUID actor){pending.remove(actor);}
    public void clear(){pending.clear();}
}
