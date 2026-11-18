package com.sirin.hk3gtl.common.review;
import java.util.*;
 
public final class Hk3ReviewReadingBarrier {
    private final Set<UUID> confirmed=new HashSet<>();
    public boolean confirm(UUID player,Set<UUID> participants){return participants.contains(player)&&confirmed.add(player);}
    public boolean ready(Set<UUID> participants){return !participants.isEmpty()&&confirmed.containsAll(participants);}
    public void reset(){confirmed.clear();}
}
