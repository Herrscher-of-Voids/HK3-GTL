package com.sirin.hk3gtl.common.narrative;

import com.sirin.hk3gtl.common.communication.*;
import com.sirin.hk3gtl.common.research.*;
import com.sirin.hk3gtl.common.review.*;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.server.level.ServerPlayer;

 





 
 
 
 
 
 
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
        com.sirin.hk3gtl.common.easter.Hk3EggPhone.finaleInspection(player);
        return 1;
    }
}

 
