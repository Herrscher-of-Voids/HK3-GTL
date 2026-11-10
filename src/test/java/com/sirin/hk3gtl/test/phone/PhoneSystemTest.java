package com.sirin.hk3gtl.test.phone;

import com.sirin.hk3gtl.common.phone.Hk3PhoneData;
import com.sirin.hk3gtl.common.phone.Hk3NotificationQueue;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.nbt.NbtIo;
import java.util.UUID;

/**
 * 【变更记录 #1】2026-09-30 16:22:31（内测5修订110）
 * 删除：被新版通知读取流程替代的旧分支，历史备注保留。
 * 新增／修改：直接验证生产账本、NBT恢复、超过128条历史、读/处理分离、2秒合并、32队列与优先级，非游戏验收。
 * 用途：通知与业务结果分离，服务端授权和个人持久化；不改结构、贴图和贸易。
 */
/** 【变更记录 #2】2026-11-01 00:37:02（第2次备注 · 内测5修订192）：删除无；新增调用后台状态包传输与无发送者边界回归；修改保留原账本测试；用途：常规手机系统测试同时防止后台聊天轮询导致长篇阅读被踢。 */
public final class PhoneSystemTest {
    private static int checks;
    private static void check(boolean condition,String label){if(!condition)throw new AssertionError(label);checks++;}
    private static Hk3NotificationQueue.Notice notice(String id,String kind,int priority){return new Hk3NotificationQueue.Notice(id,id,"原文",kind,priority);}
    public static void main(String[] args)throws Exception{
        PhoneStatusPacketTest.main(args);
        UUID a=UUID.randomUUID(),b=UUID.randomUUID();var data=new Hk3PhoneData();
        check(data.install(a)&&!data.install(a)&&!data.installed(b),"安装资格个人隔离且幂等");
        for(int i=0;i<2000;i++)check(data.add(a,"event_"+i,"消息"+i,"正文"+i,i),"首次投递");
        check(data.count(a)==2000&&data.entry(a,"event_0")!=null,"超过128条不裁剪正式消息");
        check(!data.add(a,"event_0","重传","改写原文",9999),"重传不增加或覆盖");
        check(data.entry(a,"event_0").body().equals("正文0"),"正文保持原投递内容");
        check(data.count(b)==0&&data.entry(b,"event_0")==null,"其他玩家不能取得私人消息");
        check(data.page(a,0).size()==8&&data.page(a,0).get(0).id().equals("event_1999"),"倒序分页八条");
        check(data.page(a,249).get(7).id().equals("event_0"),"最早记录仍能分页读取");
        check(data.page(a,Integer.MAX_VALUE).isEmpty(),"大页号不整数溢出");
        check(data.unread(a)==2000,"读取列表不算已读");
        data.read(b,"event_0");check(!data.entry(a,"event_0").read(),"其他玩家确认不影响本人");
        data.read(a,"event_0");data.read(a,"event_0");check(data.unread(a)==1999,"确认已读幂等");
        data.add(a,"proposal","合作来信","阅读不等于接受",0,"letter","0",true);
        data.read(a,"proposal");check(data.count(a,"pending")==1&&data.entry(a,"proposal").pending(),"阅读不清待处理");
        data.resolve(a,"proposal");check(data.count(a,"pending")==0,"业务处理后才清待处理");
        var bytes=new java.io.ByteArrayOutputStream();NbtIo.writeCompressed(data.save(new CompoundTag()),bytes);
        var restored=Hk3PhoneData.load(NbtIo.readCompressed(new java.io.ByteArrayInputStream(bytes.toByteArray())));
        check(restored.count(a)==2001&&restored.unread(a)==1999&&restored.installed(a),"重启保留全部历史、已读和安装");
        check(!restored.add(a,"event_0","再次重传","",0),"恢复后仍防重");
        var legacy=data.save(new CompoundTag());var rows=legacy.getCompound("Users").getList(a.toString(),10);
        var old=new CompoundTag();old.putString("Id","first_contact_letter");old.putString("Title","旧首信");old.putString("Body","旧摘要");rows.add(old);
        var migrated=Hk3PhoneData.load(legacy);check(migrated.entry(a,"first_contact_letter").kind().equals("letter")&&migrated.entry(a,"first_contact_letter").pending(),"旧首信推导正文路由");
        var queue=new Hk3NotificationQueue();
        for(int i=0;i<100;i++)check(queue.offer(notice("r"+i,"research",1),1000+i),"研究独立事件入队");
        check(!queue.offer(notice("r0","research",1),1100),"客户端重传防重");
        check(queue.pendingGroups()==1&&queue.visible(2999,2).isEmpty(),"两秒内成果合并等待");
        check(queue.visible(3000,2).get(0).count()==100,"合并只影响浮层数量");
        check(queue.visible(8999,2).size()==1&&queue.visible(9000,2).isEmpty(),"约六秒后淡出");
        queue.clear();
        for(int i=0;i<40;i++)queue.offer(notice("n"+i,"notice",1),0);
        check(queue.pendingGroups()==32&&queue.overflowCount()==8,"32组队列上限及溢出计数");
        queue.offer(notice("action","letter",2),0);
        var shown=queue.visible(0,2);check(shown.size()==2&&shown.get(0).priority()==2,"待处理高优先");
        check(queue.visible(1,1).size()==1,"窄屏最多一张");
        int total=2; // 初次显示的两组中有一组因窄屏重新排队，按新的显示遍历独立验证溢出。
        queue.clear();for(int i=0;i<40;i++)queue.offer(notice("overflow"+i,"notice",1),0);
        total=0;for(int i=0;i<20;i++)for(var card:queue.visible(i*6000L,2))total+=card.count();
        check(total==40,"被合并到溢出的事件数量最终有汇总，不静默丢弃");
        queue.clear();queue.offer(notice("low","chatter",0),0);queue.offer(notice("normal","notice",1),0);queue.offer(notice("high","letter",2),0);
        shown=queue.visible(0,2);check(shown.get(0).priority()==2&&shown.get(1).priority()==1,"闲话最低优先");
        queue.clear();check(queue.visible(100000,2).isEmpty()&&queue.offer(notice("high","letter",2),100000),"断线清理全部队列和临时去重");
        check(data.unread(a)==1999,"浮层队列从未修改服务端未读状态");
        System.out.println("PhoneSystemTest: "+checks+" checks passed; live GUI and multiplayer acceptance pending");
    }
}
