package com.sirin.hk3gtl.test.narrative;

import com.google.gson.*;
import com.sirin.hk3gtl.common.narrative.*;
import com.sirin.hk3gtl.common.phone.Hk3PhoneData;
import com.sirin.hk3gtl.common.event.Hk3EasterEggClock;
import com.sirin.hk3gtl.common.event.Hk3PlayerDataCloneHandler;
import net.minecraft.nbt.*;
import java.io.*;
import java.nio.charset.StandardCharsets;
import java.time.*;
import java.util.*;
import java.util.function.Function;

/** 【变更记录 #1】2026-10-01 01:57:00（修订127）：删除无；新增全目录分类、真实NBT压缩恢复、去重、玩家隔离、正式经历不授予与时间边界测试；修改无；用途：运行生产收藏服务及重生复制路径，不伪装成客户端绘制验收。 */
/** 【变更记录 #2】2026-10-01 03:50:42（修订128）：删除：旧固定上限或被替代的分支；新增/修改：对扩展目录运行真实NBT存取、收件箱去重与个人隔离回归；用途：已审核彩蛋独立执行，不授研究或审查资格。 */
/** 【变更记录 #3】2026-10-01 20:34:36（修订148）：删除无；新增正式目录回归入口；修改收藏测试接入资格隔离核验；用途：防止收藏替代会面。 */
/** 【变更记录 #4】2026-10-01 22:50:14（第4次备注 · 内测5修订155）：删除玩家展示中的旧电压及开发说明；新增现行正文投影或对应回归；修改仅限呈现与检索，不改变进度、回执、触发条件或权限；用途：统一发布版玩家文案，历史备注保留。 */
/** 【变更记录 #5】2026-11-04 06:10:00（第5次备注 · 内测5修订196）：删除64正式正文必须等于旧bodyKey的断言；新增当前迁移原文/标题同源检查；修改仅正式64项的批准正文期望；用途：其他收藏和旧收件箱历史仍保留。 */
public final class CollectionSystemTest {
    private static int checks;
    private static void check(boolean value,String why){if(!value)throw new AssertionError(why);checks++;}
    private static CompoundTag reload(CompoundTag tag)throws IOException{
        var out=new ByteArrayOutputStream();NbtIo.writeCompressed(tag,out);
        return NbtIo.readCompressed(new ByteArrayInputStream(out.toByteArray()));
    }
    private static JsonObject language(String name)throws IOException{
        try(var in=CollectionSystemTest.class.getResourceAsStream("/assets/hk3gtl/lang/"+name+".json")){
            if(in==null)throw new AssertionError("缺少语言资源");
            return JsonParser.parseReader(new InputStreamReader(in,StandardCharsets.UTF_8)).getAsJsonObject();
        }
    }
    public static void main(String[] args)throws Exception{
        FormalArchiveTest.run();
        LegacyArchiveIntegrityTest.run();
        var nodes=Hk3NarrativeNodes.all();
        check(Hk3CollectionRecords.total("optional")==503,"500正式目录彩蛋加3残篇");
        check(Hk3CollectionRecords.total("milestone")==5,"五篇旧里程碑");
        check(Hk3CollectionRecords.total("unclassified")==0,"当前注册表逐项有分类");
        check(Hk3CollectionCatalog.kind("E-EG-999999")==Hk3CollectionCatalog.Kind.UNCLASSIFIED,"新增彩蛋不能被前缀自动豁免");
        check(!Hk3CollectionCatalog.optionalEvent("E-HQ-005"),"终局正式剧情不豁免");
        check(!Hk3CollectionCatalog.optionalEvent("unknown"),"未知事件不豁免");
        check(Hk3CollectionCatalog.optionalEvent("E-EGG-001"),"非酋旧日志是额外收藏");
        for(String lang:List.of("zh_cn","en_us")){
            var strings=language(lang);Function<String,String> tr=k->{check(strings.has(k),lang+" 缺少翻译："+k);return strings.get(k).getAsString();};
            var obsolete=java.util.regex.Pattern.compile("(海渊|虚数|量子|终焉)\\s*(III|IV|II|I|[ⅠⅡⅢⅣ一二三四1-4])|(海渊|虚数|量子|终焉)(阶段|时代|电压|级)|\\b(Abyss|Imaginary|Quantum|Finality)[ -]+(III|IV|II|I|stage|tier)\\b",java.util.regex.Pattern.CASE_INSENSITIVE);
            for(var item:strings.entrySet())if(!item.getKey().startsWith("_")){
                String text=item.getValue().getAsString();
                check(!obsolete.matcher(text).find(),"玩家语言资源残留旧电压："+item.getKey());
                check(!text.contains("档案解锁")&&!text.contains("不阻断终审")&&!text.contains("不会替代研究、工程"),"玩家语言资源残留开发文案："+item.getKey());
            }
            PlayerTextTest.run(tr);
            var inbox=new Hk3PhoneData();UUID actor=UUID.randomUUID(),other=UUID.randomUUID();var state=new CompoundTag();
            check(!Hk3NarrativeLog.unlock(state,"fake"),"拒绝任意节点注入");
            state.putBoolean(Hk3NarrativeLog.TAG_PREFIX+"fake",true);
            check(Hk3CollectionRecords.unlocked(state,"all").isEmpty(),"未知静态标记不进入收藏");
            for(var node:nodes){
                String body=Hk3CollectionRecords.body(node,tr);
                var migration=Hk3LegacyArchiveMigration.all().get(node.unlockEventId());
                if(migration==null)for(String key:node.bodyKeys())check(body.contains(tr.apply(key)),"其他收藏保留完整已批准正文");
                else check(body.equals(migration.body()),"64正式收藏使用完整新版批准正文");
                check(!body.contains("不阻断终审")&&!body.contains("不会替代研究"),"正文不附开发说明");
                var first=Hk3CollectionRecords.record(state,inbox,actor,node,100,tr);
                check(first.unlocked()&&first.delivered(),"首次解锁并投递");
                check(first.title().equals(Hk3CollectionRecords.title(node,tr)),"新消息只用完整标题");
                check(first.kind().equals(Hk3CollectionCatalog.optional(node.id())?"chatter":"narrative"),"按正文目录分优先级");
                var second=Hk3CollectionRecords.record(state,inbox,actor,node,101,tr);
                check(!second.unlocked()&&!second.delivered(),"重复触发无第二封");
                check(inbox.entry(other,"narrative_"+node.id())==null,"他人不能收到本人收藏");
            }
            check(inbox.count(actor)==nodes.size(),"一节点一永久消息");
            var beforeRead=state.copy();
            for(var node:nodes)inbox.read(actor,"narrative_"+node.id());
            check(beforeRead.equals(state),"阅读不改变任何剧情、研究或事件标记");
            check(inbox.unread(actor)==0,"阅读状态独立");
            var restored=reload(state);var restoredInbox=Hk3PhoneData.load(reload(inbox.save(new CompoundTag())));
            check(Hk3CollectionRecords.unlocked(restored,"all").size()==nodes.size(),"压缩NBT恢复全部收藏");
            for(var node:nodes){
                var receipt=Hk3CollectionRecords.record(restored,restoredInbox,actor,node,102,tr);
                check(!receipt.unlocked()&&!receipt.delivered(),"重登不再发通知");
                check(restoredInbox.entry(actor,"narrative_"+node.id()).read(),"重登保留已读状态");
            }
            var clone=new CompoundTag();state.putString("foreign_mod","untouched");
            var nested=new CompoundTag();nested.putLong("online_ticks",100);state.put("hk3gtl_egg_stats",nested);
            Hk3PlayerDataCloneHandler.copyPersistentState(state,clone);
            check(!clone.contains("foreign_mod"),"重生复制不碰其他模组");
            check(Hk3CollectionRecords.unlocked(clone,"all").size()==nodes.size(),"死亡与末地返回保留全部收藏");
            clone.getCompound("hk3gtl_egg_stats").putLong("online_ticks",200);
            check(state.getCompound("hk3gtl_egg_stats").getLong("online_ticks")==100,"不共享可变NBT");
            check(Hk3CollectionRecords.unlocked(new CompoundTag(),"all").isEmpty(),"另一玩家和另一存档不继承");
            for(String filter:List.of("optional","formal","milestone")){
                var rows=Hk3CollectionRecords.unlocked(restored,filter);
                check(rows.size()==Hk3CollectionRecords.total(filter),"类别数量准确");
                check(rows.stream().map(Hk3NarrativeNode::id).distinct().count()==rows.size(),"类别无重复");
            }
            check(Hk3CollectionRecords.unlocked(restored,"garbage").isEmpty(),"非法筛选拒绝");
            var oldState=new CompoundTag();var oldNode=Hk3NarrativeNodes.EG_003;Hk3NarrativeLog.unlock(oldState,oldNode.id());
            var oldInbox=new Hk3PhoneData();var repair=Hk3CollectionRecords.record(oldState,oldInbox,actor,oldNode,200,tr);
            check(!repair.unlocked()&&repair.delivered(),"旧解锁可补永久信箱而不新解锁");
            oldState.remove(Hk3NarrativeLog.TAG_PREFIX+oldNode.id());
            check(Hk3CollectionRecords.unlocked(oldState,"all").isEmpty(),"管理员清除不由历史信箱反向复活");
            var valid=Hk3CollectionRecords.record(oldState,oldInbox,actor,oldNode,201,tr);
            check(valid.unlocked()&&!valid.delivered(),"清除后真实重触发可恢复但不重发永久消息");
            var failState=new CompoundTag();boolean failed=false;
            try{Hk3CollectionRecords.record(failState,new Hk3PhoneData(),actor,oldNode,0,k->"x".repeat(17000));}
            catch(IllegalArgumentException expected){failed=true;}
            check(failed&&!Hk3NarrativeLog.isUnlocked(failState,oldNode.id()),"投递校验失败不写完成状态");
        }
        var sunday=LocalDateTime.of(2026,10,4,0,0);
        for(int hour=0;hour<24;hour++){
            var ids=Hk3EasterEggClock.events(sunday.withHour(hour),24000);
            check(ids.contains(60)==(hour<6),"周日凌晨边界");
            check(ids.contains(53)==(hour==3),"服务器凌晨三点边界");
        }
        for(int day=1;day<=7;day++)check(Hk3EasterEggClock.events(sunday.plusDays(day),24000).contains(60)==(day==7),"周日判定");
        check(Hk3EasterEggClock.events(LocalDateTime.of(2026,2,14,12,0),0).contains(58),"情人节正确日期");
        check(!Hk3EasterEggClock.events(LocalDateTime.of(2026,6,9,12,0),0).contains(58),"不是旧错误日期");
        check(Hk3EasterEggClock.events(LocalDateTime.of(2026,10,1,12,0),0).contains(59),"十月一日纪念");
        for(long t:List.of(5999L,6000L,6100L,6101L))check(Hk3EasterEggClock.events(sunday,t).contains(70)==(t>=6000&&t<=6100),"游戏正午窗口");
        check(!Hk3EasterEggClock.restDue(431999)&&Hk3EasterEggClock.restDue(432000),"六小时边界");
        System.out.println("Collection system: "+checks+" checks passed; "+nodes.size()+" nodes; rendering and actual triggers still need game acceptance");
    }
}
