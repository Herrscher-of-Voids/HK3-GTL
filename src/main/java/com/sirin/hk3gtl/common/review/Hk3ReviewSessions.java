package com.sirin.hk3gtl.common.review;


import com.sirin.hk3gtl.common.dialogue.DialogueRegistry;
import com.sirin.hk3gtl.common.dialogue.DialogueSessionManager;
import com.sirin.hk3gtl.common.network.*;
import com.sirin.hk3gtl.common.research.Hk3ResearchTeams;
import net.minecraft.network.chat.ClickEvent;
import net.minecraft.network.chat.Component;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.level.ServerPlayer;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.event.entity.player.PlayerEvent;
import net.minecraftforge.event.server.ServerStoppedEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import net.minecraftforge.network.PacketDistributor;
import java.util.*;

/**
 * 【变更记录 #1】2026-10-01 18:42:57（修订140）
 * 删除：无；新增：真实准入至正式会面、三问代表同步、二审合法分支、个人补行和返回调度。
 * 修改：复用持久审查账本，每页令牌只可消费一次；重播保留题序，暂停不结算，正文预览不授许可。
 * 用途：服务端主线程闭合审查流程；特效使用独立场景适配器，资格仍由真实生产者提供。
 */
@Mod.EventBusSubscriber(modid="hk3gtl")
/** 【变更记录 #2】2026-10-01 18:51:55（修订140）：删除无；新增已完成成员只读陪同；修改旁观不参与三问、阅读屏障和许可，结束或中止统一送返；用途：多人规则与本人亲历保持隔离。 */
/** 【变更记录 #3】2026-10-01 18:54:07（修订140）：删除旧页面关闭一概拒绝的时序死等；新增32页有界暂停窗口；修改关闭帧与停服清理同步销毁窗口；用途：ESC与组播交错可退出，旧选择和旧会面仍拒绝。 */
/** 【变更记录 #4】2026-11-04 18:48:13（修订199）：删除：仅一审核验维度的选择前置；新增：两审共用场景存活校验及关闭时释放临时锚点；修改：失效投影不能在轮询前继续结算；用途：阻断跨场景迟到选择，断线返程仍保留持久票据。 */
/** 【变更记录 #5】2026-11-05 22:19:02（修订211）：新增合法两问关闭、代表重连重播确认题及已完成成员陪同至会面结算的169至171事实；修改不改变会面资格、题序、令牌及结算规则。 */
public final class Hk3ReviewSessions {
    private static final org.slf4j.Logger LOGGER=com.mojang.logging.LogUtils.getLogger();
    private static final Map<UUID,Hk3ReviewFrame> FRAMES=new HashMap<>();
    private static final Map<UUID,Hk3ReviewPageWindow> PAGES=new HashMap<>();
    private static final Map<UUID,Hk3ReviewReadingBarrier> BARRIERS=new HashMap<>();
    private static final Set<String> INVITED=new HashSet<>();
    private static final Set<UUID> OBSERVERS=new HashSet<>();
    private Hk3ReviewSessions(){}
    public static boolean active(UUID player){return FRAMES.containsKey(player);}
    private static Hk3ReviewLedger.Snapshot meeting(ServerPlayer p){var f=FRAMES.get(p.getUUID());return f==null?null:Hk3ReviewData.get(p.server).snapshot().meeting(f.meeting());}
    private static boolean available(ServerPlayer p){
        return p.isAlive()&&!p.isSpectator()&&!p.isSleeping()&&!p.isPassenger()&&p.containerMenu==p.inventoryMenu&&!DialogueSessionManager.hasActiveDialogue(p.getUUID())&&Hk3ReviewReturnData.get(p.server).point(p.getUUID())==null;
    }
    private static void message(ServerPlayer p,String key){p.sendSystemMessage(Component.translatable("hk3gtl.review."+key));}
    public static int watch(ServerPlayer p){
        if(!available(p)){message(p,"busy");return 0;}
        var scope=Hk3ResearchTeams.scope(p.server,p.getUUID());var ledger=Hk3ReviewData.get(p.server).snapshot();
        if(!ledger.experienced(p.getUUID(),Hk3ReviewLedger.Kind.FIRST)){message(p,"missing");return 0;}
        var m=ledger.sessions(scope).stream().filter(s->s.kind()==Hk3ReviewLedger.Kind.FIRST&&s.phase()!=Hk3ReviewLedger.Phase.PAUSED&&s.phase()!=Hk3ReviewLedger.Phase.COMPLETE&&s.phase()!=Hk3ReviewLedger.Phase.ABANDONED&&FRAMES.values().stream().anyMatch(f->f.meeting().equals(s.id()))).findFirst().orElse(null);
        if(m==null){message(p,"busy");return 0;}
        OBSERVERS.add(p.getUUID());FRAMES.put(p.getUUID(),Hk3ReviewFrame.issue(m.id(),scope,Hk3ReviewDialogues.FIRST,""));
        try{Hk3ReviewScene.accompany(p,m);show(p,m,firstSegment(m,p.getUUID()),true);return 1;}
        catch(RuntimeException failure){LOGGER.warn("[HK3GTL] 一审陪同未进入",failure);pause(p,false,false);return 0;}
    }
    public static int begin(ServerPlayer p,Hk3ReviewLedger.Kind kind){
        if(!available(p)){message(p,"busy");return 0;}
        var scope=Hk3ResearchTeams.scope(p.server,p.getUUID());Hk3ReviewQualification.refresh(p.server,scope);
        var data=Hk3ReviewData.get(p.server);var ledger=data.snapshot();
        if(!ledger.qualified(scope,kind)||kind==Hk3ReviewLedger.Kind.SECOND&&!ledger.experienced(p.getUUID(),Hk3ReviewLedger.Kind.FIRST)){message(p,"missing");return 0;}
        if(ledger.experienced(p.getUUID(),kind)){message(p,"already");return 0;}
        if(kind==Hk3ReviewLedger.Kind.FIRST&&!Hk3ReviewScene.available(p)){message(p,"no_scene");return 0;}
        var paused=ledger.sessions(scope).stream().filter(m->m.kind()==kind&&m.phase()==Hk3ReviewLedger.Phase.PAUSED&&(kind==Hk3ReviewLedger.Kind.FIRST||m.representative().equals(p.getUUID()))).findFirst().orElse(null);
        var members=kind==Hk3ReviewLedger.Kind.FIRST?p.server.getPlayerList().getPlayers().stream().filter(q->scope.equals(Hk3ResearchTeams.scope(p.server,q.getUUID()))&&available(q)&&!ledger.experienced(q.getUUID(),kind)).map(ServerPlayer::getUUID).toList():List.of(p.getUUID());
        var m=data.change(l->kind==Hk3ReviewLedger.Kind.FIRST?(paused==null?l.beginFirst(scope,members,new Random()):l.restartFirst(paused.id(),p.getUUID(),members,new Random())):(paused==null?l.beginSecond(scope,p.getUUID()):l.resumeSecond(paused.id(),p.getUUID())));
        if(m==null){message(p,"busy");return 0;}
        try{
            for(UUID id:m.participants())FRAMES.put(id,Hk3ReviewFrame.issue(m.id(),scope,Hk3ReviewDialogues.id(kind),""));
            if(kind==Hk3ReviewLedger.Kind.FIRST){
                long room=Hk3ReviewReturnData.get(p.server).room();int index=0;
                BARRIERS.put(m.id(),new Hk3ReviewReadingBarrier());
                for(UUID id:m.participants()){
                    var member=p.server.getPlayerList().getPlayer(id);if(member==null)throw new IllegalStateException("召入成员已离线");
                    Hk3ReviewScene.enter(member,m.id(),room,index++);
                    var rep=p.server.getPlayerList().getPlayer(m.representative());
                    member.sendSystemMessage(Component.translatable("hk3gtl.review.representative",rep==null?m.representative().toString():rep.getGameProfile().getName()));
                    if(m.supplement())message(member,"supplement");
                }
                showFirst(p.server,m,true);
            }else{
                Hk3ReviewScene.projection(p);show(p,m,paused==null?m.checkpoint():"SP06",true);
            }
            return 1;
        }catch(RuntimeException failure){
            LOGGER.error("[HK3GTL] 审查场景启动失败，会面={}",m.id(),failure);
            for(UUID id:new ArrayList<>(m.participants())){var member=p.server.getPlayerList().getPlayer(id);if(member!=null)pause(member,false,false);}
            message(p,"start_failed");return 0;
        }
    }
    private static void show(ServerPlayer p,Hk3ReviewLedger.Snapshot m,String segment,boolean open){
        String id=Hk3ReviewDialogues.id(m.kind());
        if(DialogueRegistry.getDialogue(id)==null||!DialogueRegistry.getDialogue(id).segments().containsKey(segment))throw new IllegalStateException("正式审查正文缺失："+segment);
        var f=Hk3ReviewFrame.issue(m.id(),m.scope(),id,segment);FRAMES.put(p.getUUID(),f);
        PAGES.computeIfAbsent(p.getUUID(),key->new Hk3ReviewPageWindow()).sent(f);
        if(open)Hk3Network.CHANNEL.send(PacketDistributor.PLAYER.with(()->p),new DialogueOpenS2CPacket(id,segment,f.nonce()));
        else Hk3Network.CHANNEL.send(PacketDistributor.PLAYER.with(()->p),new DialogueAdvanceS2CPacket(id,segment,f.nonce()));
    }
    private static void showFirst(MinecraftServer server,Hk3ReviewLedger.Snapshot m,boolean open){
        for(UUID id:new ArrayList<>(FRAMES.keySet())){
            if(!FRAMES.get(id).meeting().equals(m.id()))continue;
            var p=server.getPlayerList().getPlayer(id);if(p==null||!active(id))continue;
            show(p,m,firstSegment(m,id),open);
        }
    }
    private static String firstSegment(Hk3ReviewLedger.Snapshot m,UUID id){
        return switch(m.phase()){
                case OPENING->"first_review.open";
                case ANSWER->"first_review.question."+m.questions().get(m.replayIndex());
                case CLOSING->m.supplement()?"supplement":"first_review.closing";
                case MENU->m.representative().equals(id)?"menu."+Hk3ReviewDialogues.mask(m):"wait";
                default->"wait";
            };
    }
    public static void action(ServerPlayer p,Hk3ReviewActionPacket packet){
        var f=FRAMES.get(p.getUUID());if(f==null)return;
        var currentScope=Hk3ResearchTeams.scope(p.server,p.getUUID());
        if(packet.choice()==-1){var pages=PAGES.get(p.getUUID());if(pages!=null&&pages.mayPause(currentScope,packet.dialogue(),packet.segment(),packet.nonce())){
            var closing=meeting(p);if(closing!=null&&closing.kind()==Hk3ReviewLedger.Kind.FIRST&&closing.questions().size()==2&&!closing.representative().equals(p.getUUID())&&!OBSERVERS.contains(p.getUUID())&&Hk3ReviewScene.valid(p,closing.kind()))com.sirin.hk3gtl.common.easter.Hk3EggVanilla.caseEvent(p,169);
            pause(p,false,false);
        }return;}
        if(!f.accepts(currentScope,packet.dialogue(),packet.segment(),packet.nonce()))return;
        var m=meeting(p);if(m==null||(!m.participants().contains(p.getUUID())&&!OBSERVERS.contains(p.getUUID()))||m.phase()==Hk3ReviewLedger.Phase.PAUSED||m.phase()==Hk3ReviewLedger.Phase.ABANDONED)return;
        if(!Hk3ReviewScene.valid(p,m.kind())){pause(p,false,false);return;}
        var def=DialogueRegistry.getDialogue(f.dialogue());var lines=def.segments().get(f.segment());var choices=lines.get(lines.size()-1).choices();
        if(choices==null||packet.choice()<0||packet.choice()>=choices.size())return;
        if(OBSERVERS.contains(p.getUUID())){
            if(m.phase()==Hk3ReviewLedger.Phase.CLOSING)pause(p,false,false);else show(p,m,"wait",false);return;
        }
        // 先消费页面令牌；即使后续广播或投递失败，旧包也不能二次推进。
        FRAMES.put(p.getUUID(),Hk3ReviewFrame.issue(m.id(),m.scope(),f.dialogue(),f.segment()));
        try{
            if(m.kind()==Hk3ReviewLedger.Kind.SECOND){
                if(f.segment().equals("SP06")){show(p,m,m.checkpoint(),false);return;}
                if(!m.checkpoint().equals(f.segment()))return;
                if(m.checkpoint().equals("S209")){finish(p,m);return;}
                if(Hk3ReviewData.get(p.server).change(l->l.advanceSecond(m.id(),p.getUUID(),f.segment(),packet.choice())))show(p,meeting(p),meeting(p).checkpoint(),false);
                else show(p,m,m.checkpoint(),false);
            }else if(f.segment().equals("wait")){show(p,m,"wait",false);
            }else if(m.phase()==Hk3ReviewLedger.Phase.MENU){
                int q=Hk3ReviewDialogues.remaining(Hk3ReviewDialogues.mask(m)).get(packet.choice());
                if(Hk3ReviewData.get(p.server).change(l->l.choose(m.id(),p.getUUID(),q))){BARRIERS.get(m.id()).reset();showFirst(p.server,meeting(p),false);}
            }else if(m.phase()==Hk3ReviewLedger.Phase.CLOSING){finish(p,m);
            }else{
                var barrier=BARRIERS.get(m.id());if(barrier==null)throw new IllegalStateException("一审阅读屏障缺失");
                barrier.confirm(p.getUUID(),m.participants());show(p,m,"wait",false);advanceFirst(p.server,m.id());
            }
        }catch(RuntimeException failure){
            LOGGER.error("[HK3GTL] 审查推进失败，会面={}",m.id(),failure);
            var representative=p.server.getPlayerList().getPlayer(m.representative());pause(representative==null?p:representative,false,false);message(p,"start_failed");
        }
    }
    private static void advanceFirst(MinecraftServer server,UUID id){
        var data=Hk3ReviewData.get(server);var m=data.snapshot().meeting(id);var b=BARRIERS.get(id);
        if(m==null||b==null||!b.ready(m.participants()))return;
        if(m.phase()!=Hk3ReviewLedger.Phase.OPENING&&m.phase()!=Hk3ReviewLedger.Phase.ANSWER)return;
        boolean changed=data.change(l->m.phase()==Hk3ReviewLedger.Phase.OPENING?l.openingRead(id,m.representative()):l.answerRead(id,m.representative(),m.questions().get(m.replayIndex())));
        if(changed){
            if(m.phase()==Hk3ReviewLedger.Phase.ANSWER){var representative=server.getPlayerList().getPlayer(m.representative());
                if(representative!=null){var marker=com.sirin.hk3gtl.common.easter.Hk3EggRuntime.state(representative).getCompound("firstReviewReconnect");
                    if(marker.getBoolean("Reconnected")&&marker.hasUUID("Meeting")&&marker.getUUID("Meeting").equals(m.id())&&marker.hasUUID("Scope")&&marker.getUUID("Scope").equals(m.scope())&&marker.getInt("Confirmed")>0&&marker.getInt("Confirmed")<=m.questions().size()&&m.replayIndex()+1==marker.getInt("Confirmed")&&java.util.Arrays.equals(marker.getIntArray("Questions"),m.questions().subList(0,marker.getInt("Confirmed")).stream().mapToInt(Integer::intValue).toArray())){
                        com.sirin.hk3gtl.common.easter.Hk3EggVanilla.caseEvent(representative,170);com.sirin.hk3gtl.common.easter.Hk3EggRuntime.state(representative).remove("firstReviewReconnect");
                    }
                }
            }
            b.reset();showFirst(server,data.snapshot().meeting(id),false);
        }
    }
    private static void finish(ServerPlayer p,Hk3ReviewLedger.Snapshot m){
        var result=Hk3ReviewData.get(p.server).change(l->m.kind()==Hk3ReviewLedger.Kind.FIRST?l.finishFirst(m.id(),p.getUUID()):l.finishSecond(m.id(),p.getUUID()));
        if(result==null)return;
        closeFrame(p);Hk3ReviewScene.removeProjection(p.getUUID());
        if(m.kind()==Hk3ReviewLedger.Kind.FIRST)Hk3ReviewScene.returnHome(p);
        Hk3ReviewProgress.sync(p);message(p,result.firstTeamSettlement()?"settled":"personal_complete");
        if(Hk3ReviewData.get(p.server).snapshot().meeting(m.id()).phase()==Hk3ReviewLedger.Phase.COMPLETE){
            BARRIERS.remove(m.id());
            for(UUID id:new ArrayList<>(OBSERVERS))if(FRAMES.containsKey(id)&&FRAMES.get(id).meeting().equals(m.id())){var observer=p.server.getPlayerList().getPlayer(id);if(observer!=null){com.sirin.hk3gtl.common.easter.Hk3EggVanilla.caseEvent(observer,171);pause(observer,false,false);}}
        }
    }
    private static void closeFrame(ServerPlayer p){
        PAGES.remove(p.getUUID());OBSERVERS.remove(p.getUUID());Hk3ReviewScene.release(p.getUUID());var old=FRAMES.remove(p.getUUID());if(old!=null)Hk3Network.CHANNEL.send(PacketDistributor.PLAYER.with(()->p),new DialogueAbortS2CPacket(old.dialogue(),""));
    }
    public static void pause(ServerPlayer p,boolean disconnect,boolean attacked){
        if(Hk3ReviewScene.moving(p.getUUID()))return;
        var m=meeting(p);if(m==null){closeFrame(p);Hk3ReviewScene.removeProjection(p.getUUID());return;}
        if(OBSERVERS.contains(p.getUUID())){closeFrame(p);if(!disconnect)Hk3ReviewScene.returnHome(p);return;}
        if(disconnect&&m.kind()==Hk3ReviewLedger.Kind.FIRST&&m.representative().equals(p.getUUID())){
            int confirmed=m.phase()==Hk3ReviewLedger.Phase.ANSWER?m.replayIndex():m.questions().size();
            if(confirmed>0){var marker=new net.minecraft.nbt.CompoundTag();marker.putUUID("Meeting",m.id());marker.putUUID("Scope",m.scope());marker.putInt("Confirmed",confirmed);marker.putIntArray("Questions",m.questions().subList(0,confirmed).stream().mapToInt(Integer::intValue).toArray());com.sirin.hk3gtl.common.easter.Hk3EggRuntime.state(p).put("firstReviewReconnect",marker);}
        }
        Hk3ReviewData.get(p.server).change(l->{l.depart(p.getUUID());return null;});
        closeFrame(p);Hk3ReviewScene.removeProjection(p.getUUID());
        if(!disconnect&&m.kind()==Hk3ReviewLedger.Kind.FIRST)Hk3ReviewScene.returnHome(p);
        var after=Hk3ReviewData.get(p.server).snapshot().meeting(m.id());
        if(after.phase()==Hk3ReviewLedger.Phase.PAUSED||after.phase()==Hk3ReviewLedger.Phase.ABANDONED){
            BARRIERS.remove(m.id());
            for(var e:new ArrayList<>(FRAMES.entrySet()))if(e.getValue().meeting().equals(m.id())){
                var member=p.server.getPlayerList().getPlayer(e.getKey());if(member!=null){closeFrame(member);Hk3ReviewScene.returnHome(member);message(member,"paused");}else{FRAMES.remove(e.getKey());OBSERVERS.remove(e.getKey());PAGES.remove(e.getKey());}
            }
        }else advanceFirst(p.server,m.id());
        if(!disconnect&&p.isAlive()&&m.kind()==Hk3ReviewLedger.Kind.SECOND)DialogueSessionManager.startAt(p,Hk3ReviewDialogues.NOTICE,attacked?"SP05":"SP04",0);
    }
    public static int returnNow(ServerPlayer p){if(active(p.getUUID()))pause(p,false,false);return Hk3ReviewScene.returnHome(p)?1:0;}
    @SubscribeEvent public static void tick(TickEvent.ServerTickEvent e){
        if(e.phase!=TickEvent.Phase.END)return;var server=net.minecraftforge.server.ServerLifecycleHooks.getCurrentServer();if(server==null||server.getTickCount()%5!=0)return;
        for(var p:server.getPlayerList().getPlayers()){
            if(active(p.getUUID())){
                var m=meeting(p);if(m==null||!m.scope().equals(Hk3ResearchTeams.scope(server,p.getUUID()))||m.phase()==Hk3ReviewLedger.Phase.ABANDONED||m.phase()==Hk3ReviewLedger.Phase.PAUSED||m.phase()==Hk3ReviewLedger.Phase.COMPLETE){pause(p,false,false);continue;}
                if(!p.isAlive()){pause(p,true,false);continue;}Hk3ReviewScene.tick(p,m.kind());
            }else if(server.getTickCount()%100==0&&p.isAlive()){
                if(Hk3ReviewReturnData.get(server).point(p.getUUID())!=null){Hk3ReviewScene.returnHome(p);continue;}
                var scope=Hk3ResearchTeams.scope(server,p.getUUID());var l=Hk3ReviewData.get(server).snapshot();
                for(var kind:Hk3ReviewLedger.Kind.values())if(l.qualified(scope,kind)&&!l.experienced(p.getUUID(),kind)&&(kind==Hk3ReviewLedger.Kind.FIRST||l.experienced(p.getUUID(),Hk3ReviewLedger.Kind.FIRST))&&INVITED.add(p.getUUID()+"/"+scope+"/"+kind)){
                    String command=kind==Hk3ReviewLedger.Kind.FIRST?"/hk3review first":"/hk3review second";
                    p.sendSystemMessage(Component.translatable("hk3gtl.review.invite",kind==Hk3ReviewLedger.Kind.FIRST?"一审":"二审",command).withStyle(s->s.withClickEvent(new ClickEvent(ClickEvent.Action.RUN_COMMAND,command))));
                }
            }
        }
    }
    @SubscribeEvent public static void login(PlayerEvent.PlayerLoggedInEvent e){if(e.getEntity() instanceof ServerPlayer p){var marker=com.sirin.hk3gtl.common.easter.Hk3EggRuntime.state(p).getCompound("firstReviewReconnect");if(marker.hasUUID("Meeting")){marker.putBoolean("Reconnected",true);com.sirin.hk3gtl.common.easter.Hk3EggRuntime.state(p).put("firstReviewReconnect",marker);}}}
    @SubscribeEvent public static void logout(PlayerEvent.PlayerLoggedOutEvent e){if(e.getEntity() instanceof ServerPlayer p){pause(p,true,false);INVITED.removeIf(k->k.startsWith(p.getUUID()+"/"));}}
    @SubscribeEvent public static void dimension(PlayerEvent.PlayerChangedDimensionEvent e){if(e.getEntity() instanceof ServerPlayer p)pause(p,false,false);}
    @SubscribeEvent public static void clonePlayer(PlayerEvent.Clone e){if(e.getEntity() instanceof ServerPlayer p)pause(p,true,false);}
    @SubscribeEvent public static void stop(ServerStoppedEvent e){FRAMES.clear();PAGES.clear();BARRIERS.clear();INVITED.clear();OBSERVERS.clear();Hk3ReviewScene.clear();}
}
