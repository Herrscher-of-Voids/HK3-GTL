package com.sirin.hk3gtl.common.communication;

/** 【变更记录 #2】2026-10-01 00:00:53（修订121）：删除无；新增/修改：预览时限边界及游戏时钟回退拒绝提交；用途：个人与团队记录隔离，保留历史与权限。 */
import java.util.*;

/** 【变更记录 #1】2026-09-30 23:58:50（修订121）：删除旧个人答复自动代表新队的生产路径；新增/修改：每位在线玩家最多一份两分钟预览令牌，绑定团队与事件；退出清理，不存API凭证；用途：团队外交、阅读与个人经历分账，不发研究或物品奖励。 */
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
