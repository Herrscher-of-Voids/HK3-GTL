package com.sirin.hk3gtl.common.easter;


/** 【变更记录 #8】2026-10-31 01:06:22（第8次备注 · 修订187）：删除无；新增服务端完整阅读确认包；修改无；用途：客户端只在服务器接受全文后开启动作按钮。 */

/** 【变更记录 #7】2026-10-31 00:46:39（第7次备注 · 修订187）：删除独立重复会话；新增共享会话验证及动作消费；修改完整阅读回调至首信服务；用途：普通命令不能绕过全读校验。 */
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.nbt.CompoundTag;
import net.minecraftforge.event.entity.player.PlayerEvent;
import net.minecraftforge.event.server.ServerStoppedEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import java.util.*;
/** 【变更记录 #1】2026-10-01 04:19:02（修订128）：删除无；新增本人授权阅读会话及逐页完成回执；修改无；用途：只生成可选收藏，正文资源/权限由原业务核验，断线关闭清理。 */
@Mod.EventBusSubscriber(modid="hk3gtl")
/** 【变更记录 #2】2026-10-01 04:30:25（修订128）：删除：旧固定上限或被替代的分支；新增/修改：101通知只统计确已投递本人信箱的全文阅读，不把任意档案或预览凑数；用途：已审核彩蛋独立执行，不授研究或审查资格。 */
/** 【变更记录 #3】2026-10-01 04:34:32（修订128）：删除：旧固定上限或被替代的分支；新增/修改：IF逐句完整阅读分为免费与正常选择集合，不改变玩家名额或终审资格；用途：已审核彩蛋独立执行，不授研究或审查资格。 */
/** 【变更记录 #4】2026-10-01 04:53:17（修订128）：删除：旧固定上限或被替代的分支；新增/修改：离线三日后只在真正读到本人既有通知全文时提示，不能通过打开任意预览凑数；用途：已审核彩蛋独立执行，不授研究或审查资格。 */
/** 【变更记录 #5】2026-10-01 06:27:59（修订128）：删除：无；新增/修改：阅读已有来信全文时记录本人当前附近AE任务，只有该任务之后正常交付才授收藏；用途：已审核彩蛋独立执行，不授研究或审查资格。 */
/** 【变更记录 #6】2026-10-01 06:45:17（修订128）：删除：无；新增/修改：阅读全文后仍记录界面开启；服务端自然跨23点再主动关闭才触发303，跳时/断线不伪造关闭；用途：已审核彩蛋独立执行，不授研究或审查资格。 */
/** 【变更记录 #9】2026-11-04 06:12:15（第9次备注 · 内测5修订196）：删除无；新增正式新版档案连续全文回调；修改正式档案会话与可选收藏统计分开；用途：复用已核验阅读令牌，不让普通已读或旧收藏代替本人正式回执。 */
/** 【变更记录 #10】2026-11-05 01:59:54（第10次备注 · 内测5修订204）：删除无；新增个人收藏正文逐片权限重验及笔记末段回调；修改断电、版本变化、过期和断线清理关联动作；用途：复用原令牌验证385/500，不以打开或客户端声明代替完整阅读。 */
public final class Hk3EggReading {
    /** 【变更记录 #11】2026-11-05（修订207）：文明总览全文逐片重验本人安装、供电和当前页面；完整读完才提交175，不计入信件阅读。 */
/** 【变更记录 #12】2026-11-05 22:19:02（修订211）：删除无；新增欢迎消息和内置回复复用的连续阅读权限核验及清理；修改不能通过普通阅读包或旧阶段越权；用途：只在服务端全文回执后解锁。 */
    private static boolean guarded(String id){return com.sirin.hk3gtl.common.phone.Hk3SocialBuiltinTopics.managed(id)||com.sirin.hk3gtl.common.phone.Hk3PhoneCollectionService.managed(id)||com.sirin.hk3gtl.common.phone.Hk3PhoneCivilizationReading.managed(id);}
    private static boolean authorized(ServerPlayer p,String id){if(com.sirin.hk3gtl.common.phone.Hk3SocialBuiltinTopics.managed(id))return com.sirin.hk3gtl.common.phone.Hk3SocialBuiltinTopics.authorize(p,id);return com.sirin.hk3gtl.common.phone.Hk3PhoneCivilizationReading.managed(id)?com.sirin.hk3gtl.common.phone.Hk3PhoneCivilizationReading.authorize(p):com.sirin.hk3gtl.common.phone.Hk3PhoneCollectionService.authorize(p,id);}
    private static final Hk3ReadingSessions READING = new Hk3ReadingSessions();
    private static final class Open { final UUID token;final String id;final long expires;long previous;boolean crossed;Open(UUID token,String id,long time,long expires){this.token=token;this.id=id;this.previous=time;this.expires=expires;} }
    private static final Map<UUID,Open> OPEN=new java.util.concurrent.ConcurrentHashMap<>();
    private Hk3EggReading(){}
    @SubscribeEvent public static void tick(net.minecraftforge.event.TickEvent.PlayerTickEvent e){if(e.phase==net.minecraftforge.event.TickEvent.Phase.END&&e.player instanceof ServerPlayer p){var open=OPEN.get(p.getUUID());if(open!=null){long now=p.server.overworld().getGameTime();if(guarded(open.id)&&(now>=open.expires||now<open.expires-36000||!authorized(p,open.id))){clear(p.getUUID());return;}long time=p.server.overworld().getDayTime();if(time==open.previous+1&&Math.floorMod(time,24000)==17000)open.crossed=true;open.previous=time;}}}
    public static void clear(UUID player){READING.clear(player);OPEN.remove(player);com.sirin.hk3gtl.common.phone.Hk3SocialBuiltinTopics.clear(player);com.sirin.hk3gtl.common.phone.Hk3PhoneCollectionService.clear(player);com.sirin.hk3gtl.common.narrative.Hk3LegacyArchiveService.clear(player);}
    public static void attach(ServerPlayer p,CompoundTag view){
        // 【变更记录 #209】2026-11-05：共用视图入口使信件等独立发送通道也废弃原相册会话。
        com.sirin.hk3gtl.common.phone.Hk3PhoneGallery.view(p,view);
        String mode=view.getString("Mode"),id=view.getString("Id");
        if(mode.equals("status")||mode.equals("toast"))return;
        com.sirin.hk3gtl.common.phone.Hk3PhoneCollectionService.viewChanged(p,view);
        com.sirin.hk3gtl.common.phone.Hk3SocialBuiltinTopics.viewChanged(p,view);
        READING.clear(p.getUUID());OPEN.remove(p.getUUID());
        String action=view.getString("Token");
        if(id.isEmpty()&&!action.isEmpty())id="preview_"+action;
        if(!Set.of("letter","detail","diplomacy_read","archive_detail").contains(mode)||id.isEmpty()||view.getString("Body").isBlank())return;
        var session=READING.open(p.getUUID(),id,view.getString("Body"),action,mode.equals("letter")||mode.equals("diplomacy_read"),p.server.overworld().getGameTime());
        var token=session.token();
        OPEN.put(p.getUUID(),new Open(token,id,p.server.overworld().getDayTime(),session.expires()));
        view.putUUID("ReadToken",token);
    }
    public static void accept(ServerPlayer p,UUID token,int start,String piece){
        if(start<0){var open=OPEN.get(p.getUUID());if(open!=null&&open.token.equals(token)){if(open.crossed&&!guarded(open.id))Hk3EggVanilla.caseEvent(p,303);clear(p.getUUID());}return;}
        var open=OPEN.get(p.getUUID());
        if(open!=null&&guarded(open.id)&&!authorized(p,open.id)){clear(p.getUUID());return;}
        var s=READING.accept(p.getUUID(),token,start,piece,p.server.overworld().getGameTime());
        if(s==null)return;
        if(guarded(s.id())){
            if(com.sirin.hk3gtl.common.phone.Hk3SocialBuiltinTopics.managed(s.id()))com.sirin.hk3gtl.common.phone.Hk3SocialBuiltinTopics.completed(p,s);
            else if(com.sirin.hk3gtl.common.phone.Hk3PhoneCivilizationReading.managed(s.id()))com.sirin.hk3gtl.common.phone.Hk3PhoneCivilizationReading.completed(p,s);
            else com.sirin.hk3gtl.common.phone.Hk3PhoneCollectionService.readCompleted(p,s);
            var ack=new CompoundTag();ack.putString("Mode","read_complete");ack.putUUID("ReadToken",token);
            com.sirin.hk3gtl.common.network.Hk3Network.CHANNEL.send(net.minecraftforge.network.PacketDistributor.PLAYER.with(()->p),new com.sirin.hk3gtl.common.phone.Hk3PhonePacket(ack));return;
        }
        if(s.id().startsWith("formal_"))com.sirin.hk3gtl.common.narrative.Hk3LegacyArchiveService.readCompleted(p,s);
        var acknowledgement=new CompoundTag();acknowledgement.putString("Mode","read_complete");acknowledgement.putUUID("ReadToken",token);
        com.sirin.hk3gtl.common.network.Hk3Network.CHANNEL.send(net.minecraftforge.network.PacketDistributor.PLAYER.with(()->p),new com.sirin.hk3gtl.common.phone.Hk3PhonePacket(acknowledgement));
        com.sirin.hk3gtl.common.communication.Hk3TeamContactService.readCompleted(p,s.id());
        if(s.id().startsWith("formal_"))return;
        var state=Hk3EggRuntime.state(p);
        if(s.id().startsWith("egg_if_")){
            boolean free=s.id().startsWith("egg_if_free_");int index=Integer.parseInt(s.id().substring(s.id().lastIndexOf('_')+1));
            if(!free)state.putInt("readNormalIf",state.getInt("readNormalIf")|(1<<index));
            Hk3EggRuntime.observe(p,"if_read",Hk3EggRuntime.fields("free",Boolean.toString(free),"complete","true","normal_count",Integer.toString(Integer.bitCount(state.getInt("readNormalIf")))));return;
        }
        var read=state.getCompound("fullyRead");if(read.size()<101&&com.sirin.hk3gtl.common.phone.Hk3PhoneData.get(p).entry(p.getUUID(),s.id())!=null)read.putBoolean(Hk3EggNotes.digest(s.id()),true);state.put("fullyRead",read);
        var first=state.getCompound("firstLetters");
        if(s.id().startsWith("contact_")&&!s.id().startsWith("contact_reply_"))first.putBoolean("158",true);
        for(var pair:Map.of("_A08","159","_A09","160","_SF01","161","_ER01","162").entrySet())if(s.id().startsWith("diplomacy_")&&s.id().endsWith(pair.getKey()))first.putBoolean(pair.getValue(),true);
        state.put("firstLetters",first);
        var facts=new LinkedHashMap<>(Hk3EggCalendar.facts(Hk3EggCalendar.now(),p.server.overworld().getDayTime()));
        facts.put("id",s.id());facts.put("letter",Boolean.toString(s.letter()));facts.put("pages",Integer.toString(s.cursor().pages()));facts.put("read_count",Integer.toString(read.size()));facts.put("first_letters",Integer.toString(first.size()));
        if(state.getBoolean("awayThreeDays")&&com.sirin.hk3gtl.common.phone.Hk3PhoneData.get(p).entry(p.getUUID(),s.id())!=null){Hk3EggVanilla.caseEvent(p,494);state.remove("awayThreeDays");}
        if(s.letter()&&com.sirin.hk3gtl.common.phone.Hk3PhoneData.get(p).entry(p.getUUID(),s.id())!=null)Hk3EggCraftingReceipts.readLetter(p);
        Hk3EggRuntime.observe(p,"reading_complete",facts);
        for(String number:first.getAllKeys())Hk3EggRuntime.observe(p,"first_letter_read",Map.of("case",number));
    }
    public static boolean consumeAction(ServerPlayer player,String token){
        return READING.consumeAction(player.getUUID(),token,player.server.overworld().getGameTime());
    }
    @SubscribeEvent public static void logout(PlayerEvent.PlayerLoggedOutEvent e){clear(e.getEntity().getUUID());}
    @SubscribeEvent public static void stop(ServerStoppedEvent e){READING.clear();OPEN.clear();com.sirin.hk3gtl.common.phone.Hk3PhoneCollectionService.clear();}
}
