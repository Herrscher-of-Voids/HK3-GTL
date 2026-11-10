package com.sirin.hk3gtl.test.persistence;

import com.sirin.hk3gtl.common.phone.*;
import com.sirin.hk3gtl.common.dimension.Hk3GraduationData;
import com.sirin.hk3gtl.common.badending.Hk3BadEndingData;
import com.sirin.hk3gtl.common.dialogue.DialogueSessionManager;
import com.sirin.hk3gtl.common.event.Hk3PlayerDataCloneHandler;
import com.sirin.hk3gtl.common.network.ResearchStateSyncRequestC2SPacket;
import com.sirin.hk3gtl.common.util.Hk3SavedDataGuard;
import net.minecraft.nbt.*;
import net.minecraft.world.level.saveddata.SavedData;
import java.nio.file.*;
import java.io.*;
import java.util.*;
import java.util.function.*;

/**
 * 【变更记录 #1】2026-10-01 17:04:49（修订136）
 * 删除：无；新增：真实压缩NBT往返、字段破坏、旧格式迁移、工厂防覆盖和临时会话隔离回归。
 * 修改：可选只读指定实例账本核验，永不保存回玩家文件；用途：验证数据恢复边界，不代替多人及GUI实机。
 */
public final class PersonalPersistenceTest {
    private static int checks;
    private static final UUID A=UUID.fromString("00000000-0000-0000-0000-000000000001"),B=UUID.fromString("00000000-0000-0000-0000-000000000002");
    private static void check(boolean pass,String why){checks++;if(!pass)throw new AssertionError(why);}
    private static void reject(Runnable r){try{r.run();throw new AssertionError("损坏内容被接受");}catch(IllegalArgumentException|IllegalStateException expected){checks++;}}
    private static CompoundTag disk(CompoundTag n)throws IOException{
        var out=new ByteArrayOutputStream();NbtIo.writeCompressed(n,out);return NbtIo.readCompressed(new ByteArrayInputStream(out.toByteArray()));
    }
    private static void corrupt(CompoundTag original,Function<CompoundTag,?> loader,Consumer<CompoundTag> mutation){
        var n=original.copy();mutation.accept(n);var before=n.copy();reject(()->loader.apply(n));check(n.equals(before),"失败读取不得修改传入数据");
    }
    public static void main(String[] args)throws Exception{
        notes();social();inbox();endings();guard();transitions();
        if(args.length>0)auditExisting(Path.of(args[0]));
        System.out.println("Personal persistence: "+checks+" checks passed; lifecycle GUI and multiplayer acceptance pending");
    }
    private static void notes()throws Exception{
        var data=new Hk3PhoneNotes();
        for(int i=0;i<64;i++)check(data.saveNote(A,"",0,"笔记"+i,"第一行\n第二行；为什么？5000",100+i),"保存64条");
        check(data.saveNote(B,"",0,"自己的笔记","私有内容",200),"其他玩家独立记录");
        var saved=disk(data.save(new CompoundTag()));var copy=Hk3PhoneNotes.load(saved);
        check(copy.list(A).size()==64&&copy.list(B).size()==1,"压缩存盘无丢笔记");
        var note=copy.list(A).get(0);
        check(copy.saveNote(A,note.id(),1,"修改后","新正文",300),"重启后版本可继续");
        check(!copy.saveNote(A,note.id(),1,"过期窗口","不能覆盖",301),"迟到请求不覆盖");
        check(Hk3PhoneNotes.load(disk(copy.save(new CompoundTag()))).find(A,note.id()).version()==2,"再次保存保留版本");
        corrupt(saved,Hk3PhoneNotes::load,n->n.remove("Users"));
        corrupt(saved,Hk3PhoneNotes::load,n->n.getCompound("Users").putString(A.toString(),"错误列表"));
        for(String field:List.of("Id","Title","Body","Version","Time"))
            corrupt(saved,Hk3PhoneNotes::load,n->n.getCompound("Users").getList(A.toString(),10).getCompound(0).remove(field));
        corrupt(saved,Hk3PhoneNotes::load,n->{var rows=n.getCompound("Users").getList(B.toString(),10);rows.add(rows.getCompound(0).copy());});
        corrupt(saved,Hk3PhoneNotes::load,n->n.getCompound("Users").getList(A.toString(),10).add(n.getCompound("Users").getList(B.toString(),10).getCompound(0).copy()));
        corrupt(saved,Hk3PhoneNotes::load,n->n.getCompound("Users").getList(B.toString(),10).getCompound(0).putString("Id","1-1-1-1-1"));
        check(Hk3PhoneNotes.load(saved).list(A).size()==64,"失败样本不污染合法原件");
    }
    private static void social()throws Exception{
        var data=new Hk3SocialData();data.advance(A,3);data.advance(B,1);
        for(int i=0;i<207;i++)data.append(A,"V01",i%2==0?"我":"角色","正文"+i,"approved",i);
        for(int day=0;day<63;day++)data.publish(A,3,day*24000L);
        data.nextReply(A,"V01","research");data.like(A,data.feed(A).getCompound(0).getString("Id"));
        var saved=disk(data.save(new CompoundTag()));var restored=Hk3SocialData.load(saved);
        check(restored.history(A,"V01").size()==200&&restored.feed(A).size()==120,"聊天和动态保留既定上限");
        check(restored.history(A,"V01").getCompound(0).getString("Body").equals("正文7"),"重启不额外删除历史");
        check(restored.stage(A)==3&&restored.stage(B)==1&&restored.history(B,"V01").isEmpty(),"阶段与隐私隔离");
        check(restored.nextReply(A,"V01","research")==1,"轮换进度保留");
        check(restored.feed(A).getCompound(0).getBoolean("Liked"),"点赞保存");
        var detached=restored.history(A,"V01");detached.clear();check(restored.history(A,"V01").size()==200,"读取返回副本");
        corrupt(saved,Hk3SocialData::load,n->n.putString("Users","坏根"));
        corrupt(saved,Hk3SocialData::load,n->n.getCompound("Users").putString(A.toString(),"坏用户"));
        for(String field:List.of("Stage","Count_V01","Rotation_V01","V01","Feed","FeedDay"))
            corrupt(saved,Hk3SocialData::load,n->n.getCompound("Users").getCompound(A.toString()).putString(field,"损坏类型"));
        for(String field:List.of("Who","Body","Source","Time"))
            corrupt(saved,Hk3SocialData::load,n->n.getCompound("Users").getCompound(A.toString()).getList("V01",10).getCompound(0).remove(field));
        corrupt(saved,Hk3SocialData::load,n->n.getCompound("Users").getCompound(A.toString()).putInt("Stage",9));
        corrupt(saved,Hk3SocialData::load,n->n.getCompound("Users").getCompound(A.toString()).getList("Feed",10).getCompound(0).putByte("Liked",(byte)2));
    }
    private static void inbox()throws Exception{
        var data=new Hk3PhoneData();data.install(A);data.install(B);
        for(int i=0;i<300;i++)data.add(A,"mail_"+i,"标题"+i,"信件正文",i,"letter","",i%2==0);
        data.read(A,"mail_0");data.resolve(A,"mail_2");
        var saved=disk(data.save(new CompoundTag()));var loaded=Hk3PhoneData.load(saved);
        check(loaded.count(A)==300&&loaded.count(B)==0,"超过旧128上限的信件全保留");
        check(loaded.entry(A,"mail_0").read()&&loaded.entry(A,"mail_0").pending(),"已读不替代待处理");
        check(!loaded.entry(A,"mail_2").pending()&&loaded.installed(A),"处理与安装保存");
        var legacy=saved.copy();legacy.remove("PhysicalMigration");
        var migrated=Hk3PhoneData.load(legacy);check(migrated.needsPhysical(A)&&migrated.needsPhysical(B),"旧消耗式安装仍可迁移");
        migrated.physicalDelivered(A);var again=Hk3PhoneData.load(disk(migrated.save(new CompoundTag())));
        check(!again.needsPhysical(A)&&again.needsPhysical(B),"补发一次重启不重复");
        corrupt(saved,Hk3PhoneData::load,n->n.putString("PhysicalMigration","损坏不得误当旧格式"));
        corrupt(saved,Hk3PhoneData::load,n->n.putString("Installed","损坏安装"));
        corrupt(saved,Hk3PhoneData::load,n->{var rows=n.getList("Installed",11);rows.add(rows.get(0).copy());});
        corrupt(saved,Hk3PhoneData::load,n->{var list=new ListTag();list.add(NbtUtils.createUUID(UUID.randomUUID()));n.put("PhysicalMigration",list);});
        corrupt(saved,Hk3PhoneData::load,n->n.getCompound("Users").putInt(A.toString(),7));
        for(String field:List.of("Id","Title","Body","Read","Pending","Kind","Time"))
            corrupt(saved,Hk3PhoneData::load,n->n.getCompound("Users").getList(A.toString(),10).getCompound(0).putInt(field,99));
        corrupt(saved,Hk3PhoneData::load,n->{var rows=n.getCompound("Users").getList(A.toString(),10);rows.add(rows.getCompound(0).copy());});
        var old=new CompoundTag();var users=new CompoundTag();var letters=new ListTag();var letter=new CompoundTag();
        letter.putString("Id","first_contact_letter");letter.putString("Title","旧信");letter.putString("Body","旧正文");letters.add(letter);users.put(A.toString(),letters);old.put("Users",users);
        check(Hk3PhoneData.load(old).entry(A,"first_contact_letter").pending(),"早期首信缺省字段仍兼容");
    }
    private static void endings()throws Exception{
        var good=new Hk3GraduationData();good.markGraduated(A);var saved=disk(good.save(new CompoundTag()));
        check(Hk3GraduationData.load(saved).isGraduated(A)&&!Hk3GraduationData.load(saved).isGraduated(B),"个人通过不串人");
        reject(()->Hk3GraduationData.load(new CompoundTag()));
        corrupt(saved,Hk3GraduationData::load,n->n.putString("Graduated","true"));
        corrupt(saved,Hk3GraduationData::load,n->n.getCompound("PassedPlayers").putBoolean("1-1-1-1-1",true));
        corrupt(saved,Hk3GraduationData::load,n->n.getCompound("PassedPlayers").putByte(A.toString(),(byte)2));
        var legacyGood=new CompoundTag();legacyGood.putBoolean("Graduated",true);
        check(!Hk3GraduationData.load(legacyGood).isGraduated(A),"旧全服结果只保留不授权");
        var bad=new Hk3BadEndingData();UUID meeting=bad.beginEncounter(A);bad.erase(A,meeting);bad.markReturned(A);
        for(int i=1;i<=4;i++)bad.advanceLine(A,i);
        var badSaved=disk(bad.save(new CompoundTag()));var restored=Hk3BadEndingData.load(badSaved);
        check(restored.line(A)==4&&restored.meeting(A).equals(meeting)&&restored.badCount(A)==1,"坏结局断点与历史完整");
        check(restored.getStage(B)==0,"坏结局不串人");
        reject(()->Hk3BadEndingData.load(new CompoundTag()));
        for(String field:List.of("Meeting","Stage","Returned","BadCount","Line"))
            corrupt(badSaved,Hk3BadEndingData::load,n->n.getCompound("Personal").getCompound(A.toString()).remove(field));
        corrupt(badSaved,Hk3BadEndingData::load,n->n.putString("AttackCount","错误类型"));
        corrupt(badSaved,Hk3BadEndingData::load,n->n.getCompound("Personal").getCompound(A.toString()).putByte("Returned",(byte)2));
    }
    private static final Map<String,Function<CompoundTag,? extends SavedData>> LOADERS=Map.of(
        "hk3gtl_phone_notes.dat",Hk3PhoneNotes::load,"hk3gtl_social.dat",Hk3SocialData::load,
        "hk3gtl_phone_v5.dat",Hk3PhoneData::load,"hk3gtl_graduation.dat",Hk3GraduationData::load,"hk3gtl_bad_ending.dat",Hk3BadEndingData::load);
    private static void guard()throws Exception{
        Path folder=Path.of("build","persistence-r136",UUID.randomUUID().toString());Files.createDirectories(folder);
        for(String file:LOADERS.keySet()){
            Path target=folder.resolve(file);byte[] bytes={31,-117,8,99};Files.write(target,bytes);
            reject(()->Hk3SavedDataGuard.freshIfMissing(target,()->{throw new AssertionError("损坏文件走了新档工厂");}));
            check(Arrays.equals(bytes,Files.readAllBytes(target)),"损坏磁盘字节保持原样");
        }
        check(Hk3SavedDataGuard.freshIfMissing(folder.resolve("new.dat"),Hk3PhoneNotes::new)!=null,"仅真正新档可空建");
    }
    @SuppressWarnings("unchecked") private static void transitions()throws Exception{
        var field=DialogueSessionManager.class.getDeclaredField("ACTIVE_SESSIONS");field.setAccessible(true);
        var active=(Map<UUID,DialogueSessionManager.DialogueSession>)field.get(null);
        active.put(A,new DialogueSessionManager.DialogueSession("preview","start",0));active.put(B,new DialogueSessionManager.DialogueSession("preview","start",0));
        DialogueSessionManager.onPlayerDisconnect(A);check(!DialogueSessionManager.hasActiveDialogue(A)&&DialogueSessionManager.hasActiveDialogue(B),"断线只清本人临时会话");
        DialogueSessionManager.clearForServerStop();check(!DialogueSessionManager.hasActiveDialogue(B),"停服清空旧会话");
        var rate=ResearchStateSyncRequestC2SPacket.class.getDeclaredField("LAST_ACCEPTED_TICK");rate.setAccessible(true);var limits=(Map<UUID,Integer>)rate.get(null);
        limits.put(A,5000);limits.put(B,3000);ResearchStateSyncRequestC2SPacket.clearRateLimit(A);check(limits.size()==1&&limits.containsKey(B),"重生限流只清本人");
        ResearchStateSyncRequestC2SPacket.clearForServerStop();check(limits.isEmpty(),"跨存档限流清空");
        var old=new CompoundTag();var nested=new CompoundTag();nested.putInt("record",4);old.put("hk3gtl_story",nested);old.putString("other_mod","保留其他模组");
        var next=new CompoundTag();Hk3PlayerDataCloneHandler.copyPersistentState(old,next);next.getCompound("hk3gtl_story").putInt("record",7);
        check(old.getCompound("hk3gtl_story").getInt("record")==4&&!next.contains("other_mod"),"死亡迁移深拷贝只含本模组");
        String lifecycle=Files.readString(Path.of("src/main/java/com/sirin/hk3gtl/common/dialogue/Hk3DialogueLifecycle.java"));
        check(lifecycle.contains("PlayerEvent.Clone")&&lifecycle.contains("PlayerChangedDimensionEvent")&&lifecycle.contains("ServerStoppedEvent"),"生产事件接线存在");
        String phone=Files.readString(Path.of("src/main/java/com/sirin/hk3gtl/client/phone/Hk3PhoneKey.java"));
        check(phone.contains("LoggingOut")&&phone.contains("Hk3PhoneScreen.reset()"),"客户端断线清通知与AI连接配置入口保留");
    }
    /** 指定实例已存在账本只读复核；输出统计，不打印信件、笔记或聊天内容。 */
    private static void auditExisting(Path saves)throws Exception{
        check(Files.isDirectory(saves),"目标存档目录存在");int files=0;var counts=new TreeMap<String,Integer>();
        try(var worlds=Files.list(saves)){
            for(Path world:worlds.filter(p->Files.isDirectory(p,LinkOption.NOFOLLOW_LINKS)).toList())for(var entry:LOADERS.entrySet()){
                Path file=world.resolve("data").resolve(entry.getKey());if(!Files.isRegularFile(file,LinkOption.NOFOLLOW_LINKS))continue;
                byte[] before=Files.readAllBytes(file);CompoundTag root;
                try(var input=new ByteArrayInputStream(before)){root=NbtIo.readCompressed(input);}
                check(root.contains("data",Tag.TAG_COMPOUND),"实际SavedData包装合法");entry.getValue().apply(root.getCompound("data"));
                check(Arrays.equals(before,Files.readAllBytes(file)),"实际存档只读不变");files++;counts.merge(entry.getKey(),1,Integer::sum);
            }
        }
        System.out.println("Existing save audit: "+files+" read-only files accepted; counts="+counts);
    }
}
