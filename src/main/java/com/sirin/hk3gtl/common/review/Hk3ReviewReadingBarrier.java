package com.sirin.hk3gtl.common.review;
import java.util.*;
/** 【变更记录 #1】2026-10-01 18:42:57（修订140）：删除无；新增一审每段在场者阅读屏障；修改离场者不阻塞、重复确认不叠加；用途：代表推进不能替他人确认阅读，重开必须重读。 */
public final class Hk3ReviewReadingBarrier {
    private final Set<UUID> confirmed=new HashSet<>();
    public boolean confirm(UUID player,Set<UUID> participants){return participants.contains(player)&&confirmed.add(player);}
    public boolean ready(Set<UUID> participants){return !participants.isEmpty()&&confirmed.containsAll(participants);}
    public void reset(){confirmed.clear();}
}
