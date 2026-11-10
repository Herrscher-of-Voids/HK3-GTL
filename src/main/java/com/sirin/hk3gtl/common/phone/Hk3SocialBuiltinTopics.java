package com.sirin.hk3gtl.common.phone;

import com.sirin.hk3gtl.common.easter.*;
import com.sirin.hk3gtl.common.review.*;
import net.minecraft.nbt.*;
import net.minecraft.server.level.ServerPlayer;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.event.entity.player.PlayerEvent;
import net.minecraftforge.event.server.ServerStoppedEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import java.util.*;

/** 【变更记录 #1】2026-11-05（修订211）：新增已审内置话题、欢迎正文及连续阅读回执；自由输入和AI回复不冒充内置选择，预览、失电、换阶段和旧阅读令牌拒绝结算。 */
/** 【变更记录 #2】2026-11-05 22:30:19（修订211）：删除：无；新增：28项既定话题菜单、8项欢迎正文完整阅读、V14回看及雨后/熟食/拖动/样本事实校验；修改：自由输入不作内置选择，缺失败与维修生产者的102/108/132不授予；用途：个人彩蛋旁注，不改联系人资格、研究或奖励。 */
@Mod.EventBusSubscriber(modid="hk3gtl")
public final class Hk3SocialBuiltinTopics {
    public record Topic(int egg,String contact,String text) {}
    public static final List<Topic> TOPICS=List.of(
        new Topic(101,"V01","吃过饭了吗"),new Topic(102,"V01","今天不太顺利"),
        new Topic(104,"V02","明天的计划"),new Topic(105,"V03","看看我的工厂"),new Topic(106,"V03","今天想歇一会儿"),
        new Topic(107,"V04","刚刚吃饱了"),new Topic(108,"V04","修好了"),new Topic(110,"V05","下一步呢"),
        new Topic(111,"V06","仓库又满了"),new Topic(113,"V07","我拿到了材料，研究算完成吗"),new Topic(114,"V07","数据和预期不一样"),
        new Topic(115,"V08","休息时做什么"),new Topic(116,"V08","新发现"),new Topic(118,"V09","今天没什么进展"),
        new Topic(122,"V11","你是谁"),new Topic(124,"V12","你在看着我吗"),new Topic(125,"V13","工程很难"),new Topic(126,"V13","还要继续吗"),
        new Topic(127,"V14","你好"),new Topic(129,"V15","按钮太多了"),new Topic(130,"V15","桌面整理好了"),
        new Topic(131,"V16","样本有什么用"),new Topic(132,"V16","实验出了意外"),new Topic(134,"V17","故事会结束吗"),
        new Topic(135,"V18","我卡住了"),new Topic(136,"V18","替我选吧"),new Topic(138,"V19","你能保证结果吗"),new Topic(140,"V20","你不明白也没关系"));
    private static final Map<String,Integer> WELCOME=Map.of("V02",103,"V05",109,"V10",119,"V11",121,"V12",123,"V17",133,"V19",137,"V20",139);
    private record Open(String id,String contact,int stage,int egg,boolean welcome,boolean reread) {}
    private static final Map<UUID,Open> OPEN=new HashMap<>();
    private Hk3SocialBuiltinTopics() {}
    public static Topic topic(String contact,String text){return TOPICS.stream().filter(t->t.contact().equals(contact)&&t.text().equals(text)).findFirst().orElse(null);}
    public static boolean available(ServerPlayer p,String contact){var c=Hk3SocialCatalog.get(contact);return c!=null&&c.available(Hk3SocialService.stage(p))&&Hk3PhoneData.get(p).installed(p.getUUID())&&Hk3PhoneRuntime.powered(p);}
    public static void menu(ServerPlayer p,String contact){
        if(!available(p,contact))return;var view=new CompoundTag();view.putString("Mode","social_topics");view.putString("Contact",contact);view.putString("Name",Hk3SocialCatalog.get(contact).name());
        var rows=new ListTag();TOPICS.stream().filter(t->t.contact().equals(contact)).forEach(t->{var row=new CompoundTag();row.putString("Text",t.text());rows.add(row);});view.put("Rows",rows);Hk3PhoneService.send(p,view);
    }
    public static void welcome(ServerPlayer p,String contact){
        if(!available(p,contact))return;var c=Hk3SocialCatalog.get(contact);
        String body=c.lines().stream().filter(l->l.topic().equals("greeting")).findFirst().orElseThrow().text();
        boolean reread=Hk3EggRuntime.state(p).getBoolean("welcomeRead_"+contact);
        show(p,contact,WELCOME.getOrDefault(contact,0),true,reread,c.finish(body));
    }
    private static void show(ServerPlayer p,String contact,int egg,boolean welcome,boolean reread,String body){
        String id="social_read_"+UUID.randomUUID();OPEN.put(p.getUUID(),new Open(id,contact,Hk3SocialService.stage(p),egg,welcome,reread));
        var view=new CompoundTag();view.putString("Mode","archive_detail");view.putString("Id",id);view.putString("Title",Hk3SocialCatalog.get(contact).name()+(welcome?" · 欢迎消息":" · 内置话题回复"));view.putString("Body",body);Hk3PhoneService.send(p,view);
    }
    public static boolean eligible(ServerPlayer p,Topic t){
        var state=Hk3EggRuntime.state(p);
        return switch(t.egg()){
            case 101->state.getBoolean("socialRainEnded");
            case 131->p.getInventory().items.stream().anyMatch(stack->!stack.isEmpty()&&stack.is(com.sirin.hk3gtl.common.item.honkai.HonkaiMaterialItems.WORLD_BUBBLE_SAMPLE.get()))||p.getOffhandItem().is(com.sirin.hk3gtl.common.item.honkai.HonkaiMaterialItems.WORLD_BUBBLE_SAMPLE.get());
            case 102,108,132->false; // 对应真实研究失败、设备修复或样本交付尚无现行生产者，不能用旧存档计数替代。
            case 107->state.getBoolean("ateCooked");
            case 110->Hk3ReviewData.get(p.server).experienced(p.getUUID(),Hk3ReviewLedger.Kind.SECOND);
            case 130->state.getBoolean("desktopMoved");
            default->true;
        };
    }
    public static void replied(ServerPlayer p,String contact,String text){
        var t=topic(contact,text);if(t==null||!available(p,contact))return;
        var state=Hk3EggRuntime.state(p);
        if(state.getBoolean("socialAiDisabled")){Hk3EggVanilla.caseEvent(p,180);state.remove("socialAiDisabled");}
        if(!eligible(p,t))return;
        if(t.egg()==101){var history=Hk3SocialData.get(p).history(p.getUUID(),contact);if(!history.isEmpty())show(p,contact,101,false,false,history.getCompound(history.size()-1).getString("Body"));}
        else Hk3EggVanilla.caseEvent(p,t.egg());
    }
    public static boolean managed(String id){return id.startsWith("social_read_");}
    public static boolean authorize(ServerPlayer p,String id){var open=OPEN.get(p.getUUID());return open!=null&&open.id().equals(id)&&open.stage()==Hk3SocialService.stage(p)&&available(p,open.contact());}
    public static void viewChanged(ServerPlayer p,CompoundTag view){var open=OPEN.get(p.getUUID());if(open!=null&&!open.id().equals(view.getString("Id")))clear(p.getUUID());}
    public static void completed(ServerPlayer p,Hk3ReadingSessions.Session session){
        var open=OPEN.get(p.getUUID());if(open==null||!session.cursor().done()||!authorize(p,session.id()))return;
        if(open.egg()>0)Hk3EggVanilla.caseEvent(p,open.egg());
        if(open.welcome()){
            if(open.contact().equals("V14")&&open.reread())Hk3EggVanilla.caseEvent(p,128);
            Hk3EggRuntime.state(p).putBoolean("welcomeRead_"+open.contact(),true);
        }
    }
    public static void clear(UUID player){OPEN.remove(player);}
    @SubscribeEvent public static void stop(ServerStoppedEvent e){OPEN.clear();}
    @SubscribeEvent public static void logout(PlayerEvent.PlayerLoggedOutEvent e){clear(e.getEntity().getUUID());if(e.getEntity() instanceof ServerPlayer p){var state=Hk3EggRuntime.state(p);state.remove("socialWeatherDimension");state.remove("socialAiDisabled");state.remove("socialAiEnabled");}}
    @SubscribeEvent public static void weather(TickEvent.PlayerTickEvent e){
        if(e.phase!=TickEvent.Phase.END||!(e.player instanceof ServerPlayer p)||p.tickCount%20!=0)return;
        var state=Hk3EggRuntime.state(p);String dimension=p.level().dimension().location().toString();boolean rain=p.level().isRaining();
        if(dimension.equals(state.getString("socialWeatherDimension"))&&state.getBoolean("socialRaining")&&!rain)state.putBoolean("socialRainEnded",true);
        state.putString("socialWeatherDimension",dimension);state.putBoolean("socialRaining",rain);
    }
}
