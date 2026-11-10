package com.sirin.hk3gtl.test.integration;

import com.google.gson.*;
import com.sirin.hk3gtl.common.integration.*;
import com.sirin.hk3gtl.common.research.*;
import net.minecraft.nbt.*;
import org.objectweb.asm.ClassReader;
import org.objectweb.asm.tree.ClassNode;
import java.nio.charset.StandardCharsets;
import java.nio.file.*;
import java.util.*;

/** 八章真实资源解析、100题前置、读写隔离、移档与当前FTB字节码接口；不替代实际游戏加载。 */
/** 【变更记录 #1】2026-10-01 14:12:23（修订129）：删除：无；新增/修改：实际SNBT解析、100题依赖与来源隔离、旧六章无损迁移、FTB方法签名回归；用途：任务和进度只投影真实账本，不授研究、物品或审查资格。 */
/** 【变更记录 #2】2026-10-01 14:16:54（修订129）：删除：无；新增/修改：追加FTB自带SNBT解析器与Minecraft解析结果逐章比对；用途：任务和进度只投影真实账本，不授研究、物品或审查资格。 */
/** 【变更记录 #3】2026-10-01 15:13:33（修订131）：删除旧研究所分章规则；新增/修改：新增17电压页153任务按tier核验，同时覆盖原六章及修订129八章迁移；用途：按GTL电压页组织玩家教程，保留真实研究与既有任务进度。 */
/** 【变更记录 #4】2026-10-01 15:18:00（修订131）：删除旧研究所分章规则；新增/修改：补入FTB跨页链接解析、唯一ID及任务节点位置检查；用途：按GTL电压页组织玩家教程，保留真实研究与既有任务进度。 */
/** 【变更记录 #5】2026-10-01 15:45:32（修订132）：删除无；新增研究最多两行与同页前置左到右校验；修改布局测试边界；用途：防止后续生成重新变成纵向堆叠，不代替游戏视觉验收。 */
/** 【变更记录 #6】2026-10-01 16:16:03（修订133）：删除活动构建中的132横向约束，草稿测试完整另存；新增任务延期边界记录；修改回归资源基线为已部署131；用途：其他系统更新不得夹带暂停的任务改版。 */
public final class QuestCatalogTest {
    private static int checks;
    private static void check(boolean yes,String why){checks++;if(!yes)throw new AssertionError(why);}
    private static byte[] bytes(String path)throws Exception{try(var in=QuestCatalogTest.class.getResourceAsStream(path)){if(in==null)throw new AssertionError("资源缺失："+path);return in.readAllBytes();}}
    private static String text(String path)throws Exception{return new String(bytes(path),StandardCharsets.UTF_8);}
    private static void method(String type,String name,String desc)throws Exception{
        var node=new ClassNode();new ClassReader(bytes('/'+type+".class")).accept(node,ClassReader.SKIP_CODE);
        check(node.methods.stream().anyMatch(m->m.name.equals(name)&&m.desc.equals(desc)),"FTB接口不存在："+type+'.'+name+desc);
    }
    public static void main(String[] args)throws Exception{
        var catalog=Hk3QuestCatalog.all();var byQuest=new HashMap<String,CompoundTag>();var ids=new HashSet<String>();var chapters=new ArrayList<String>();var links=new ArrayList<String>();
        var byKey=new HashMap<String,Hk3QuestCatalog.Entry>();catalog.forEach(e->byKey.put(e.key(),e));
        for(int i=0;i<17;i++){
            String file="chapters/hk3_voltage_%02d.snbt".formatted(i);chapters.add(file);
            var root=TagParser.parseTag(text("/assets/hk3gtl/ftbquests/"+file));
            var ftbRoot=dev.ftb.mods.ftblibrary.snbt.SNBT.readLines(text("/assets/hk3gtl/ftbquests/"+file).lines().toList());
            check(ftbRoot!=null&&root.equals(ftbRoot),"FTB实际SNBT解析与Minecraft解析一致："+file);
            check(ids.add(root.getString("id")),"章节ID唯一");
            var positions=new HashSet<String>();
            for(Tag raw:root.getList("quest_links",Tag.TAG_COMPOUND)){
                var link=(CompoundTag)raw;check(ids.add(link.getString("id")),"跨页链接ID唯一");links.add(link.getString("linked_quest"));
                check(positions.add(link.getDouble("x")+":"+link.getDouble("y")),"跨页链接位置不重叠");
            }

            for(Tag raw:root.getList("quests",Tag.TAG_COMPOUND)){
                var q=(CompoundTag)raw;check(ids.add(q.getString("id")),"任务ID唯一");byQuest.put(q.getString("id"),q);
                check(positions.add(q.getDouble("x")+":"+q.getDouble("y")),"任务节点位置不重叠");
                check(q.getList("rewards",Tag.TAG_COMPOUND).isEmpty(),"引导不发放越级奖励");
                check(q.getList("description",Tag.TAG_STRING).size()>=3,"完整教程而非单句拿物品");
                for(Tag task:q.getList("tasks",Tag.TAG_COMPOUND))check(ids.add(((CompoundTag)task).getString("id")),"子任务ID唯一");
            }
        }
        check(byQuest.size()==153&&catalog.size()==153,"17电压页153任务");
        for(String link:links)check(byQuest.containsKey(link),"跨页链接指向实际任务");
        var empty=new Hk3QuestCatalog.Facts(Set.of(),0,false,false);
        var complete=new Hk3QuestCatalog.Facts(Hk3ResearchCatalog.bundled().topics().keySet(),7,true,true);
        for(var e:catalog){
            var q=byQuest.get(e.quest());check(q!=null,"清单指向实际任务");var ts=q.getList("tasks",Tag.TAG_COMPOUND);check(ts.size()==1,"每项有独立完成入口");
            var task=ts.getCompound(0);check(task.getString("id").equals(e.task()),"检测ID与SNBT一致");
            check(task.getList("tags",Tag.TAG_STRING).getString(0).equals(e.tag()),"带本模组验证标签");
            check(task.getString("type").equals(e.kind().equals("reading")?"checkmark":"custom"),"只有阅读可手动确认");
            check(!Hk3QuestCatalog.satisfied(e,empty),"空研究不能完成任何实际任务");
            check(Hk3QuestCatalog.satisfied(e,complete)!=e.kind().equals("reading"),"自动检测不能勾选阅读说明");
            for(Tag dep:q.getList("dependencies",Tag.TAG_STRING))check(byQuest.containsKey(dep.getAsString()),"不存在悬空依赖");
            if(e.kind().equals("research")){
                var topic=Hk3ResearchCatalog.bundled().get(e.value());
                var expected=new HashSet<String>();for(String parent:topic.prerequisites())expected.add(byKey.get(parent).quest());
                var actual=new HashSet<String>();for(Tag dep:q.getList("dependencies",Tag.TAG_STRING))actual.add(dep.getAsString());
                check(actual.equals(expected),"逐题与正式前置一致："+e.value());
                check(e.chapter().equals("hk3_voltage_%02d".formatted(topic.tier())),"按正式课题电压分章");
                var advancement=JsonParser.parseString(text("/data/hk3gtl/advancements/guide/research/"+e.value().toLowerCase(Locale.ROOT)+".json")).getAsJsonObject();
                check(advancement.getAsJsonObject("criteria").getAsJsonObject("verified").get("trigger").getAsString().equals("minecraft:impossible"),"只由服务端真实账本授予");
                check(!advancement.has("rewards"),"原版进度无反向解锁");
            }
        }
        // 对真实研究账本做存盘/换队隔离检查，不能由FTB勾选或伪造孤立完成节点补足祖先。
        UUID owner=UUID.randomUUID(),other=UUID.randomUUID();var data=new Hk3ResearchData();
        check(data.recordCompletion(owner,"RN-HED",1),"合法起步研究");
        var before=data.save(new CompoundTag()).copy();
        var f=new Hk3QuestCatalog.Facts(Set.of("RN-HED"),0,false,false);
        check(Hk3QuestCatalog.satisfied(byKey.get("RN-HED"),f),"对应任务读取真实完成");
        check(!Hk3QuestCatalog.satisfied(byKey.get("RN-HSA"),f),"前置完成不等于后续完成");
        check(before.equals(data.save(new CompoundTag())),"投影不修改研究账本");
        var restored=Hk3ResearchData.load(before);check(restored.completed(owner,"RN-HED")&&!restored.completed(other,"RN-HED"),"重载与个人隔离");
        check(!restored.recordCompletion(other,"RN-HSA",1),"拒绝无祖先的研究完成");
        migration(chapters);
        method("dev/ftb/mods/ftbquests/quest/BaseQuestFile","getTask","(J)Ldev/ftb/mods/ftbquests/quest/task/Task;");
        method("dev/ftb/mods/ftbquests/quest/BaseQuestFile","getNullableTeamData","(Ljava/util/UUID;)Ldev/ftb/mods/ftbquests/quest/TeamData;");
        method("dev/ftb/mods/ftbquests/quest/ServerQuestFile","withPlayerContext","(Lnet/minecraft/server/level/ServerPlayer;Ljava/lang/Runnable;)V");
        method("dev/ftb/mods/ftbquests/quest/TeamData","setProgress","(Ldev/ftb/mods/ftbquests/quest/task/Task;J)V");
        System.out.println("Industrial quests: "+checks+" checks passed; 17 voltage chapters, 153 quests, 100 research projections; actual FTB loading and UI remain untested.");
    }
    private static void migration(List<String> chapters)throws Exception{
        var root=Files.createTempDirectory("hk3gtl-r129-quest-test-").resolve("quests");Files.createDirectories(root.resolve("chapters"));
        var legacy=new ArrayList<>(List.of("chapters/hk3_ch1_honkai.snbt","chapters/hk3_ch2_abyss.snbt","chapters/hk3_ch3_imaginary.snbt","chapters/hk3_ch4_quantum.snbt","chapters/hk3_ch5_finality.snbt","chapters/hk3_ch6_finale.snbt"));
        for(int i=1;i<=8;i++)legacy.add("chapters/hk3_industrial_%02d.snbt".formatted(i));
        for(String path:legacy)Files.writeString(root.resolve(path),"原始旧章节："+path);
        Files.writeString(root.resolve("chapters/other_pack.snbt"),"其他包不可修改");
        var world=root.resolveSibling("world-progress.nbt");Files.writeString(world,"独立玩家队伍任务存档");
        var backup=Hk3QuestFileInstaller.install(root,".version","r129",chapters,legacy,path->QuestCatalogTest.class.getResourceAsStream("/assets/hk3gtl/ftbquests/"+path));
        for(String path:legacy){check(!Files.exists(root.resolve(path)),"旧文件不再加载");check(Files.readString(backup.resolve("retired").resolve(path)).equals("原始旧章节："+path),"逐份保留旧内容");}
        for(String path:chapters)check(Arrays.equals(Files.readAllBytes(root.resolve(path)),bytes("/assets/hk3gtl/ftbquests/"+path)),"实际17章迁移一致");
        check(Files.readString(root.resolve("chapters/other_pack.snbt")).equals("其他包不可修改"),"其他模组保留");
        check(Files.readString(world).equals("独立玩家队伍任务存档"),"不改玩家队伍进度");
        check(Hk3QuestFileInstaller.install(root,".version","r129",chapters,legacy,path->null)==null,"二次启动不覆盖");
    }
}

// 【变更记录 · 修订161】2026-10-17 14:11:55：本轮仅将活动类名、资源与工业配方引用迁移为长期业务命名；历史备注保留，不代表旧逻辑已全部按现行设计重写。
