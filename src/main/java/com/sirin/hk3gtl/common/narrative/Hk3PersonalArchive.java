package com.sirin.hk3gtl.common.narrative;

import com.sirin.hk3gtl.common.communication.*;
import com.sirin.hk3gtl.common.research.*;
import com.sirin.hk3gtl.common.review.*;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.server.level.ServerPlayer;

/**
 * 【变更记录 #1】2026-10-01 00:41:04（修订123）
 * 删除：无；新增：手机与卷轴共用的服务端本人经历投影。
 * 修改：研究读本队完成账本；交流读本人回执；审查读本人会面结算；旧节点仅作为收藏。
 * 用途：展示真实进度与缺项，不提供虚假的满级/终审许可，也不消费卷轴或生成他人经历。
 */
/** 【变更记录 #2】2026-10-01 00:59:10（修订124）：删除无；新增/修改：六组正式通信目录统一核验，包含教学附件，不把通信完成等同终审资格；用途：按五方交流系统整链收口，真实权限和本人经历不混用。 */
/** 【变更记录 #3】2026-10-01 01:54:14（修订127）：删除：被替代的旧分支；新增/修改：显示可选收藏数量并明确剧情档案回看不代替正式会面回执；用途：个人收藏与正式资格分离，保留历史记录。 */
/** 【变更记录 #4】2026-10-01 01:59:30（修订127）：删除：被替代的旧分支；新增/修改：每次打开卷轴附带本人已解锁节点快照，避免客户端缓存不同步；用途：个人收藏与正式资格分离，保留历史记录。 */
/** 【变更记录 #5】2026-10-01 16:49:18（修订135）：删除笼统终审未接说明；新增统一终审逐项查询；修改手机和卷轴共用已完成/未完成/等待接入三态；用途：工程来源未接不能显示成玩家未做，也不假装满级档案。 */
/** 【变更记录 #6】2026-10-01 20:33:47（修订148）：删除固定目录等待文案；新增/修改：手机与卷轴显示研究逐题和去重后的旧正式剧情缺项；用途：逐项核验本人经历，保留真实未接来源，不授予虚假资格。 */
/** 【变更记录 #7】2026-10-01 22:50:14（第7次备注 · 内测5修订155）：删除玩家展示中的旧电压及开发说明；新增现行正文投影或对应回归；修改仅限呈现与检索，不改变进度、回执、触发条件或权限；用途：统一发布版玩家文案，历史备注保留。 */
public final class Hk3PersonalArchive {
    private Hk3PersonalArchive() {}
    public static String summary(ServerPlayer player) {
        UUIDs ids=new UUIDs(player.getUUID(),Hk3ResearchTeams.scope(player.server,player.getUUID()));
        var research=Hk3ResearchData.get(player);
        long done=Hk3ResearchPlans.all().keySet().stream().filter(id->research.completed(ids.team,id)).count();
        var contacts=Hk3TeamContactData.get(player.server);
        var diplomacy=Hk3DiplomacyData.get(player.server);
        var personal=Hk3PersonalCommunicationData.get(player.server);
        var communication=Hk3CommunicationCompletion.status(contacts,personal,ids.actor);
        var text=new StringBuilder("研究 · 当前团队共享\n已完成 "+done+" / "+Hk3ResearchPlans.all().size()+" 项。\n\n个人正式交流\n");
        text.append("通信目录：").append(communication.completed()).append(" / 6 组。\n");
        text.append("奥托首次交流：").append(contacts.experienced(ids.actor)?"已有本人完成记录":"尚缺本人补谈").append("\n");
        if(contacts.settled(ids.team))text.append("本队首信补谈：").append(contacts.personalStep(ids.team,ids.actor)).append(" / ").append(Hk3TeamContactData.PERSONAL_STEPS).append(" 步；信件 → 奥托首信 → 个人补谈。\n");
        for(var topic:Hk3DiplomacyData.TOPICS){
            String name=topic.name();var path=diplomacy.personalPath(ids.team,topic.id());
            boolean history=personal.experienced(ids.actor,topic.id());
            text.append("\n").append(name).append("：").append(history?"已有本人历史经历":"尚无本人完成回执").append("。\n");
            if(path.isEmpty())text.append("本队当前路线尚未结算，等待来信、答复或真实资料提交。\n");
            else if(personal.completedCurrent(ids.actor,ids.team,topic.id(),diplomacy.version(ids.team,topic.id()),path))text.append("本队当前路线补谈已完成。\n");
            else {
                var n=personal.snapshot(ids.actor,ids.team,topic.id());
                boolean same=Hk3PersonalCommunicationData.valid(n)&&n.getInt("Version")==diplomacy.version(ids.team,topic.id())&&Hk3PersonalCommunicationData.documents(n).equals(path);
                text.append("本队当前路线待补谈：").append(same?n.getInt("Step"):0).append(" / ").append(path.size()).append(" 篇。手机信件 → ").append(name).append(" → 亲自补行本段交流。\n");
            }
        }
        var review=Hk3ReviewData.get(player.server);
        text.append("\n正式审查 · 本人会面记录\n一审：").append(review.experienced(ids.actor,Hk3ReviewLedger.Kind.FIRST)?"已完成":"未完成")
            .append("\n二审：").append(review.experienced(ids.actor,Hk3ReviewLedger.Kind.SECOND)?"已完成":"未完成")
            .append("\n\n档案与收藏\n");
        long legacy=Hk3NarrativeNodes.all().stream().filter(n->Hk3NarrativeLog.isUnlocked(player,n.id())).count();
        text.append("已收录：").append(legacy).append(" 篇。\n")
            .append("")
            .append("")
            .append("可以在手机或文明档案卷轴中重温这些经历。");
        text.append("\n\n收藏：").append(Hk3CollectionRecords.unlocked(player.getPersistentData(),"optional").size())
            .append(" / ").append(Hk3CollectionRecords.total("optional")).append(" 篇。");
        text.append("\n\n").append(com.sirin.hk3gtl.common.finale.Hk3FinaleAdmission.summary(player));
        text.append("\n\n").append(Hk3FormalArchive.summary(Hk3FormalArchive.evaluate(player)));
        return text.toString();
    }
    private record UUIDs(java.util.UUID actor,java.util.UUID team) {}
    public static int openCodex(ServerPlayer player) {
        boolean present=false;
        for(var stack:player.getInventory().items)if(stack.getItem() instanceof com.sirin.hk3gtl.common.item.NarrativeCodexItem){present=true;break;}
        if(player.getOffhandItem().getItem() instanceof com.sirin.hk3gtl.common.item.NarrativeCodexItem)present=true;
        if(!present)return 0;
        var view=new CompoundTag();view.putString("Mode","codex_progress");view.putString("Body",summary(player));
        var unlocked=new net.minecraft.nbt.ListTag();
        for(var node:Hk3CollectionRecords.unlocked(player.getPersistentData(),"all"))unlocked.add(net.minecraft.nbt.StringTag.valueOf(node.id()));
        view.put("Unlocked",unlocked);
        com.sirin.hk3gtl.common.network.Hk3Network.CHANNEL.send(net.minecraftforge.network.PacketDistributor.PLAYER.with(()->player),new com.sirin.hk3gtl.common.phone.Hk3PhonePacket(view));
        return 1;
    }
}

// 【变更记录 · 修订161】2026-10-17 14:11:55：本轮仅将活动类名、资源与工业配方引用迁移为长期业务命名；历史备注保留，不代表旧逻辑已全部按现行设计重写。
