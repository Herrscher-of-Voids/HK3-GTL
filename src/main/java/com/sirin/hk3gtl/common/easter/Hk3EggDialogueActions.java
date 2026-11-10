package com.sirin.hk3gtl.common.easter;
import com.sirin.hk3gtl.common.dialogue.*;
import com.sirin.hk3gtl.common.dialogue.definition.SirinDialogueDefinitions;
import net.minecraft.server.level.ServerPlayer;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.event.entity.player.PlayerEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import java.util.*;
/** 【变更记录 #1】2026-10-01 05:33:27（修订128）：删除无；新增当前终审节点等待与输入节奏观察；修改无；用途：会话身份、节点、在线状态由服务器校验，关闭/换段释放，不替玩家选择或结算。 */
@Mod.EventBusSubscriber(modid="hk3gtl")
public final class Hk3EggDialogueActions {
    private static final class Page {
        final DialogueSessionManager.DialogueSession session;long since,lastSeen,lastInputTick;int inputsThisTick;String lastInput="";boolean choice;
        final ArrayDeque<Long> presses=new ArrayDeque<>();
        Page(DialogueSessionManager.DialogueSession session,long now){this.session=session;since=now;lastSeen=now;}
    }
    private static final Map<UUID,Page> ACTIVE=new java.util.concurrent.ConcurrentHashMap<>();
    private Hk3EggDialogueActions(){}
    public static void input(ServerPlayer p,String payload){
        String[] parts=payload.split("\\|",-1);if(parts.length!=3)return;
        var session=DialogueSessionManager.getSession(p.getUUID());
        if(session==null||!session.dialogueId().equals(SirinDialogueDefinitions.DIALOGUE_ID)||!session.dialogueId().equals(parts[1])||!session.currentSegmentId().equals(parts[2]))return;
        if(parts[0].equals("close")){ACTIVE.remove(p.getUUID());return;}
        long now=p.server.overworld().getGameTime();var page=ACTIVE.get(p.getUUID());
        if(page==null||page.session!=session){page=new Page(session,now);ACTIVE.put(p.getUUID(),page);}
        if(now!=page.lastInputTick){page.inputsThisTick=0;page.lastInputTick=now;}if(++page.inputsThisTick>32)return;
        if(parts[0].equals("choice")){
            var definition=DialogueRegistry.getDialogue(session.dialogueId());
            if(definition==null||definition.segments().getOrDefault(session.currentSegmentId(),List.of()).stream().noneMatch(l->l.choices()!=null&&!l.choices().isEmpty()))return;
            if(!page.choice||now-page.lastSeen>40)page.since=now;page.choice=true;page.lastSeen=now;
        }else if(parts[0].matches("press_[mk][0-9]{1,3}")){
            if(!parts[0].equals(page.lastInput))page.presses.clear();page.lastInput=parts[0];
            while(!page.presses.isEmpty()&&now-page.presses.peekFirst()>40)page.presses.removeFirst();
            if(page.presses.size()<8)page.presses.addLast(now);
            if(page.presses.size()==8)Hk3EggVanilla.caseEvent(p,74);
        }
    }
    @SubscribeEvent public static void tick(TickEvent.PlayerTickEvent e){
        if(e.phase!=TickEvent.Phase.END||!(e.player instanceof ServerPlayer p))return;var page=ACTIVE.get(p.getUUID());if(page==null)return;
        long now=p.server.overworld().getGameTime();
        if(DialogueSessionManager.getSession(p.getUUID())!=page.session||now<page.since){ACTIVE.remove(p.getUUID());return;}
        if(page.choice&&now-page.lastSeen>40){page.choice=false;page.since=now;}
        if(page.choice&&now-page.since>=1200)Hk3EggVanilla.caseEvent(p,23);
    }
    @SubscribeEvent public static void logout(PlayerEvent.PlayerLoggedOutEvent e){ACTIVE.remove(e.getEntity().getUUID());}
    @SubscribeEvent public static void stop(net.minecraftforge.event.server.ServerStoppedEvent e){ACTIVE.clear();}
}
