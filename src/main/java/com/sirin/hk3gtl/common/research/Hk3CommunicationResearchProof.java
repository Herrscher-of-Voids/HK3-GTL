package com.sirin.hk3gtl.common.research;

/** 【变更记录 #2】2026-09-30 23:58:50（修订121）：删除旧个人答复自动代表新队的生产路径；新增/修改：停止旧个人回信投影，研究来源仅同步新团队真实结算；用途：团队外交、阅读与个人经历分账，不发研究或物品奖励。 */



import net.minecraft.nbt.CompoundTag;
import net.minecraft.server.level.ServerPlayer;
import java.nio.charset.StandardCharsets;
import java.util.UUID;

/**
 * 【文件职责】将服务端实际提交的首次回信记入当前团队的交流来源。
 * 不读背包或静态任务标记；已回复档案只投影交流前置，不代替HCCO实验和付款。
 */
/**
 * 【变更记录 #1】2026-09-29 23:37:35（内测5修订101）
 * 删除：本轮被替代的单前置或旧提示分支；其余历史保留。
 * 新增／修改：仅以服务端已确认回信账本提供交流前置，追溯核验不补造历史时间、不直接完成课题。
 * 用途：补足研究接线并如实保留未接物理执行器及结构审批边界。
 * 追溯：logs/research-mainline-r101；R101_FINAL_RECORD。
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

// 【变更记录 · 修订161】2026-10-17 14:11:55：本轮仅将活动类名、资源与工业配方引用迁移为长期业务命名；历史备注保留，不代表旧逻辑已全部按现行设计重写。
