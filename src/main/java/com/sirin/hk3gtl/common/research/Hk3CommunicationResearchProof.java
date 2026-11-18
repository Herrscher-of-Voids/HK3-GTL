package com.sirin.hk3gtl.common.research;

 



import net.minecraft.nbt.CompoundTag;
import net.minecraft.server.level.ServerPlayer;
import java.nio.charset.StandardCharsets;
import java.util.UUID;

/**
 * 【文件职责】将服务端实际提交的首次回信记入当前团队的交流来源。
 * 不读背包或静态任务标记；已回复档案只投影交流前置，不代替HCCO实验和付款。
 */
 






public final class Hk3CommunicationResearchProof {
    private Hk3CommunicationResearchProof() {}
    /** 读取本存档真实回信账本；旧记录不补造原发生时间或原团队，记录此次核验时间。 */
    public static void reconcile(ServerPlayer player){
        if(!player.server.isSameThread())throw new IllegalStateException("Communication reconciliation must be on server thread");
        com.sirin.hk3gtl.common.communication.Hk3TeamContactService.ensure(player);
    }
    public static boolean project(com.sirin.hk3gtl.common.communication.Hk3CommunicationData communication,
            Hk3ResearchData research,UUID player,UUID scope,long observedTick){
        return false; // 旧个人答复仅归档，缺团队授权和原始归属，不能投影到任意新队。
    }
    public static void onReply(ServerPlayer player,boolean accepted){
        if(!player.server.isSameThread())throw new IllegalStateException("Communication settlement must be on server thread");
        reconcile(player);
    }
    /** 来源于唯一实际回信事件；独立路线与合作路线同等有效，不发材料或知识奖励。 */
    public static CompoundTag receipt(UUID player,UUID team,boolean accepted,long tick){
        var receipt=new CompoundTag();receipt.putUUID("Batch",UUID.nameUUIDFromBytes(
                ("first-contact-reply/"+player).getBytes(StandardCharsets.UTF_8)));
        receipt.putUUID("Team",team);receipt.putUUID("Actor",player);
        receipt.putString("Facility","communication:"+player);receipt.putString("Recipe","hk3gtl:first_contact_reply");receipt.putLong("Tick",tick);
        var input=new CompoundTag();input.putString("Letter","otto_first_contact");
        var output=new CompoundTag();output.putString("Reply",accepted?"accepted":"declined");
        receipt.put("Inputs",input);receipt.put("Outputs",output);return receipt;
    }
}

 
